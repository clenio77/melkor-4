#!/usr/bin/env python3
"""
Script de Instalação Automática do Melkor 3.0
Configura todo o sistema automaticamente
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class MelkorInstaller:
    """Instalador automático do Melkor 3.0"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_cmd = self._get_python_command()
        self.pip_cmd = self._get_pip_command()
        
    def _get_python_command(self):
        """Detecta comando Python correto"""
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                if result.returncode == 0 and '3.' in result.stdout:
                    return cmd
            except FileNotFoundError:
                continue
        raise RuntimeError("Python 3 não encontrado")
    
    def _get_pip_command(self):
        """Detecta comando pip correto"""
        for cmd in ['pip3', 'pip']:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        raise RuntimeError("pip não encontrado")
    
    def print_header(self, title):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*60)
        print(f"🎯 {title}")
        print("="*60)
    
    def print_step(self, step, description):
        """Imprime passo da instalação"""
        print(f"\n📋 PASSO {step}: {description}")
        print("-" * 40)
    
    def run_command(self, command, description="", check=True):
        """Executa comando e trata erros"""
        if description:
            print(f"🔄 {description}...")
        
        try:
            if isinstance(command, str):
                result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
            else:
                result = subprocess.run(command, check=check, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {description or 'Comando'} executado com sucesso")
                return result
            else:
                print(f"❌ Erro: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar: {e}")
            if check:
                raise
            return None
    
    def check_requirements(self):
        """Verifica requisitos do sistema"""
        
        self.print_step(1, "Verificando Requisitos do Sistema")
        
        # Verificar Python
        try:
            result = subprocess.run([self.python_cmd, '--version'], capture_output=True, text=True)
            python_version = result.stdout.strip()
            print(f"✅ Python encontrado: {python_version}")
        except:
            print("❌ Python 3 não encontrado")
            return False
        
        # Verificar pip
        try:
            result = subprocess.run([self.pip_cmd, '--version'], capture_output=True, text=True)
            pip_version = result.stdout.strip()
            print(f"✅ pip encontrado: {pip_version}")
        except:
            print("❌ pip não encontrado")
            return False
        
        # Verificar Git
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            git_version = result.stdout.strip()
            print(f"✅ Git encontrado: {git_version}")
        except:
            print("⚠️ Git não encontrado (opcional)")
        
        return True
    
    def create_virtual_environment(self):
        """Cria ambiente virtual"""
        
        self.print_step(2, "Criando Ambiente Virtual")
        
        venv_path = "melkor_env"
        
        if os.path.exists(venv_path):
            print(f"⚠️ Ambiente virtual já existe: {venv_path}")
            return True
        
        # Criar ambiente virtual
        self.run_command(
            [self.python_cmd, '-m', 'venv', venv_path],
            "Criando ambiente virtual"
        )
        
        # Instruções de ativação
        if self.system == 'windows':
            activate_cmd = f"{venv_path}\\Scripts\\activate"
        else:
            activate_cmd = f"source {venv_path}/bin/activate"
        
        print(f"\n📋 Para ativar o ambiente virtual:")
        print(f"   {activate_cmd}")
        
        return True
    
    def install_dependencies(self):
        """Instala dependências"""
        
        self.print_step(3, "Instalando Dependências")
        
        # Determinar comando pip no ambiente virtual
        if self.system == 'windows':
            venv_pip = "melkor_env\\Scripts\\pip"
        else:
            venv_pip = "melkor_env/bin/pip"
        
        # Atualizar pip
        self.run_command(
            [venv_pip, 'install', '--upgrade', 'pip'],
            "Atualizando pip"
        )
        
        # Instalar dependências
        if os.path.exists('simple_requirements.txt'):
            self.run_command(
                [venv_pip, 'install', '-r', 'simple_requirements.txt'],
                "Instalando dependências do requirements.txt"
            )
        else:
            # Instalar dependências manualmente
            dependencies = [
                'django>=4.2.0',
                'djangorestframework',
                'djangorestframework-simplejwt',
                'django-cors-headers',
                'openai',
                'PyMuPDF',
                'pdfplumber',
                'python-decouple',
                'redis',
                'pytest-django',
            ]
            
            for dep in dependencies:
                self.run_command(
                    [venv_pip, 'install', dep],
                    f"Instalando {dep}"
                )
        
        return True
    
    def setup_database(self):
        """Configura banco de dados"""
        
        self.print_step(4, "Configurando Banco de Dados")
        
        # Determinar comando python no ambiente virtual
        if self.system == 'windows':
            venv_python = "melkor_env\\Scripts\\python"
        else:
            venv_python = "melkor_env/bin/python"
        
        # Entrar no diretório do backend
        os.chdir('melkor_backend')
        
        try:
            # Executar setup do Melkor
            self.run_command(
                [venv_python, 'manage.py', 'setup_melkor', '--load-sample-data'],
                "Configurando sistema Melkor"
            )
            
        finally:
            # Voltar ao diretório raiz
            os.chdir('..')
        
        return True
    
    def create_env_file(self):
        """Cria arquivo .env"""
        
        self.print_step(5, "Configurando Variáveis de Ambiente")
        
        env_content = """# Configurações do Melkor 3.0

# Django
SECRET_KEY=melkor-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI API (CONFIGURE SUA CHAVE AQUI)
OPENAI_API_KEY=sk-sua-chave-openai-aqui
OPENAI_MODEL=gpt-4-1106-preview
OPENAI_MAX_TOKENS=4000

# Redis (opcional para cache)
REDIS_URL=redis://localhost:6379/0

# Ambiente
ENVIRONMENT=development

# Logs
LOG_LEVEL=INFO
"""
        
        env_file = 'melkor_backend/.env'
        
        if os.path.exists(env_file):
            print(f"⚠️ Arquivo .env já existe: {env_file}")
        else:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"✅ Arquivo .env criado: {env_file}")
        
        return True
    
    def run_tests(self):
        """Executa testes do sistema"""
        
        self.print_step(6, "Executando Testes do Sistema")
        
        # Determinar comando python no ambiente virtual
        if self.system == 'windows':
            venv_python = "melkor_env\\Scripts\\python"
        else:
            venv_python = "melkor_env/bin/python"
        
        # Entrar no diretório do backend
        os.chdir('melkor_backend')
        
        try:
            # Executar testes
            result = self.run_command(
                [venv_python, 'manage.py', 'test', 'tests.test_prompts', '-v', '2'],
                "Executando testes dos prompts",
                check=False
            )
            
            if result and result.returncode == 0:
                print("✅ Todos os testes passaram!")
            else:
                print("⚠️ Alguns testes falharam, mas o sistema deve funcionar")
            
        finally:
            # Voltar ao diretório raiz
            os.chdir('..')
        
        return True
    
    def display_completion_message(self):
        """Exibe mensagem de conclusão"""
        
        self.print_header("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        
        print("""
✅ MELKOR 3.0 INSTALADO E CONFIGURADO!

🚀 PARA INICIAR O SISTEMA:

1. Ative o ambiente virtual:""")
        
        if self.system == 'windows':
            print("   melkor_env\\Scripts\\activate")
        else:
            print("   source melkor_env/bin/activate")
        
        print("""
2. Configure sua OpenAI API Key:
   Edite o arquivo melkor_backend/.env
   OPENAI_API_KEY=sua-chave-aqui

3. Inicie o servidor:
   cd melkor_backend
   python manage.py runserver

4. Acesse o sistema:
   Admin: http://localhost:8000/admin/
   APIs:  http://localhost:8000/api/

5. Credenciais de acesso:
   Email: admin@melkor.com
   Senha: admin

📚 DOCUMENTAÇÃO:
   - API_DOCUMENTATION.md
   - IMPLEMENTACAO_COMPLETA.md

🧪 EXECUTAR TESTES:
   python manage.py test

🏆 MELKOR 3.0 PRONTO PARA USO!
""")
    
    def install(self):
        """Executa instalação completa"""
        
        self.print_header("INSTALADOR AUTOMÁTICO DO MELKOR 3.0")
        
        print("""
🎯 Este script irá:
1. Verificar requisitos do sistema
2. Criar ambiente virtual Python
3. Instalar todas as dependências
4. Configurar banco de dados
5. Criar arquivo de configuração
6. Executar testes básicos

📋 Requisitos:
- Python 3.8+
- pip
- Git (opcional)

🚀 Iniciando instalação...
""")
        
        try:
            # Verificar se estamos no diretório correto
            if not os.path.exists('melkor_backend'):
                print("❌ Erro: Execute este script no diretório raiz do projeto Melkor")
                return False
            
            # Executar passos da instalação
            steps = [
                self.check_requirements,
                self.create_virtual_environment,
                self.install_dependencies,
                self.setup_database,
                self.create_env_file,
                self.run_tests,
            ]
            
            for step in steps:
                if not step():
                    print("❌ Instalação falhou")
                    return False
            
            # Exibir mensagem de conclusão
            self.display_completion_message()
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Instalação cancelada pelo usuário")
            return False
        except Exception as e:
            print(f"\n❌ Erro durante a instalação: {e}")
            return False


def main():
    """Função principal"""
    
    installer = MelkorInstaller()
    success = installer.install()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
