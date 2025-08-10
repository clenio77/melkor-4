#!/usr/bin/env python3
"""
Ponto de entrada principal para o sistema de desenvolvimento automatizado BMad
Executa o ciclo completo de desenvolvimento do Kermartin 3.0
"""

import os
import sys
import argparse
from pathlib import Path
from decouple import config

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from development.workflow.bmad_orchestrator import BMadOrchestrator


def setup_environment():
    """Configura ambiente de desenvolvimento"""
    
    print("🔧 Configurando ambiente de desenvolvimento...")
    
    # Verificar se .env existe
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado. Criando template...")
        
        env_template = """
# Configurações do Kermartin 3.0 - BMad Development

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here

# Database (PostgreSQL)
DB_NAME=kermartin_dev
DB_USER=kermartin_user
DB_PASSWORD=kermartin_pass
DB_HOST=localhost
DB_PORT=5432

# Redis (Cache)
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Desenvolvimento
ENVIRONMENT=development
"""
        
        with open(env_file, 'w') as f:
            f.write(env_template.strip())
        
        print(f"📝 Template .env criado em: {env_file}")
        print("🔑 Configure suas chaves de API antes de continuar!")
        return False
    
    return True


def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description="BMad Method - Desenvolvimento Automatizado Kermartin 3.0")
    parser.add_argument(
        "command",
        choices=["setup", "create-stories", "implement", "full-cycle", "status", "single"],
        help="Comando a executar"
    )
    parser.add_argument(
        "--epic",
        help="ID do épico para comando 'single' (ex: E001)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Apenas validar ambiente sem executar"
    )
    
    args = parser.parse_args()
    
    print("🚀 BMad Method - Kermartin 3.0 Development Automation")
    print("=" * 60)
    
    # Configurar ambiente
    if not setup_environment():
        print("❌ Configure o arquivo .env antes de continuar")
        return 1
    
    # Inicializar orquestrador
    orchestrator = BMadOrchestrator()
    
    # Validar ambiente
    if not orchestrator.validate_environment():
        print("❌ Ambiente não está configurado corretamente")
        return 1
    
    if args.validate_only:
        print("✅ Ambiente validado com sucesso!")
        return 0
    
    try:
        if args.command == "setup":
            print("\n🏗️ Configurando estrutura do projeto...")
            orchestrator.setup_product_structure()
            orchestrator.initialize_agents()
            print("✅ Setup concluído!")
            
        elif args.command == "create-stories":
            print("\n📝 Criando histórias para todos os épicos...")
            orchestrator.initialize_agents()
            stories = orchestrator.create_all_stories()
            
            success_count = len([s for s in stories if s.get('status') == 'created'])
            print(f"\n📊 Resultado: {success_count} histórias criadas com sucesso")
            
        elif args.command == "implement":
            print("\n💻 Implementando todas as histórias...")
            orchestrator.initialize_agents()
            implementations = orchestrator.implement_all_stories()
            
            success_count = len([i for i in implementations if i.get('status') == 'implemented'])
            print(f"\n📊 Resultado: {success_count} implementações concluídas")
            
        elif args.command == "full-cycle":
            print("\n🔄 Executando ciclo completo de desenvolvimento...")
            results = orchestrator.execute_full_development_cycle()
            
            if results["status"] == "completed":
                print("\n🎉 Ciclo completo executado com sucesso!")
                print(f"📋 Histórias criadas: {len(results['stories_created'])}")
                print(f"💻 Implementações: {len(results['implementations'])}")
            else:
                print(f"\n❌ Ciclo falhou: {results.get('error', 'Erro desconhecido')}")
                return 1
                
        elif args.command == "single":
            if not args.epic:
                print("❌ Especifique o épico com --epic (ex: --epic E001)")
                return 1
            
            print(f"\n🎯 Executando ciclo para épico {args.epic}...")
            orchestrator.initialize_agents()
            result = orchestrator.implement_single_story(args.epic)
            
            if result["status"] == "completed":
                print(f"✅ Épico {args.epic} concluído com sucesso!")
            else:
                print(f"❌ Falha no épico {args.epic}: {result.get('error', 'Erro desconhecido')}")
                return 1
                
        elif args.command == "status":
            print("\n📊 Status do projeto:")
            status = orchestrator.get_project_status()
            
            print(f"Status geral: {status['project_status']}")
            print(f"Histórias criadas: {status['stories_created']}")
            print(f"Implementações: {status['implementations_done']}")
            print(f"Épico atual: {status.get('current_epic', 'Nenhum')}")
            
            agents = status['agents_initialized']
            print(f"Agentes inicializados:")
            print(f"  - SM (Bob): {'✅' if agents['sm'] else '❌'}")
            print(f"  - Dev (James): {'✅' if agents['dev'] else '❌'}")
            print(f"  - QA (Sarah): {'✅' if agents['qa'] else '❌'}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
