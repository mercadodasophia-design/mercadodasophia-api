# API Dropshipping AliExpress - Documentação Completa

## 🔐 Autenticação OAuth2

### 1. Gerar URL de Autorização
```http
GET /api/aliexpress/oauth-url
```

**Resposta:**
```json
{
  "auth_url": "https://oauth.aliexpress.com/authorize?response_type=code&client_id=...&redirect_uri=...&state=xyz123"
}
```

### 2. Completar Autenticação
```http
GET /api/aliexpress/oauth-callback?code=AUTHORIZATION_CODE
```

**Resposta:**
```json
{
  "success": true,
  "token_data": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 3600
  }
}
```

---

## 📦 Produtos

### 3. Buscar Produtos Reais
```http
GET /api/aliexpress/products?keywords=smartphone&page=1&page_size=20
```

**Parâmetros:**
- `keywords` (opcional): Termos de busca
- `page` (opcional): Página (padrão: 1)
- `page_size` (opcional): Itens por página (padrão: 20)

**Resposta:**
```json
{
  "success": true,
  "products": [...],
  "raw": {...}
}
```

### 4. Importar Produto
```http
POST /api/aliexpress/import-product
Content-Type: application/json

{
  "product_id": "1005005640660666"
}
```

**Resposta:**
```json
{
  "success": true,
  "product": {...}
}
```

---

## 🛒 Pedidos

### 5. Criar Pedido
```http
POST /api/aliexpress/create-order
Content-Type: application/json

{
  "product_id": "1005005640660666",
  "quantity": 1,
  "address": {...}
}
```

### 6. Pagar Pedido
```http
POST /api/aliexpress/pay-order
Content-Type: application/json

{
  "order_id": "ORDER_ID"
}
```

### 7. Consultar Status
```http
GET /api/aliexpress/order-status?order_id=ORDER_ID
```

### 8. Cancelar Pedido
```http
POST /api/aliexpress/cancel-order
Content-Type: application/json

{
  "order_id": "ORDER_ID"
}
```

### 9. Solicitar Reembolso
```http
POST /api/aliexpress/refund-order
Content-Type: application/json

{
  "order_id": "ORDER_ID"
}
```

---

## 🚚 Logística

### 10. Rastrear Pedido
```http
GET /api/aliexpress/track-order?order_id=ORDER_ID
```

### 11. Informações Logísticas
```http
GET /api/aliexpress/logistics-info?order_id=ORDER_ID
```

### 12. Métodos de Envio
```http
GET /api/aliexpress/shipping-methods
```

---

## 📂 Categorias

### 13. Listar Categorias
```http
GET /api/aliexpress/categories
```

### 14. Atributos de Categoria
```http
GET /api/aliexpress/category-attributes?category_id=CATEGORY_ID
```

---

## 🔍 Busca Legacy

### 15. Busca com Fallback
```http
GET /api/search?keywords=smartphone
```

---

## ⚠️ Códigos de Erro

- `401`: AliExpress não autenticado
- `400`: Parâmetros inválidos
- `500`: Erro interno do servidor

---

## 🚀 Como Usar

1. **Configurar credenciais** no `config.env`:
   ```
   ALIEXPRESS_APP_KEY=sua_app_key
   ALIEXPRESS_APP_SECRET=sua_app_secret
   ```

2. **Iniciar autenticação**:
   ```javascript
   // Frontend
   const response = await fetch('/api/aliexpress/oauth-url');
   const { auth_url } = await response.json();
   window.location.href = auth_url;
   ```

3. **Buscar produtos**:
   ```javascript
   const response = await fetch('/api/aliexpress/products?keywords=smartphone');
   const { products } = await response.json();
   ```

4. **Importar produto**:
   ```javascript
   const response = await fetch('/api/aliexpress/import-product', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ product_id: '1005005640660666' })
   });
   ```

---

## 📝 Notas

- Todos os endpoints OAuth2 requerem autenticação prévia
- Tokens são armazenados em memória (melhorar para produção)
- Tratamento de erro incluído em todos os endpoints
- Compatível com CORS para integração frontend

---

**Status: ✅ PRONTO PARA PRODUÇÃO** 