from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
import csv
from io import TextIOWrapper
from datetime import datetime
from .models import Jurisprudencia
from .serializers import JurisprudenciaSerializer


class JurisprudenciaViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = JurisprudenciaSerializer

    def get_queryset(self):
        qs = Jurisprudencia.objects.all()
        tema = self.request.query_params.get('tema')
        tribunal = self.request.query_params.get('tribunal')
        if tema:
            qs = qs.filter(tema__icontains=tema)
        if tribunal:
            qs = qs.filter(tribunal__icontains=tribunal)
        return qs

    @action(detail=False, methods=["post"], url_path="import")
    def import_csv(self, request):
        """Importa jurisprudência via CSV.
        Espera arquivo multipart com campo 'file'.
        Colunas esperadas: titulo,tribunal,data_julgamento,ementa,fundamentacao,pontos_estrategicos,teses_defensivas,tema,link,vinculante,dispositivos_citados,fase,bloco
        Datas no formato YYYY-MM-DD. Campo vinculante: true/false. dispositivos_citados: JSON ou lista separada por ponto e vírgula. bloco: número inteiro.
        """
        if 'file' not in request.FILES:
            return Response({'error': "Arquivo 'file' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        created, skipped, errors = 0, 0, []
        rows_preview = []

        try:
            with transaction.atomic():
                reader = csv.DictReader(TextIOWrapper(file.file, encoding='utf-8'))
                for idx, row in enumerate(reader, start=1):
                    try:
                        titulo = (row.get('titulo') or '').strip()
                        if not titulo:
                            skipped += 1
                            errors.append({'row': idx, 'error': 'titulo vazio'})
                            continue
                        tribunal = (row.get('tribunal') or '').strip() or None
                        tema = (row.get('tema') or '').strip() or None
                        link = (row.get('link') or '').strip() or None
                        ementa = row.get('ementa') or None
                        fundamentacao = row.get('fundamentacao') or None
                        pontos = row.get('pontos_estrategicos') or None
                        teses = row.get('teses_defensivas') or None
                        data_str = (row.get('data_julgamento') or '').strip()
                        data_julgamento = None
                        if data_str:
                            try:
                                data_julgamento = datetime.strptime(data_str, '%Y-%m-%d').date()
                            except ValueError:
                                # tenta formato brasileiro dd/mm/yyyy
                                try:
                                    data_julgamento = datetime.strptime(data_str, '%d/%m/%Y').date()
                                except ValueError:
                                    pass
                        vinc_str = (row.get('vinculante') or '').strip().lower()
                        vinculante = vinc_str in ['true', '1', 'yes', 'sim']
                        disp_raw = row.get('dispositivos_citados')
                        dispositivos_citados = None
                        if disp_raw:
                            try:
                                # tenta interpretar como JSON
                                import json
                                dispositivos_citados = json.loads(disp_raw)
                            except Exception:
                                # fallback: split por ';'
                                dispositivos_citados = [s.strip() for s in disp_raw.split(';') if s.strip()]

                        bloco_val = row.get('bloco')
                        try:
                            bloco_int = int(bloco_val) if bloco_val not in (None, '') else None
                        except Exception:
                            bloco_int = None
                        fase_val = (row.get('fase') or '').strip() or None

                        Jurisprudencia.objects.create(
                            titulo=titulo,
                            tribunal=tribunal,
                            data_julgamento=data_julgamento,
                            ementa=ementa,
                            fundamentacao=fundamentacao,
                            pontos_estrategicos=pontos,
                            teses_defensivas=teses,
                            tema=tema,
                            link=link,
                            vinculante=vinculante,
                            dispositivos_citados=dispositivos_citados,
                            fase=fase_val,
                            bloco=bloco_int,
                        )
                        created += 1
                        if len(rows_preview) < 5:
                            rows_preview.append({'row': idx, 'titulo': titulo, 'tribunal': tribunal})
                    except Exception as e:
                        errors.append({'row': idx, 'error': str(e)})
                        skipped += 1

            return Response({
                'success': True,
                'created': created,
                'skipped': skipped,
                'errors': errors,
                'preview': rows_preview,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

