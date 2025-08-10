"""
Processador de Documentos do Kermartin 3.0
Extração de texto de PDFs e processamento de documentos jurídicos
"""

import os
import hashlib
import logging
from typing import Optional, Dict, List
import fitz  # PyMuPDF
import pdfplumber
from django.conf import settings

logger = logging.getLogger('ai_engine')


class DocumentProcessor:
    """Processador de documentos PDF"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = ['.pdf']
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrai texto de arquivo PDF
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            str: Texto extraído do PDF
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"Arquivo muito grande: {file_size} bytes")
        
        try:
            # Tentar com PyMuPDF primeiro (mais rápido)
            text = self._extract_with_pymupdf(file_path)
            
            # Se não conseguir texto suficiente, tentar com pdfplumber
            if len(text.strip()) < 100:
                logger.info("Tentando extração com pdfplumber...")
                text = self._extract_with_pdfplumber(file_path)
            
            # Limpar e formatar texto
            text = self._clean_text(text)
            
            if len(text.strip()) < 50:
                raise ValueError("Não foi possível extrair texto suficiente do PDF")
            
            logger.info(f"Texto extraído com sucesso: {len(text)} caracteres")
            return text
            
        except Exception as e:
            logger.error(f"Erro na extração de texto: {e}")
            raise
    
    def _extract_with_pymupdf(self, file_path: str) -> str:
        """Extrai texto usando PyMuPDF"""
        
        text = ""
        
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text.strip():
                    text += f"\n--- PÁGINA {page_num + 1} ---\n"
                    text += page_text
                    text += "\n"
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Erro no PyMuPDF: {e}")
            raise
        
        return text
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extrai texto usando pdfplumber (melhor para tabelas)"""
        
        text = ""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text += f"\n--- PÁGINA {page_num + 1} ---\n"
                        text += page_text
                        text += "\n"
                    
                    # Extrair tabelas se houver
                    tables = page.extract_tables()
                    if tables:
                        text += "\n--- TABELAS ---\n"
                        for table in tables:
                            for row in table:
                                if row:
                                    text += " | ".join(str(cell) if cell else "" for cell in row)
                                    text += "\n"
                        text += "\n"
        
        except Exception as e:
            logger.error(f"Erro no pdfplumber: {e}")
            raise
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Limpa e formata o texto extraído"""
        
        if not text:
            return ""
        
        # Remover caracteres de controle
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Normalizar quebras de linha
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remover linhas vazias excessivas
        lines = text.split('\n')
        cleaned_lines = []
        empty_count = 0
        
        for line in lines:
            line = line.strip()
            
            if line:
                cleaned_lines.append(line)
                empty_count = 0
            else:
                empty_count += 1
                if empty_count <= 2:  # Máximo 2 linhas vazias consecutivas
                    cleaned_lines.append('')
        
        # Juntar linhas
        text = '\n'.join(cleaned_lines)
        
        # Remover espaços excessivos
        text = ' '.join(text.split())
        
        # Adicionar quebras de linha em pontos apropriados
        text = text.replace('. ', '.\n')
        text = text.replace('? ', '?\n')
        text = text.replace('! ', '!\n')
        
        return text.strip()
    
    def generate_file_hash(self, file_path: str) -> str:
        """Gera hash SHA-256 do arquivo"""
        
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao gerar hash: {e}")
            raise
    
    def analyze_document_structure(self, text: str) -> Dict:
        """Analisa estrutura do documento jurídico"""
        
        structure = {
            'tipo_provavel': 'desconhecido',
            'secoes_identificadas': [],
            'tem_assinaturas': False,
            'tem_carimbos': False,
            'qualidade_texto': 'boa'
        }
        
        text_lower = text.lower()
        
        # Identificar tipo de documento
        if 'inquérito policial' in text_lower or 'auto de prisão' in text_lower:
            structure['tipo_provavel'] = 'inquerito'
        elif 'denúncia' in text_lower and 'ministério público' in text_lower:
            structure['tipo_provavel'] = 'denuncia'
        elif 'sentença' in text_lower and 'pronúncia' in text_lower:
            structure['tipo_provavel'] = 'sentenca_pronuncia'
        elif 'alegações finais' in text_lower:
            structure['tipo_provavel'] = 'alegacoes_finais'
        elif 'ata' in text_lower and 'julgamento' in text_lower:
            structure['tipo_provavel'] = 'ata_julgamento'
        
        # Identificar seções
        secoes_comuns = [
            'relatório', 'fundamentação', 'dispositivo', 'conclusão',
            'dos fatos', 'do direito', 'das provas', 'preliminares'
        ]
        
        for secao in secoes_comuns:
            if secao in text_lower:
                structure['secoes_identificadas'].append(secao)
        
        # Verificar assinaturas e carimbos
        indicadores_assinatura = ['assinado', 'assinatura', 'subscrito']
        indicadores_carimbo = ['carimbo', 'selo', 'rubrica']
        
        structure['tem_assinaturas'] = any(ind in text_lower for ind in indicadores_assinatura)
        structure['tem_carimbos'] = any(ind in text_lower for ind in indicadores_carimbo)
        
        # Avaliar qualidade do texto
        if len(text) < 500:
            structure['qualidade_texto'] = 'baixa'
        elif text.count('?') > len(text) / 100:  # Muitos caracteres não reconhecidos
            structure['qualidade_texto'] = 'media'
        
        return structure
    
    def extract_key_information(self, text: str) -> Dict:
        """Extrai informações-chave do documento"""
        
        info = {
            'numeros_processo': [],
            'nomes_pessoas': [],
            'datas': [],
            'valores_monetarios': [],
            'artigos_lei': []
        }
        
        import re
        
        # Números de processo
        processo_pattern = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
        info['numeros_processo'] = re.findall(processo_pattern, text)
        
        # Datas
        data_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2} de \w+ de \d{4}'
        ]
        
        for pattern in data_patterns:
            info['datas'].extend(re.findall(pattern, text))
        
        # Valores monetários
        valor_pattern = r'R\$\s*\d+(?:\.\d{3})*(?:,\d{2})?'
        info['valores_monetarios'] = re.findall(valor_pattern, text)
        
        # Artigos de lei
        artigo_pattern = r'art(?:igo)?\.?\s*\d+(?:[-º°]\w*)?'
        info['artigos_lei'] = re.findall(artigo_pattern, text, re.IGNORECASE)
        
        return info
    
    def validate_pdf_integrity(self, file_path: str) -> bool:
        """Valida integridade do arquivo PDF"""
        
        try:
            # Tentar abrir com PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False
            
            # Tentar extrair texto da primeira página
            doc = fitz.open(file_path)
            first_page = doc.load_page(0)
            text = first_page.get_text()
            doc.close()
            
            # PDF válido deve ter pelo menos algum conteúdo
            return len(text.strip()) > 0 or True  # Aceitar PDFs só com imagens
            
        except Exception as e:
            logger.error(f"PDF inválido: {e}")
            return False
