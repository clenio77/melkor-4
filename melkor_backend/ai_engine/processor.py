"""
Processador Principal do Melkor 3.0
Engine de IA para análise jurídica especializada em Tribunal do Júri
"""

import time
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from openai import OpenAI
from .prompts import get_prompt, get_prompt_title, MELKOR_PERSONA
from .security import SecurityValidator
from core.models import ResultadoAnalise, SessaoAnalise, Documento

logger = logging.getLogger('ai_engine')


class MelkorProcessor:
    """Processador principal do agente Melkor"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.security = SecurityValidator()
        
    def analyze_document(
        self, 
        documento: Documento, 
        bloco: int, 
        subetapa: int,
        sessao: SessaoAnalise
    ) -> Dict:
        """
        Analisa um documento específico usando o bloco e subetapa
        
        Args:
            documento: Instância do modelo Documento
            bloco: Número do bloco (1-4)
            subetapa: Número da subetapa (1-6)
            sessao: Sessão de análise atual
            
        Returns:
            Dict com resultado da análise
        """
        
        try:
            # Validação de segurança
            if not self.security.validate_document_content(documento.texto_extraido):
                raise SecurityError("Documento contém conteúdo suspeito")
            
            # Verificar cache
            cache_key = self._generate_cache_key(documento, bloco, subetapa)
            cached_result = cache.get(cache_key)
            
            if cached_result and settings.MELKOR_SETTINGS['CACHE_ANALYSIS_RESULTS']:
                logger.info(f"Resultado encontrado em cache: {cache_key}")
                return cached_result
            
            # Gerar prompt específico
            prompt = get_prompt(bloco, subetapa, documento.texto_extraido)
            
            # Validar prompt contra injection
            if not self.security.validate_prompt_injection(prompt):
                raise SecurityError("Tentativa de prompt injection detectada")
            
            # Processar com OpenAI
            start_time = time.time()
            response = self._call_openai(prompt)
            processing_time = time.time() - start_time
            
            # Preparar resultado
            result = {
                'bloco': bloco,
                'subetapa': subetapa,
                'titulo': get_prompt_title(bloco, subetapa),
                'resposta': response['content'],
                'tokens_prompt': response['tokens_prompt'],
                'tokens_resposta': response['tokens_response'],
                'tokens_total': response['tokens_total'],
                'tempo_processamento': processing_time,
                'modelo_usado': self.model,
                'prompt_usado': prompt[:1000] + "..." if len(prompt) > 1000 else prompt
            }
            
            # Salvar no banco
            self._save_analysis_result(documento, sessao, result)
            
            # Salvar em cache
            if settings.MELKOR_SETTINGS['CACHE_ANALYSIS_RESULTS']:
                cache.set(
                    cache_key, 
                    result, 
                    timeout=settings.MELKOR_SETTINGS['CACHE_TIMEOUT']
                )
            
            logger.info(f"Análise concluída: Bloco {bloco}.{subetapa} - {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            raise
    
    def analyze_complete_process(
        self, 
        documentos: List[Documento], 
        sessao: SessaoAnalise,
        blocos_selecionados: List[int] = None
    ) -> Dict:
        """
        Executa análise completa de um processo
        
        Args:
            documentos: Lista de documentos do processo
            sessao: Sessão de análise
            blocos_selecionados: Blocos a analisar (default: todos)
            
        Returns:
            Dict com resultados consolidados
        """
        
        if not blocos_selecionados:
            blocos_selecionados = [1, 2, 3, 4]
        
        resultados = {}
        total_tokens = 0
        total_time = 0
        
        try:
            sessao.status = 'em_progresso'
            sessao.save()
            
            for bloco in blocos_selecionados:
                resultados[f'bloco_{bloco}'] = {}
                
                # Determinar número de subetapas por bloco
                max_subetapas = self._get_max_subetapas(bloco)
                
                for subetapa in range(1, max_subetapas + 1):
                    sessao.bloco_atual = bloco
                    sessao.subetapa_atual = subetapa
                    sessao.save()
                    
                    # Analisar cada documento
                    for documento in documentos:
                        try:
                            resultado = self.analyze_document(
                                documento, bloco, subetapa, sessao
                            )
                            
                            doc_key = f"documento_{documento.id}"
                            if doc_key not in resultados[f'bloco_{bloco}']:
                                resultados[f'bloco_{bloco}'][doc_key] = {}
                            
                            resultados[f'bloco_{bloco}'][doc_key][f'subetapa_{subetapa}'] = resultado
                            
                            total_tokens += resultado['tokens_total']
                            total_time += resultado['tempo_processamento']
                            
                        except Exception as e:
                            logger.error(f"Erro na análise do documento {documento.id}: {e}")
                            continue
            
            # Finalizar sessão
            sessao.finalizar_sessao()
            
            # Consolidar resultados
            consolidado = {
                'sessao_id': str(sessao.id),
                'status': 'concluida',
                'resultados': resultados,
                'estatisticas': {
                    'total_tokens': total_tokens,
                    'total_tempo': total_time,
                    'documentos_analisados': len(documentos),
                    'blocos_processados': len(blocos_selecionados)
                }
            }
            
            logger.info(f"Análise completa finalizada: {total_time:.2f}s, {total_tokens} tokens")
            return consolidado
            
        except Exception as e:
            sessao.status = 'erro'
            sessao.save()
            logger.error(f"Erro na análise completa: {e}")
            raise
    
    def _call_openai(self, prompt: str) -> Dict:
        """Chama a API da OpenAI"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": MELKOR_PERSONA},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,
                top_p=0.9
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_prompt': response.usage.prompt_tokens,
                'tokens_response': response.usage.completion_tokens,
                'tokens_total': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {e}")
            raise OpenAIError(f"Falha na comunicação com OpenAI: {e}")
    
    def _save_analysis_result(
        self, 
        documento: Documento, 
        sessao: SessaoAnalise, 
        result: Dict
    ):
        """Salva resultado da análise no banco"""
        
        try:
            ResultadoAnalise.objects.update_or_create(
                sessao=sessao,
                documento=documento,
                bloco=result['bloco'],
                subetapa=result['subetapa'],
                defaults={
                    'prompt_usado': result['prompt_usado'],
                    'resposta_ia': result['resposta'],
                    'tokens_prompt': result['tokens_prompt'],
                    'tokens_resposta': result['tokens_resposta'],
                    'tokens_total': result['tokens_total'],
                    'tempo_processamento': result['tempo_processamento'],
                    'modelo_usado': result['modelo_usado']
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultado: {e}")
            raise
    
    def _generate_cache_key(
        self, 
        documento: Documento, 
        bloco: int, 
        subetapa: int
    ) -> str:
        """Gera chave de cache para análise"""
        
        content_hash = hashlib.sha256(
            documento.texto_extraido.encode('utf-8')
        ).hexdigest()[:16]
        
        return f"melkor_analysis_{documento.id}_{bloco}_{subetapa}_{content_hash}"
    
    def _get_max_subetapas(self, bloco: int) -> int:
        """Retorna número máximo de subetapas por bloco"""
        
        subetapas_map = {
            1: 6,  # Fase de Inquérito
            2: 5,  # Primeira Fase do Procedimento
            3: 5,  # Segunda Fase do Procedimento
            4: 5,  # Debates no Júri
        }
        
        return subetapas_map.get(bloco, 6)
    
    def get_analysis_summary(self, sessao: SessaoAnalise) -> Dict:
        """Retorna resumo de uma análise"""
        
        resultados = ResultadoAnalise.objects.filter(sessao=sessao)
        
        summary = {
            'sessao_id': str(sessao.id),
            'processo': sessao.processo.titulo,
            'modo_analise': sessao.get_modo_analise_display(),
            'status': sessao.get_status_display(),
            'tempo_total': str(sessao.tempo_total) if sessao.tempo_total else None,
            'estatisticas': {
                'total_analises': resultados.count(),
                'total_tokens': sum(r.tokens_total for r in resultados),
                'tempo_medio': resultados.aggregate(
                    avg_time=models.Avg('tempo_processamento')
                )['avg_time'] or 0
            },
            'blocos_analisados': list(
                resultados.values_list('bloco', flat=True).distinct().order_by('bloco')
            )
        }
        
        return summary


class SecurityError(Exception):
    """Exceção para erros de segurança"""
    pass


class OpenAIError(Exception):
    """Exceção para erros da OpenAI"""
    pass
