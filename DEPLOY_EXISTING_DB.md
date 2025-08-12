# 🗄️ DEPLOY COM BANCO POSTGRESQL EXISTENTE

## 🎯 Usando Seu Banco PostgreSQL Existente no Render

Se você já tem um banco PostgreSQL no Render, **NÃO precisa criar outro!** Siga este guia para usar o banco existente.

---

## 🚀 DEPLOY COM BANCO EXISTENTE

### **OPÇÃO A: Deploy Manual (Recomendado)**

#### **PASSO 1: Deploy Apenas do Web Service**

1. **No Render Dashboard:**
   - Clique em "New +" → "Web Service"
   - Conecte ao repositório `kermartin-4`
   - Branch: `master`

2. **Configurações Básicas:**
   ```
   Name: kermartin-backend
   Environment: Python
   Build Command: ./build.sh
   Start Command: cd kermartin_backend && gunicorn kermartin_project.wsgi:application
   ```

#### **PASSO 2: Configurar Variáveis de Ambiente**

1. **Obter URL do Seu Banco Existente:**
   - Vá para seu banco PostgreSQL existente
   - Copie a "External Database URL"
   - Formato: `postgresql://user:password@host:port/database`

2. **Configurar no Web Service:**
   ```env
   # Banco de dados existente
   DATABASE_URL=postgresql://user:password@host:port/database
   
   # Configurações obrigatórias
   DJANGO_SETTINGS_MODULE=kermartin_project.settings
   DEBUG=false
   ALLOWED_HOSTS=kermartin-backend.onrender.com,localhost,127.0.0.1
   SECRET_KEY=sua-secret-key-aqui
   
   # OpenAI (configure sua chave)
   OPENAI_API_KEY=sk-sua-chave-openai-aqui
   OPENAI_MODEL=gpt-4-1106-preview
   OPENAI_MAX_TOKENS=4000
   
   # Ambiente
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   DISABLE_COLLECTSTATIC=1
   ```

#### **PASSO 3: Configurar Redis (Opcional)**

Se quiser cache Redis:

1. **Criar Redis Service:**
   - "New +" → "Redis"
   - Name: `kermartin-redis`
   - Plan: Starter

2. **Adicionar ao Web Service:**
   ```env
   REDIS_URL=redis://kermartin-redis:6379/0
   ```

---

### **OPÇÃO B: Blueprint com Banco Existente**

#### **PASSO 1: Usar Blueprint Modificado**

1. **Renomear arquivo:**
   ```bash
   # No seu repositório local
   mv render.yaml render-new-db.yaml
   mv render-existing-db.yaml render.yaml
   ```

2. **Fazer commit e push:**
   ```bash
   git add .
   git commit -m "Configuração para banco existente"
   git push origin master
   ```

3. **Deploy via Blueprint:**
   - "New +" → "Blueprint"
   - Selecionar repositório
   - Configurar DATABASE_URL manualmente após deploy

---

## 🔧 CONFIGURAÇÃO DO BANCO EXISTENTE

### **PASSO 1: Preparar o Banco**

1. **Conectar ao seu banco existente:**
   ```sql
   -- Opcional: Criar schema separado para Kermartin
   CREATE SCHEMA IF NOT EXISTS kermartin;
   
   -- Ou usar database separado
   CREATE DATABASE kermartin_production;
   ```

2. **Verificar permissões:**
   ```sql
   -- Verificar se usuário tem permissões necessárias
   GRANT ALL PRIVILEGES ON DATABASE kermartin_production TO seu_usuario;
   ```

### **PASSO 2: Configurar DATABASE_URL**

Formato da URL do banco:
```
postgresql://usuario:senha@host:porta/database
```

**Exemplo:**
```
DATABASE_URL=postgresql://kermartin_user:senha123@dpg-abc123-a.oregon-postgres.render.com:5432/kermartin_db
```

### **PASSO 3: Testar Conexão**

