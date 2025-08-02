# 🔐 Guia OAuth2 AliExpress - Passo a Passo

## 🎯 Objetivo
Completar a autenticação OAuth2 para acessar as APIs protegidas do AliExpress.

## 📋 Passos para Autenticação

### 1. Gerar URL de Autorização
Acesse: http://localhost:3000/api/aliexpress/oauth-url

**Resposta esperada:**
```json
{
  "auth_url": "https://oauth.aliexpress.com/authorize?response_type=code&client_id=517616&redirect_uri=https%3A%2F%2Fmercadodasophia.com%2Fcallback&state=xyz123"
}
```

### 2. Acessar a URL de Autorização
- Copie a URL retornada
- Abra no navegador
- Faça login na sua conta AliExpress
- Autorize a aplicação

### 3. Capturar o Código de Autorização
Após autorizar, você será redirecionado para:
```
https://mercadodasophia.com/callback?code=ABC123&state=xyz123
```

**Importante:** Copie o valor do parâmetro `code` (ex: ABC123)

### 4. Trocar Código por Token
Faça uma requisição POST para:
```
http://localhost:3000/api/aliexpress/oauth-callback?code=ABC123
```

**Exemplo usando curl:**
```bash
curl -X GET "http://localhost:3000/api/aliexpress/oauth-callback?code=ABC123"
```

### 5. Verificar Autenticação
Após o sucesso, teste os endpoints protegidos:
- http://localhost:3000/api/aliexpress/products?keywords=phone
- http://localhost:3000/api/aliexpress/categories
- http://localhost:3000/api/aliexpress/shipping-methods

## 🧪 Teste Rápido

### 1. Abrir no navegador:
```
http://localhost:3000/api/aliexpress/oauth-url
```

### 2. Copiar a URL de autorização e abrir

### 3. Após autorizar, usar o código para autenticar

## ⚠️ Problemas Comuns

### URL de callback não funciona
- Use: `http://localhost:3000/api/aliexpress/oauth-callback` (para testes)
- Configure no AliExpress Open Platform

### Erro de permissão
- Verifique se as APIs estão ativadas na sua aplicação
- Aguarde a aprovação da aplicação

### Token expirado
- O token expira em algumas horas
- Use o refresh_token para renovar

## 🎉 Sucesso!
Após completar o OAuth2, você poderá:
- ✅ Buscar produtos reais do AliExpress
- ✅ Importar produtos para o catálogo
- ✅ Criar e gerenciar pedidos
- ✅ Rastrear envios
- ✅ Consultar categorias e atributos 