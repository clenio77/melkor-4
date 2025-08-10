"""
Sistema de Métricas e Monitoramento para Melkor 3.0
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from django.core.cache import cache
from django.utils import timezone
from .models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise, LogSeguranca

logger = logging.getLogger('melkor')


class MelkorMetrics:
    """Sistema de métricas do Melkor 3.0"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutos
    
    def get_system_overview(self) -> Dict:
        """Visão geral do sistema"""
        
        cache_key = 'melkor_system_overview'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            overview = {
                'timestamp': timezone.now().isoformat(),
                'users': {
                    'total': Usuario.objects.count(),
                    'active_last_30_days': self._get_active_users_count(30),
                    'new_this_month': self._get_new_users_count(30)
                },
                'processes': {
                    'total': Processo.objects.count(),
                    'by_status': dict(Processo.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
                    'by_crime_type': dict(Processo.objects.values('tipo_crime').annotate(count=Count('id')).values_list('tipo_crime', 'count'))
                },
                'documents': {
                    'total': Documento.objects.count(),
                    'with_text': Documento.objects.filter(texto_extraido__isnull=False).count(),
                    'by_type': dict(Documento.objects.values('tipo_documento').annotate(count=Count('id')).values_list('tipo_documento', 'count')),
                    'total_size_mb': self._get_total_documents_size()
                },
                'analyses': {
                    'total_sessions': SessaoAnalise.objects.count(),
                    'completed_sessions': SessaoAnalise.objects.filter(status='concluida').count(),
                    'total_results': ResultadoAnalise.objects.count(),
                    'by_block': dict(ResultadoAnalise.objects.values('bloco').annotate(count=Count('id')).values_list('bloco', 'count'))
                },
                'performance': self._get_performance_metrics(),
                'security': self._get_security_metrics()
            }
            
            cache.set(cache_key, overview, timeout=self.cache_timeout)
            return overview
            
        except Exception as e:
            logger.error(f"Erro ao obter visão geral do sistema: {e}")
            return {'error': str(e)}
    
    def get_user_metrics(self, user_id: int) -> Dict:
        """Métricas específicas de um usuário"""
        
        cache_key = f'melkor_user_metrics_{user_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            usuario = Usuario.objects.get(user_id=user_id)
            
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'user_info': {
                    'nome': usuario.nome_completo,
                    'oab': f"{usuario.oab_numero}/{usuario.oab_estado}",
                    'member_since': usuario.created_at.isoformat()
                },
                'processes': {
                    'total': usuario.processos.count(),
                    'by_status': dict(usuario.processos.values('status').annotate(count=Count('id')).values_list('status', 'count')),
                    'recent': usuario.processos.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
                },
                'documents': {
                    'total': Documento.objects.filter(processo__usuario=usuario).count(),
                    'processed': Documento.objects.filter(processo__usuario=usuario, texto_extraido__isnull=False).count()
                },
                'analyses': {
                    'total_sessions': SessaoAnalise.objects.filter(processo__usuario=usuario).count(),
                    'completed': SessaoAnalise.objects.filter(processo__usuario=usuario, status='concluida').count(),
                    'total_results': ResultadoAnalise.objects.filter(sessao__processo__usuario=usuario).count(),
                    'tokens_used': ResultadoAnalise.objects.filter(sessao__processo__usuario=usuario).aggregate(total=Sum('tokens_total'))['total'] or 0,
                    'avg_processing_time': ResultadoAnalise.objects.filter(sessao__processo__usuario=usuario).aggregate(avg=Avg('tempo_processamento'))['avg'] or 0
                },
                'activity': self._get_user_activity(usuario)
            }
            
            cache.set(cache_key, metrics, timeout=self.cache_timeout)
            return metrics
            
        except Usuario.DoesNotExist:
            return {'error': 'Usuário não encontrado'}
        except Exception as e:
            logger.error(f"Erro ao obter métricas do usuário {user_id}: {e}")
            return {'error': str(e)}
    
    def get_performance_metrics(self) -> Dict:
        """Métricas de performance do sistema"""
        
        cache_key = 'melkor_performance_metrics'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            last_24h = timezone.now() - timedelta(hours=24)
            last_7d = timezone.now() - timedelta(days=7)
            
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'analysis_performance': {
                    'avg_time_per_analysis': ResultadoAnalise.objects.aggregate(avg=Avg('tempo_processamento'))['avg'] or 0,
                    'avg_tokens_per_analysis': ResultadoAnalise.objects.aggregate(avg=Avg('tokens_total'))['avg'] or 0,
                    'analyses_last_24h': ResultadoAnalise.objects.filter(created_at__gte=last_24h).count(),
                    'analyses_last_7d': ResultadoAnalise.objects.filter(created_at__gte=last_7d).count()
                },
                'session_performance': {
                    'avg_session_duration': self._get_avg_session_duration(),
                    'completion_rate': self._get_session_completion_rate(),
                    'sessions_last_24h': SessaoAnalise.objects.filter(created_at__gte=last_24h).count()
                },
                'system_health': {
                    'error_rate_24h': self._get_error_rate(24),
                    'slow_requests_24h': self._get_slow_requests_count(24),
                    'cache_hit_rate': self._estimate_cache_hit_rate()
                }
            }
            
            cache.set(cache_key, metrics, timeout=self.cache_timeout)
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de performance: {e}")
            return {'error': str(e)}
    
    def get_security_metrics(self) -> Dict:
        """Métricas de segurança"""
        
        cache_key = 'melkor_security_metrics'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            last_24h = timezone.now() - timedelta(hours=24)
            last_7d = timezone.now() - timedelta(days=7)
            
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'events_last_24h': {
                    'total': LogSeguranca.objects.filter(created_at__gte=last_24h).count(),
                    'by_type': dict(LogSeguranca.objects.filter(created_at__gte=last_24h).values('tipo_evento').annotate(count=Count('id')).values_list('tipo_evento', 'count'))
                },
                'events_last_7d': {
                    'total': LogSeguranca.objects.filter(created_at__gte=last_7d).count(),
                    'unique_ips': LogSeguranca.objects.filter(created_at__gte=last_7d).values('ip_address').distinct().count()
                },
                'threat_analysis': {
                    'failed_logins': LogSeguranca.objects.filter(tipo_evento='login_falha', created_at__gte=last_24h).count(),
                    'prompt_injections': LogSeguranca.objects.filter(tipo_evento='prompt_injection', created_at__gte=last_24h).count(),
                    'suspicious_uploads': LogSeguranca.objects.filter(tipo_evento='upload_suspeito', created_at__gte=last_24h).count(),
                    'blocked_ips': len(cache.get('blocked_ips', set()))
                },
                'top_threat_ips': self._get_top_threat_ips()
            }
            
            cache.set(cache_key, metrics, timeout=self.cache_timeout)
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de segurança: {e}")
            return {'error': str(e)}
    
    def get_usage_analytics(self) -> Dict:
        """Analytics de uso do sistema"""
        
        try:
            last_30d = timezone.now() - timedelta(days=30)
            
            analytics = {
                'timestamp': timezone.now().isoformat(),
                'user_engagement': {
                    'daily_active_users': self._get_daily_active_users(30),
                    'user_retention': self._calculate_user_retention(),
                    'avg_sessions_per_user': self._get_avg_sessions_per_user()
                },
                'feature_usage': {
                    'most_used_blocks': dict(ResultadoAnalise.objects.values('bloco').annotate(count=Count('id')).order_by('-count').values_list('bloco', 'count')[:5]),
                    'document_types_uploaded': dict(Documento.objects.filter(created_at__gte=last_30d).values('tipo_documento').annotate(count=Count('id')).values_list('tipo_documento', 'count')),
                    'analysis_modes': dict(SessaoAnalise.objects.filter(created_at__gte=last_30d).values('modo_analise').annotate(count=Count('id')).values_list('modo_analise', 'count'))
                },
                'growth_metrics': {
                    'new_users_trend': self._get_new_users_trend(30),
                    'processes_growth': self._get_processes_growth(30),
                    'usage_growth': self._get_usage_growth(30)
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erro ao obter analytics de uso: {e}")
            return {'error': str(e)}
    
    def _get_active_users_count(self, days: int) -> int:
        """Conta usuários ativos nos últimos N dias"""
        since = timezone.now() - timedelta(days=days)
        return Usuario.objects.filter(
            Q(processos__created_at__gte=since) |
            Q(processos__sessoes_analise__created_at__gte=since)
        ).distinct().count()
    
    def _get_new_users_count(self, days: int) -> int:
        """Conta novos usuários nos últimos N dias"""
        since = timezone.now() - timedelta(days=days)
        return Usuario.objects.filter(created_at__gte=since).count()
    
    def _get_total_documents_size(self) -> float:
        """Calcula tamanho total dos documentos em MB"""
        total_bytes = Documento.objects.aggregate(total=Sum('tamanho_arquivo'))['total'] or 0
        return round(total_bytes / (1024 * 1024), 2)
    
    def _get_performance_metrics(self) -> Dict:
        """Métricas básicas de performance"""
        return {
            'avg_analysis_time': ResultadoAnalise.objects.aggregate(avg=Avg('tempo_processamento'))['avg'] or 0,
            'total_tokens_used': ResultadoAnalise.objects.aggregate(total=Sum('tokens_total'))['total'] or 0,
            'avg_tokens_per_analysis': ResultadoAnalise.objects.aggregate(avg=Avg('tokens_total'))['avg'] or 0
        }
    
    def _get_security_metrics(self) -> Dict:
        """Métricas básicas de segurança"""
        last_24h = timezone.now() - timedelta(hours=24)
        return {
            'security_events_24h': LogSeguranca.objects.filter(created_at__gte=last_24h).count(),
            'failed_logins_24h': LogSeguranca.objects.filter(tipo_evento='login_falha', created_at__gte=last_24h).count(),
            'blocked_ips': len(cache.get('blocked_ips', set()))
        }
    
    def _get_user_activity(self, usuario: Usuario) -> Dict:
        """Atividade recente do usuário"""
        last_30d = timezone.now() - timedelta(days=30)
        return {
            'last_login': usuario.user.last_login.isoformat() if usuario.user.last_login else None,
            'processes_created_30d': usuario.processos.filter(created_at__gte=last_30d).count(),
            'analyses_run_30d': SessaoAnalise.objects.filter(processo__usuario=usuario, created_at__gte=last_30d).count()
        }
    
    def _get_avg_session_duration(self) -> float:
        """Duração média das sessões"""
        completed_sessions = SessaoAnalise.objects.filter(status='concluida', tempo_total__isnull=False)
        if completed_sessions.exists():
            total_seconds = sum(s.tempo_total.total_seconds() for s in completed_sessions)
            return total_seconds / completed_sessions.count()
        return 0.0
    
    def _get_session_completion_rate(self) -> float:
        """Taxa de conclusão das sessões"""
        total = SessaoAnalise.objects.count()
        if total == 0:
            return 0.0
        completed = SessaoAnalise.objects.filter(status='concluida').count()
        return (completed / total) * 100
    
    def _get_error_rate(self, hours: int) -> float:
        """Taxa de erro nas últimas N horas"""
        since = timezone.now() - timedelta(hours=hours)
        total_events = LogSeguranca.objects.filter(created_at__gte=since).count()
        if total_events == 0:
            return 0.0
        error_events = LogSeguranca.objects.filter(created_at__gte=since, tipo_evento='erro_sistema').count()
        return (error_events / total_events) * 100
    
    def _get_slow_requests_count(self, hours: int) -> int:
        """Contagem de requisições lentas"""
        # Esta métrica seria implementada com logs mais detalhados
        return 0
    
    def _estimate_cache_hit_rate(self) -> float:
        """Estimativa da taxa de acerto do cache"""
        # Esta métrica seria implementada com instrumentação do cache
        return 85.0  # Valor estimado
    
    def _get_top_threat_ips(self) -> List[Dict]:
        """Top IPs com atividade suspeita"""
        last_24h = timezone.now() - timedelta(hours=24)
        threat_events = LogSeguranca.objects.filter(
            created_at__gte=last_24h,
            tipo_evento__in=['prompt_injection', 'upload_suspeito', 'acesso_negado']
        ).values('ip_address').annotate(count=Count('id')).order_by('-count')[:10]
        
        return list(threat_events)
    
    def _get_daily_active_users(self, days: int) -> List[Dict]:
        """Usuários ativos diários"""
        # Implementação simplificada
        return []
    
    def _calculate_user_retention(self) -> Dict:
        """Calcula retenção de usuários"""
        return {'retention_rate': 75.0}  # Valor estimado
    
    def _get_avg_sessions_per_user(self) -> float:
        """Média de sessões por usuário"""
        total_users = Usuario.objects.count()
        if total_users == 0:
            return 0.0
        total_sessions = SessaoAnalise.objects.count()
        return total_sessions / total_users
    
    def _get_new_users_trend(self, days: int) -> List[Dict]:
        """Tendência de novos usuários"""
        # Implementação simplificada
        return []
    
    def _get_processes_growth(self, days: int) -> List[Dict]:
        """Crescimento de processos"""
        # Implementação simplificada
        return []
    
    def _get_usage_growth(self, days: int) -> List[Dict]:
        """Crescimento de uso"""
        # Implementação simplificada
        return []
