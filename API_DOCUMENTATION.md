# 📚 DOCUMENTAÇÃO COMPLETA DA API - KERMARTIN 3.0

## 🎯 Visão Geral

A API do Kermartin 3.0 é uma API REST completa para análise jurídica especializada em Tribunal do Júri. Todas as rotas requerem autenticação JWT, exceto onde indicado.

**Base URL:** `http://localhost:8000/api/`

---

## 🔐 AUTENTICAÇÃO

### Registro de Usuário
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "advogado@escritorio.com",
  "password": "senha123",
  "nome_completo": "Dr. João Silva",
  "oab_numero": "123456",
  "oab_estado": "SP",
  "telefone": "(11) 99999-9999",
  "escritorio": "Silva & Associados"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Usuário criado com sucesso",
  "user_id": 1
}
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "advogado@escritorio.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 👤 USUÁRIOS

### Perfil do Usuário
```http
GET /api/usuarios/perfil/
Authorization: Bearer {access_token}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "advogado@escritorio.com",
  "nome_completo": "Dr. João Silva",
  "oab_numero": "123456",
  "oab_estado": "SP",
  "telefone": "(11) 99999-9999",
  "escritorio": "Silva & Associados",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 📋 PROCESSOS

### Listar Processos
```http
GET /api/processos/
Authorization: Bearer {access_token}
```

### Criar Processo
```http
POST /api/processos/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "titulo": "Homicídio Qualificado - João Silva",
  "numero_processo": "0001234-56.2024.8.26.0001",
  "tipo_crime": "homicidio",
  "comarca": "São Paulo",
  "vara": "1ª Vara do Tribunal do Júri",
  "reu_nome": "João da Silva",
  "vitima_nome": "Maria Santos",
  "observacoes": "Caso complexo com múltiplas qualificadoras"
}
```

### Obter Processo
```http
GET /api/processos/{id}/
Authorization: Bearer {access_token}
```

### Documentos do Processo
```http
GET /api/processos/{id}/documentos/
Authorization: Bearer {access_token}
```

### Análises do Processo
```http
GET /api/processos/{id}/analises/
Authorization: Bearer {access_token}
```

---

## 📄 DOCUMENTOS

### Listar Documentos
```http
GET /api/documentos/
Authorization: Bearer {access_token}
```

### Upload de Documento
```http
POST /api/documentos/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

arquivo_original: [arquivo.pdf]
tipo_documento: "inquerito"
processo: {processo_id}
```

**Tipos de documento:**
- `inquerito` - Inquérito Policial
- `denuncia` - Denúncia
- `resposta_acusacao` - Resposta à Acusação
- `sentencia_pronuncia` - Sentença de Pronúncia
- `alegacoes_finais` - Alegações Finais
- `ata_julgamento` - Ata de Julgamento
- `outros` - Outros

---

## 🧠 ANÁLISES

### Iniciar Análise Individual
```http
POST /api/analises/iniciar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "processo_id": "uuid-do-processo",
  "modo_analise": "individual",
  "bloco": 1,
  "subetapa": 1
}
```

### Iniciar Análise Completa
```http
POST /api/analises/iniciar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "processo_id": "uuid-do-processo",
  "modo_analise": "completa"
}
```

### Iniciar Análise Personalizada
```http
POST /api/analises/iniciar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "processo_id": "uuid-do-processo",
  "modo_analise": "personalizada",
  "blocos_selecionados": [1, 2, 4]
}
```

### Listar Análises
```http
GET /api/analises/
Authorization: Bearer {access_token}
```

### Resultados de uma Análise
```http
GET /api/analises/{id}/resultados/
Authorization: Bearer {access_token}
```

### Resumo de uma Análise
```http
GET /api/analises/{id}/resumo/
Authorization: Bearer {access_token}
```

---

## 📋 MENU INTERATIVO

### Opções do Menu
```http
GET /api/menu/opcoes/
```

**Resposta:**
```json
{
  "1": {
    "titulo": "Bloco 1 - Fase de Inquérito",
    "descricao": "Análise da fase investigativa e construção da defesa inicial",
    "subetapas": 6
  },
  "2": {
    "titulo": "Bloco 2 - Primeira Fase do Procedimento",
    "descricao": "Da denúncia até a pronúncia",
    "subetapas": 5
  },
  "3": {
    "titulo": "Bloco 3 - Segunda Fase do Procedimento",
    "descricao": "Preparação para o Tribunal do Júri",
    "subetapas": 5
  },
  "4": {
    "titulo": "Bloco 4 - Debates no Júri",
    "descricao": "Estratégias para o plenário do júri",
    "subetapas": 5
  },
  "5": {
    "titulo": "Análise Completa",
    "descricao": "Executa todos os blocos sequencialmente",
    "subetapas": 21
  }
}
```

### Processar Opção do Menu
```http
POST /api/menu/processar/
Content-Type: application/json

