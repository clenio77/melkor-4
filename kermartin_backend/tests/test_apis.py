"""
Testes para APIs do Kermartin 3.0
"""

import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Usuario, Processo, Documento


class TestAuthenticationAPI(APITestCase):
    """Testes para APIs de autenticação"""
    
    def test_register_user(self):
        """Testa registro de usuário"""
        url = reverse('authentication:register')
        data = {
            "email": "test@kermartin.com",
            "password": "senha123",
            "nome_completo": "Dr. João Silva",
            "oab_numero": "123456",
            "oab_estado": "SP",
            "telefone": "(11) 99999-9999"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('user_id', response.data)
        
        # Verificar se usuário foi criado
        self.assertTrue(User.objects.filter(email="test@kermartin.com").exists())
        self.assertTrue(Usuario.objects.filter(oab_numero="123456").exists())
    
    def test_login_user(self):
        """Testa login de usuário"""
        # Criar usuário primeiro
        user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
            password="senha123"
        )
        
        url = reverse('token_obtain_pair')
        data = {
            "username": "test@kermartin.com",
            "password": "senha123"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class TestMenuAPI(APITestCase):
    """Testes para API do menu"""
    
    def test_menu_opcoes(self):
        """Testa endpoint de opções do menu"""
        url = reverse('core:menu-opcoes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se tem 5 opções
        self.assertEqual(len(response.data), 5)
        
        # Verificar estrutura das opções
        for opcao_num, opcao_data in response.data.items():
            self.assertIn('titulo', opcao_data)
            self.assertIn('descricao', opcao_data)
            self.assertIn('subetapas', opcao_data)
    
    def test_menu_processar(self):
        """Testa processamento de opção do menu"""
        url = reverse('core:menu-processar')
        data = {"opcao": 1}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo'], 'bloco_individual')
        self.assertEqual(response.data['bloco'], 1)


class TestProcessoAPI(APITestCase):
    """Testes para API de processos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        
        # Autenticar usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_criar_processo(self):
        """Testa criação de processo"""
        url = reverse('core:processo-list')
        data = {
            "titulo": "Homicídio Qualificado - Teste",
            "numero_processo": "0001234-56.2024.8.26.0001",
            "tipo_crime": "homicidio",
            "comarca": "São Paulo",
            "reu_nome": "João da Silva"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], "Homicídio Qualificado - Teste")
        self.assertEqual(response.data['tipo_crime'], "homicidio")
    
    def test_listar_processos(self):
        """Testa listagem de processos"""
        # Criar processo
        Processo.objects.create(
            usuario=self.usuario,
            titulo="Processo Teste"
        )
        
        url = reverse('core:processo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], "Processo Teste")
    
    def test_processo_sem_autenticacao(self):
        """Testa acesso sem autenticação"""
        self.client.credentials()  # Remove autenticação
        
        url = reverse('core:processo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDocumentoAPI(APITestCase):
    """Testes para API de documentos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
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
        
        # Autenticar usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_listar_documentos(self):
        """Testa listagem de documentos"""
        # Criar documento
        Documento.objects.create(
            processo=self.processo,
            nome_arquivo="teste.pdf",
            tipo_documento="inquerito"
        )
        
        url = reverse('core:documento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome_arquivo'], "teste.pdf")


class TestAnaliseAPI(APITestCase):
    """Testes para API de análises"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
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
            tipo_documento="inquerito",
            texto_extraido="Texto extraído do PDF"
        )
        
        # Autenticar usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_iniciar_analise_individual_validation(self):
        """Testa validação para análise individual"""
        url = reverse('core:analise-iniciar')
        
        # Dados incompletos
        data = {
            "processo_id": str(self.processo.id),
            "modo_analise": "individual"
            # Faltam bloco e subetapa
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bloco e subetapa são obrigatórios', str(response.data))
    
    def test_iniciar_analise_personalizada_validation(self):
        """Testa validação para análise personalizada"""
        url = reverse('core:analise-iniciar')
        
        # Dados incompletos
        data = {
            "processo_id": str(self.processo.id),
            "modo_analise": "personalizada"
            # Falta blocos_selecionados
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('blocos_selecionados é obrigatório', str(response.data))


class TestEstatisticasAPI(APITestCase):
    """Testes para API de estatísticas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
            password="senha123"
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo="Dr. João Silva",
            oab_numero="123456",
            oab_estado="SP"
        )
        
        # Autenticar usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_dashboard_estatisticas(self):
        """Testa endpoint de estatísticas do dashboard"""
        url = reverse('core:estatisticas-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estrutura da resposta
        expected_fields = [
            'total_processos', 'total_documentos', 'total_analises',
            'tokens_utilizados', 'tempo_total_analises', 'processos_por_status',
            'analises_por_bloco', 'documentos_por_tipo', 'media_tempo_analise'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)


class TestSecurityAPI(APITestCase):
    """Testes para segurança das APIs"""
    
    def test_rate_limiting_simulation(self):
        """Simula teste de rate limiting"""
        # Este teste seria mais complexo em um ambiente real
        # Aqui apenas verificamos se o endpoint existe
        
        user = User.objects.create_user(
            username="test@kermartin.com",
            email="test@kermartin.com",
            password="senha123"
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:menu-opcoes')
        
        # Fazer várias requisições
        for i in range(5):
            response = self.client.get(url)
            # Primeiras requisições devem funcionar
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_token(self):
        """Testa acesso com token inválido"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token-invalido')
        
        url = reverse('core:processo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
