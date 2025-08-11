from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JurisprudenciaViewSet

router = DefaultRouter()
router.register(r'jurisprudencias', JurisprudenciaViewSet, basename='jurisprudencia')

urlpatterns = [
    path('', include(router.urls)),
]

