"""
URLs do app Core - Melkor 3.0
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, ProcessoViewSet, DocumentoViewSet,
    AnaliseViewSet, MenuViewSet, EstatisticasViewSet
)

app_name = 'core'

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'processos', ProcessoViewSet, basename='processo')
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'analises', AnaliseViewSet, basename='analise')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'estatisticas', EstatisticasViewSet, basename='estatisticas')

urlpatterns = [
    path('', include(router.urls)),
]
