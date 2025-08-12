# Kermartin 3.0 – Guia de Desenvolvimento

Este guia resume como preparar, desenvolver, testar e enviar mudanças no projeto.

## Requisitos
- Python 3.12+
- Node.js 20+
- pip, npm

## Setup rápido
```bash
# Instalar dependências backend + frontend
make setup

# (Opcional) Instalar hooks de qualidade
make pre-commit-install

# Variáveis locais (exemplo)
cp kermartin_backend/.env.example kermartin_backend/.env  # se existir
# ou crie um .env com: SECRET_KEY, DEBUG, OPENAI_API_KEY, REDIS_URL etc.
```

## Desenvolvimento
- Backend (Django):
  ```bash
  make dev-backend          # http://127.0.0.1:8000
  ```
- Frontend (Next.js):
  ```bash
  make dev-frontend         # http://127.0.0.1:3000
  ```

### Docker (opcional)
```bash
# subir stack completa (db, redis, backend, frontend)
docker compose up --build

# logs
docker compose logs -f backend
```

## Qualidade (lint/format)
```bash
make lint                   # flake8, black --check, isort --check-only, ESLint
make format                 # black + isort
```

## Testes
```bash
make test                   # pytest (backend)
```

## Build Frontend
```bash
make build-frontend
```

## CI/CD
- GitHub Actions roda automaticamente: lint + testes backend e lint + build frontend a cada push/PR.
- Arquivo: `.github/workflows/ci.yml`.

## BMAD (Automação de Dev)
- Arquivos e orquestrador em `development/`.
- Config: `development/config/core-config.yaml`.
- Comandos principais:
  ```bash
  python development/main.py setup
  python development/main.py create-stories
  python development/main.py implement
  python development/main.py full-cycle
  ```

## Estrutura de diretórios
```
kermartin-4/
├─ kermartin_backend/      # Django (APIs, IA, segurança)
├─ product/frontend/       # Next.js (UI)
├─ development/            # BMAD (orquestração de histórias)
├─ .github/workflows/      # CI
├─ Makefile                # Tarefas úteis
└─ README_DEV.md           # Este guia
```

## Convenções
- Nome do projeto e namespaces: "Kermartin".
- Sem credenciais em código/repos.
- Commits curtos e descritivos.

## Suporte
- Documentação de API: `API_DOCUMENTATION.md`
- Deploy: `DEPLOY_RENDER.md`, `DEPLOY_EXISTING_DB.md`
- Padrões: `development/standards/`
