"""
Serializers para as APIs do Kermartin 3.0
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para modelo Usuario"""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'username', 'nome_completo', 'oab_numero', 
            'oab_estado', 'telefone', 'escritorio', 'especialidades',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcessoSerializer(serializers.ModelSerializer):
    """Serializer para modelo Processo"""
    
    usuario_nome = serializers.CharField(source='usuario.nome_completo', read_only=True)
    total_documentos = serializers.SerializerMethodField()
    ultima_analise = serializers.SerializerMethodField()
    
    class Meta:
        model = Processo
        fields = [
            'id', 'titulo', 'numero_processo', 'tipo_crime', 'comarca', 'vara',
            'reu_nome', 'vitima_nome', 'status', 'observacoes',
            'usuario_nome', 'total_documentos', 'ultima_analise',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_documentos(self, obj):
        return obj.documentos.count()
    
    def get_ultima_analise(self, obj):
        ultima_sessao = obj.sessoes_analise.order_by('-created_at').first()
        if ultima_sessao:
            return {
                'id': str(ultima_sessao.id),
                'modo': ultima_sessao.get_modo_analise_display(),
                'status': ultima_sessao.get_status_display(),
                'data': ultima_sessao.created_at
            }
        return None


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para modelo Documento"""
    
    processo_titulo = serializers.CharField(source='processo.titulo', read_only=True)
    tamanho_formatado = serializers.SerializerMethodField()
    tem_texto_extraido = serializers.SerializerMethodField()
    
    class Meta:
        model = Documento
        fields = [
            'id', 'nome_arquivo', 'arquivo_original', 'tipo_documento',
            'texto_extraido', 'tamanho_arquivo', 'tamanho_formatado',
            'processo_titulo', 'tem_texto_extraido',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'texto_extraido', 'tamanho_arquivo', 'created_at', 'updated_at']
    
    def get_tamanho_formatado(self, obj):
        """Retorna tamanho formatado em KB/MB"""
        size = obj.tamanho_arquivo
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_tem_texto_extraido(self, obj):
        return bool(obj.texto_extraido)


class DocumentoUploadSerializer(serializers.ModelSerializer):
    """Serializer específico para upload de documentos"""
    
    class Meta:
        model = Documento
        fields = ['arquivo_original', 'tipo_documento', 'processo']
    
    def validate_arquivo_original(self, value):
        """Valida arquivo enviado"""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Apenas arquivos PDF são permitidos")
        
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("Arquivo muito grande. Máximo 10MB")
        
        return value


class SessaoAnaliseSerializer(serializers.ModelSerializer):
    """Serializer para modelo SessaoAnalise"""
    
    processo_titulo = serializers.CharField(source='processo.titulo', read_only=True)
    total_resultados = serializers.SerializerMethodField()
    tempo_total_formatado = serializers.SerializerMethodField()
    
    class Meta:
        model = SessaoAnalise
        fields = [
            'id', 'modo_analise', 'status', 'bloco_atual', 'subetapa_atual',
            'blocos_selecionados', 'configuracoes', 'processo_titulo',
            'total_resultados', 'tempo_inicio', 'tempo_fim', 'tempo_total_formatado',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tempo_inicio', 'tempo_fim', 'created_at', 'updated_at']
    
    def get_total_resultados(self, obj):
        return obj.resultados.count()
    
    def get_tempo_total_formatado(self, obj):
        if obj.tempo_total:
            total_seconds = obj.tempo_total.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        return None


class ResultadoAnaliseSerializer(serializers.ModelSerializer):
    """Serializer para modelo ResultadoAnalise"""
    
    documento_nome = serializers.CharField(source='documento.nome_arquivo', read_only=True)
    bloco_titulo = serializers.SerializerMethodField()
    tempo_formatado = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultadoAnalise
        fields = [
            'id', 'bloco', 'subetapa', 'resposta_ia', 'tokens_total',
            'tempo_processamento', 'modelo_usado', 'documento_nome',
            'bloco_titulo', 'tempo_formatado', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_bloco_titulo(self, obj):
        """Retorna título do bloco/subetapa"""
        from ai_engine.prompts import get_prompt_title
        try:
            return get_prompt_title(obj.bloco, obj.subetapa)
        except:
            return f"Bloco {obj.bloco} - Subetapa {obj.subetapa}"
    
    def get_tempo_formatado(self, obj):
        """Retorna tempo formatado"""
        return f"{obj.tempo_processamento:.2f}s"


class IniciarAnaliseSerializer(serializers.Serializer):
    """Serializer para iniciar análise"""
    
    processo_id = serializers.UUIDField()
    modo_analise = serializers.ChoiceField(
        choices=['individual', 'completa', 'personalizada']
    )
    blocos_selecionados = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=4),
        required=False,
        allow_empty=False
    )
    bloco = serializers.IntegerField(min_value=1, max_value=4, required=False)
    subetapa = serializers.IntegerField(min_value=1, max_value=6, required=False)
    
    def validate(self, data):
        """Validação customizada"""
        modo = data['modo_analise']
        
        if modo == 'individual':
            if not data.get('bloco') or not data.get('subetapa'):
                raise serializers.ValidationError(
                    "Para análise individual, bloco e subetapa são obrigatórios"
                )
        
        elif modo == 'personalizada':
            if not data.get('blocos_selecionados'):
                raise serializers.ValidationError(
                    "Para análise personalizada, blocos_selecionados é obrigatório"
                )
        
        return data


class MenuInterativoSerializer(serializers.Serializer):
    """Serializer para menu interativo"""
    
    opcao = serializers.IntegerField(min_value=1, max_value=5)
    confirmacao = serializers.CharField(max_length=1, required=False)
    processo_id = serializers.UUIDField(required=False)
    
    def validate_opcao(self, value):
        """Valida opção do menu"""
        opcoes_validas = [1, 2, 3, 4, 5]
        if value not in opcoes_validas:
            raise serializers.ValidationError("Opção inválida")
        return value
    
    def validate_confirmacao(self, value):
        """Valida confirmação"""
        if value and value.upper() not in ['S', 'N', 'M']:
            raise serializers.ValidationError("Confirmação deve ser S, N ou M")
        return value.upper() if value else None


class EstatisticasSerializer(serializers.Serializer):
    """Serializer para estatísticas do sistema"""
    
    total_processos = serializers.IntegerField()
    total_documentos = serializers.IntegerField()
    total_analises = serializers.IntegerField()
    tokens_utilizados = serializers.IntegerField()
    tempo_total_analises = serializers.CharField()
    
    processos_por_status = serializers.DictField()
    analises_por_bloco = serializers.DictField()
    documentos_por_tipo = serializers.DictField()
    
    ultima_atividade = serializers.DateTimeField()
    media_tempo_analise = serializers.FloatField()
