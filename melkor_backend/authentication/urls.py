"""
URLs do app Authentication
"""

from django.urls import path
from .views import RegisterView, ProfileView

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