Após configurar, o build.sh automaticamente:
- ✅ Executa migrações
- ✅ Cria tabelas do Kermartin
- ✅ Cria superusuário
- ✅ Testa conexão

---

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### **Backup do Banco Existente:**
```bash
# Antes de fazer deploy, faça backup
pg_dump -h host -U usuario -d database > backup_antes_kermartin.sql
```

### **Isolamento de Dados:**
- **Opção 1:** Usar schema separado (`kermartin`)
- **Opção 2:** Usar database separado
- **Opção 3:** Usar prefixo nas tabelas

### **Configuração de Schema (Opcional):**
```python
# No settings.py, se usar schema separado
DATABASES = {
    'default': {
        # ... configuração normal ...
        'OPTIONS': {
            'options': '-c search_path=kermartin,public'
        }
    }
}
```

---

## 🧪 TESTE DE CONEXÃO

### **Verificar se Funcionou:**

1. **Logs do Build:**
   ```
   ✅ Migrações executadas
   ✅ Superusuário criado
   ✅ Testes básicos passaram
   ```

2. **Testar Acesso:**
   ```bash
   # Testar API
   curl https://kermartin-backend.onrender.com/api/menu/opcoes/
   
   # Testar Admin
   # Acesse: https://kermartin-backend.onrender.com/admin/
   ```

3. **Verificar Tabelas Criadas:**
   ```sql
   -- Conectar ao banco e verificar
   \dt  -- Listar tabelas
   
   -- Deve mostrar tabelas do Kermartin:
   -- core_usuario
   -- core_processo
   -- core_documento
   -- etc.
   ```

---

## 💰 ECONOMIA DE CUSTOS

### **Usando Banco Existente:**
```
🌐 Web Service: $7/mês
🔄 Redis (opcional): $7/mês
📊 Total: $7-14/mês (vs $21/mês com novo banco)
```

### **Vantagens:**
- ✅ **Economia:** $7/mês
- ✅ **Dados existentes:** Preservados
- ✅ **Backup:** Já configurado
- ✅ **Monitoramento:** Já ativo

---

## 🔄 MIGRAÇÃO DE DADOS (Se Necessário)

### **Se Quiser Migrar Dados Existentes:**

1. **Backup dos dados atuais:**
   ```bash
   pg_dump -h host -U user -d database --data-only > dados_existentes.sql
   ```

2. **Após deploy do Kermartin:**
   ```bash
   # Restaurar dados específicos se necessário
   psql -h host -U user -d database < dados_existentes.sql
   ```

---

## 🛠️ TROUBLESHOOTING

### **Erro de Conexão:**
```
ERRO: could not connect to server
SOLUÇÃO: Verificar DATABASE_URL e permissões
```

### **Erro de Permissões:**
```
ERRO: permission denied for relation
SOLUÇÃO: GRANT ALL PRIVILEGES ON DATABASE TO usuario;
```

### **Conflito de Tabelas:**
```
ERRO: relation already exists
SOLUÇÃO: Usar schema separado ou prefixo
```

### **Erro de Migração:**
```
ERRO: migration failed
SOLUÇÃO: Verificar se banco está vazio ou usar --fake-initial
```

---

## 🎯 RESUMO RÁPIDO

### **Para Usar Banco Existente:**

1. ✅ **Deploy:** Web Service apenas (não Blueprint completo)
2. ✅ **DATABASE_URL:** Configurar com seu banco existente
3. ✅ **Migrações:** Executadas automaticamente
4. ✅ **Teste:** Verificar se tudo funciona
5. ✅ **Economia:** $7/mês vs $21/mês

### **Comandos Essenciais:**
```bash
# 1. Obter URL do banco existente
# 2. Configurar DATABASE_URL no web service
# 3. Deploy automático faz o resto!
```

**🏆 Resultado: Kermartin 3.0 rodando com seu banco existente!**
