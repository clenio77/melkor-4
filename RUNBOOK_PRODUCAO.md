# Runbook de Produção – Kermartin 3.0 (Backend + Frontend + GraphRAG)

## 1. Variáveis de Ambiente (.env)

Recomendado copiar do .env.example e ajustar:

- Básico
  - DEBUG=false
  - SECRET_KEY=<valor forte>
  - ALLOWED_HOSTS=seu.dominio.com,api.seu.dominio.com
- OpenAI
  - OPENAI_API_KEY=<sua chave>
  - OPENAI_MODEL=gpt-4o-mini
  - OPENAI_EMBEDDING_MODEL=text-embedding-3-small
- Redis
  - REDIS_URL=redis://localhost:6379/0
- GraphRAG
  - JURIS_GRAPH_ENABLED=false (ou true se usar Neo4j)
  - JURIS_RETRIEVAL_PROVIDER=simple | graph | hybrid
  - JURIS_GRAPH_URL=bolt://host:7687
  - JURIS_GRAPH_USER=neo4j
  - JURIS_GRAPH_PASSWORD=<senha>
  - JURIS_GRAPH_TIMEOUT_MS=2000
  - JURIS_RAG_TOPK=8
- CORS
  - CORS_ALLOWED_ORIGINS=https://seu-front.com

## 2. Preparação do Backend (Django)

1) Migrar banco
- python3 kermartin_backend/manage.py migrate --noinput

2) Coletar estáticos
- python3 kermartin_backend/manage.py collectstatic --noinput

3) Checagem de segurança
- python3 kermartin_backend/manage.py check --deploy

4) Executar
- gunicorn kermartin_project.wsgi:application \
  --chdir kermartin_backend --bind 0.0.0.0:8000 --workers 3

## 3. Preparação do Frontend (Next.js)

1) Instalar deps e build
- cd product/frontend
- npm ci
- npm run build
- npm run start (ou servir via Node/PM2/NGINX)

## 4. Ingestão da Base de Jurisprudência

1) Import CSV
- POST /api/jurisprudencias/import (multipart, campo file)
- Colunas: titulo,tribunal,data_julgamento,ementa,fundamentacao,pontos_estrategicos,teses_defensivas,tema,link,vinculante,dispositivos_citados,fase,bloco

2) Indexação de embeddings (opcional para busca semântica)
- python3 kermartin_backend/manage.py index_juris_embeddings --batch 50

## 5. GraphRAG (opcional – Neo4j)

1) Exportar grafo para CSV
- python3 kermartin_backend/manage.py export_juris_graph_csv

2) Importar no Neo4j Desktop/Browser
- Importar nodes (juris_nodes.csv) e rels (juris_rels.csv)
- Criar índices (exemplo):
  - CREATE INDEX IF NOT EXISTS FOR (j:Juris) ON (j.id);
  - CREATE INDEX IF NOT EXISTS FOR (t:Tema) ON (t.id);

3) Ativar no .env
- JURIS_GRAPH_ENABLED=true
- JURIS_RETRIEVAL_PROVIDER=hybrid (recomendado) ou graph

## 6. Rollback rápido (toggle)

1) .env
- JURIS_GRAPH_ENABLED=false
- JURIS_RETRIEVAL_PROVIDER=simple

2) Reiniciar backend

3) Smoke test
- GET /api/ai/jurisprudencia/sugestoes?tema=cadeia

## 7. Observabilidade mínima

- As respostas incluem: provider_used, provider_effective, count, latency_ms, trace_id
- Logfiles: kermartin_backend/logs/kermartin.log

## 8. Segurança

- DEBUG=false, SECRET_KEY forte, HTTPS com proxy
- Em produção (DEBUG=false) o settings aplica Whitenoise, SSL redirect, HSTS, cookies secure

## 9. Smoke Tests (manuais)

- GET /api/ai/jurisprudencia/sugestoes?tema=cadeia&vinculante=true
- GET /api/ai/jurisprudencia/search?q=nulidade&tribunal=STJ
- UI: /jurisprudencia com filtros e provider selector
- Caso use Neo4j: provider=graph|hybrid nas consultas

