from django.core.management.base import BaseCommand
from django.conf import settings
from ai_engine.processor import OpenAI
from juris.models import Jurisprudencia, JurisEmbedding


def embed_texts(client: OpenAI, texts: list[str]) -> list[list[float]]:
    # Usa API de embeddings padrão text-embedding-3-small (ou config via env depois)
    model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


class Command(BaseCommand):
    help = 'Indexa embeddings para Jurisprudencia (título+ementa+fundamentação).'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, default=50)
        parser.add_argument('--reindex', action='store_true')

    def handle(self, *args, **options):
        batch_size = options['batch']
        reindex = options['reindex']

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        qs = Jurisprudencia.objects.all()
        count = qs.count()
        self.stdout.write(self.style.NOTICE(f"Indexando {count} registros (batch={batch_size})"))

        done = 0
        for offset in range(0, count, batch_size):
            chunk = list(qs[offset:offset+batch_size])
            texts = []
            for j in chunk:
                if (not reindex) and hasattr(j, 'embedding'):
                    continue
                text = (j.titulo or '') + "\n" + (j.ementa or '') + "\n" + (j.fundamentacao or '')
                texts.append(text[:8000])  # segurança no tamanho
            if not texts:
                continue
            embs = embed_texts(client, texts)
            idx = 0
            for j in chunk:
                if (not reindex) and hasattr(j, 'embedding'):
                    continue
                vec = embs[idx]
                idx += 1
                JurisEmbedding.objects.update_or_create(
                    jurisprudencia=j, defaults={'embedding': vec, 'dim': len(vec)}
                )
                done += 1
        self.stdout.write(self.style.SUCCESS(f"Embeddings indexados/atualizados: {done}"))

