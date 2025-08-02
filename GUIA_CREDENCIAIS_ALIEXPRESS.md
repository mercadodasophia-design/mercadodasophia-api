# 🔑 Guia para Obter Credenciais AliExpress API

## 📋 Passos para Configurar AliExpress Open Platform

### 1. Acessar AliExpress Open Platform
- Vá para: https://developers.aliexpress.com/
- Faça login com sua conta AliExpress

### 2. Criar Aplicação
- Clique em "Create App" ou "Criar Aplicação"
- Preencha os dados:
  - **App Name**: Mercado da Sophia
  - **App Description**: E-commerce dropshipping
  - **Category**: E-commerce
  - **Platform**: Web

### 3. Obter Credenciais
Após criar a aplicação, você receberá:
- **App Key**: Chave única da sua aplicação
- **App Secret**: Chave secreta para autenticação

### 4. Configurar Callback URL
- Vá nas configurações da sua aplicação
- Adicione a URL de callback: `https://mercadodasophia.com/callback`
- Ou use: `http://localhost:3000/api/aliexpress/oauth-callback` (para testes)

### 5. Ativar APIs Necessárias
Na sua aplicação, ative estas APIs:
- ✅ `aliexpress.ds.product.list` - Listar produtos
- ✅ `aliexpress.solution.product.info.get` - Detalhes do produto
- ✅ `aliexpress.trade.create` - Criar pedido
- ✅ `aliexpress.trade.pay` - Pagar pedido
- ✅ `aliexpress.trade.get` - Consultar pedido
- ✅ `aliexpress.logistics.buyer.tracking` - Rastrear pedido
- ✅ `aliexpress.category.redefining.getallchildattributesresult` - Categorias

## 🔧 Configurar o Projeto

### 1. Editar config.env
```bash
# Abra o arquivo config.env e substitua:
ALIEXPRESS_APP_KEY=SUA_APP_KEY_REAL_AQUI
ALIEXPRESS_APP_SECRET=SEU_APP_SECRET_REAL_AQUI
```

### 2. Exemplo de config.env correto:
```env
# Configurações AliExpress Dropshipping
ALIEXPRESS_APP_KEY=517616
ALIEXPRESS_APP_SECRET=TTqNmTMs5Q0QiPbulDNenhXr2My18nN4

# Configurações da API
API_BASE_URL=https://api-sg.aliexpress.com/sync
OAUTH_REDIRECT_URI=https://mercadodasophia.com/callback

# Configurações do Servidor
PORT=3000
DEBUG=true
```

## 🧪 Testar Configuração

### 1. Reiniciar API
```bash
python minimal_api.py
```

### 2. Verificar Status
Acesse: http://localhost:3000/api/health

Deve mostrar:
```json
{
  "success": true,
  "message": "API funcionando!",
  "app_key_configured": true,
  "app_secret_configured": true
}
```

### 3. Testar OAuth2
Acesse: http://localhost:3000/api/aliexpress/oauth-url

Deve retornar uma URL de autorização válida.

## ⚠️ Importante

1. **Nunca compartilhe suas credenciais**
2. **Use variáveis de ambiente em produção**
3. **Mantenha o App Secret seguro**
4. **Teste primeiro em ambiente de desenvolvimento**

## 🆘 Problemas Comuns

### Credenciais não carregam
- Verifique se o arquivo `config.env` está na pasta correta
- Confirme que não há espaços extras nas credenciais
- Reinicie o servidor após alterações

### Erro de autenticação
- Verifique se as APIs estão ativadas na sua aplicação
- Confirme se o callback URL está configurado corretamente
- Teste primeiro com as APIs básicas

### Erro de permissão
- Verifique se sua aplicação foi aprovada pelo AliExpress
- Aguarde a aprovação (pode levar alguns dias)
- Entre em contato com o suporte se necessário 