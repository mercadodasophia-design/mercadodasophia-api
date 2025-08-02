# 🚀 API Express - Mercado da Sophia

API para integração com AliExpress e gestão de produtos do Mercado da Sophia.

## 📋 Funcionalidades

### 🔍 **Busca de Produtos**
- Busca por termo no AliExpress
- Filtros por categoria, preço, avaliação
- Paginação e ordenação
- Cache inteligente (30 minutos)

### 📦 **Importação de Produtos**
- Importação individual por URL
- Importação em lote (múltiplas URLs)
- Processamento automático de dados
- Multiplicador de preços configurável

### 📊 **Estatísticas e Monitoramento**
- Estatísticas da API em tempo real
- Cache de produtos
- Uptime e uso de memória
- Logs detalhados

## 🛠️ Instalação

### **Pré-requisitos**
- Node.js 16+
- npm ou yarn

### **1. Instalar dependências**
```bash
cd api-express
npm install
```

### **2. Configurar variáveis de ambiente**
Crie um arquivo `.env` na raiz do projeto:
```env
PORT=3000
NODE_ENV=development
```

### **3. Iniciar servidor**
```bash
# Desenvolvimento
npm run dev

# Produção
npm start

# Windows (script automático)
start-api.bat
```

## 📚 Endpoints da API

### **Busca de Produtos**
```http
GET /api/search?q=smartphone&sort=rating&page=1&limit=20
```

**Parâmetros:**
- `q` (obrigatório): Termo de busca
- `sort`: Ordenação (rating, price, sales)
- `page`: Número da página
- `limit`: Limite de produtos (máx: 50)

**Resposta:**
```json
{
  "query": "smartphone",
  "total": 20,
  "page": 1,
  "sort": "rating",
  "products": [
    {
      "id": "prod-1",
      "name": "Smartphone Case Premium",
      "price": "R$ 15,90",
      "originalPrice": "R$ 29,90",
      "rating": "4.8",
      "reviewsCount": "2.5k",
      "salesCount": "15.2k",
      "image": "https://...",
      "url": "https://www.aliexpress.com/item/...",
      "shipping": "Frete grátis",
      "store": "TechStore Official",
      "aliexpressId": "123456789"
    }
  ]
}
```

### **Detalhes do Produto**
```http
GET /api/product?url=https://www.aliexpress.com/item/123456789.html
```

**Resposta:**
```json
{
  "id": "123456789",
  "name": "Smartphone Case Premium - Ultra Protection",
  "price": "R$ 15,90",
  "originalPrice": "R$ 29,90",
  "rating": "4.8",
  "reviewsCount": "2.5k reviews",
  "salesCount": "15.2k sold",
  "images": ["https://...", "https://..."],
  "description": "Case premium para smartphone...",
  "specifications": {
    "Material": "Silicone Premium",
    "Compatibilidade": "iPhone 13/14/15"
  },
  "shipping": "Frete grátis - Entrega em 15-30 dias",
  "store": "TechStore Official",
  "url": "https://www.aliexpress.com/item/123456789.html",
  "aliexpressId": "123456789"
}
```

### **Importação Individual**
```http
POST /api/import
Content-Type: application/json

{
  "url": "https://www.aliexpress.com/item/123456789.html",
  "categoryId": "electronics",
  "priceOverride": 25.90,
  "stockQuantity": 50
}
```

### **Importação em Lote**
```http
POST /api/import/bulk
Content-Type: application/json

{
  "urls": [
    "https://www.aliexpress.com/item/123456789.html",
    "https://www.aliexpress.com/item/987654321.html"
  ],
  "categoryId": "electronics",
  "priceMultiplier": 1.5
}
```

### **Produtos em Tendência**
```http
GET /api/trending
```

### **Categorias**
```http
GET /api/categories
```

### **Estatísticas**
```http
GET /api/stats
```

## 🔧 Configurações Avançadas

### **Cache**
- Duração: 30 minutos
- Limpeza automática
- Cache por URL e busca

### **Rate Limiting**
- 1 segundo entre requisições
- Timeout: 10-15 segundos
- Headers de navegador simulados

### **Tratamento de Erros**
- Fallback para dados simulados
- Logs detalhados
- Timeout configurável

## 📊 Monitoramento

### **Logs**
```bash
# Logs de busca
🔍 Searching for: smartphone (page: 1, sort: rating)

# Logs de importação
📦 Importing product: https://www.aliexpress.com/item/...

# Logs de cache
📦 Returning cached results
```

### **Estatísticas**
```json
{
  "cacheSize": 15,
  "uptime": 3600,
  "memory": {
    "heapUsed": 52428800,
    "heapTotal": 104857600
  },
  "timestamp": "2024-01-08T15:30:45.123Z"
}
```

## 🚀 Deploy

### **Local**
```bash
npm start
```

### **Produção**
```bash
# PM2
pm2 start server.js --name "mercadodasophia-api"

# Docker
docker build -t mercadodasophia-api .
docker run -p 3000:3000 mercadodasophia-api
```

### **Heroku**
```bash
git push heroku main
```

## 🔒 Segurança

- **Helmet**: Headers de segurança
- **CORS**: Configurado para desenvolvimento
- **Rate Limiting**: Proteção contra spam
- **Input Validation**: Validação de parâmetros

## 🐛 Troubleshooting

### **Erro de Timeout**
```bash
# Aumentar timeout no código
timeout: 30000 // 30 segundos
```

### **Erro de Conexão**
```bash
# Verificar se o AliExpress está acessível
curl -I https://www.aliexpress.com
```

### **Cache não funcionando**
```bash
# Limpar cache
node -e "console.log('Cache cleared')"
```

## 📞 Suporte

- **Email**: contato@mercadodasophia.com
- **Issues**: GitHub Issues
- **Documentação**: Este README

---

**Desenvolvido com ❤️ pela equipe do Mercado da Sophia** 