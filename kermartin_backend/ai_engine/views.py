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
from .document_processor import DocumentProcessor

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
