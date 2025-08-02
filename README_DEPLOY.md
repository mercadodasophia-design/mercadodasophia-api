# 🚀 Deploy no Render - API AliExpress

## 📋 Passos para Deploy

### 1. Criar conta no Render
- Acesse: https://render.com
- Faça login/cadastro

### 2. Conectar Repositório
- Clique em "New +"
- Selecione "Web Service"
- Conecte seu repositório GitHub

### 3. Configurar Deploy
**Nome:** `mercadodasophia-api`
**Runtime:** Python 3
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `gunicorn minimal_api:app --bind 0.0.0.0:$PORT`

### 4. Configurar Variáveis de Ambiente
No Render, vá em "Environment" e adicione:

```
ALIEXPRESS_APP_KEY=517616
ALIEXPRESS_APP_SECRET=TTqNmTMs5Q0QiPbulDNenhXr2My18nN4
```

### 5. Deploy
- Clique em "Create Web Service"
- Aguarde o deploy (2-3 minutos)

### 6. Atualizar Callback URL no AliExpress
Após o deploy, você receberá uma URL como:
`https://mercadodasophia-api.onrender.com`

Vá no AliExpress Open Platform e atualize:
- **Callback URL:** `https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback`

## ✅ Teste após Deploy

1. **Health Check:**
   ```
   GET https://sua-api.onrender.com/api/health
   ```

2. **OAuth URL:**
   ```
   GET https://sua-api.onrender.com/api/aliexpress/oauth-url
   ```

3. **Busca de Produtos:**
   ```
   GET https://sua-api.onrender.com/api/search?keywords=smartphone
   ```

## 🔧 Troubleshooting

- **Erro 500:** Verifique as variáveis de ambiente
- **Timeout:** Render pode ter cold start (primeira requisição mais lenta)
- **CORS:** Já configurado no código 