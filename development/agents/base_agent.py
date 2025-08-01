"""
Base Agent para o sistema BMad Method
Implementa funcionalidades comuns para todos os agentes
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any
from crewai import Agent
from langchain_openai import ChatOpenAI
from decouple import config


class BMadBaseAgent:
    """Classe base para todos os agentes BMad"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.config = self.load_config()
        self.llm = self.setup_llm()
        self.agent_config = self.config['agents'].get(agent_name.lower().replace(' ', '_'), {})
        
    def load_config(self) -> Dict:
        """Carrega configuração do core-config.yaml"""
        config_path = Path(__file__).parent.parent / "config" / "core-config.yaml"
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def setup_llm(self) -> ChatOpenAI:
        """Configura o modelo LLM"""
        return ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0.1,
            openai_api_key=config('OPENAI_API_KEY', default='your-openai-key-here')
        )
    
    def load_required_files(self, additional_files: List[str] = None) -> Dict[str, str]:
        """Carrega arquivos obrigatórios definidos no config"""
        files_content = {}
        
        # Arquivos obrigatórios do config
        required_files = self.config.get('devLoadAlwaysFiles', [])
        
        # Arquivos adicionais específicos do agente
        if additional_files:
            required_files.extend(additional_files)
        
        for file_path in required_files:
            try:
                full_path = Path(__file__).parent.parent.parent / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as file:
                        files_content[file_path] = file.read()
                else:
                    print(f"⚠️ Arquivo não encontrado: {file_path}")
            except Exception as e:
                print(f"❌ Erro ao carregar {file_path}: {e}")
        
        return files_content
    
    def create_agent(self, role: str, goal: str, backstory: str, tools: List = None) -> Agent:
        """Cria um agente CrewAI com configurações padrão"""
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=tools or [],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def save_output(self, content: str, filename: str, directory: str = "output") -> str:
        """Salva saída do agente em arquivo"""
        output_dir = Path(__file__).parent.parent / directory
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return str(file_path)
    
    def get_project_context(self) -> str:
        """Retorna contexto do projeto para os agentes"""
        return f"""
        PROJETO: {self.config['project']['name']}
        VERSÃO: {self.config['project']['version']}
        DESCRIÇÃO: {self.config['project']['description']}
        
        STACK TECNOLÓGICO:
        - Backend: {self.config['product_structure']['backend']['framework']}
        - Database: {self.config['product_structure']['backend']['database']}
        - Frontend: {self.config['product_structure']['frontend']['framework']}
        - IA: {self.config['product_structure']['backend']['ai_integration']}
        - Cache: {self.config['product_structure']['backend']['cache']}

        METODOLOGIA: BMad Method - Desenvolvimento Guiado por Documentos
        """
