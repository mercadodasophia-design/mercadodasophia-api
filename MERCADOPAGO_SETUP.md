# 🔐 Configuração do Mercado Pago

Este documento explica como configurar o Mercado Pago para funcionar tanto em modo de teste (sandbox) quanto em produção.

## 📋 Credenciais Disponíveis

### 🧪 **Modo Sandbox (Teste)**
```bash
# Access Token
TEST-6048716701718688-080816-b095cf4abaa34073116ac070ff38e8f4-1514652489

# Public Key
TEST-ce63c4af-fb50-4bef-b3dd-f0003f16cea3

# Client ID
6048716701718688

# Client Secret
YUC3Q0GxRueSrVQTHidGk7bMt9MJq7Sg
```

### 🚀 **Modo Produção**
```bash
# Access Token
APP_USR-6048716701718688-080816-ccba418de4c43b693e377903478dcd79-1514652489

# Public Key
APP_USR-145ec693-11d0-464b-8a18-b06b0e66006c

# Client ID
6048716701718688

# Client Secret
YUC3Q0GxRueSrVQTHidGk7bMt9MJq7Sg
```

## ⚙️ Como Configurar

### 1. **Usando Variáveis de Ambiente**

#### Para Sandbox (Padrão):
```bash
export MP_MODE=sandbox
export MP_ACCESS_TOKEN=TEST-6048716701718688-080816-b095cf4abaa34073116ac070ff38e8f4-1514652489
export MP_PUBLIC_KEY=TEST-ce63c4af-fb50-4bef-b3dd-f0003f16cea3
export MP_CLIENT_ID=6048716701718688
export MP_CLIENT_SECRET=YUC3Q0GxRueSrVQTHidGk7bMt9MJq7Sg
```

#### Para Produção:
```bash
export MP_MODE=production
export MP_ACCESS_TOKEN=APP_USR-6048716701718688-080816-ccba418de4c43b693e377903478dcd79-1514652489
export MP_PUBLIC_KEY=APP_USR-145ec693-11d0-464b-8a18-b06b0e66006c
export MP_CLIENT_ID=6048716701718688
export MP_CLIENT_SECRET=YUC3Q0GxRueSrVQTHidGk7bMt9MJq7Sg
```

### 2. **Usando Arquivo .env**

Crie um arquivo `.env` na raiz do projeto:

```env
# Modo: 'sandbox' para testes, 'production' para produção
MP_MODE=sandbox

# Credenciais de SANDBOX/TESTE
MP_ACCESS_TOKEN_SANDBOX=TEST-6048716701718688-080816-b095cf4abaa34073116ac070ff38e8f4-1514652489
MP_PUBLIC_KEY_SANDBOX=TEST-ce63c4af-fb50-4bef-b3dd-f0003f16cea3

# Credenciais de PRODUÇÃO
MP_ACCESS_TOKEN_PRODUCTION=APP_USR-6048716701718688-080816-ccba418de4c43b693e377903478dcd79-1514652489
MP_PUBLIC_KEY_PRODUCTION=APP_USR-145ec693-11d0-464b-8a18-b06b0e66006c
MP_CLIENT_ID=6048716701718688
MP_CLIENT_SECRET=YUC3Q0GxRueSrVQTHidGk7bMt9MJq7Sg
```

## 🔍 Verificar Configuração

### Endpoint de Status
```bash
GET /api/mercadopago/status
```

**Resposta:**
```json
{
  "success": true,
  "mode": "sandbox",
  "sandbox": true,
  "access_token": "TEST-6048716701...1514652489",
  "public_key": "TEST-ce63c4af...f0003f16cea3",
  "client_id": "6048716701718688",
  "status": "active"
}
```

## 🚨 Segurança

### ✅ **Credenciais de Teste**
- Podem ser commitadas no repositório
- Seguras para desenvolvimento
- Não processam pagamentos reais

### ⚠️ **Credenciais de Produção**
- **NUNCA** commitar no repositório
- Usar apenas variáveis de ambiente
- Processam pagamentos reais

## 🔄 Alternando Entre Modos

### Para Teste:
```bash
export MP_MODE=sandbox
```

### Para Produção:
```bash
export MP_MODE=production
```

## 📱 Frontend Flutter

O frontend Flutter detecta automaticamente o modo baseado na resposta do endpoint `/api/mercadopago/status` e ajusta a interface conforme necessário.

## 🎯 Funcionalidades

- ✅ **Checkout Mercado Pago** como forma de pagamento padrão
- ✅ **Webhook** para confirmação automática de pagamentos
- ✅ **Sistema de status** de pedidos
- ✅ **Suporte completo** para sandbox e produção
- ✅ **Configuração automática** baseada no modo
