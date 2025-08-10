"""
Agente Developer (James) - BMad Method
Responsável por implementar código baseado nas histórias criadas pelo SM
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from crewai import Agent, Task, Crew
from .base_agent import BMadBaseAgent


class DeveloperAgent(BMadBaseAgent):
    """Agente Developer especializado em implementar histórias BMad"""
    
    def __init__(self):
        super().__init__("developer")
        self.agent = self.create_developer_agent()
        self.product_root = Path(__file__).parent.parent.parent / "product"
        
    def create_developer_agent(self) -> Agent:
        """Cria o agente Developer com configurações específicas"""
        
        # Carrega arquivos obrigatórios
        files_content = self.load_required_files([
            "development/standards/coding-standards.md",
            "development/standards/testing-strategy.md"
        ])
        
        context = f"""
        {self.get_project_context()}
        
        ARQUIVOS CARREGADOS:
        {self._format_files_content(files_content)}
        
        RESPONSABILIDADES DO DEVELOPER:
        1. Implementar código baseado EXCLUSIVAMENTE na história fornecida
        2. Seguir padrões de codificação definidos
        3. Implementar testes para cada funcionalidade
        4. Executar validações (testes, linting)
        5. Atualizar File List na história
        6. Marcar tarefas como concluídas apenas após validação
        
        ESTRUTURA DO PRODUTO:
        {self._get_product_structure()}
        
        TECNOLOGIAS:
        - Django 4.2 + PostgreSQL
        - Django REST Framework
        - OpenAI API para IA
        - Redis para cache
        - Celery para tarefas assíncronas
        """
        
        return self.create_agent(
            role="Senior Developer especializado em Django e IA",
            goal="Implementar funcionalidades de alta qualidade baseadas nas histórias, seguindo rigorosamente os padrões BMad Method",
            backstory=f"""Você é James, um desenvolvedor sênior especializado em:
            - Django e PostgreSQL
            - APIs REST com DRF
            - Integração com OpenAI
            - Desenvolvimento orientado por testes
            - Metodologia BMad
            
            Você NUNCA consulta documentos externos além da história fornecida.
            Toda informação necessária está nas Dev Notes da história.
            
            Seu processo é rigoroso:
            1. Lê a história completa
            2. Implementa tarefa por tarefa sequencialmente
            3. Escreve testes para cada implementação
            4. Executa validações
            5. Marca tarefa como concluída APENAS se tudo passar
            6. Atualiza File List com arquivos modificados
            
            CONTEXTO TÉCNICO:
            {context}"""
        )
    
    def implement_story(self, story_path: str) -> str:
        """Implementa uma história completa"""
        
        # Carrega a história
        story_content = self._load_story(story_path)
        
        task = Task(
            description=f"""
            Implemente a história completa seguindo rigorosamente o BMad Method:
            
            HISTÓRIA A IMPLEMENTAR:
            {story_content}
            
            PROCESSO OBRIGATÓRIO:
            1. Leia TODA a história e Dev Notes
            2. Execute as tarefas SEQUENCIALMENTE
            3. Para cada tarefa:
               - Implemente o código necessário
               - Escreva testes correspondentes
               - Execute validações (pytest, flake8)
               - Marque como [x] APENAS se tudo passar
            4. Atualize a File List com TODOS os arquivos criados/modificados
            5. Preencha Completion Notes com resumo do trabalho
            
            ESTRUTURA DO PROJETO:
            - Backend Django em: product/backend/
            - Modelos em: product/backend/core/models.py
            - Views em: product/backend/core/views.py
            - URLs em: product/backend/core/urls.py
            - IA Engine em: product/backend/ai_engine/
            - Testes em: product/backend/tests/
            
            VALIDAÇÕES OBRIGATÓRIAS:
            - Todos os testes devem passar
            - Código deve seguir PEP8 (flake8)
            - Migrações Django devem ser criadas se necessário
            - Documentação inline deve estar presente
            
            IMPORTANTE: 
            - Use APENAS as informações da história
            - NÃO consulte documentos externos
            - Implemente EXATAMENTE o que está especificado
            - Marque tarefas como concluídas APENAS após validação
            """,
            agent=self.agent,
            expected_output="História implementada com todas as tarefas marcadas como concluídas e File List atualizada"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Salva resultado da implementação
        impl_filename = f"implementation_{Path(story_path).stem}.md"
        impl_path = self.save_output(result, impl_filename, "implementations")
        
        print(f"✅ Implementação concluída: {impl_path}")
        return result
    
    def run_tests(self, test_path: str = None) -> Tuple[bool, str]:
        """Executa testes do projeto"""
        try:
            backend_path = self.product_root / "backend"
            if not backend_path.exists():
                return False, "Diretório backend não encontrado"
            
            # Executa pytest
            cmd = ["python", "-m", "pytest", "-v"]
            if test_path:
                cmd.append(test_path)
            
            result = subprocess.run(
                cmd,
                cwd=backend_path,
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
            return success, output
            
        except Exception as e:
            return False, f"Erro ao executar testes: {e}"
    
    def run_linting(self) -> Tuple[bool, str]:
        """Executa linting do código"""
        try:
            backend_path = self.product_root / "backend"
            if not backend_path.exists():
                return False, "Diretório backend não encontrado"
            
            # Executa flake8
            result = subprocess.run(
                ["flake8", ".", "--max-line-length=88", "--exclude=migrations"],
                cwd=backend_path,
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
            return success, output
            
        except Exception as e:
            return False, f"Erro ao executar linting: {e}"
    
    def create_django_migrations(self) -> Tuple[bool, str]:
        """Cria migrações Django"""
        try:
            backend_path = self.product_root / "backend"
            manage_py = backend_path / "manage.py"
            
            if not manage_py.exists():
                return False, "manage.py não encontrado"
            
            # Executa makemigrations
            result = subprocess.run(
                ["python", "manage.py", "makemigrations"],
                cwd=backend_path,
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
            return success, output
            
        except Exception as e:
            return False, f"Erro ao criar migrações: {e}"
    
    def _load_story(self, story_path: str) -> str:
        """Carrega conteúdo da história"""
        try:
            with open(story_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Erro ao carregar história {story_path}: {e}")
    
    def _format_files_content(self, files_content: Dict[str, str]) -> str:
        """Formata o conteúdo dos arquivos para o contexto"""
        formatted = ""
        for file_path, content in files_content.items():
            formatted += f"\n--- {file_path} ---\n{content[:800]}...\n"
        return formatted
    
    def _get_product_structure(self) -> str:
        """Retorna estrutura do produto"""
        return """
        product/
        ├── backend/
        │   ├── kermartin_project/
        │   │   ├── settings.py
        │   │   ├── urls.py
        │   │   └── wsgi.py
        │   ├── core/
        │   │   ├── models.py
        │   │   ├── views.py
        │   │   ├── serializers.py
        │   │   └── urls.py
        │   ├── ai_engine/
        │   │   ├── processor.py
        │   │   ├── prompts.py
        │   │   └── security.py
        │   ├── authentication/
        │   │   ├── models.py
        │   │   ├── views.py
        │   │   └── serializers.py
        │   ├── tests/
        │   └── manage.py
        └── frontend/
            ├── pages/
            ├── components/
            └── services/
        """
