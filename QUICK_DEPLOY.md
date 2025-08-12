# ⚡ DEPLOY RÁPIDO - KERMARTIN 3.0

## 🚀 Deploy em 5 Minutos no Render

### **PASSO 1: Preparação (1 min)**
1. Tenha sua **OpenAI API Key** em mãos
2. Acesse [render.com](https://render.com) e faça login
3. Conecte sua conta GitHub

### **PASSO 2: Escolher Tipo de Deploy**

#### **OPÇÃO A: Banco Novo (Blueprint)**
1. **No Render Dashboard:**
   - Clique em "New +" → "Blueprint"
   - Selecione repositório `kermartin-4`
   - Branch: `master`
   - Clique em "Create New Blueprint"

#### **OPÇÃO B: Banco Existente (Web Service)**
1. **No Render Dashboard:**
   - Clique em "New +" → "Web Service"
   - Selecione repositório `kermartin-4`
   - Branch: `master`
   - Build Command: `./build.sh`
   - Start Command: `cd kermartin_backend && gunicorn kermartin_project.wsgi:application`

2. **Aguarde o Build:**
   - ⏱️ Tempo: ~3-5 minutos
   - 📊 Acompanhe logs em tempo real

### **PASSO 3: Configurar Variáveis (1 min)**
1. **Após build concluído:**
   - Vá para serviço `kermartin-backend`
   - Clique em "Environment"
   - Configure:

**Para Banco Novo (Blueprint):**
```env
OPENAI_API_KEY=sua-chave-aqui
```

**Para Banco Existente (Web Service):**
```env
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=sua-chave-aqui
SECRET_KEY=sua-secret-key
```

2. **Clique em "Save Changes"**

### **PASSO 4: Acessar Sistema**
```
🌐 URL: https://kermartin-backend.onrender.com
🔧 Admin: https://kermartin-backend.onrender.com/admin/
📡 API: https://kermartin-backend.onrender.com/api/

👤 Login: admin@kermartin.com
🔑 Senha: KermartinAdmin2024!
```

## ✅ PRONTO! Sistema funcionando em produção!

---

## 🔧 Configuração Automática Incluída

O `render.yaml` já configura automaticamente:

✅ **Web Service** - Django Backend
✅ **PostgreSQL** - Banco de dados
✅ **Redis** - Cache
✅ **SSL/HTTPS** - Certificado automático
✅ **Domínio** - kermartin-backend.onrender.com
✅ **Migrações** - Executadas automaticamente
✅ **Superusuário** - Criado automaticamente
✅ **Static Files** - Configurados com Whitenoise

---

## 📊 Custos

**Plano Starter:** ~$21/mês
- Web Service: $7/mês
- PostgreSQL: $7/mês  
- Redis: $7/mês

**Plano Free:** $0/mês (limitado)
- Sleep após 15min inatividade
- 750 horas/mês

---

## 🛠️ Troubleshooting Rápido

### **Build Falha?**
- Verifique logs no dashboard
- Comum: problema com requirements.txt

### **Erro OpenAI?**
- Configure `OPENAI_API_KEY` corretamente
- Teste a chave em: https://platform.openai.com

### **Erro 500?**
- Verifique logs da aplicação
- Comum: variável de ambiente faltando

### **Não consegue acessar?**
- Aguarde 2-3 minutos após deploy
- Verifique se build foi concluído

---

## 📞 Suporte

- 📚 **Documentação completa:** DEPLOY_RENDER.md
- 🐛 **Issues:** GitHub Issues
- 💬 **Render Support:** Dashboard → Help

---

## 🎯 Próximos Passos

Após deploy bem-sucedido:

1. ✅ Alterar senha do admin
2. ✅ Testar upload de documentos
3. ✅ Executar análise de teste
4. ✅ Configurar domínio personalizado (opcional)
5. ✅ Configurar monitoramento (opcional)

**🏆 Kermartin 3.0 rodando em produção!**