{
  "opcao": 1,
  "confirmacao": "S",
  "processo_id": "uuid-do-processo"
}
```

---

## 📊 ESTATÍSTICAS

### Dashboard
```http
GET /api/estatisticas/dashboard/
Authorization: Bearer {access_token}
```

**Resposta:**
```json
{
  "total_processos": 15,
  "total_documentos": 45,
  "total_analises": 23,
  "tokens_utilizados": 125000,
  "tempo_total_analises": "2:15:30",
  "processos_por_status": {
    "draft": 5,
    "analyzing": 3,
    "completed": 7
  },
  "analises_por_bloco": {
    "1": 12,
    "2": 8,
    "3": 2,
    "4": 1
  },
  "documentos_por_tipo": {
    "inquerito": 15,
    "denuncia": 12,
    "outros": 18
  },
  "ultima_atividade": "2024-01-15T14:30:00Z",
  "media_tempo_analise": 3.2
}
```

---

## 🤖 AI ENGINE

### Processar Documento
```http
POST /api/ai/processar-documento/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "documento_id": "uuid-do-documento"
}
```

### Análise Individual
```http
POST /api/ai/analise-individual/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "documento_id": "uuid-do-documento",
  "bloco": 1,
  "subetapa": 1
}
```

### Análise Completa
```http
POST /api/ai/analise-completa/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "processo_id": "uuid-do-processo",
  "blocos": [1, 2, 3, 4]
}
```

### Status de Segurança
```http
GET /api/ai/status-seguranca/
Authorization: Bearer {access_token}
```

---

## 🔒 CÓDIGOS DE STATUS

### Sucesso
- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Operação bem-sucedida sem conteúdo

### Erro do Cliente
- `400 Bad Request` - Dados inválidos
- `401 Unauthorized` - Token inválido ou ausente
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `429 Too Many Requests` - Rate limit excedido

### Erro do Servidor
- `500 Internal Server Error` - Erro interno
- `503 Service Unavailable` - Serviço temporariamente indisponível

---

## 🛡️ SEGURANÇA

### Rate Limiting
- **Análises:** 50 por hora por usuário
- **Uploads:** 20 por hora por usuário
- **Login:** 10 tentativas por hora por IP

### Validações
- **Arquivos:** Apenas PDF, máximo 10MB
- **Prompt Injection:** Proteção automática
- **JWT:** Tokens com expiração de 24h

### Headers Obrigatórios
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

## 📝 EXEMPLOS DE USO

### Fluxo Completo
```bash
# 1. Registrar usuário
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@kermartin.com","password":"senha123","nome_completo":"Dr. Teste","oab_numero":"123456","oab_estado":"SP"}'

# 2. Fazer login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@kermartin.com","password":"senha123"}'

# 3. Criar processo
curl -X POST http://localhost:8000/api/processos/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Processo Teste","tipo_crime":"homicidio"}'

# 4. Iniciar análise
curl -X POST http://localhost:8000/api/analises/iniciar/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"processo_id":"{id}","modo_analise":"completa"}'
```

---

## 🎯 BLOCOS DE ANÁLISE

### Bloco 1 - Fase de Inquérito (6 subetapas)
1. Análise da Tipificação do Crime
2. Revisão do Inquérito Policial
3. Direitos Constitucionais e Garantias Violadas
4. Análise do Auto de Prisão em Flagrante
5. Qualificadoras e Possibilidades de Desclassificação
6. Construção do Projeto de Defesa

### Bloco 2 - Primeira Fase do Procedimento (5 subetapas)
1. Análise da Denúncia e Primeiras Teses Defensivas
2. Resposta à Acusação
3. Audiência de Instrução e Julgamento (AIJ)
4. Nulidades e Impugnação de Provas
5. Alegações Finais da Primeira Fase

### Bloco 3 - Segunda Fase do Procedimento (5 subetapas)
1. Requisitos e Diligências da Defesa
2. Preparação Estratégica para o Plenário
3. Controle da Dinâmica do Júri
4. Estratégias de Persuasão e Psicodrama
5. Preparação para os Debates Orais

### Bloco 4 - Debates no Júri (5 subetapas)
1. Estruturação dos Debates
2. Técnicas de Desconstrução da Acusação
3. Uso de Psicodrama e CNV
4. Tréplica e Controle da Narrativa
5. Exortação Final e Última Impressão

---

**📞 Suporte:** Para dúvidas sobre a API, consulte a documentação técnica ou entre em contato com a equipe de desenvolvimento.
