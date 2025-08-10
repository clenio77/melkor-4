"""
Sistema de Segurança do Kermartin 3.0
Proteção contra prompt injection e validações de segurança
"""

import re
import logging
from typing import List, Dict, Optional
from django.core.cache import cache
from core.models import LogSeguranca

logger = logging.getLogger('ai_engine')


class SecurityValidator:
    """Validador de segurança para o sistema Kermartin"""
    
    def __init__(self):
        self.dangerous_patterns = self._load_dangerous_patterns()
        # Permitir override pelo settings
        try:
            from django.conf import settings
            self.max_content_length = settings.KERMARTIN_SETTINGS.get('SECURITY_MAX_CONTENT_LENGTH', 300000)
        except Exception:
            self.max_content_length = 50000  # fallback
        self.max_prompt_length = 100000  # 100KB
    
    def validate_prompt_injection(self, prompt: str) -> bool:
        """
        Valida se o prompt contém tentativas de injection
        
        Args:
            prompt: Texto do prompt a ser validado
            
        Returns:
            bool: True se seguro, False se suspeito
        """
        
        if not prompt or len(prompt) > self.max_prompt_length:
            return False
        
        prompt_lower = prompt.lower()
        
        # Verificar padrões perigosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                self._log_security_event(
                    'prompt_injection',
                    f"Padrão suspeito detectado: {pattern}",
                    {'prompt_snippet': prompt[:200]}
                )
                return False
        
        # Verificar comandos de sistema
        system_commands = [
            'rm -rf', 'del ', 'format c:', 'sudo ', 'chmod ',
            'passwd', 'useradd', 'userdel', 'kill ', 'killall'
        ]
        
        for cmd in system_commands:
            if cmd in prompt_lower:
                self._log_security_event(
                    'prompt_injection',
                    f"Comando de sistema detectado: {cmd}",
                    {'prompt_snippet': prompt[:200]}
                )
                return False
        
        return True
    
    def validate_document_content(self, content: str) -> bool:
        """
        Valida conteúdo de documento
        
        Args:
            content: Conteúdo do documento
            
        Returns:
            bool: True se válido, False se suspeito
        """
        
        if not content:
            return False
        
        if len(content) > self.max_content_length:
            logger.warning(f"Documento muito grande: {len(content)} chars")
            return False
        
        # Verificar conteúdo malicioso
        malicious_content = [
            '<script', 'javascript:', 'data:text/html',
            'eval(', 'exec(', 'system(', 'shell_exec'
        ]
        
        content_lower = content.lower()
        for pattern in malicious_content:
            if pattern in content_lower:
                self._log_security_event(
                    'upload_suspeito',
                    f"Conteúdo malicioso detectado: {pattern}",
                    {'content_snippet': content[:200]}
                )
                return False
        
        return True
    
    def validate_file_upload(self, file_obj) -> Dict[str, bool]:
        """
        Valida upload de arquivo
        
        Args:
            file_obj: Objeto de arquivo Django
            
        Returns:
            Dict com resultado da validação
        """
        
        result = {
            'valid': True,
            'errors': []
        }
        
        # Verificar extensão
        if not file_obj.name.lower().endswith('.pdf'):
            result['valid'] = False
            result['errors'].append('Apenas arquivos PDF são permitidos')
        
        # Verificar tamanho
        max_size = 10 * 1024 * 1024  # 10MB
        if file_obj.size > max_size:
            result['valid'] = False
            result['errors'].append(f'Arquivo muito grande: {file_obj.size} bytes')
        
        # Verificar nome do arquivo
        dangerous_names = ['..', '/', '\\', '<', '>', '|', ':', '*', '?', '"']
        for char in dangerous_names:
            if char in file_obj.name:
                result['valid'] = False
                result['errors'].append('Nome de arquivo contém caracteres perigosos')
                break
        
        if not result['valid']:
            self._log_security_event(
                'upload_suspeito',
                f"Upload rejeitado: {file_obj.name}",
                {'errors': result['errors'], 'size': file_obj.size}
            )
        
        return result
    
    def check_rate_limit(self, user_id: str, action: str = 'analysis') -> bool:
        """
        Verifica limite de taxa para usuário
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação
            
        Returns:
            bool: True se dentro do limite, False se excedido
        """
        
        cache_key = f"rate_limit_{user_id}_{action}"
        current_count = cache.get(cache_key, 0)
        
        # Limites por hora
        limits = {
            'analysis': 50,
            'upload': 20,
            'login': 10
        }
        
        limit = limits.get(action, 10)
        
        if current_count >= limit:
            self._log_security_event(
                'rate_limit_exceeded',
                f"Limite excedido para {action}: {current_count}/{limit}",
                {'user_id': user_id, 'action': action}
            )
            return False
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, timeout=3600)  # 1 hora
        return True
    
    def validate_api_request(self, request) -> Dict[str, any]:
        """
        Valida requisição da API
        
        Args:
            request: Objeto request do Django
            
        Returns:
            Dict com resultado da validação
        """
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or len(user_agent) < 10:
            result['warnings'].append('User-Agent suspeito')
        
        # Verificar IP
        ip_address = self._get_client_ip(request)
        if self._is_blocked_ip(ip_address):
            result['valid'] = False
            result['errors'].append('IP bloqueado')
        
        # Verificar headers suspeitos
        suspicious_headers = ['x-forwarded-for', 'x-real-ip', 'x-cluster-client-ip']
        for header in suspicious_headers:
            if header in request.META:
                result['warnings'].append(f'Header suspeito: {header}')
        
        return result
    
    def _load_dangerous_patterns(self) -> List[str]:
        """Carrega padrões perigosos para detecção de injection"""
        
        return [
            # Comandos de bypass
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything\s+above',
            r'disregard\s+the\s+above',
            r'new\s+instructions?:',
            
            # Tentativas de revelação
            r'show\s+me\s+your\s+prompts?',
            r'reveal\s+your\s+system\s+message',
            r'what\s+are\s+your\s+instructions',
            r'translate\s+your\s+instructions',
            
            # Comandos de sistema
            r'system\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            r'import\s+os',
            r'subprocess\.',
            
            # Tentativas de escape
            r'```\s*python',
            r'```\s*bash',
            r'```\s*shell',
            r'<script',
            r'javascript:',
            
            # Manipulação de contexto
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'act\s+as\s+if',
            r'roleplay\s+as',
            
            # Comandos de administração
            r'admin\s+mode',
            r'developer\s+mode',
            r'debug\s+mode',
            r'maintenance\s+mode',
        ]
    
    def _log_security_event(
        self, 
        event_type: str, 
        description: str, 
        extra_data: Dict = None
    ):
        """Registra evento de segurança"""
        
        try:
            LogSeguranca.objects.create(
                tipo_evento=event_type,
                descricao=description,
                ip_address='127.0.0.1',  # Será preenchido pela view
                dados_extras=extra_data or {}
            )
            
            logger.warning(f"SECURITY EVENT: {event_type} - {description}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar evento de segurança: {e}")
    
    def _get_client_ip(self, request) -> str:
        """Obtém IP real do cliente"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip or '127.0.0.1'
    
    def _is_blocked_ip(self, ip_address: str) -> bool:
        """Verifica se IP está bloqueado"""
        
        # Lista de IPs bloqueados (pode vir do banco ou cache)
        blocked_ips = cache.get('blocked_ips', set())
        
        return ip_address in blocked_ips
    
    def block_ip(self, ip_address: str, duration: int = 3600):
        """Bloqueia IP por tempo determinado"""
        
        blocked_ips = cache.get('blocked_ips', set())
        blocked_ips.add(ip_address)
        cache.set('blocked_ips', blocked_ips, timeout=duration)
        
        self._log_security_event(
            'ip_blocked',
            f"IP bloqueado: {ip_address}",
            {'duration': duration}
        )
    
    def get_security_summary(self) -> Dict:
        """Retorna resumo de segurança"""
        
        from django.utils import timezone
        from datetime import timedelta
        
        last_24h = timezone.now() - timedelta(hours=24)
        
        events = LogSeguranca.objects.filter(created_at__gte=last_24h)
        
        summary = {
            'total_events': events.count(),
            'events_by_type': {},
            'blocked_ips': len(cache.get('blocked_ips', set())),
            'last_24h': {
                'prompt_injections': events.filter(tipo_evento='prompt_injection').count(),
                'suspicious_uploads': events.filter(tipo_evento='upload_suspeito').count(),
                'rate_limits': events.filter(tipo_evento='rate_limit_exceeded').count(),
            }
        }
        
        # Contar eventos por tipo
        for event in events.values('tipo_evento').distinct():
            event_type = event['tipo_evento']
            summary['events_by_type'][event_type] = events.filter(
                tipo_evento=event_type
            ).count()
        
        return summary
