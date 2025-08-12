"""
Comando Django para configuração inicial do Kermartin 3.0
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from core.models import Usuario


class Command(BaseCommand):
    """Comando para configuração inicial do sistema"""
    
    help = 'Configura o sistema Kermartin 3.0 para primeira execução'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@kermartin.com',
            help='Email do administrador'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin',
            help='Senha do administrador'
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Pular execução de migrações'
        )
        parser.add_argument(
            '--load-sample-data',
            action='store_true',
            help='Carregar dados de exemplo'
        )
    
    def handle(self, *args, **options):
        """Executa a configuração inicial"""
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Configurando Kermartin 3.0...')
        )
        
        try:
            # 1. Executar migrações
            if not options['skip_migrations']:
                self._run_migrations()
            
            # 2. Criar superusuário
            self._create_superuser(options['admin_email'], options['admin_password'])
            
            # 3. Configurar diretórios
            self._setup_directories()
            
            # 4. Carregar dados de exemplo
            if options['load_sample_data']:
                self._load_sample_data()
            
            # 5. Verificar configurações
            self._verify_configuration()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Kermartin 3.0 configurado com sucesso!')
            )
            
            self._display_next_steps()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na configuração: {e}')
            )
            raise
    
    def _run_migrations(self):
        """Executa migrações do banco de dados"""
        
        self.stdout.write('📊 Executando migrações...')
        
        try:
            call_command('makemigrations', verbosity=0)
            call_command('migrate', verbosity=0)
            self.stdout.write('  ✅ Migrações executadas')
        except Exception as e:
            self.stdout.write(f'  ❌ Erro nas migrações: {e}')
            raise
    
    def _create_superuser(self, email: str, password: str):
        """Cria superusuário se não existir"""
        
        self.stdout.write('👤 Configurando superusuário...')
        
        try:
            # Verificar se já existe
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write('  ⚠️ Superusuário já existe')
                return
            
            # Criar superusuário
            user = User.objects.create_superuser(
                username=email,
                email=email,
                password=password
            )
            
            # Criar perfil de usuário
            Usuario.objects.create(
                user=user,
                nome_completo='Administrador Kermartin',
                oab_numero='000000',
                oab_estado='SP',
                telefone='(11) 99999-9999',
                escritorio='Kermartin Legal Tech'
            )
            
            self.stdout.write(f'  ✅ Superusuário criado: {email}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro ao criar superusuário: {e}')
            raise
    
    def _setup_directories(self):
        """Configura diretórios necessários"""
        
        self.stdout.write('📁 Configurando diretórios...')
        
        directories = [
            'media',
            'media/documentos',
            'logs',
            'backups',
            'static',
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.stdout.write(f'  ✅ Diretório criado: {directory}')
    
    def _load_sample_data(self):
        """Carrega dados de exemplo"""
        
        self.stdout.write('📋 Carregando dados de exemplo...')
        
        try:
            # Criar usuário de exemplo
            if not User.objects.filter(username='demo@kermartin.com').exists():
                demo_user = User.objects.create_user(
                    username='demo@kermartin.com',
                    email='demo@kermartin.com',
                    password='demo123'
                )
                
                Usuario.objects.create(
                    user=demo_user,
                    nome_completo='Dr. João Silva',
                    oab_numero='123456',
                    oab_estado='SP',
                    telefone='(11) 98765-4321',
                    escritorio='Silva & Associados'
                )
                
                self.stdout.write('  ✅ Usuário de demonstração criado')
            
            # Criar processo de exemplo
            from core.models import Processo
            
            if not Processo.objects.exists():
                usuario_demo = Usuario.objects.get(user__username='demo@kermartin.com')
                
                Processo.objects.create(
                    usuario=usuario_demo,
                    titulo='Homicídio Qualificado - Caso Demonstração',
                    numero_processo='0001234-56.2024.8.26.0001',
                    tipo_crime='homicidio',
                    comarca='São Paulo',
                    vara='1ª Vara do Tribunal do Júri',
                    reu_nome='João da Silva',
                    vitima_nome='Maria Santos',
                    observacoes='Processo de demonstração do sistema Kermartin 3.0'
                )
                
                self.stdout.write('  ✅ Processo de demonstração criado')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro ao carregar dados de exemplo: {e}')
    
    def _verify_configuration(self):
        """Verifica configurações do sistema"""
        
        self.stdout.write('🔍 Verificando configurações...')
        
        checks = [
            ('Banco de dados', self._check_database),
            ('Superusuário', self._check_superuser),
            ('Diretórios', self._check_directories),
            ('Configurações Django', self._check_django_settings),
        ]
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.stdout.write(f'  ✅ {check_name}: OK')
                else:
                    self.stdout.write(f'  ⚠️ {check_name}: Problema detectado')
            except Exception as e:
                self.stdout.write(f'  ❌ {check_name}: Erro - {e}')
    
    def _check_database(self) -> bool:
        """Verifica conexão com banco de dados"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def _check_superuser(self) -> bool:
        """Verifica se existe superusuário"""
        return User.objects.filter(is_superuser=True).exists()
    
    def _check_directories(self) -> bool:
        """Verifica se diretórios existem"""
        required_dirs = ['media', 'logs']
        return all(os.path.exists(d) for d in required_dirs)
    
    def _check_django_settings(self) -> bool:
        """Verifica configurações básicas do Django"""
        from django.conf import settings
        
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'INSTALLED_APPS',
        ]
        
        return all(hasattr(settings, setting) for setting in required_settings)
    
    def _display_next_steps(self):
        """Exibe próximos passos"""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 KERMARTIN 3.0 CONFIGURADO COM SUCESSO!'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n📋 PRÓXIMOS PASSOS:')
        self.stdout.write('')
        self.stdout.write('1. 🔑 Configure sua OpenAI API Key no arquivo .env:')
        self.stdout.write('   OPENAI_API_KEY=sua-chave-aqui')
        self.stdout.write('')
        self.stdout.write('2. 🚀 Inicie o servidor de desenvolvimento:')
        self.stdout.write('   python manage.py runserver')
        self.stdout.write('')
        self.stdout.write('3. 🌐 Acesse o sistema:')
        self.stdout.write('   Admin: http://localhost:8000/admin/')
        self.stdout.write('   APIs:  http://localhost:8000/api/')
        self.stdout.write('')
        self.stdout.write('4. 👤 Credenciais de acesso:')
        self.stdout.write('   Email: admin@kermartin.com')
        self.stdout.write('   Senha: admin')
        self.stdout.write('')
        self.stdout.write('5. 📚 Documentação:')
        self.stdout.write('   Consulte API_DOCUMENTATION.md')
        self.stdout.write('')
        self.stdout.write('6. 🧪 Execute os testes:')
        self.stdout.write('   python manage.py test')
        self.stdout.write('')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🏆 KERMARTIN 3.0 PRONTO PARA USO!'))
        self.stdout.write('='*60)
