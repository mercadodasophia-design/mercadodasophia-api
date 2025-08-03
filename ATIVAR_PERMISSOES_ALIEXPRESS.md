# 🔓 ATIVAR PERMISSÕES ALIEXPRESS OPEN PLATFORM

## 🚨 PROBLEMA ATUAL
A API está retornando: `App does not have permission to access this api`

## ✅ SOLUÇÃO: ATIVAR PERMISSÕES

### 1. Acessar AliExpress Open Platform
- Vá para: https://developers.aliexpress.com/
- Faça login com sua conta

### 2. Encontrar sua Aplicação
- Vá em "My Apps" ou "Minhas Aplicações"
- Procure pela aplicação com App Key: `517616`

### 3. Ativar APIs Necessárias
Na sua aplicação, você precisa ativar estas APIs:

#### 📋 APIs OBRIGATÓRIAS:
- **aliexpress.ds.product.get** - Buscar produtos
- **aliexpress.ds.product.details.get** - Detalhes de produtos  
- **aliexpress.ds.category.get** - Categorias
- **aliexpress.ds.hotproduct.get** - Produtos em alta
- **aliexpress.ds.affiliate.link.generate** - Links de afiliado

### 4. Como Ativar:
1. Clique na sua aplicação
2. Vá em "API Management" ou "Gerenciamento de API"
3. Procure por cada API na lista acima
4. Clique em "Activate" ou "Ativar" para cada uma
5. Aguarde a aprovação (pode levar algumas horas)

### 5. Verificar Status
- Após ativar, o status deve mudar de "Pending" para "Active"
- Só então a API funcionará

## 🧪 TESTE APÓS ATIVAÇÃO

Quando as permissões estiverem ativas, teste com:

```bash
python test_api.py
```

## 📞 SUPORTE
Se não conseguir ativar, entre em contato com o suporte do AliExpress Open Platform.

## 🎯 RESULTADO ESPERADO
Após ativar as permissões, a API deve retornar produtos reais do AliExpress! 