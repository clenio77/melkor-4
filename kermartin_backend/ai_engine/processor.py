"""
Processador Principal do Kermartin 3.0
Engine de IA para análise jurídica especializada em Tribunal do Júri
"""

import time
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from openai import OpenAI
from .prompts import get_prompt, get_prompt_title, KERMARTIN_PERSONA
from .security import SecurityValidator
from core.models import ResultadoAnalise, SessaoAnalise, Documento

logger = logging.getLogger('ai_engine')


class KermartinProcessor:
    """Processador principal do agente Kermartin"""
    
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
            
            if cached_result and settings.KERMARTIN_SETTINGS['CACHE_ANALYSIS_RESULTS']:
                logger.info(f"Resultado encontrado em cache: {cache_key}")
                return cached_result
            
            # Preparar chunking para documentos longos
            from django.conf import settings as djsettings
            full_text = documento.texto_extraido or ''
            chunk_size = djsettings.KERMARTIN_SETTINGS.get('CHUNK_SIZE_CHARS', 12000)
            overlap = djsettings.KERMARTIN_SETTINGS.get('CHUNK_OVERLAP_CHARS', 800)

            def make_chunks(text, size, ov):
                chunks = []
                i = 0
                n = len(text)
                if n == 0:
                    return [""]
                while i < n:
                    end = min(i + size, n)
                    chunks.append(text[i:end])
                    if end >= n:
                        break
                    i = max(end - ov, i + 1)
                return chunks

            text_chunks = make_chunks(full_text, chunk_size, overlap)

            # Agregar respostas e tokens de todos os chunks
            total_prompt_tokens = 0
            total_response_tokens = 0
            total_tokens = 0
            respostas = []
            start_time = time.time()

            for idx, piece in enumerate(text_chunks, start=1):
                # Gerar prompt específico por chunk
                prompt = get_prompt(bloco, subetapa, piece)

                # Validar prompt contra injection
                if not self.security.validate_prompt_injection(prompt):
                    raise SecurityError("Tentativa de prompt injection detectada")

                # Retry com backoff para rate-limit 429
                resp = self._call_openai_with_retry(prompt)
                respostas.append(f"[Parte {idx}/{len(text_chunks)}]\n" + resp['content'])
                total_prompt_tokens += resp['tokens_prompt']
                total_response_tokens += resp['tokens_response']
                total_tokens += resp['tokens_total']

                # Pequena espera entre chunks para aliviar TPM
                sleep_sec = djsettings.KERMARTIN_SETTINGS.get('OPENAI_CHUNK_SLEEP_SEC', 0.25)
                if sleep_sec:
                    time.sleep(sleep_sec)

            processing_time = time.time() - start_time
            resposta_final = "\n\n".join(respostas)
            prompt_usado = f"Documento dividido em {len(text_chunks)} partes; chunk_size={chunk_size}, overlap={overlap}."

            # Preparar resultado
            result = {
                'bloco': bloco,
                'subetapa': subetapa,
                'titulo': get_prompt_title(bloco, subetapa),
                'resposta': resposta_final,
                'tokens_prompt': total_prompt_tokens,
                'tokens_resposta': total_response_tokens,
                'tokens_total': total_tokens,
                'tempo_processamento': processing_time,
                'modelo_usado': self.model,
                'prompt_usado': prompt_usado
            }
            
            # Salvar no banco
            self._save_analysis_result(documento, sessao, result)
            
            # Salvar em cache
            if settings.KERMARTIN_SETTINGS['CACHE_ANALYSIS_RESULTS']:
                cache.set(
                    cache_key, 
                    result, 
                    timeout=settings.KERMARTIN_SETTINGS['CACHE_TIMEOUT']
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
        """Chama a API da OpenAI (uma tentativa)"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": KERMARTIN_PERSONA},
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

    def _call_openai_with_retry(self, prompt: str) -> Dict:
        """Chama a API da OpenAI com retry e backoff progressivo em caso de 429"""
        from django.conf import settings as djsettings
        max_attempts = djsettings.KERMARTIN_SETTINGS.get('OPENAI_RETRY_MAX_ATTEMPTS', 6)
        base_delay = djsettings.KERMARTIN_SETTINGS.get('OPENAI_RETRY_BASE_DELAY_SEC', 1.5)

        attempt = 0
        while True:
            attempt += 1
            try:
                return self._call_openai(prompt)
            except Exception as e:
                msg = str(e)
                if 'rate_limit' in msg or '429' in msg:
                    if attempt >= max_attempts:
                        logger.error(f"OpenAI rate limit após {attempt} tentativas: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Rate limit: tentativa {attempt}/{max_attempts}, aguardando {delay:.2f}s")
                    time.sleep(delay)
                    continue
                # Outros erros: propaga
                raise
    
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
        
        return f"kermartin_analysis_{documento.id}_{bloco}_{subetapa}_{content_hash}"
    
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
