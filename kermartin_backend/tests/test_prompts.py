"""
Testes para o sistema de prompts do Kermartin 3.0
"""

import pytest
from django.test import TestCase
from ai_engine.prompts import get_prompt, get_prompt_title, KERMARTIN_PERSONA


class TestPrompts(TestCase):
    """Testes para sistema de prompts"""
    
    def setUp(self):
        self.documento_teste = """
        INQUÉRITO POLICIAL Nº 123/2024
        
        Relatório: O indiciado João Silva praticou homicídio qualificado
        contra a vítima Maria Santos, mediante emprego de arma de fogo,
        por motivo fútil e com recurso que dificultou a defesa.
        """
    
    def test_bloco_1_prompts(self):
        """Testa todos os prompts do Bloco 1"""
        for subetapa in range(1, 7):
            prompt = get_prompt(1, subetapa, self.documento_teste)
            titulo = get_prompt_title(1, subetapa)
            
            # Verificar se prompt contém persona
            self.assertIn("Kermartin", prompt)
            self.assertIn("advogado criminalista", prompt)
            
            # Verificar se contém documento
            self.assertIn(self.documento_teste, prompt)
            
            # Verificar se título não está vazio
            self.assertIsNotNone(titulo)
            self.assertTrue(len(titulo) > 0)
    
    def test_bloco_2_prompts(self):
        """Testa todos os prompts do Bloco 2"""
        for subetapa in range(1, 6):
            prompt = get_prompt(2, subetapa, self.documento_teste)
            titulo = get_prompt_title(2, subetapa)
            
            self.assertIn("Kermartin", prompt)
            self.assertIn(self.documento_teste, prompt)
            self.assertIsNotNone(titulo)
    
    def test_bloco_3_prompts(self):
        """Testa todos os prompts do Bloco 3"""
        for subetapa in range(1, 6):
            prompt = get_prompt(3, subetapa, self.documento_teste)
            titulo = get_prompt_title(3, subetapa)
            
            self.assertIn("Kermartin", prompt)
            self.assertIn(self.documento_teste, prompt)
            self.assertIsNotNone(titulo)
    
    def test_bloco_4_prompts(self):
        """Testa todos os prompts do Bloco 4"""
        for subetapa in range(1, 6):
            prompt = get_prompt(4, subetapa, self.documento_teste)
            titulo = get_prompt_title(4, subetapa)
            
            self.assertIn("Kermartin", prompt)
            self.assertIn(self.documento_teste, prompt)
            self.assertIsNotNone(titulo)
    
    def test_prompt_invalido(self):
        """Testa comportamento com bloco/subetapa inválidos"""
        with self.assertRaises(ValueError):
            get_prompt(5, 1, self.documento_teste)  # Bloco inexistente
        
        with self.assertRaises(ValueError):
            get_prompt(1, 10, self.documento_teste)  # Subetapa inexistente
    
    def test_persona_kermartin(self):
        """Testa se persona está bem definida"""
        self.assertIn("advogado criminalista", KERMARTIN_PERSONA)
        self.assertIn("Tribunal do Júri", KERMARTIN_PERSONA)
        self.assertIn("experiência", KERMARTIN_PERSONA)
        self.assertIn("estratégia", KERMARTIN_PERSONA)
    
    def test_titulos_especificos(self):
        """Testa títulos específicos dos prompts"""
        # Bloco 1
        self.assertEqual(get_prompt_title(1, 1), "Análise da Tipificação do Crime")
        self.assertEqual(get_prompt_title(1, 6), "Construção do Projeto de Defesa")
        
        # Bloco 2
        self.assertEqual(get_prompt_title(2, 1), "Análise da Denúncia e Primeiras Teses Defensivas")
        self.assertEqual(get_prompt_title(2, 5), "Alegações Finais da Primeira Fase")
        
        # Bloco 3
        self.assertEqual(get_prompt_title(3, 1), "Requisitos e Diligências da Defesa")
        self.assertEqual(get_prompt_title(3, 5), "Preparação para os Debates Orais")
        
        # Bloco 4
        self.assertEqual(get_prompt_title(4, 1), "Estruturação dos Debates")
        self.assertEqual(get_prompt_title(4, 5), "Exortação Final e Última Impressão")
    
    def test_prompt_length(self):
        """Testa se prompts têm tamanho adequado"""
        for bloco in range(1, 5):
            max_subetapas = 6 if bloco == 1 else 5
            for subetapa in range(1, max_subetapas + 1):
                prompt = get_prompt(bloco, subetapa, self.documento_teste)
                
                # Prompt deve ter pelo menos 1000 caracteres
                self.assertGreater(len(prompt), 1000)
                
                # Prompt não deve ser excessivamente longo
                self.assertLess(len(prompt), 10000)
    
    def test_prompt_structure(self):
        """Testa estrutura dos prompts"""
        prompt = get_prompt(1, 1, self.documento_teste)
        
        # Deve conter seções estruturadas
        self.assertIn("TAREFA:", prompt)
        self.assertIn("DOCUMENTO PARA ANÁLISE:", prompt)
        
        # Deve conter instruções específicas
        self.assertIn("Analise", prompt)
        self.assertIn("estratégia", prompt)


class TestPromptIntegration(TestCase):
    """Testes de integração dos prompts"""
    
    def test_all_blocks_available(self):
        """Testa se todos os blocos estão disponíveis"""
        documento = "Documento de teste"
        
        # Testar todos os blocos e subetapas
        blocos_subetapas = {
            1: 6,  # Bloco 1 tem 6 subetapas
            2: 5,  # Bloco 2 tem 5 subetapas
            3: 5,  # Bloco 3 tem 5 subetapas
            4: 5,  # Bloco 4 tem 5 subetapas
        }
        
        for bloco, max_subetapas in blocos_subetapas.items():
            for subetapa in range(1, max_subetapas + 1):
                # Não deve gerar exceção
                prompt = get_prompt(bloco, subetapa, documento)
                titulo = get_prompt_title(bloco, subetapa)
                
                self.assertIsNotNone(prompt)
                self.assertIsNotNone(titulo)
                self.assertGreater(len(prompt), 100)
                self.assertGreater(len(titulo), 5)
    
    def test_prompt_consistency(self):
        """Testa consistência entre prompts"""
        documento = "Documento de teste"
        
        # Todos os prompts devem conter a persona
        for bloco in range(1, 5):
            max_subetapas = 6 if bloco == 1 else 5
            for subetapa in range(1, max_subetapas + 1):
                prompt = get_prompt(bloco, subetapa, documento)
                
                # Verificar elementos obrigatórios
                self.assertIn("Kermartin", prompt)
                self.assertIn("advogado", prompt)
                self.assertIn(documento, prompt)
    
    def test_total_prompts_count(self):
        """Testa contagem total de prompts"""
        total_prompts = 0
        
        blocos_subetapas = {1: 6, 2: 5, 3: 5, 4: 5}
        
        for bloco, max_subetapas in blocos_subetapas.items():
            total_prompts += max_subetapas
        
        # Deve ter 21 prompts no total
        self.assertEqual(total_prompts, 21)
        
        # Verificar se todos estão acessíveis
        documento = "Teste"
        prompts_acessiveis = 0
        
        for bloco, max_subetapas in blocos_subetapas.items():
            for subetapa in range(1, max_subetapas + 1):
                try:
                    get_prompt(bloco, subetapa, documento)
                    prompts_acessiveis += 1
                except:
                    pass
        
        self.assertEqual(prompts_acessiveis, 21)
