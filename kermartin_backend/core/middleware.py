"""
Middleware personalizado para Kermartin 3.0
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from .models import LogSeguranca

logger = logging.getLogger('kermartin')


class SecurityMiddleware(MiddlewareMixin):
    """Middleware de segurança para monitoramento e proteção"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Processa requisição antes da view"""
        
        # Adicionar timestamp para medir tempo de resposta
        request.start_time = time.time()
        
        # Obter IP real do cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        request.client_ip = ip
        
        # Verificar se IP está bloqueado
        blocked_ips = cache.get('blocked_ips', set())
        if ip in blocked_ips:
            logger.warning(f"Acesso negado para IP bloqueado: {ip}")
            return JsonResponse(
                {'error': 'Acesso negado'}, 
                status=403
            )
        
        # Monitorar tentativas de acesso suspeitas
        self._monitor_suspicious_activity(request)
        
        return None
    
    def process_response(self, request, response):
        """Processa resposta após a view"""
        
        # Calcular tempo de resposta
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            response['X-Response-Time'] = f"{response_time:.3f}s"
        
        # Log de requisições importantes
        if request.path.startswith('/api/'):
            self._log_api_request(request, response)
        
        return response
    
    def _monitor_suspicious_activity(self, request):
        """Monitora atividades suspeitas"""
        
        suspicious_patterns = [
            'admin', 'wp-admin', 'phpmyadmin', '.env', 'config',
            'backup', 'sql', 'database', 'shell', 'cmd'
        ]
        
        path = request.path.lower()
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Verificar padrões suspeitos na URL
        for pattern in suspicious_patterns:
            if pattern in path:
                self._log_security_event(
                    request,
                    'acesso_suspeito',
                    f"Tentativa de acesso a: {request.path}"
                )
                break
        
        # Verificar User-Agent suspeito
        suspicious_agents = ['bot', 'crawler', 'scanner', 'hack']
        for agent in suspicious_agents:
            if agent in user_agent:
                self._log_security_event(
                    request,
                    'user_agent_suspeito',
                    f"User-Agent suspeito: {user_agent[:100]}"
                )
                break
    
    def _log_api_request(self, request, response):
        """Log de requisições da API"""
        
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            
            # Log apenas requisições lentas ou com erro
            if response_time > 5.0 or response.status_code >= 400:
                logger.info(
                    f"API Request: {request.method} {request.path} "
                    f"- Status: {response.status_code} "
                    f"- Time: {response_time:.3f}s "
                    f"- IP: {request.client_ip}"
                )
    
    def _log_security_event(self, request, event_type, description):
        """Registra evento de segurança"""
        
        try:
            LogSeguranca.objects.create(
                tipo_evento=event_type,
                descricao=description,
                ip_address=request.client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                dados_extras={
                    'path': request.path,
                    'method': request.method,
                    'headers': dict(request.headers)
                }
            )
        except Exception as e:
            logger.error(f"Erro ao registrar evento de segurança: {e}")


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para rate limiting"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Verifica rate limiting"""
        
        # Aplicar rate limiting apenas para APIs críticas
        if not request.path.startswith('/api/'):
            return None
        
        # Obter identificador do cliente
        if request.user.is_authenticated:
            client_id = f"user_{request.user.id}"
        else:
            client_id = f"ip_{request.client_ip}"
        
        # Verificar diferentes tipos de rate limit
        limits = {
            '/api/analises/': {'limit': 10, 'window': 3600},  # 10 análises por hora
            '/api/documentos/': {'limit': 20, 'window': 3600},  # 20 uploads por hora
            '/api/auth/login/': {'limit': 5, 'window': 3600},  # 5 logins por hora
        }
        
        for path_prefix, config in limits.items():
            if request.path.startswith(path_prefix):
                if self._is_rate_limited(client_id, path_prefix, config):
                    logger.warning(f"Rate limit excedido: {client_id} - {path_prefix}")
                    return JsonResponse(
                        {'error': 'Rate limit excedido. Tente novamente mais tarde.'},
                        status=429
                    )
        
        return None
    
    def _is_rate_limited(self, client_id, path, config):
        """Verifica se cliente excedeu rate limit"""
        
        cache_key = f"rate_limit_{client_id}_{path.replace('/', '_')}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= config['limit']:
            return True
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, timeout=config['window'])
        return False


class PerformanceMiddleware(MiddlewareMixin):
    """Middleware para monitoramento de performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Inicia monitoramento de performance"""
        request.perf_start = time.time()
        return None
    
    def process_response(self, request, response):
        """Finaliza monitoramento de performance"""
        
        if hasattr(request, 'perf_start'):
            duration = time.time() - request.perf_start
            
            # Log de requisições lentas
            if duration > 2.0:  # Mais de 2 segundos
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )
            
            # Adicionar header de performance
            response['X-Performance-Time'] = f"{duration:.3f}s"
        
        return response


class CORSMiddleware(MiddlewareMixin):
    """Middleware personalizado para CORS"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """Adiciona headers CORS personalizados"""
        
        # Headers de segurança
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Headers específicos do Kermartin
        response['X-Kermartin-Version'] = '3.0'
        response['X-Powered-By'] = 'Kermartin AI Legal Analysis'
        
        return response
