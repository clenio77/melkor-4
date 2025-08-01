"""
Views de autenticação
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from core.models import Usuario


class RegisterView(APIView):
    """View para registro de usuários"""
    
    def post(self, request):
        """Registra novo usuário"""
        
        data = request.data
        required_fields = ['email', 'password', 'nome_completo', 'oab_numero', 'oab_estado']
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} é obrigatório'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Criar usuário Django
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password']
            )
            
            # Criar perfil estendido
            usuario = Usuario.objects.create(
                user=user,
                nome_completo=data['nome_completo'],
                oab_numero=data['oab_numero'],
                oab_estado=data['oab_estado'],
                telefone=data.get('telefone', ''),
                escritorio=data.get('escritorio', '')
            )
            
            return Response({
                'success': True,
                'message': 'Usuário criado com sucesso',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    """View para perfil do usuário"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retorna perfil do usuário"""
        
        try:
            usuario = Usuario.objects.get(user=request.user)
            
            return Response({
                'id': usuario.id,
                'email': request.user.email,
                'nome_completo': usuario.nome_completo,
                'oab_numero': usuario.oab_numero,
                'oab_estado': usuario.oab_estado,
                'telefone': usuario.telefone,
                'escritorio': usuario.escritorio
            })
            
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Perfil não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
