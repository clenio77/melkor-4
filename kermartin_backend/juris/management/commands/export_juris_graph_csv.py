from django.core.management.base import BaseCommand
from juris.models import Jurisprudencia
import csv

class Command(BaseCommand):
    help = 'Exporta CSVs para import no Neo4j (nós e arestas).'

    def add_arguments(self, parser):
        parser.add_argument('--nodes', default='juris_nodes.csv')
        parser.add_argument('--rels', default='juris_rels.csv')

    def handle(self, *args, **options):
        nodes_path = options['nodes']
        rels_path = options['rels']

        # Coletar valores distintos
        temas: dict[str, str] = {}
        dispositivos: dict[str, str] = {}
        fases: dict[str, str] = {}
        blocos: dict[int, str] = {}
        teses: dict[str, str] = {}

        for j in Jurisprudencia.objects.all():
            # Tema
            if j.tema:
                temas.setdefault(j.tema, f"TEMA_{len(temas)+1}")
            # Dispositivos
            if j.dispositivos_citados:
                for d in j.dispositivos_citados:
                    if isinstance(d, str) and d.strip():
                        dispositivos.setdefault(d.strip(), f"DISP_{len(dispositivos)+1}")
            # Fase
            if j.fase:
                fases.setdefault(j.fase, f"FASE_{len(fases)+1}")
            # Bloco
            if j.bloco is not None:
                blocos.setdefault(int(j.bloco), f"BLOCO_{len(blocos)+1}")
            # Teses (split por ';')
            if j.teses_defensivas:
                for t in [s.strip() for s in j.teses_defensivas.split(';') if s.strip()]:
                    teses.setdefault(t, f"TESE_{len(teses)+1}")

        # Escrever nós
        with open(nodes_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['id:ID', 'label:LABEL', 'titulo', 'tribunal', 'data', 'tema', 'link', 'vinculante:boolean', 'fase', 'bloco:int'])
            # Nós Juris
            for j in Jurisprudencia.objects.all():
                data = j.data_julgamento.isoformat() if j.data_julgamento else ''
                w.writerow([f"J_{j.id}", 'Juris', j.titulo, j.tribunal or '', data, j.tema or '', j.link or '', bool(j.vinculante), j.fase or '', j.bloco or ''])
            # Nós Tema
            for tema, tema_id in temas.items():
                w.writerow([tema_id, 'Tema', tema, '', '', tema, '', '', '', ''])
            # Nós Dispositivo
            for nome, disp_id in dispositivos.items():
                w.writerow([disp_id, 'Dispositivo', nome, '', '', '', '', '', '', ''])
            # Nós Fase
            for nome, fase_id in fases.items():
                w.writerow([fase_id, 'Fase', nome, '', '', '', '', '', '', ''])
            # Nós Bloco
            for numero, bloco_id in blocos.items():
                w.writerow([bloco_id, 'Bloco', f'Bloco {numero}', '', '', '', '', '', '', numero])
            # Nós Tese
            for nome, tese_id in teses.items():
                w.writerow([tese_id, 'Tese', nome, '', '', '', '', '', '', ''])

        # Escrever arestas
        with open(rels_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow([':START_ID', ':END_ID', ':TYPE'])
            for j in Jurisprudencia.objects.all():
                jid = f"J_{j.id}"
                # HAS_TEMA
                if j.tema:
                    w.writerow([jid, temas[j.tema], 'HAS_TEMA'])
                # CITES
                if j.dispositivos_citados:
                    for d in j.dispositivos_citados:
                        if isinstance(d, str) and d.strip():
                            w.writerow([jid, dispositivos[d.strip()], 'CITES'])
                # APPLIES_TO -> Fase
                if j.fase:
                    w.writerow([jid, fases[j.fase], 'APPLIES_TO'])
                # APPLIES_TO -> Bloco
                if j.bloco is not None:
                    w.writerow([jid, blocos[int(j.bloco)], 'APPLIES_TO'])
                # SUPPORTS -> Tese
                if j.teses_defensivas:
                    for t in [s.strip() for s in j.teses_defensivas.split(';') if s.strip()]:
                        w.writerow([jid, teses[t], 'SUPPORTS'])

        self.stdout.write(self.style.SUCCESS(f"Export concluído: nodes={nodes_path}, rels={rels_path}"))

