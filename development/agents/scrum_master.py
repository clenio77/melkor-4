"""
Agente Scrum Master (Bob) - BMad Method
Responsável por criar histórias detalhadas baseadas nos épicos
"""

import json
from pathlib import Path
from typing import Dict, List
from crewai import Agent, Task, Crew
from .base_agent import BMadBaseAgent


class ScrumMasterAgent(BMadBaseAgent):
    """Agente Scrum Master especializado em criar histórias do BMad Method"""
    
    def __init__(self):
        super().__init__("scrum_master")
        self.agent = self.create_scrum_master_agent()
        
    def create_scrum_master_agent(self) -> Agent:
        """Cria o agente Scrum Master com configurações específicas"""
        
        # Carrega arquivos obrigatórios
        files_content = self.load_required_files()
        
        # Contexto específico do SM
        context = f"""
        {self.get_project_context()}
        
        ARQUIVOS CARREGADOS:
        {self._format_files_content(files_content)}
        
        RESPONSABILIDADES DO SCRUM MASTER:
        1. Analisar épicos e quebrar em histórias executáveis
        2. Criar Dev Notes com extratos relevantes da arquitetura
        3. Definir tarefas sequenciais e critérios de aceitação
        4. Garantir que histórias sejam autocontidas
        5. Seguir rigorosamente o template de história BMad
        
        ÉPICOS DISPONÍVEIS:
        {self._format_epics()}
        """
        
        return self.create_agent(
            role="Scrum Master Especialista em BMad Method",
            goal="Criar histórias detalhadas e autocontidas que permitam ao agente dev implementar funcionalidades sem consultar documentos externos",
            backstory=f"""Você é Bob, um Scrum Master experiente especializado no BMad Method. 
            Sua expertise está em transformar épicos complexos em histórias executáveis.
            
            Você entende profundamente:
            - O projeto Melkor 3.0 (sistema jurídico com IA)
            - Arquitetura Django + PostgreSQL + Next.js
            - Integração com OpenAI para análise jurídica
            - Metodologia BMad de desenvolvimento guiado por documentos
            
            Seu trabalho é essencial para o sucesso do projeto, pois você prepara
            o contexto perfeito para que o agente dev (James) possa implementar
            sem ambiguidades ou necessidade de consultar documentos externos.
            
            CONTEXTO DO PROJETO:
            {context}"""
        )
    
    def create_story_from_epic(self, epic_id: str) -> str:
        """Cria uma história detalhada baseada em um épico"""
        
        epic = self._get_epic_by_id(epic_id)
        if not epic:
            raise ValueError(f"Épico {epic_id} não encontrado")
        
        task = Task(
            description=f"""
            Crie uma história detalhada para o épico: {epic['title']}
            
            ÉPICO COMPLETO:
            ID: {epic['id']}
            Título: {epic['title']}
            Descrição: {epic['description']}
            
            INSTRUÇÕES ESPECÍFICAS:
            1. Use EXATAMENTE o template de história BMad
            2. Inclua Dev Notes com extratos relevantes dos documentos carregados
            3. Defina tarefas sequenciais e específicas
            4. Garanta que a história seja autocontida
            5. Inclua critérios de aceitação claros
            6. Considere a arquitetura PostgreSQL + Django + Next.js
            
            TEMPLATE OBRIGATÓRIO:
            ```markdown
            # História: [TÍTULO]
            
            **ID:** [ID_ÚNICO]
            **Épico:** {epic['id']} - {epic['title']}
            **Status:** Draft
            **Estimativa:** [PONTOS]
            
            ## História do Usuário
            Como [PERSONA]
            Eu quero [FUNCIONALIDADE]
            Para que [BENEFÍCIO]
            
            ## Critérios de Aceitação
            - [ ] Critério 1
            - [ ] Critério 2
            - [ ] Critério 3
            
            ## Dev Notes
            ### Arquitetura Relevante
            [EXTRATOS DOS DOCUMENTOS DE ARQUITETURA]
            
            ### Modelos Django Necessários
            [MODELOS ESPECÍFICOS]
            
            ### APIs REST Necessárias
            [ENDPOINTS ESPECÍFICOS]
            
            ### Integração OpenAI
            [DETALHES DA INTEGRAÇÃO]
            
            ## Tarefas de Implementação
            - [ ] Tarefa 1: [DESCRIÇÃO ESPECÍFICA]
              - [ ] Subtarefa 1.1
              - [ ] Subtarefa 1.2
            - [ ] Tarefa 2: [DESCRIÇÃO ESPECÍFICA]
              - [ ] Subtarefa 2.1
              - [ ] Subtarefa 2.2
            - [ ] Tarefa 3: Testes
              - [ ] Testes unitários
              - [ ] Testes de integração
            
            ## Definição de Pronto
            - [ ] Código implementado
            - [ ] Testes passando
            - [ ] Documentação atualizada
            - [ ] Code review aprovado
            
            ## Dev Agent Record
            ### Completion Notes
            [SERÁ PREENCHIDO PELO AGENTE DEV]
            
            ### File List
            [SERÁ PREENCHIDO PELO AGENTE DEV]
            ```
            
            IMPORTANTE: A história deve ser completamente autocontida. O agente dev
            NÃO deve precisar consultar outros documentos além desta história.
            """,
            agent=self.agent,
            expected_output="História completa em formato markdown seguindo exatamente o template BMad"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Salva a história criada
        story_filename = f"story_{epic_id.lower()}.md"
        story_path = self.save_output(result, story_filename, "stories")
        
        print(f"✅ História criada: {story_path}")
        return result
    
    def _format_files_content(self, files_content: Dict[str, str]) -> str:
        """Formata o conteúdo dos arquivos para o contexto"""
        formatted = ""
        for file_path, content in files_content.items():
            formatted += f"\n--- {file_path} ---\n{content[:1000]}...\n"
        return formatted
    
    def _format_epics(self) -> str:
        """Formata os épicos para o contexto"""
        epics = self.config.get('epics', [])
        formatted = ""
        for epic in epics:
            formatted += f"\n{epic['id']}: {epic['title']} - {epic['description']}\n"
        return formatted
    
    def _get_epic_by_id(self, epic_id: str) -> Dict:
        """Busca épico por ID"""
        epics = self.config.get('epics', [])
        for epic in epics:
            if epic['id'] == epic_id:
                return epic
        return None
    
    def list_available_epics(self) -> List[Dict]:
        """Lista todos os épicos disponíveis"""
        return self.config.get('epics', [])
    
    def create_all_stories(self) -> List[str]:
        """Cria histórias para todos os épicos"""
        epics = self.list_available_epics()
        stories = []
        
        for epic in epics:
            print(f"🔄 Criando história para épico {epic['id']}...")
            story = self.create_story_from_epic(epic['id'])
            stories.append(story)
            
        return stories
