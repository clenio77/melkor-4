"""
Testes para modelos do Melkor 3.0
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise, LogSeguranca


class TestUsuarioModel(TestCase):
    """Testes para modelo Usuario"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
    
    def test_criar_usuario(self):
        """Testa criação de usuário"""
        usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP",
            telefone="(11) 99999-9999",
            escritorio="Silva & Associados"
        )
        
        self.assertEqual(usuario.nome_completo, "Dr. João Silva")
        self.assertEqual(usuario.oab_numero, "123456")
        self.assertEqual(usuario.oab_estado, "SP")
        self.assertEqual(str(usuario), "Dr. João Silva - OAB 123456/SP")
    
    def test_usuario_unique_oab(self):
        """Testa unicidade do número da OAB"""
        Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        
        # Criar outro usuário
        user2 = User.objects.create_user(
            username="test2@melkor.com",
            email="test2@melkor.com",
            password="senha123"
        )
        
        # Deve dar erro ao tentar usar mesmo número OAB
        with self.assertRaises(Exception):
            Usuario.objects.create(
                user=user2,
                nome_completo="Dr. Maria Santos",
                oab_numero="123456",  # Mesmo número
                oab_estado="RJ"
            )


class TestProcessoModel(TestCase):
    """Testes para modelo Processo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
    
    def test_criar_processo(self):
        """Testa criação de processo"""
        processo = Processo.objects.create(
            usuario=self.usuario,
            titulo="Homicídio Qualificado - Caso Teste",
            numero_processo="0001234-56.2024.8.26.0001",
            tipo_crime="homicidio",
            comarca="São Paulo",
            vara="1ª Vara do Tribunal do Júri",
            reu_nome="João da Silva",
            vitima_nome="Maria Santos"
        )
        
        self.assertEqual(processo.titulo, "Homicídio Qualificado - Caso Teste")
        self.assertEqual(processo.tipo_crime, "homicidio")
        self.assertEqual(processo.status, "draft")  # Status padrão
        self.assertEqual(str(processo), "Homicídio Qualificado - Caso Teste - 0001234-56.2024.8.26.0001")
    
    def test_processo_choices(self):
        """Testa choices dos campos"""
        processo = Processo.objects.create(
            usuario=self.usuario,
            titulo="Teste",
            tipo_crime="latrocinio",
            status="analyzing"
        )
        
        self.assertEqual(processo.get_tipo_crime_display(), "Latrocínio")
        self.assertEqual(processo.get_status_display(), "Em Análise")


class TestDocumentoModel(TestCase):
    """Testes para modelo Documento"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        self.processo = Processo.objects.create(
            usuario=self.usuario,
            titulo="Processo Teste"
        )
    
    def test_criar_documento(self):
        """Testa criação de documento"""
        # Simular arquivo PDF
        arquivo_fake = SimpleUploadedFile(
            "inquerito.pdf",
            b"conteudo do pdf",
            content_type="application/pdf"
        )
        
        documento = Documento.objects.create(
            processo=self.processo,
            nome_arquivo="inquerito.pdf",
            arquivo_original=arquivo_fake,
            tipo_documento="inquerito",
            texto_extraido="Texto extraído do PDF",
            tamanho_arquivo=1024
        )
        
        self.assertEqual(documento.nome_arquivo, "inquerito.pdf")
        self.assertEqual(documento.tipo_documento, "inquerito")
        self.assertEqual(documento.get_tipo_documento_display(), "Inquérito Policial")
        self.assertTrue(documento.texto_extraido)


class TestSessaoAnaliseModel(TestCase):
    """Testes para modelo SessaoAnalise"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        self.processo = Processo.objects.create(
            usuario=self.usuario,
            titulo="Processo Teste"
        )
    
    def test_criar_sessao_analise(self):
        """Testa criação de sessão de análise"""
        sessao = SessaoAnalise.objects.create(
            processo=self.processo,
            modo_analise="individual",
            blocos_selecionados=[1, 2],
            configuracoes={"teste": "valor"}
        )
        
        self.assertEqual(sessao.modo_analise, "individual")
        self.assertEqual(sessao.status, "iniciada")  # Status padrão
        self.assertEqual(sessao.bloco_atual, 1)  # Valor padrão
        self.assertEqual(sessao.blocos_selecionados, [1, 2])
    
    def test_finalizar_sessao(self):
        """Testa finalização de sessão"""
        sessao = SessaoAnalise.objects.create(
            processo=self.processo,
            modo_analise="completa"
        )
        
        # Finalizar sessão
        sessao.finalizar_sessao()
        
        self.assertEqual(sessao.status, "concluida")
        self.assertIsNotNone(sessao.tempo_fim)
        self.assertIsNotNone(sessao.tempo_total)


class TestResultadoAnaliseModel(TestCase):
    """Testes para modelo ResultadoAnalise"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        self.processo = Processo.objects.create(
            usuario=self.usuario,
            titulo="Processo Teste"
        )
        self.documento = Documento.objects.create(
            processo=self.processo,
            nome_arquivo="teste.pdf",
            tipo_documento="inquerito"
        )
        self.sessao = SessaoAnalise.objects.create(
            processo=self.processo,
            modo_analise="individual"
        )
    
    def test_criar_resultado_analise(self):
        """Testa criação de resultado de análise"""
        resultado = ResultadoAnalise.objects.create(
            sessao=self.sessao,
            documento=self.documento,
            bloco=1,
            subetapa=1,
            prompt_usado="Prompt de teste",
            resposta_ia="Resposta da IA",
            tokens_total=1000,
            tempo_processamento=2.5
        )
        
        self.assertEqual(resultado.bloco, 1)
        self.assertEqual(resultado.subetapa, 1)
        self.assertEqual(resultado.tokens_total, 1000)
        self.assertEqual(resultado.tempo_processamento, 2.5)
    
    def test_unique_together(self):
        """Testa constraint unique_together"""
        # Criar primeiro resultado
        ResultadoAnalise.objects.create(
            sessao=self.sessao,
            documento=self.documento,
            bloco=1,
            subetapa=1,
            prompt_usado="Prompt 1",
            resposta_ia="Resposta 1"
        )
        
        # Tentar criar resultado duplicado deve dar erro
        with self.assertRaises(Exception):
            ResultadoAnalise.objects.create(
                sessao=self.sessao,
                documento=self.documento,
                bloco=1,  # Mesmo bloco
                subetapa=1,  # Mesma subetapa
                prompt_usado="Prompt 2",
                resposta_ia="Resposta 2"
            )


class TestLogSegurancaModel(TestCase):
    """Testes para modelo LogSeguranca"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@melkor.com",
            email="test@melkor.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
    
    def test_criar_log_seguranca(self):
        """Testa criação de log de segurança"""
        log = LogSeguranca.objects.create(
            usuario=self.usuario,
            tipo_evento="login_sucesso",
            descricao="Login realizado com sucesso",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0...",
            dados_extras={"teste": "valor"}
        )
        
        self.assertEqual(log.tipo_evento, "login_sucesso")
        self.assertEqual(log.ip_address, "192.168.1.1")
        self.assertEqual(log.dados_extras, {"teste": "valor"})
        self.assertEqual(log.get_tipo_evento_display(), "Login Bem-sucedido")
    
    def test_log_sem_usuario(self):
        """Testa log sem usuário (para eventos anônimos)"""
        log = LogSeguranca.objects.create(
            tipo_evento="prompt_injection",
            descricao="Tentativa de prompt injection detectada",
            ip_address="192.168.1.100"
        )
        
        self.assertIsNone(log.usuario)
        self.assertEqual(log.tipo_evento, "prompt_injection")
