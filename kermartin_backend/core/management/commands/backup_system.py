"""
Comando Django para backup do sistema Kermartin 3.0
"""

import os
import json
import gzip
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from core.models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise, LogSeguranca


class Command(BaseCommand):
    """Comando para backup completo do sistema"""
    
    help = 'Cria backup completo do sistema Kermartin 3.0'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Diretório de saída para o backup'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compactar backup com gzip'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Incluir arquivos de mídia no backup'
        )
        parser.add_argument(
            '--exclude-logs',
            action='store_true',
            help='Excluir logs de segurança do backup'
        )
    
    def handle(self, *args, **options):
        """Executa o backup"""
        
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando backup do Kermartin 3.0...')
        )
        
        # Criar diretório de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(options['output_dir'], f'kermartin_backup_{timestamp}')
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            # Backup dos dados
            self._backup_database(backup_dir, options['exclude_logs'])
            
            # Backup de arquivos de mídia
            if options['include_media']:
                self._backup_media_files(backup_dir)
            
            # Backup de configurações
            self._backup_configurations(backup_dir)
            
            # Criar arquivo de metadados
            self._create_metadata_file(backup_dir, options)
            
            # Compactar se solicitado
            if options['compress']:
                self._compress_backup(backup_dir)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Backup concluído: {backup_dir}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro no backup: {e}')
            )
            raise
    
    def _backup_database(self, backup_dir: str, exclude_logs: bool = False):
        """Backup dos dados do banco"""
        
        self.stdout.write('📊 Fazendo backup dos dados...')
        
        models_to_backup = [
            ('usuarios', Usuario),
            ('processos', Processo),
            ('documentos', Documento),
            ('sessoes_analise', SessaoAnalise),
            ('resultados_analise', ResultadoAnalise),
        ]
        
        if not exclude_logs:
            models_to_backup.append(('logs_seguranca', LogSeguranca))
        
        for filename, model in models_to_backup:
            self.stdout.write(f'  📋 Backup de {model._meta.verbose_name_plural}...')
            
            # Serializar dados
            data = serializers.serialize('json', model.objects.all(), indent=2)
            
            # Salvar arquivo
            filepath = os.path.join(backup_dir, f'{filename}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            count = model.objects.count()
            self.stdout.write(f'    ✅ {count} registros salvos')
    
    def _backup_media_files(self, backup_dir: str):
        """Backup dos arquivos de mídia"""
        
        self.stdout.write('📁 Fazendo backup dos arquivos de mídia...')
        
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            media_backup_dir = os.path.join(backup_dir, 'media')
            shutil.copytree(media_root, media_backup_dir)
            
            # Contar arquivos
            file_count = sum(len(files) for _, _, files in os.walk(media_backup_dir))
            self.stdout.write(f'  ✅ {file_count} arquivos de mídia salvos')
        else:
            self.stdout.write('  ⚠️ Diretório de mídia não encontrado')
    
    def _backup_configurations(self, backup_dir: str):
        """Backup das configurações"""
        
        self.stdout.write('⚙️ Fazendo backup das configurações...')
        
        config_data = {
            'django_settings': {
                'DEBUG': settings.DEBUG,
                'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
                'DATABASES': {
                    'default': {
                        'ENGINE': settings.DATABASES['default']['ENGINE'],
                        'NAME': settings.DATABASES['default']['NAME'],
                        # Não incluir credenciais sensíveis
                    }
                },
                'INSTALLED_APPS': settings.INSTALLED_APPS,
                'MIDDLEWARE': settings.MIDDLEWARE,
            },
            'kermartin_settings': getattr(settings, 'KERMARTIN_SETTINGS', {}),
            'openai_model': getattr(settings, 'OPENAI_MODEL', ''),
            'backup_timestamp': datetime.now().isoformat(),
        }
        
        config_file = os.path.join(backup_dir, 'configurations.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write('  ✅ Configurações salvas')
    
    def _create_metadata_file(self, backup_dir: str, options: dict):
        """Cria arquivo de metadados do backup"""
        
        self.stdout.write('📋 Criando metadados do backup...')
        
        # Calcular estatísticas
        stats = {
            'usuarios': Usuario.objects.count(),
            'processos': Processo.objects.count(),
            'documentos': Documento.objects.count(),
            'sessoes_analise': SessaoAnalise.objects.count(),
            'resultados_analise': ResultadoAnalise.objects.count(),
            'logs_seguranca': LogSeguranca.objects.count() if not options['exclude_logs'] else 0,
        }
        
        metadata = {
            'backup_info': {
                'version': '3.0',
                'timestamp': datetime.now().isoformat(),
                'type': 'full_backup',
                'compressed': options['compress'],
                'include_media': options['include_media'],
                'exclude_logs': options['exclude_logs'],
            },
            'statistics': stats,
            'system_info': {
                'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'database_engine': settings.DATABASES['default']['ENGINE'],
            },
            'restore_instructions': {
                'command': 'python manage.py restore_system --backup-dir <backup_directory>',
                'requirements': [
                    'Django instalado',
                    'Banco de dados configurado',
                    'Dependências do requirements.txt instaladas'
                ]
            }
        }
        
        metadata_file = os.path.join(backup_dir, 'backup_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.stdout.write('  ✅ Metadados criados')
        
        # Exibir estatísticas
        self.stdout.write('\n📊 Estatísticas do backup:')
        for model, count in stats.items():
            self.stdout.write(f'  • {model}: {count} registros')
    
    def _compress_backup(self, backup_dir: str):
        """Compacta o backup"""
        
        self.stdout.write('🗜️ Compactando backup...')
        
        # Criar arquivo tar.gz
        archive_name = f'{backup_dir}.tar.gz'
        shutil.make_archive(backup_dir, 'gztar', backup_dir)
        
        # Remover diretório original
        shutil.rmtree(backup_dir)
        
        # Calcular tamanho
        size_mb = os.path.getsize(archive_name) / (1024 * 1024)
        
        self.stdout.write(f'  ✅ Backup compactado: {archive_name} ({size_mb:.2f} MB)')


class RestoreCommand(BaseCommand):
    """Comando para restaurar backup do sistema"""
    
    help = 'Restaura backup do sistema Kermartin 3.0'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-dir',
            type=str,
            required=True,
            help='Diretório do backup a ser restaurado'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força restauração sem confirmação'
        )
        parser.add_argument(
            '--exclude-media',
            action='store_true',
            help='Não restaurar arquivos de mídia'
        )
    
    def handle(self, *args, **options):
        """Executa a restauração"""
        
        backup_dir = options['backup_dir']
        
        if not os.path.exists(backup_dir):
            self.stdout.write(
                self.style.ERROR(f'❌ Diretório de backup não encontrado: {backup_dir}')
            )
            return
        
        # Verificar se é um backup válido
        metadata_file = os.path.join(backup_dir, 'backup_metadata.json')
        if not os.path.exists(metadata_file):
            self.stdout.write(
                self.style.ERROR('❌ Arquivo de metadados não encontrado. Backup inválido.')
            )
            return
        
        # Ler metadados
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 Iniciando restauração do backup...')
        )
        self.stdout.write(f'📅 Data do backup: {metadata["backup_info"]["timestamp"]}')
        
        # Confirmação
        if not options['force']:
            confirm = input('⚠️ Esta operação irá sobrescrever os dados existentes. Continuar? (s/N): ')
            if confirm.lower() != 's':
                self.stdout.write('❌ Restauração cancelada.')
                return
        
        try:
            # Restaurar dados
            self._restore_database(backup_dir)
            
            # Restaurar mídia
            if not options['exclude_media']:
                self._restore_media_files(backup_dir)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Restauração concluída com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na restauração: {e}')
            )
            raise
    
    def _restore_database(self, backup_dir: str):
        """Restaura dados do banco"""
        
        self.stdout.write('📊 Restaurando dados do banco...')
        
        # Arquivos de dados
        data_files = [
            'usuarios.json',
            'processos.json',
            'documentos.json',
            'sessoes_analise.json',
            'resultados_analise.json',
            'logs_seguranca.json',
        ]
        
        for filename in data_files:
            filepath = os.path.join(backup_dir, filename)
            if os.path.exists(filepath):
                self.stdout.write(f'  📋 Restaurando {filename}...')
                
                # Carregar e deserializar dados
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                # Deserializar e salvar
                for obj in serializers.deserialize('json', data):
                    obj.save()
                
                self.stdout.write(f'    ✅ {filename} restaurado')
    
    def _restore_media_files(self, backup_dir: str):
        """Restaura arquivos de mídia"""
        
        self.stdout.write('📁 Restaurando arquivos de mídia...')
        
        media_backup_dir = os.path.join(backup_dir, 'media')
        if os.path.exists(media_backup_dir):
            media_root = settings.MEDIA_ROOT
            
            # Remover mídia existente
            if os.path.exists(media_root):
                shutil.rmtree(media_root)
            
            # Copiar backup
            shutil.copytree(media_backup_dir, media_root)
            
            file_count = sum(len(files) for _, _, files in os.walk(media_root))
            self.stdout.write(f'  ✅ {file_count} arquivos de mídia restaurados')
        else:
            self.stdout.write('  ⚠️ Backup de mídia não encontrado')
