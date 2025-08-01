"""
Views/APIs do Melkor 3.0
Sistema de análise jurídica especializado em Tribunal do Júri
"""

import logging
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from ai_engine.processor import MelkorProcessor, SecurityError, OpenAIError
from ai_engine.security import SecurityValidator
from ai_engine.document_processor import DocumentProcessor
from .models import Usuario, Processo, Documento, SessaoAnalise, ResultadoAnalise
from .serializers import (
    UsuarioSerializer, ProcessoSerializer, DocumentoSerializer,
    DocumentoUploadSerializer, SessaoAnaliseSerializer, ResultadoAnaliseSerializer,
    IniciarAnaliseSerializer, MenuInterativoSerializer, EstatisticasSerializer
)

logger = logging.getLogger('melkor')


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para usuários"""
    
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Usuario.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Retorna perfil do usuário logado"""
        try:
            usuario = Usuario.objects.get(user=request.user)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Perfil não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ProcessoViewSet(viewsets.ModelViewSet):
    """ViewSet para processos"""
    
    serializer_class = ProcessoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        usuario = Usuario.objects.get(user=self.request.user)
        return Processo.objects.filter(usuario=usuario)
    
    def perform_create(self, serializer):
        usuario = Usuario.objects.get(user=self.request.user)
        serializer.save(usuario=usuario)
    
    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        """Lista documentos do processo"""
        processo = self.get_object()
        documentos = processo.documentos.all()
        serializer = DocumentoSerializer(documentos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analises(self, request, pk=None):
        """Lista análises do processo"""
        processo = self.get_object()
        sessoes = processo.sessoes_analise.all().order_by('-created_at')
        serializer = SessaoAnaliseSerializer(sessoes, many=True)
        return Response(serializer.data)


class DocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para documentos"""
    
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        usuario = Usuario.objects.get(user=self.request.user)
        return Documento.objects.filter(processo__usuario=usuario)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentoUploadSerializer
        return DocumentoSerializer
    
    def create(self, request, *args, **kwargs):
        """Upload de documento com processamento"""
        
        security = SecurityValidator()
        
        # Validar rate limit
        if not security.check_rate_limit(str(request.user.id), 'upload'):
            return Response(
                {'error': 'Limite de uploads excedido. Tente novamente em 1 hora.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Validar arquivo
        arquivo = request.FILES.get('arquivo_original')
        if arquivo:
            validation = security.validate_file_upload(arquivo)
            if not validation['valid']:
                return Response(
                    {'error': validation['errors']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Criar documento
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            documento = serializer.save()
            
            # Processar documento em background
            try:
                processor = DocumentProcessor()
                texto_extraido = processor.extract_text_from_pdf(documento.arquivo_original.path)
                
                documento.texto_extraido = texto_extraido
                documento.tamanho_arquivo = documento.arquivo_original.size
                documento.save()
                
                logger.info(f"Documento processado: {documento.nome_arquivo}")
                
            except Exception as e:
                logger.error(f"Erro ao processar documento: {e}")
                # Documento é salvo mesmo com erro no processamento
            
            # Retornar com serializer de leitura
            response_serializer = DocumentoSerializer(documento)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnaliseViewSet(viewsets.ModelViewSet):
    """ViewSet para análises"""
    
    serializer_class = SessaoAnaliseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        usuario = Usuario.objects.get(user=self.request.user)
        return SessaoAnalise.objects.filter(processo__usuario=usuario)
    
    @action(detail=False, methods=['post'])
    def iniciar(self, request):
        """Inicia nova análise"""
        
        serializer = IniciarAnaliseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Validar rate limit
            security = SecurityValidator()
            if not security.check_rate_limit(str(request.user.id), 'analysis'):
                return Response(
                    {'error': 'Limite de análises excedido. Tente novamente em 1 hora.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Buscar processo
            usuario = Usuario.objects.get(user=request.user)
            processo = Processo.objects.get(
                id=data['processo_id'],
                usuario=usuario
            )
            
            # Verificar se há documentos
            documentos = processo.documentos.filter(texto_extraido__isnull=False)
            if not documentos.exists():
                return Response(
                    {'error': 'Processo não possui documentos processados'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Criar sessão
            sessao = SessaoAnalise.objects.create(
                processo=processo,
                modo_analise=data['modo_analise'],
                blocos_selecionados=data.get('blocos_selecionados', []),
                configuracoes={}
            )
            
            # Iniciar processamento
            processor = MelkorProcessor()
            
            if data['modo_analise'] == 'individual':
                # Análise individual
                documento = documentos.first()
                resultado = processor.analyze_document(
                    documento, 
                    data['bloco'], 
                    data['subetapa'], 
                    sessao
                )
                
                response_data = {
                    'sessao_id': str(sessao.id),
                    'tipo': 'individual',
                    'resultado': resultado
                }
                
            else:
                # Análise completa ou personalizada
                blocos = data.get('blocos_selecionados', [1, 2, 3, 4])
                resultado = processor.analyze_complete_process(
                    list(documentos), 
                    sessao, 
                    blocos
                )
                
                response_data = {
                    'sessao_id': str(sessao.id),
                    'tipo': data['modo_analise'],
                    'resultado': resultado
                }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Processo.DoesNotExist:
            return Response(
                {'error': 'Processo não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except SecurityError as e:
            return Response(
                {'error': f'Erro de segurança: {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except OpenAIError as e:
            return Response(
                {'error': f'Erro na análise: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        """Lista resultados de uma análise"""
        sessao = self.get_object()
        resultados = sessao.resultados.all().order_by('bloco', 'subetapa')
        serializer = ResultadoAnaliseSerializer(resultados, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resumo(self, request, pk=None):
        """Resumo de uma análise"""
        sessao = self.get_object()
        processor = MelkorProcessor()
        resumo = processor.get_analysis_summary(sessao)
        return Response(resumo)


class MenuViewSet(viewsets.ViewSet):
    """ViewSet para menu interativo"""

    permission_classes = []  # Menu público
    
    @action(detail=False, methods=['get'])
    def opcoes(self, request):
        """Retorna opções do menu"""
        
        opcoes = {
            1: {
                'titulo': 'Bloco 1 - Fase de Inquérito',
                'descricao': 'Análise da fase investigativa e construção da defesa inicial',
                'subetapas': 6
            },
            2: {
                'titulo': 'Bloco 2 - Primeira Fase do Procedimento',
                'descricao': 'Da denúncia até a pronúncia',
                'subetapas': 5
            },
            3: {
                'titulo': 'Bloco 3 - Segunda Fase do Procedimento',
                'descricao': 'Preparação para o Tribunal do Júri',
                'subetapas': 5
            },
            4: {
                'titulo': 'Bloco 4 - Debates no Júri',
                'descricao': 'Estratégias para o plenário do júri',
                'subetapas': 5
            },
            5: {
                'titulo': 'Análise Completa',
                'descricao': 'Executa todos os blocos sequencialmente',
                'subetapas': 21
            }
        }
        
        return Response(opcoes)
    
    @action(detail=False, methods=['post'])
    def processar(self, request):
        """Processa opção do menu"""
        
        serializer = MenuInterativoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        opcao = data['opcao']
        
        if opcao in [1, 2, 3, 4]:
            # Bloco individual
            return Response({
                'tipo': 'bloco_individual',
                'bloco': opcao,
                'mensagem': f'Bloco {opcao} selecionado. Escolha o processo para análise.',
                'proxima_acao': 'selecionar_processo'
            })
        
        elif opcao == 5:
            # Análise completa
            return Response({
                'tipo': 'analise_completa',
                'mensagem': 'Análise completa selecionada. Escolha o processo.',
                'proxima_acao': 'selecionar_processo'
            })
        
        return Response(
            {'error': 'Opção inválida'},
            status=status.HTTP_400_BAD_REQUEST
        )


class EstatisticasViewSet(viewsets.ViewSet):
    """ViewSet para estatísticas"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Estatísticas do dashboard"""
        
        usuario = Usuario.objects.get(user=request.user)
        
        # Contadores básicos
        total_processos = Processo.objects.filter(usuario=usuario).count()
        total_documentos = Documento.objects.filter(processo__usuario=usuario).count()
        total_analises = SessaoAnalise.objects.filter(processo__usuario=usuario).count()
        
        # Tokens utilizados
        tokens_utilizados = ResultadoAnalise.objects.filter(
            sessao__processo__usuario=usuario
        ).aggregate(total=Sum('tokens_total'))['total'] or 0
        
        # Tempo total de análises
        tempo_total = SessaoAnalise.objects.filter(
            processo__usuario=usuario,
            tempo_total__isnull=False
        ).aggregate(total=Sum('tempo_total'))['total']
        
        tempo_total_str = str(tempo_total) if tempo_total else "0:00:00"
        
        # Distribuições
        processos_por_status = dict(
            Processo.objects.filter(usuario=usuario)
            .values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        analises_por_bloco = dict(
            ResultadoAnalise.objects.filter(sessao__processo__usuario=usuario)
            .values('bloco')
            .annotate(count=Count('id'))
            .values_list('bloco', 'count')
        )
        
        documentos_por_tipo = dict(
            Documento.objects.filter(processo__usuario=usuario)
            .values('tipo_documento')
            .annotate(count=Count('id'))
            .values_list('tipo_documento', 'count')
        )
        
        # Última atividade
        ultima_atividade = SessaoAnalise.objects.filter(
            processo__usuario=usuario
        ).order_by('-created_at').first()
        
        ultima_atividade_data = ultima_atividade.created_at if ultima_atividade else None
        
        # Média de tempo
        media_tempo = ResultadoAnalise.objects.filter(
            sessao__processo__usuario=usuario
        ).aggregate(media=Avg('tempo_processamento'))['media'] or 0
        
        estatisticas = {
            'total_processos': total_processos,
            'total_documentos': total_documentos,
            'total_analises': total_analises,
            'tokens_utilizados': tokens_utilizados,
            'tempo_total_analises': tempo_total_str,
            'processos_por_status': processos_por_status,
            'analises_por_bloco': analises_por_bloco,
            'documentos_por_tipo': documentos_por_tipo,
            'ultima_atividade': ultima_atividade_data,
            'media_tempo_analise': round(media_tempo, 2)
        }
        
        serializer = EstatisticasSerializer(estatisticas)
        return Response(serializer.data)
