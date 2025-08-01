"""
Modelos principais do Melkor 3.0
Sistema de análise jurídica especializado em Tribunal do Júri
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class Usuario(models.Model):
    """Perfil estendido do usuário advogado"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome_completo = models.CharField(max_length=200)
    oab_numero = models.CharField(max_length=20, unique=True)
    oab_estado = models.CharField(max_length=2)
    telefone = models.CharField(max_length=20, blank=True)
    escritorio = models.CharField(max_length=200, blank=True)
    especialidades = models.TextField(blank=True, help_text="Especialidades jurídicas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome_completo} - OAB {self.oab_numero}/{self.oab_estado}"


class Processo(models.Model):
    """Processo penal no sistema"""
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('analyzing', 'Em Análise'),
        ('completed', 'Concluído'),
        ('archived', 'Arquivado'),
    ]
    
    TIPO_CRIME_CHOICES = [
        ('homicidio', 'Homicídio'),
        ('latrocinio', 'Latrocínio'),
        ('estupro', 'Estupro'),
        ('roubo', 'Roubo'),
        ('trafico', 'Tráfico de Drogas'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='processos')
    
    titulo = models.CharField(max_length=300)
    numero_processo = models.CharField(max_length=50, blank=True)
    tipo_crime = models.CharField(max_length=20, choices=TIPO_CRIME_CHOICES, blank=True)
    comarca = models.CharField(max_length=100, blank=True)
    vara = models.CharField(max_length=100, blank=True)
    
    reu_nome = models.CharField(max_length=200, blank=True)
    vitima_nome = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    observacoes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processos'
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} - {self.numero_processo}"


class Documento(models.Model):
    """Documentos anexados aos processos"""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('inquerito', 'Inquérito Policial'),
        ('denuncia', 'Denúncia'),
        ('resposta_acusacao', 'Resposta à Acusação'),
        ('sentencia_pronuncia', 'Sentença de Pronúncia'),
        ('alegacoes_finais', 'Alegações Finais'),
        ('ata_julgamento', 'Ata de Julgamento'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='documentos')
    
    nome_arquivo = models.CharField(max_length=255)
    arquivo_original = models.FileField(
        upload_to='documentos/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    
    texto_extraido = models.TextField(blank=True)
    hash_arquivo = models.CharField(max_length=64, blank=True)  # SHA-256
    tamanho_arquivo = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome_arquivo} - {self.get_tipo_documento_display()}"


class SessaoAnalise(models.Model):
    """Sessão de análise do Melkor"""
    
    MODO_CHOICES = [
        ('individual', 'Análise Individual'),
        ('completa', 'Análise Completa'),
        ('personalizada', 'Análise Personalizada'),
    ]
    
    STATUS_CHOICES = [
        ('iniciada', 'Iniciada'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='sessoes_analise')
    
    modo_analise = models.CharField(max_length=20, choices=MODO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='iniciada')
    
    bloco_atual = models.PositiveIntegerField(default=1)
    subetapa_atual = models.PositiveIntegerField(default=1)
    
    blocos_selecionados = models.JSONField(default=list)  # [1, 2, 3, 4]
    configuracoes = models.JSONField(default=dict)
    
    tempo_inicio = models.DateTimeField(auto_now_add=True)
    tempo_fim = models.DateTimeField(null=True, blank=True)
    tempo_total = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sessoes_analise'
        verbose_name = 'Sessão de Análise'
        verbose_name_plural = 'Sessões de Análise'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Análise {self.get_modo_analise_display()} - {self.processo.titulo}"
    
    def finalizar_sessao(self):
        """Finaliza a sessão de análise"""
        self.tempo_fim = timezone.now()
        self.tempo_total = self.tempo_fim - self.tempo_inicio
        self.status = 'concluida'
        self.save()


class ResultadoAnalise(models.Model):
    """Resultados das análises por bloco/subetapa"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(SessaoAnalise, on_delete=models.CASCADE, related_name='resultados')
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='analises')
    
    bloco = models.PositiveIntegerField()  # 1-4
    subetapa = models.PositiveIntegerField()  # 1-6
    
    prompt_usado = models.TextField()
    resposta_ia = models.TextField()
    
    tokens_prompt = models.PositiveIntegerField(default=0)
    tokens_resposta = models.PositiveIntegerField(default=0)
    tokens_total = models.PositiveIntegerField(default=0)
    
    tempo_processamento = models.FloatField(default=0.0)  # segundos
    modelo_usado = models.CharField(max_length=50, default='gpt-4-1106-preview')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resultados_analise'
        verbose_name = 'Resultado de Análise'
        verbose_name_plural = 'Resultados de Análise'
        ordering = ['bloco', 'subetapa', '-created_at']
        unique_together = ['sessao', 'documento', 'bloco', 'subetapa']
    
    def __str__(self):
        return f"Bloco {self.bloco}.{self.subetapa} - {self.documento.nome_arquivo}"


class LogSeguranca(models.Model):
    """Log de eventos de segurança"""
    
    TIPO_EVENTO_CHOICES = [
        ('login_sucesso', 'Login Bem-sucedido'),
        ('login_falha', 'Falha no Login'),
        ('prompt_injection', 'Tentativa de Prompt Injection'),
        ('upload_suspeito', 'Upload Suspeito'),
        ('acesso_negado', 'Acesso Negado'),
        ('erro_sistema', 'Erro do Sistema'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    descricao = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    dados_extras = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'logs_seguranca'
        verbose_name = 'Log de Segurança'
        verbose_name_plural = 'Logs de Segurança'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.created_at}"
