"""
Sistema de Cache Avançado para Melkor 3.0
Otimização de performance para análises de IA
"""

import hashlib
import json
import logging
from typing import Dict, Optional, Any
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger('ai_engine')


class MelkorCacheManager:
    """Gerenciador de cache especializado para o Melkor"""
    
    def __init__(self):
        self.default_timeout = getattr(settings, 'MELKOR_CACHE_TIMEOUT', 3600)  # 1 hora
        self.prefix = 'melkor_3_0'
    
    def get_analysis_cache_key(self, documento_id: str, bloco: int, subetapa: int, content_hash: str = None) -> str:
        """Gera chave de cache para análise"""
        
        if content_hash:
            key_data = f"{documento_id}_{bloco}_{subetapa}_{content_hash}"
        else:
            key_data = f"{documento_id}_{bloco}_{subetapa}"
        
        # Gerar hash da chave para garantir tamanho consistente
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.prefix}_analysis_{key_hash}"
    
    def get_document_cache_key(self, documento_id: str, operation: str) -> str:
        """Gera chave de cache para operações de documento"""
        return f"{self.prefix}_doc_{documento_id}_{operation}"
    
    def get_user_cache_key(self, user_id: str, operation: str) -> str:
        """Gera chave de cache para operações de usuário"""
        return f"{self.prefix}_user_{user_id}_{operation}"
    
    def cache_analysis_result(
        self, 
        documento_id: str, 
        bloco: int, 
        subetapa: int, 
        result: Dict,
        content_hash: str = None,
        timeout: int = None
    ) -> bool:
        """Armazena resultado de análise no cache"""
        
        try:
            cache_key = self.get_analysis_cache_key(documento_id, bloco, subetapa, content_hash)
            
            # Preparar dados para cache
            cache_data = {
                'result': result,
                'cached_at': datetime.now().isoformat(),
                'bloco': bloco,
                'subetapa': subetapa,
                'documento_id': documento_id
            }
            
            timeout = timeout or self.default_timeout
            success = cache.set(cache_key, cache_data, timeout=timeout)
            
            if success:
                logger.info(f"Resultado de análise cacheado: {cache_key}")
            else:
                logger.warning(f"Falha ao cachear resultado: {cache_key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao cachear análise: {e}")
            return False
    
    def get_cached_analysis(
        self, 
        documento_id: str, 
        bloco: int, 
        subetapa: int,
        content_hash: str = None
    ) -> Optional[Dict]:
        """Recupera resultado de análise do cache"""
        
        try:
            cache_key = self.get_analysis_cache_key(documento_id, bloco, subetapa, content_hash)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Resultado encontrado em cache: {cache_key}")
                return cached_data['result']
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar cache: {e}")
            return None
    
    def cache_document_analysis(self, documento_id: str, analysis_data: Dict, timeout: int = None) -> bool:
        """Cache de análise completa de documento"""
        
        try:
            cache_key = self.get_document_cache_key(documento_id, 'full_analysis')
            
            cache_data = {
                'analysis': analysis_data,
                'cached_at': datetime.now().isoformat(),
                'documento_id': documento_id
            }
            
            timeout = timeout or (self.default_timeout * 2)  # 2 horas para análise completa
            return cache.set(cache_key, cache_data, timeout=timeout)
            
        except Exception as e:
            logger.error(f"Erro ao cachear análise de documento: {e}")
            return False
    
    def get_cached_document_analysis(self, documento_id: str) -> Optional[Dict]:
        """Recupera análise completa de documento do cache"""
        
        try:
            cache_key = self.get_document_cache_key(documento_id, 'full_analysis')
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data['analysis']
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar cache de documento: {e}")
            return None
    
    def cache_user_statistics(self, user_id: str, stats: Dict, timeout: int = None) -> bool:
        """Cache de estatísticas do usuário"""
        
        try:
            cache_key = self.get_user_cache_key(user_id, 'statistics')
            
            cache_data = {
                'stats': stats,
                'cached_at': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            timeout = timeout or 1800  # 30 minutos para estatísticas
            return cache.set(cache_key, cache_data, timeout=timeout)
            
        except Exception as e:
            logger.error(f"Erro ao cachear estatísticas: {e}")
            return False
    
    def get_cached_user_statistics(self, user_id: str) -> Optional[Dict]:
        """Recupera estatísticas do usuário do cache"""
        
        try:
            cache_key = self.get_user_cache_key(user_id, 'statistics')
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data['stats']
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar cache de estatísticas: {e}")
            return None
    
    def invalidate_analysis_cache(self, documento_id: str, bloco: int = None, subetapa: int = None) -> bool:
        """Invalida cache de análise específica ou todas de um documento"""
        
        try:
            if bloco and subetapa:
                # Invalidar análise específica
                cache_key = self.get_analysis_cache_key(documento_id, bloco, subetapa)
                cache.delete(cache_key)
                logger.info(f"Cache invalidado: {cache_key}")
            else:
                # Invalidar todas as análises do documento
                # Isso requer uma implementação mais complexa com padrões
                self.invalidate_document_cache(documento_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return False
    
    def invalidate_document_cache(self, documento_id: str) -> bool:
        """Invalida todo o cache relacionado a um documento"""
        
        try:
            # Invalidar análise completa
            cache_key = self.get_document_cache_key(documento_id, 'full_analysis')
            cache.delete(cache_key)
            
            # Invalidar análises individuais (implementação simplificada)
            for bloco in range(1, 5):
                max_subetapas = 6 if bloco == 1 else 5
                for subetapa in range(1, max_subetapas + 1):
                    cache_key = self.get_analysis_cache_key(documento_id, bloco, subetapa)
                    cache.delete(cache_key)
            
            logger.info(f"Cache de documento invalidado: {documento_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar cache de documento: {e}")
            return False
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalida cache do usuário"""
        
        try:
            cache_key = self.get_user_cache_key(user_id, 'statistics')
            cache.delete(cache_key)
            
            logger.info(f"Cache de usuário invalidado: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar cache de usuário: {e}")
            return False
    
    def get_cache_statistics(self) -> Dict:
        """Retorna estatísticas do cache"""
        
        try:
            # Esta implementação depende do backend de cache usado
            # Para Redis, seria possível obter estatísticas mais detalhadas
            
            stats = {
                'cache_backend': str(cache.__class__),
                'default_timeout': self.default_timeout,
                'prefix': self.prefix,
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de cache: {e}")
            return {}
    
    def warm_up_cache(self, documento_id: str, content: str) -> bool:
        """Pré-aquece cache com análises comuns"""
        
        try:
            # Gerar hash do conteúdo
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            # Cache de metadados do documento
            metadata = {
                'content_hash': content_hash,
                'content_length': len(content),
                'warmed_up_at': datetime.now().isoformat()
            }
            
            cache_key = self.get_document_cache_key(documento_id, 'metadata')
            cache.set(cache_key, metadata, timeout=self.default_timeout * 4)  # 4 horas
            
            logger.info(f"Cache pré-aquecido para documento: {documento_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao pré-aquecer cache: {e}")
            return False
    
    def cleanup_expired_cache(self) -> Dict:
        """Limpa cache expirado (implementação básica)"""
        
        try:
            # Esta funcionalidade depende do backend de cache
            # Para implementação completa, seria necessário usar Redis diretamente
            
            result = {
                'cleaned': True,
                'timestamp': datetime.now().isoformat(),
                'message': 'Limpeza automática pelo backend de cache'
            }
            
            logger.info("Limpeza de cache executada")
            return result
            
        except Exception as e:
            logger.error(f"Erro na limpeza de cache: {e}")
            return {'cleaned': False, 'error': str(e)}
