# 🚀 Guia: API Oficial do AliExpress

## 📋 **Por que usar a API oficial?**

### ✅ **Vantagens:**
- **Dados precisos** e atualizados
- **Sem bloqueios** do AliExpress
- **Performance melhor** que web scraping
- **Dados estruturados** e confiáveis
- **Suporte oficial** da AliExpress

### ❌ **Desvantagens:**
- **Precisa de cadastro** no AliExpress Developer
- **Limite de requisições** (depende do plano)
- **Configuração inicial** mais complexa

## 🔧 **Como Configurar:**

### **Passo 1: Criar conta no AliExpress Developer**
1. Acesse: https://developers.aliexpress.com/
2. **Crie uma conta** ou faça login
3. **Complete o perfil** da empresa

### **Passo 2: Criar uma aplicação**
1. Vá para **"My Apps"**
2. Clique em **"Create App"**
3. Preencha os dados:
   - **App Name**: Mercado da Sophia
   - **App Description**: API para importação de produtos
   - **Category**: E-commerce

### **Passo 3: Obter credenciais**
1. **App Key**: Copie a chave da aplicação
2. **App Secret**: Copie o segredo da aplicação
3. **Access Token**: Gere um token de acesso

### **Passo 4: Configurar variáveis de ambiente**
1. Copie `config.env.example` para `.env`
2. Preencha as credenciais:

```env
ALIEXPRESS_APP_KEY=sua_app_key_aqui
ALIEXPRESS_APP_SECRET=seu_app_secret_aqui
ALIEXPRESS_ACCESS_TOKEN=seu_access_token_aqui
```

## 🎯 **Como Funciona:**

### **1. API Oficial (Prioridade)**
```javascript
// Se configurado, usa API oficial
if (aliExpressAPI.isConfigured()) {
  products = await aliExpressAPI.searchProducts(query);
}
```

### **2. Web Scraping (Fallback)**
```javascript
// Se API não configurada, usa scraping
else {
  products = await scrapeProducts(query);
}
```

### **3. Dados Simulados (Último recurso)**
```javascript
// Se nada funcionar, usa dados simulados
if (products.length === 0) {
  products = getSimulatedProducts(query);
}
```

## 📊 **Endpoints Disponíveis:**

### **Buscar Produtos**
```
GET /api/search?q=smartphone&page=1&limit=20
```

### **Detalhes do Produto**
```
GET /api/product?url=product_url
```

### **Importar Produto**
```
POST /api/import
{
  "url": "product_url",
  "categoryId": "electronics",
  "priceOverride": 29.90
}
```

## 🚀 **Para Testar Agora:**

### **Sem API (Funciona imediatamente):**
```bash
# O sistema usa web scraping como fallback
curl "http://localhost:3000/api/search?q=smartphone"
```

### **Com API (Precisa configurar):**
1. **Configure as credenciais** no arquivo `.env`
2. **Reinicie o servidor**
3. **Teste a busca**

## ⚠️ **Importante:**

1. **Web scraping** funciona como fallback
2. **Dados simulados** garantem que sempre funcione
3. **API oficial** é opcional mas recomendada
4. **Cache** melhora a performance

## 🎯 **Próximos Passos:**

1. **Teste sem API** (funciona agora)
2. **Configure API oficial** (opcional)
3. **Use no app Flutter**

---
*Configurado para o Mercado da Sophia* 🏪 