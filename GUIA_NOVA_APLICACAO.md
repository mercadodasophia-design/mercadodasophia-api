# 🚀 Guia: Criar Nova Aplicação AliExpress Developer

## 📋 **Passo 1: Acessar AliExpress Developer**

1. **Acesse:** https://developers.aliexpress.com/
2. **Faça login** com sua conta do AliExpress
3. **Complete o perfil** da empresa (se necessário)

## 🔧 **Passo 2: Criar Nova Aplicação**

1. **Vá para "My Apps"**
2. **Clique em "Create App"**
3. **Preencha os dados:**

```
App Name: Mercado da Sophia
App Description: API para importação de produtos do AliExpress
Category: E-commerce
Platform: Web
```

## 🔑 **Passo 3: Obter Credenciais**

Após criar a aplicação, você receberá:

- **App Key** (Client ID)
- **App Secret** (Client Secret)

## ⚙️ **Passo 4: Configurar Callback URL**

1. **Vá em "App Settings"**
2. **Adicione a URL de callback:**
   ```
   https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback
   ```

## 🔄 **Passo 5: Atualizar Configuração**

1. **Edite o arquivo `config.env`:**
   ```env
   ALIEXPRESS_APP_KEY=SUA_NOVA_APP_KEY
   ALIEXPRESS_APP_SECRET=SEU_NOVO_APP_SECRET
   ```

2. **Faça commit e push:**
   ```bash
   git add config.env
   git commit -m "Update AliExpress credentials"
   git push origin master
   ```

## 🚀 **Passo 6: Testar**

1. **A API será redeployada automaticamente**
2. **Teste o endpoint de health:**
   ```bash
   curl https://mercadodasophia-api.onrender.com/api/health
   ```

## 📊 **Status Atual:**

- ✅ API funcionando no Render
- ✅ Endpoints básicos OK
- ❌ Credenciais OAuth2 inválidas
- ⏳ Aguardando novas credenciais

## 🎯 **Próximos Passos:**

1. Criar nova aplicação no AliExpress Developer
2. Obter novas credenciais
3. Atualizar configuração
4. Testar OAuth2
5. Testar busca de produtos

---

**Nota:** O processo pode levar alguns minutos para o redeploy no Render. 