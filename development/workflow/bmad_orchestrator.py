"""
Orquestrador BMad Method - Coordena todo o ciclo de desenvolvimento
Gerencia a execução sequencial: SM → Dev → QA
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from decouple import config

from ..agents.scrum_master import ScrumMasterAgent
from ..agents.developer import DeveloperAgent
from ..agents.qa_agent import QAAgent


class BMadOrchestrator:
    """Orquestrador principal do BMad Method para Melkor 3.0"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.stories_dir = Path(__file__).parent.parent / "stories"
        self.stories_dir.mkdir(exist_ok=True)
        
        # Inicializar agentes
        self.sm_agent = None
        self.dev_agent = None
        self.qa_agent = None
        
        # Estado do projeto
        self.current_epic = None
        self.current_story = None
        self.project_status = "initialized"
        
    def initialize_agents(self):
        """Inicializa todos os agentes BMad"""
        print("🤖 Inicializando agentes BMad...")
        
        try:
            self.sm_agent = ScrumMasterAgent()
            print("✅ Scrum Master (Bob) inicializado")
            
            self.dev_agent = DeveloperAgent()
            print("✅ Developer (James) inicializado")
            
            # QA será implementado depois
            # self.qa_agent = QAAgent()
            # print("✅ QA (Sarah) inicializado")
            
            print("🚀 Todos os agentes prontos!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar agentes: {e}")
            raise
    
    def execute_full_development_cycle(self) -> Dict[str, str]:
        """Executa o ciclo completo de desenvolvimento para todos os épicos"""
        
        print("🏗️ Iniciando ciclo completo de desenvolvimento BMad...")
        
        if not self.sm_agent:
            self.initialize_agents()
        
        results = {
            "stories_created": [],
            "implementations": [],
            "qa_results": [],
            "status": "in_progress"
        }
        
        try:
            # Fase 1: Criar todas as histórias
            print("\n📋 FASE 1: Criação de Histórias")
            stories = self.create_all_stories()
            results["stories_created"] = stories
            
            # Fase 2: Implementar histórias sequencialmente
            print("\n💻 FASE 2: Implementação")
            implementations = self.implement_all_stories()
            results["implementations"] = implementations
            
            # Fase 3: QA (futuro)
            print("\n🔍 FASE 3: Quality Assurance")
            print("⏳ QA será implementado na próxima iteração")
            
            results["status"] = "completed"
            print("\n🎉 Ciclo de desenvolvimento concluído com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro no ciclo de desenvolvimento: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def create_all_stories(self) -> List[str]:
        """Cria histórias para todos os épicos"""
        
        print("📝 Criando histórias para todos os épicos...")
        
        epics = self.sm_agent.list_available_epics()
        stories_created = []
        
        for epic in epics:
            print(f"\n🔄 Processando épico {epic['id']}: {epic['title']}")
            
            try:
                story = self.sm_agent.create_story_from_epic(epic['id'])
                stories_created.append({
                    "epic_id": epic['id'],
                    "epic_title": epic['title'],
                    "story_content": story,
                    "status": "created"
                })
                
                print(f"✅ História criada para {epic['id']}")
                
                # Pequena pausa entre criações
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Erro ao criar história para {epic['id']}: {e}")
                stories_created.append({
                    "epic_id": epic['id'],
                    "epic_title": epic['title'],
                    "status": "failed",
                    "error": str(e)
                })
        
        print(f"\n📊 Resumo: {len([s for s in stories_created if s['status'] == 'created'])} histórias criadas")
        return stories_created
    
    def implement_all_stories(self) -> List[str]:
        """Implementa todas as histórias criadas"""
        
        print("⚙️ Implementando todas as histórias...")
        
        # Buscar arquivos de histórias
        story_files = list(self.stories_dir.glob("story_*.md"))
        implementations = []
        
        if not story_files:
            print("⚠️ Nenhuma história encontrada para implementar")
            return implementations
        
        # Ordenar por épico (E001, E002, etc.)
        story_files.sort(key=lambda x: x.name)
        
        for story_file in story_files:
            print(f"\n🔧 Implementando história: {story_file.name}")
            
            try:
                implementation = self.dev_agent.implement_story(str(story_file))
                implementations.append({
                    "story_file": story_file.name,
                    "implementation": implementation,
                    "status": "implemented"
                })
                
                print(f"✅ História {story_file.name} implementada")
                
                # Pausa entre implementações
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Erro ao implementar {story_file.name}: {e}")
                implementations.append({
                    "story_file": story_file.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        print(f"\n📊 Resumo: {len([i for i in implementations if i['status'] == 'implemented'])} implementações concluídas")
        return implementations
    
    def implement_single_story(self, epic_id: str) -> Dict[str, str]:
        """Implementa uma única história (ciclo SM → Dev → QA)"""
        
        print(f"🎯 Executando ciclo para épico {epic_id}")
        
        if not self.sm_agent:
            self.initialize_agents()
        
        result = {
            "epic_id": epic_id,
            "story_created": False,
            "implemented": False,
            "qa_passed": False,
            "status": "in_progress"
        }
        
        try:
            # 1. SM cria história
            print(f"📋 SM: Criando história para {epic_id}")
            story = self.sm_agent.create_story_from_epic(epic_id)
            result["story_created"] = True
            result["story_content"] = story
            
            # 2. Dev implementa
            print(f"💻 DEV: Implementando {epic_id}")
            story_file = self.stories_dir / f"story_{epic_id.lower()}.md"
            implementation = self.dev_agent.implement_story(str(story_file))
            result["implemented"] = True
            result["implementation"] = implementation
            
            # 3. QA revisa (futuro)
            print(f"🔍 QA: Revisando {epic_id} (placeholder)")
            result["qa_passed"] = True  # Placeholder
            
            result["status"] = "completed"
            print(f"✅ Ciclo completo para {epic_id}")
            
        except Exception as e:
            print(f"❌ Erro no ciclo {epic_id}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def get_project_status(self) -> Dict:
        """Retorna status atual do projeto"""
        
        stories_dir = Path(__file__).parent.parent / "stories"
        implementations_dir = Path(__file__).parent.parent / "implementations"
        
        story_files = list(stories_dir.glob("*.md")) if stories_dir.exists() else []
        impl_files = list(implementations_dir.glob("*.md")) if implementations_dir.exists() else []
        
        return {
            "project_status": self.project_status,
            "stories_created": len(story_files),
            "implementations_done": len(impl_files),
            "current_epic": self.current_epic,
            "agents_initialized": {
                "sm": self.sm_agent is not None,
                "dev": self.dev_agent is not None,
                "qa": self.qa_agent is not None
            }
        }
    
    def setup_product_structure(self):
        """Cria estrutura inicial do produto"""
        
        print("🏗️ Criando estrutura do produto...")
        
        product_dirs = [
            "product/backend/melkor_project",
            "product/backend/core",
            "product/backend/ai_engine",
            "product/backend/authentication",
            "product/backend/tests/unit",
            "product/backend/tests/integration",
            "product/backend/tests/e2e",
            "product/frontend/pages",
            "product/frontend/components",
            "product/frontend/services",
            "product/frontend/styles"
        ]
        
        for dir_path in product_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Criar __init__.py para diretórios Python
            if "backend" in dir_path and not dir_path.endswith("tests"):
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
        
        print("✅ Estrutura do produto criada")
    
    def validate_environment(self) -> bool:
        """Valida se ambiente está configurado corretamente"""
        
        print("🔍 Validando ambiente...")
        
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not config(var, default=None):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variáveis de ambiente faltando: {missing_vars}")
            return False
        
        print("✅ Ambiente validado")
        return True
