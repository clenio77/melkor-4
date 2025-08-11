"""
URLs do AI Engine - Kermartin 3.0
"""

from django.urls import path
from .views import (
    ProcessarDocumentoView, AnaliseIndividualView,
    AnaliseCompletaView, StatusSegurancaView,
    JurisprudenciaSearchView, JurisprudenciaSugestoesView, JurisprudenciaHealthView, InfraHealthView,
)

app_name = 'ai_engine'

urlpatterns = [
    path('processar-documento/', ProcessarDocumentoView.as_view(), name='processar_documento'),
    path('analise-individual/', AnaliseIndividualView.as_view(), name='analise_individual'),
    path('analise-completa/', AnaliseCompletaView.as_view(), name='analise_completa'),
    path('status-seguranca/', StatusSegurancaView.as_view(), name='status_seguranca'),
    # Jurisprudência (GraphRAG-ready): provider=? simple|graph|hybrid
    path('jurisprudencia/search/', JurisprudenciaSearchView.as_view(), name='jurisprudencia_search'),
    path('jurisprudencia/sugestoes/', JurisprudenciaSugestoesView.as_view(), name='jurisprudencia_sugestoes'),
    path('jurisprudencia/health/', JurisprudenciaHealthView.as_view(), name='jurisprudencia_health'),
    path('infra/health/', InfraHealthView.as_view(), name='infra_health'),
]
