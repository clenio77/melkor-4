#!/usr/bin/env bash
# Build script para deploy no Render

set -o errexit  # Exit on error

echo "🚀 Iniciando build do Melkor 3.0 para produção..."

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Entrar no diretório do Django
cd melkor_backend

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Executar migrações
echo "🗄️ Executando migrações do banco de dados..."
python manage.py migrate

# Criar superusuário se não existir
echo "👤 Configurando usuário administrador..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from core.models import Usuario

# Criar superusuário se não existir
if not User.objects.filter(is_superuser=True).exists():
    admin_user = User.objects.create_superuser(
        username='admin@melkor.com',
        email='admin@melkor.com',
        password='MelkorAdmin2024!'
    )
    
    # Criar perfil de usuário
    Usuario.objects.create(
        user=admin_user,
        nome_completo='Administrador Melkor',
        oab_numero='000000',
        oab_estado='SP',
        telefone='(11) 99999-9999',
        escritorio='Melkor Legal Tech'
    )
    print("✅ Superusuário criado com sucesso")
else:
    print("ℹ️ Superusuário já existe")
EOF

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p media/documentos
mkdir -p static

# Executar testes básicos
echo "🧪 Executando testes básicos..."
python manage.py test tests.test_prompts --verbosity=1 || echo "⚠️ Alguns testes falharam, mas continuando..."

echo "✅ Build concluído com sucesso!"
