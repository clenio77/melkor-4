"""
URLs do AI Engine - Melkor 3.0
"""

from django.urls import path
from .views import (
    ProcessarDocumentoView, AnaliseIndividualView, 
    AnaliseCompletaView, StatusSegurancaView
)

app_name = 'ai_engine'

urlpatterns = [
    path('processar-documento/', ProcessarDocumentoView.as_view(), name='processar_documento'),
    path('analise-individual/', AnaliseIndividualView.as_view(), name='analise_individual'),
    path('analise-completa/', AnaliseCompletaView.as_view(), name='analise_completa'),
    path('status-seguranca/', StatusSegurancaView.as_view(), name='status_seguranca'),
]
