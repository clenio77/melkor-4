"""
Views do AI Engine - Kermartin 3.0
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .processor import KermartinProcessor
from .security import SecurityValidator
from django.conf import settings
import time
from .document_processor import DocumentProcessor
from .retrieval import get_service, make_response, GraphRAGRetrieval

logger = logging.getLogger('ai_engine')


class ProcessarDocumentoView(APIView):
    """View para processar documentos"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Processa documento PDF"""

        documento_id = request.data.get('documento_id')
        if not documento_id:
            return Response(
                {'error': 'documento_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from core.models import Documento, Usuario

            usuario = Usuario.objects.get(user=request.user)
            documento = Documento.objects.get(
                id=documento_id,
                processo__usuario=usuario
            )

            processor = DocumentProcessor()

            # Extrair texto
            texto = processor.extract_text_from_pdf(documento.arquivo_original.path)

            # Analisar estrutura
            estrutura = processor.analyze_document_structure(texto)

            # Extrair informações-chave
            info_chave = processor.extract_key_information(texto)

            # Salvar texto extraído
            documento.texto_extraido = texto
            documento.save()

            return Response({
                'success': True,
                'documento_id': str(documento.id),
                'texto_extraido': len(texto) > 0,
                'caracteres': len(texto),
                'estrutura': estrutura,
                'informacoes_chave': info_chave
            })

        except Exception as e:
            logger.error(f"Erro ao processar documento: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseIndividualView(APIView):
    """View para análise individual"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Executa análise individual"""

        data = request.data
        required_fields = ['documento_id', 'bloco', 'subetapa']

        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} é obrigatório'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            from core.models import Documento, Usuario, SessaoAnalise

            usuario = Usuario.objects.get(user=request.user)
            documento = Documento.objects.get(
                id=data['documento_id'],
                processo__usuario=usuario
            )

            # Criar sessão temporária
            sessao = SessaoAnalise.objects.create(
                processo=documento.processo,
                modo_analise='individual'
            )

            # Executar análise
            processor = KermartinProcessor()
            resultado = processor.analyze_document(
                documento,
                int(data['bloco']),
                int(data['subetapa']),
                sessao
            )

            return Response({
                'success': True,
                'resultado': resultado
            })

        except Exception as e:
            logger.error(f"Erro na análise individual: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseCompletaView(APIView):
    """View para análise completa"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Executa análise completa"""

        processo_id = request.data.get('processo_id')
        blocos = request.data.get('blocos', [1, 2, 3, 4])

        if not processo_id:
            return Response(
                {'error': 'processo_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from core.models import Processo, Usuario, SessaoAnalise

            usuario = Usuario.objects.get(user=request.user)
            processo = Processo.objects.get(
                id=processo_id,
                usuario=usuario
            )

            documentos = processo.documentos.filter(texto_extraido__isnull=False)
            if not documentos.exists():
                return Response(
                    {'error': 'Processo não possui documentos processados'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Criar sessão
            sessao = SessaoAnalise.objects.create(
                processo=processo,
                modo_analise='completa',
                blocos_selecionados=blocos
            )

            # Executar análise
            processor = KermartinProcessor()
            resultado = processor.analyze_complete_process(
                list(documentos),
                sessao,
                blocos
            )

            return Response({
                'success': True,
                'resultado': resultado
            })

        except Exception as e:
            logger.error(f"Erro na análise completa: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StatusSegurancaView(APIView):
    """View para status de segurança"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna status de segurança"""

        try:
            security = SecurityValidator()
            summary = security.get_security_summary()

            return Response({
                'success': True,
                'seguranca': summary
            })

        except Exception as e:
            logger.error(f"Erro ao obter status de segurança: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JurisprudenciaSearchView(APIView):
    """Search jurisprudence via provider (simple/graph/hybrid)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider = request.query_params.get('provider')
            q = request.query_params.get('q')
            filters = {
                'tema': request.query_params.get('tema'),
                'fase': request.query_params.get('fase'),
                'bloco': request.query_params.get('bloco'),
                'tribunal': request.query_params.get('tribunal'),
                'vinculante': request.query_params.get('vinculante') or request.query_params.get('vinculancia'),
                'dispositivo': request.query_params.get('dispositivo'),
                'tese': request.query_params.get('tese'),
            }
            topk = int(request.query_params.get('topk', 8))

            service = get_service(provider)
            t0 = time.time()
            items = service.search(q, filters, topk=topk)
            latency_ms = int((time.time() - t0) * 1000)
            # provider efetivo (em hybrid podemos ter fallback)
            provider_default = provider or getattr(settings, 'JURIS_RETRIEVAL_PROVIDER', 'simple')
            provider_effective = getattr(service, 'last_used', None) or provider_default
            resp = make_response(items, provider_default)
            resp.update({
                'provider_effective': provider_effective,
                'count': len(items),
                'latency_ms': latency_ms,
                'filters': filters,
            })
            return Response(resp)
        except Exception as e:
            logger.error(f"Erro na busca de jurisprudência: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JurisprudenciaSugestoesView(APIView):
    """Suggestions by fase/bloco/tema with provider toggle."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider = request.query_params.get('provider')
            filters = {
                'tema': request.query_params.get('tema'),
                'fase': request.query_params.get('fase'),
                'bloco': request.query_params.get('bloco'),
                'tribunal': request.query_params.get('tribunal'),
                'vinculante': request.query_params.get('vinculante') or request.query_params.get('vinculancia'),
                'dispositivo': request.query_params.get('dispositivo'),
                'tese': request.query_params.get('tese'),
            }
            topk = int(request.query_params.get('topk', 8))

            service = get_service(provider)
            t0 = time.time()
            items = service.sugestoes(filters, topk=topk)
            latency_ms = int((time.time() - t0) * 1000)
            provider_default = provider or getattr(settings, 'JURIS_RETRIEVAL_PROVIDER', 'simple')
            provider_effective = getattr(service, 'last_used', None) or provider_default
            resp = make_response(items, provider_default)
            resp.update({
                'provider_effective': provider_effective,
                'count': len(items),
                'latency_ms': latency_ms,
                'filters': filters,
            })
            return Response(resp)
        except Exception as e:
            logger.error(f"Erro nas sugestões de jurisprudência: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JurisprudenciaHealthView(APIView):
    """Health check para GraphRAG/OpenAI/toggles."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            graph_enabled = getattr(settings, 'JURIS_GRAPH_ENABLED', False)
            graph_ok = None
            if graph_enabled:
                try:
                    g = GraphRAGRetrieval()
                    rows = g._run("RETURN 1 as ok", {})
                    graph_ok = isinstance(rows, list)
                except Exception:
                    graph_ok = False

            openai_key = bool(getattr(settings, 'OPENAI_API_KEY', ''))
            embedding_model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
            provider_default = getattr(settings, 'JURIS_RETRIEVAL_PROVIDER', 'simple')

            return Response({
                'graph': {
                    'enabled': graph_enabled,
                    'ok': graph_ok,
                },
                'openai': {
                    'configured': openai_key,
                    'embedding_model': embedding_model,
                },
                'retrieval_provider_default': provider_default,
            })
        except Exception as e:
            logger.error(f"Erro no health de jurisprudência: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class InfraHealthView(APIView):
    """Health check para Redis e DB."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db import connection
        import redis
        import os
        status_db = False
        status_redis = None
        err_db = None
        err_redis = None
        # DB check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                status_db = True
        except Exception as e:
            err_db = str(e)
        # Redis check
        redis_url = getattr(settings, 'REDIS_URL', os.getenv('REDIS_URL'))
        if redis_url:
            try:
                r = redis.Redis.from_url(redis_url)
                pong = r.ping()
                status_redis = bool(pong)
            except Exception as e:
                status_redis = False
                err_redis = str(e)
        return Response({
            'db': {'ok': status_db, 'error': err_db},
            'redis': {'ok': status_redis, 'error': err_redis},
        })

