# 🚀 API AliExpress Dropshipping

API para integração com AliExpress para dropshipping, desenvolvida em Python com Flask.

## 📋 Endpoints

### Health Check
```
GET /api/health
```

### Buscar Produtos
```
GET /api/aliexpress/products?keywords=smartphone&page=1&page_size=20
```

### Detalhes do Produto
```
GET /api/aliexpress/products/details?product_ids=1005005640660666
```

### Categorias
```
GET /api/aliexpress/categories
```

### Produtos em Alta
```
GET /api/aliexpress/hot-products?page=1&page_size=20
```

## 🔧 Configuração

1. Configure as variáveis de ambiente no arquivo `config.env`:
```
ALIEXPRESS_APP_KEY=sua_app_key
ALIEXPRESS_APP_SECRET=sua_app_secret
ALIEXPRESS_TRACKING_ID=seu_tracking_id
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a API:
```bash
python app.py
```

## 🚀 Deploy

A API está configurada para deploy no Render. O Procfile está configurado para usar `python app.py`.

## 📊 Status

- ✅ Health Check funcionando
- ✅ Busca de produtos
- ✅ Detalhes de produtos
- ✅ Categorias
- ✅ Produtos em alta

## 🔗 URL da API

https://mercadodasophia-api.onrender.com 