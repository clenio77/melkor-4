"""
Configuração do Django Admin para Kermartin 3.0
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise, LogSeguranca


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Admin para modelo Usuario"""
    
    list_display = ['nome_completo', 'oab_numero', 'oab_estado', 'email', 'telefone', 'created_at']
    list_filter = ['oab_estado', 'created_at']
    search_fields = ['nome_completo', 'oab_numero', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('user', 'nome_completo', 'telefone')
        }),
        ('Informações Profissionais', {
            'fields': ('oab_numero', 'oab_estado', 'escritorio', 'especialidades')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    """Admin para modelo Processo"""
    
    list_display = ['titulo', 'numero_processo', 'tipo_crime', 'status', 'usuario_nome', 'created_at']
    list_filter = ['tipo_crime', 'status', 'created_at', 'comarca']
    search_fields = ['titulo', 'numero_processo', 'reu_nome', 'vitima_nome']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'titulo', 'numero_processo', 'status')
        }),
        ('Detalhes do Crime', {
            'fields': ('tipo_crime', 'comarca', 'vara')
        }),
        ('Pessoas Envolvidas', {
            'fields': ('reu_nome', 'vitima_nome')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def usuario_nome(self, obj):
        return obj.usuario.nome_completo
    usuario_nome.short_description = 'Advogado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Admin para modelo Documento"""
    
    list_display = ['nome_arquivo', 'tipo_documento', 'processo_titulo', 'tamanho_formatado', 'tem_texto', 'created_at']
    list_filter = ['tipo_documento', 'created_at']
    search_fields = ['nome_arquivo', 'processo__titulo']
    readonly_fields = ['id', 'hash_arquivo', 'tamanho_arquivo', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações do Arquivo', {
            'fields': ('processo', 'nome_arquivo', 'arquivo_original', 'tipo_documento')
        }),
        ('Conteúdo Extraído', {
            'fields': ('texto_extraido',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('hash_arquivo', 'tamanho_arquivo', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def processo_titulo(self, obj):
        return obj.processo.titulo
    processo_titulo.short_description = 'Processo'
    
    def tamanho_formatado(self, obj):
        size = obj.tamanho_arquivo
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    tamanho_formatado.short_description = 'Tamanho'
    
    def tem_texto(self, obj):
        if obj.texto_extraido:
            return format_html('<span style="color: green;">✓ Sim</span>')
        return format_html('<span style="color: red;">✗ Não</span>')
    tem_texto.short_description = 'Texto Extraído'


@admin.register(SessaoAnalise)
class SessaoAnaliseAdmin(admin.ModelAdmin):
    """Admin para modelo SessaoAnalise"""
    
    list_display = ['processo_titulo', 'modo_analise', 'status', 'bloco_atual', 'subetapa_atual', 'tempo_total_formatado', 'created_at']
    list_filter = ['modo_analise', 'status', 'created_at']
    search_fields = ['processo__titulo']
    readonly_fields = ['id', 'tempo_inicio', 'tempo_fim', 'tempo_total', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Configuração da Análise', {
            'fields': ('processo', 'modo_analise', 'status')
        }),
        ('Progresso', {
            'fields': ('bloco_atual', 'subetapa_atual', 'blocos_selecionados')
        }),
        ('Configurações Avançadas', {
            'fields': ('configuracoes',),
            'classes': ('collapse',)
        }),
        ('Tempo de Execução', {
            'fields': ('tempo_inicio', 'tempo_fim', 'tempo_total'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def processo_titulo(self, obj):
        return obj.processo.titulo
    processo_titulo.short_description = 'Processo'
    
    def tempo_total_formatado(self, obj):
        if obj.tempo_total:
            total_seconds = obj.tempo_total.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        return "-"
    tempo_total_formatado.short_description = 'Tempo Total'


@admin.register(ResultadoAnalise)
class ResultadoAnaliseAdmin(admin.ModelAdmin):
    """Admin para modelo ResultadoAnalise"""
    
    list_display = ['sessao_processo', 'bloco', 'subetapa', 'documento_nome', 'tokens_total', 'tempo_processamento', 'modelo_usado', 'created_at']
    list_filter = ['bloco', 'subetapa', 'modelo_usado', 'created_at']
    search_fields = ['documento__nome_arquivo', 'sessao__processo__titulo']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('sessao', 'documento', 'bloco', 'subetapa')
        }),
        ('Prompt e Resposta', {
            'fields': ('prompt_usado', 'resposta_ia')
        }),
        ('Métricas', {
            'fields': ('tokens_prompt', 'tokens_resposta', 'tokens_total', 'tempo_processamento', 'modelo_usado')
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def sessao_processo(self, obj):
        return obj.sessao.processo.titulo
    sessao_processo.short_description = 'Processo'
    
    def documento_nome(self, obj):
        return obj.documento.nome_arquivo
    documento_nome.short_description = 'Documento'


@admin.register(LogSeguranca)
class LogSegurancaAdmin(admin.ModelAdmin):
    """Admin para modelo LogSeguranca"""
    
    list_display = ['tipo_evento', 'usuario_nome', 'ip_address', 'descricao_resumida', 'created_at']
    list_filter = ['tipo_evento', 'created_at']
    search_fields = ['descricao', 'ip_address', 'usuario__nome_completo']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Evento', {
            'fields': ('tipo_evento', 'descricao')
        }),
        ('Usuário e Localização', {
            'fields': ('usuario', 'ip_address', 'user_agent')
        }),
        ('Dados Extras', {
            'fields': ('dados_extras',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def usuario_nome(self, obj):
        if obj.usuario:
            return obj.usuario.nome_completo
        return "Anônimo"
    usuario_nome.short_description = 'Usuário'
    
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 50:
            return obj.descricao[:50] + "..."
        return obj.descricao
    descricao_resumida.short_description = 'Descrição'


# Customização do Admin Site
admin.site.site_header = "Kermartin 3.0 - Administração"
admin.site.site_title = "Kermartin 3.0"
admin.site.index_title = "Sistema de Análise Jurídica"

# Adicionar ações personalizadas
def marcar_como_concluido(modeladmin, request, queryset):
    """Marca processos como concluídos"""
    queryset.update(status='completed')
    modeladmin.message_user(request, f"{queryset.count()} processos marcados como concluídos.")

marcar_como_concluido.short_description = "Marcar processos selecionados como concluídos"

ProcessoAdmin.actions = [marcar_como_concluido]
