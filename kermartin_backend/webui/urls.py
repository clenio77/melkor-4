from django.urls import path
from . import views

app_name = 'webui'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('processos/novo/', views.novo_processo, name='novo_processo'),
    path('documentos/upload/<uuid:processo_id>/', views.upload_documento, name='upload_documento'),
    path('analise/iniciar/<uuid:processo_id>/', views.iniciar_analise, name='iniciar_analise'),
    path('analise/resultado/<uuid:sessao_id>/', views.ver_resultado, name='ver_resultado'),
]
