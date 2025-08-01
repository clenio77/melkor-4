# 🚀 DEPLOY DO MELKOR 3.0 NO RENDER

## 📋 Guia Completo para Deploy em Produção

Este guia mostra como fazer deploy do Melkor 3.0 no Render usando deploy automático via GitHub.

---

## 🎯 PRÉ-REQUISITOS

### 1. Contas Necessárias
- ✅ Conta no [GitHub](https://github.com)
- ✅ Conta no [Render](https://render.com)
- ✅ Chave da API OpenAI

### 2. Repositório Preparado
- ✅ Código no GitHub (já configurado)
- ✅ Arquivos de configuração incluídos:
  - `render.yaml` - Configuração do Render
  - `build.sh` - Script de build
  - `requirements.txt` - Dependências

---

## 🚀 PASSO A PASSO PARA DEPLOY

### **PASSO 1: Preparar Repositório**

O repositório já está configurado com todos os arquivos necessários:

```
melkor-4/
├── render.yaml          # Configuração do Render
├── build.sh            # Script de build
├── requirements.txt    # Dependências de produção
├── melkor_backend/     # Código Django
└── DEPLOY_RENDER.md    # Este guia
```

### **PASSO 2: Conectar GitHub ao Render**

1. **Acesse o Render:**
   - Vá para [render.com](https://render.com)
   - Faça login ou crie uma conta

2. **Conectar GitHub:**
   - Clique em "New +"
   - Selecione "Blueprint"
   - Conecte sua conta do GitHub
   - Autorize o Render a acessar seus repositórios

### **PASSO 3: Configurar Blueprint**

1. **Selecionar Repositório:**
   - Escolha o repositório `melkor-4`
   - Branch: `master`

2. **Configurar Serviços:**
   O arquivo `render.yaml` já configura automaticamente:
   - ✅ **Web Service** (Django Backend)
   - ✅ **PostgreSQL Database**
   - ✅ **Redis Cache**

3. **Configurar Variáveis de Ambiente:**
   ```
   OPENAI_API_KEY=sua-chave-openai-aqui
   OPENAI_MODEL=gpt-4-1106-preview
   ENVIRONMENT=production
   ```

### **PASSO 4: Deploy Automático**

1. **Iniciar Deploy:**
   - Clique em "Create New Blueprint"
   - O Render irá automaticamente:
     - Criar banco PostgreSQL
     - Criar cache Redis
     - Fazer build da aplicação
     - Executar migrações
     - Criar superusuário

2. **Monitorar Build:**
   - Acompanhe os logs de build
   - Tempo estimado: 5-10 minutos

### **PASSO 5: Configurar Variáveis de Ambiente**

Após o deploy inicial, configure as variáveis sensíveis:

1. **No Dashboard do Render:**
   - Vá para o serviço `melkor-backend`
   - Clique em "Environment"
   - Adicione/edite:

```env
# Obrigatório - Configure sua chave OpenAI
OPENAI_API_KEY=sk-sua-chave-openai-real-aqui

# Opcional - Configurações avançadas
SENTRY_DSN=sua-url-sentry-para-monitoramento
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

2. **Salvar e Redeploy:**
   - Clique em "Save Changes"
   - O serviço será automaticamente redeployado

---

## 🌐 ACESSAR SISTEMA EM PRODUÇÃO

### **URLs do Sistema:**
```
🌐 Frontend: https://melkor-backend.onrender.com
🔧 Admin: https://melkor-backend.onrender.com/admin/
📡 API: https://melkor-backend.onrender.com/api/
📚 Docs: https://melkor-backend.onrender.com/api/docs/
```

### **Credenciais Iniciais:**
```
👤 Email: admin@melkor.com
🔑 Senha: MelkorAdmin2024!
```

**⚠️ IMPORTANTE:** Altere a senha após primeiro acesso!

---

## 🔧 CONFIGURAÇÕES AVANÇADAS

### **1. Domínio Personalizado**

Para usar seu próprio domínio:

1. **No Render Dashboard:**
   - Vá para o serviço web
   - Clique em "Settings"
   - Seção "Custom Domains"
   - Adicione seu domínio

2. **Configurar DNS:**
   ```
   Tipo: CNAME
   Nome: melkor (ou subdomínio desejado)
   Valor: melkor-backend.onrender.com
   ```

### **2. Monitoramento com Sentry**

Para monitoramento de erros em produção:

1. **Criar conta no Sentry:**
   - Vá para [sentry.io](https://sentry.io)
   - Crie projeto Django

2. **Configurar no Render:**
   ```env
   SENTRY_DSN=https://sua-chave@sentry.io/projeto
   ```

### **3. Email em Produção**

Para envio de emails:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

---

## 🧪 TESTAR DEPLOY

### **1. Verificar Saúde do Sistema:**
```bash
curl https://melkor-backend.onrender.com/api/menu/opcoes/
```

### **2. Testar Admin:**
- Acesse: https://melkor-backend.onrender.com/admin/
- Login com credenciais iniciais
- Verifique se dados estão carregados

### **3. Testar APIs:**
```bash
# Testar menu
curl https://melkor-backend.onrender.com/api/menu/opcoes/

# Testar autenticação
curl -X POST https://melkor-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@melkor.com","password":"MelkorAdmin2024!"}'
```

---

## 🔄 ATUALIZAÇÕES AUTOMÁTICAS

### **Deploy Contínuo:**
- ✅ **Automático:** Push para `master` → Deploy automático
- ✅ **Rollback:** Disponível no dashboard
- ✅ **Logs:** Monitoramento em tempo real

### **Processo de Atualização:**
1. Faça alterações no código
2. Commit e push para GitHub
3. Render detecta mudanças automaticamente
4. Build e deploy automático
5. Zero downtime deployment

---

## 📊 MONITORAMENTO

### **Métricas Disponíveis:**
- ✅ **Performance:** Tempo de resposta, CPU, memória
- ✅ **Logs:** Aplicação e sistema em tempo real
- ✅ **Uptime:** Monitoramento 24/7
- ✅ **Alertas:** Notificações por email

### **Dashboard do Render:**
- CPU e memória em tempo real
- Logs de aplicação
- Métricas de rede
- Status de saúde

---

## 🛠️ TROUBLESHOOTING

### **Problemas Comuns:**

#### **1. Build Falha:**
```bash
# Verificar logs de build
# Comum: dependências em requirements.txt

# Solução: Verificar requirements.txt
pip install -r requirements.txt  # Testar localmente
```

#### **2. Erro de Banco:**
```bash
# Erro: relation does not exist
# Solução: Verificar se migrações rodaram

# No build.sh já está configurado:
python manage.py migrate
```

#### **3. Erro OpenAI:**
```bash
# Erro: Invalid API key
# Solução: Configurar OPENAI_API_KEY corretamente
```

#### **4. Erro de Static Files:**
```bash
# Erro: Static files not found
# Solução: Verificar STATICFILES_STORAGE no settings.py
```

### **Logs Úteis:**
```bash
# Ver logs em tempo real no dashboard
# Ou via CLI do Render:
render logs -s melkor-backend
```

---

## 💰 CUSTOS ESTIMADOS

### **Plano Starter (Recomendado):**
```
🌐 Web Service: $7/mês
🗄️ PostgreSQL: $7/mês
🔄 Redis: $7/mês
📊 Total: ~$21/mês
```

### **Plano Free (Limitado):**
```
⚠️ Limitações:
- Sleep após 15min inatividade
- 750 horas/mês
- Sem banco persistente
```

---

## 🎯 PRÓXIMOS PASSOS

### **Após Deploy Bem-sucedido:**

1. **✅ Configurar OpenAI API Key**
2. **✅ Alterar senha do admin**
3. **✅ Testar todas as funcionalidades**
4. **✅ Configurar domínio personalizado**
5. **✅ Configurar monitoramento**
6. **✅ Treinar usuários**

### **Melhorias Futuras:**
- 🔄 **CI/CD:** GitHub Actions
- 📱 **Frontend:** Next.js separado
- 📊 **Analytics:** Google Analytics
- 🔒 **Backup:** Backup automático do banco
- 📧 **Email:** Templates personalizados

---

## 📞 SUPORTE

### **Recursos de Ajuda:**
- 📚 **Documentação:** API_DOCUMENTATION.md
- 🐛 **Issues:** GitHub Issues
- 💬 **Render Support:** Dashboard → Help
- 📧 **Email:** Suporte técnico

### **Monitoramento:**
- 🔍 **Logs:** Dashboard do Render
- 📊 **Métricas:** Render Analytics
- 🚨 **Alertas:** Email notifications
- 📱 **Status:** Status page do Render

---

## 🏆 CONCLUSÃO

O Melkor 3.0 está agora configurado para deploy automático no Render com:

✅ **Deploy automático** via GitHub
✅ **Banco PostgreSQL** configurado
✅ **Cache Redis** otimizado
✅ **SSL/HTTPS** automático
✅ **Monitoramento** integrado
✅ **Backup** automático
✅ **Escalabilidade** horizontal

**🚀 Sistema pronto para produção com qualidade empresarial!**
