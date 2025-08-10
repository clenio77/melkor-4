# 🚀 Kermartin 3.0 - Desenvolvimento Automatizado com BMad Method

Sistema de desenvolvimento automatizado usando **CrewAI** para construir o **Kermartin 3.0**, um agente de IA especialista em análise jurídica para Tribunal do Júri.

## 📋 Visão Geral

Este projeto implementa o **BMad Method** (Desenvolvimento Guiado por Documentos) usando agentes de IA especializados para automatizar todo o ciclo de desenvolvimento:

- **🤖 Agente SM (Bob)**: Cria histórias detalhadas baseadas em épicos
- **💻 Agente Dev (James)**: Implementa código seguindo as histórias
- **🔍 Agente QA (Sarah)**: Revisa qualidade e testes (futuro)

## 🏗️ Arquitetura do Produto Final

**Kermartin 3.0** será uma aplicação web completa:

- **Backend**: Django + PostgreSQL + Redis
- **Frontend**: Next.js + TailwindCSS  
- **IA**: OpenAI GPT-4 com persona de advogado criminalista
- **Funcionalidade**: Análise de processos penais em 4 blocos especializados

## 🚀 Quick Start

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <repo-url>
cd kermartin-4

# Instalar dependências
pip install -r development/requirements.txt

# Configurar ambiente
python development/main.py setup
```

### 2. Configurar .env

Edite o arquivo `.env` criado automaticamente:

```env
# OpenAI API (OBRIGATÓRIO)
OPENAI_API_KEY=sk-your-openai-key-here

# Database
DB_NAME=kermartin_dev
DB_USER=kermartin_user
DB_PASSWORD=kermartin_pass
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 3. Iniciar Infraestrutura

```bash
# Subir PostgreSQL e Redis
cd development
docker-compose up -d

# Verificar se serviços estão rodando
docker-compose ps
```

### 4. Executar Desenvolvimento Automatizado

```bash
# Ciclo completo (recomendado)
python development/main.py full-cycle

# Ou por etapas:
python development/main.py create-stories  # Criar histórias
python development/main.py implement       # Implementar código

# Épico específico
python development/main.py single --epic E001
```

## 📊 Comandos Disponíveis

```bash
# Configurar projeto
python development/main.py setup

# Criar todas as histórias
python development/main.py create-stories

# Implementar todas as histórias
python development/main.py implement

# Ciclo completo (SM → Dev → QA)
python development/main.py full-cycle

# Implementar épico específico
python development/main.py single --epic E001

# Ver status do projeto
python development/main.py status

# Validar ambiente
python development/main.py setup --validate-only
```

## 🎯 Épicos do Kermartin 3.0

| ID | Título | Descrição |
|----|--------|-----------|
| E001 | Configuração do Banco de Dados | Modelos Django para usuários, processos, documentos |
| E002 | Sistema de Autenticação | Login JWT para advogados |
| E003 | Upload e Processamento | Sistema de upload de PDFs com extração de texto |
| E004 | Engine de Análise Jurídica | Agente Kermartin com persona e prompts especializados |
| E005 | Interface de Menu | Menu interativo com 5 blocos de análise |
| E006 | Sistema de Análise por Blocos | 4 blocos de análise jurídica com subetapas |
| E007 | Sistema de Sessões | Gerenciar sessões de análise e persistência |
| E008 | Interface Frontend | Interface Next.js responsiva |

## 🔧 Estrutura do Projeto

```
kermartin-4/
├── development/                 # Sistema de desenvolvimento automatizado
│   ├── agents/                 # Agentes CrewAI (SM, Dev, QA)
│   ├── config/                 # Configurações BMad
│   ├── standards/              # Padrões de código e testes
│   ├── workflow/               # Orquestrador BMad
│   ├── stories/                # Histórias geradas pelo SM
│   ├── implementations/        # Resultados das implementações
│   └── main.py                 # Ponto de entrada
│
├── product/                    # Produto final (Kermartin 3.0)
│   ├── backend/                # Django + PostgreSQL
│   └── frontend/               # Next.js
│
├── docs/                       # Documentação original
│   ├── persona-kermartin.md       # Persona do advogado criminalista
│   ├── instrucoes-analises.md  # Instruções detalhadas dos 4 blocos
│   └── metodologia.md          # Metodologia de desenvolvimento
│
└── README.md                   # Este arquivo
```

## 🤖 Como Funciona o BMad Method

### 1. Scrum Master (Bob)
- Lê os épicos definidos
- Cria histórias detalhadas e autocontidas
- Inclui Dev Notes com extratos da arquitetura
- Define tarefas sequenciais para implementação

### 2. Developer (James)
- Recebe história completa
- Implementa código seguindo padrões rigorosos
- Escreve testes para cada funcionalidade
- Executa validações (pytest, flake8)
- Marca tarefas como concluídas apenas após validação

### 3. QA (Sarah) - Futuro
- Revisa código implementado
- Executa testes de regressão
- Valida qualidade e padrões
- Aprova ou rejeita implementação

## 📈 Monitoramento

### Status do Projeto
```bash
python development/main.py status
```

### Logs dos Agentes
- Histórias criadas: `development/stories/`
- Implementações: `development/implementations/`
- Outputs gerais: `development/output/`

### Infraestrutura
```bash
# PostgreSQL Admin
http://localhost:8080
# User: admin@kermartin.com / Pass: admin123

# Redis Commander  
http://localhost:8081
```

## 🔒 Segurança

O sistema implementa proteções contra:
- Prompt injection na IA
- Validação de uploads de arquivos
- Autenticação JWT robusta
- Logs de auditoria

## 🧪 Testes

O sistema segue TDD rigoroso:
- **Cobertura mínima**: 80%
- **Testes unitários**: 70% dos testes
- **Testes de integração**: 20% dos testes  
- **Testes E2E**: 10% dos testes

## 📚 Documentação Técnica

- **Padrões de Código**: `development/standards/coding-standards.md`
- **Estratégia de Testes**: `development/standards/testing-strategy.md`
- **Configuração BMad**: `development/config/core-config.yaml`

## 🤝 Contribuição

Este projeto usa desenvolvimento automatizado. Para contribuir:

1. Modifique os épicos em `development/config/core-config.yaml`
2. Execute `python development/main.py full-cycle`
3. Os agentes implementarão automaticamente as mudanças

## 📄 Licença

MIT License - veja `LICENSE` para detalhes.

---

**Desenvolvido com ❤️ usando BMad Method + CrewAI**
