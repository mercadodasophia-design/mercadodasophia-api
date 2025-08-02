# 🔍 Verificar Credenciais AliExpress

## 🚨 Problema Identificado
**Erro:** `param-appkey.not.exists` - App Key não reconhecido

## 📋 Passos para Corrigir

### 1. Acessar AliExpress Open Platform
- Vá para: https://developers.aliexpress.com/
- Faça login com sua conta AliExpress

### 2. Verificar Aplicação Existente
- Vá em "My Apps" ou "Minhas Aplicações"
- Procure por uma aplicação com App Key: `517616`
- Se não encontrar, a aplicação não existe

### 3. Criar Nova Aplicação (se necessário)
Se não encontrar a aplicação:

**Dados para criar:**
- **App Name**: Mercado da Sophia
- **App Description**: E-commerce dropshipping platform
- **Category**: E-commerce
- **Platform**: Web

### 4. Obter Novas Credenciais
Após criar, você receberá:
- **Novo App Key** (diferente de 517616)
- **Novo App Secret**

### 5. Ativar APIs Necessárias
Na nova aplicação, ative:
- ✅ `aliexpress.ds.product.list`
- ✅ `aliexpress.solution.product.info.get`
- ✅ `aliexpress.trade.create`
- ✅ `aliexpress.trade.pay`
- ✅ `aliexpress.trade.get`
- ✅ `aliexpress.logistics.buyer.tracking`
- ✅ `aliexpress.category.redefining.getallchildattributesresult`

### 6. Configurar Callback URL
Adicione: `https://mercadodasophia.com/callback`

### 7. Atualizar config.env
```env
ALIEXPRESS_APP_KEY=NOVO_APP_KEY_AQUI
ALIEXPRESS_APP_SECRET=NOVO_APP_SECRET_AQUI
```

### 8. Reiniciar API
```bash
python minimal_api.py
```

## ⚠️ Possíveis Causas

### Aplicação não existe
- O App Key 517616 nunca foi criado
- Aplicação foi deletada
- Credenciais são de teste/desenvolvimento

### Aplicação não aprovada
- AliExpress ainda não aprovou a aplicação
- Aguarde aprovação (pode levar dias)

### APIs não ativadas
- As APIs necessárias não estão ativadas
- Verifique na configuração da aplicação

## 🧪 Teste Após Correção

1. **Verificar credenciais:**
   ```
   http://localhost:3000/api/health
   ```

2. **Testar OAuth URL:**
   ```
   http://localhost:3000/api/aliexpress/oauth-url
   ```

3. **Se funcionar, a URL deve abrir sem erro**

## 📞 Suporte
Se o problema persistir:
- Entre em contato com AliExpress Open Platform
- Verifique se sua conta tem permissões para criar aplicações
- Confirme se o domínio está aprovado 