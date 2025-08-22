# AliExpress API Documentation

## 📋 Visão Geral
Este documento descreve a estrutura de dados retornada pela API do AliExpress para integração com o sistema de dropshipping.

## 🔗 Endpoints Principais

### `/api/aliexpress/feeds/complete`
**Método:** GET  
**Descrição:** Retorna feeds completos com produtos detalhados usando o fluxo de 3 etapas.

**Parâmetros:**
- `page` (int): Número da página (padrão: 1)
- `page_size` (int): Produtos por página (padrão: 1)
- `max_feeds` (int): Máximo de feeds a processar (padrão: 1)

**Exemplo de uso:**
```
https://service-api-aliexpress.mercadodasophia.com.br/api/aliexpress/feeds/complete?page=1&page_size=100&max_feeds=3
```

## 📊 Estrutura da Resposta

### Estrutura Principal
```json
{
  "success": true,
  "timestamp": "2025-08-22T15:33:37.287186",
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_feeds": 3
  },
  "feeds": [
    {
      "feed_id": "1",
      "feed_name": "AEB_ SummerProducts_EG",
      "display_name": "AEB_ SummerProducts_EG",
      "description": "AEB_ SummerProducts_EG",
      "product_count": 16322,
      "item_ids": {
        "PRODUCT_ID": { DADOS_COMPLETOS }
      },
      "products": [
        {
          "product_id": "1005009135748244",
          "title": "Título do produto",
          "price": "42.79",
          "currency": "BRL",
          "main_image": "URL da imagem"
        }
      ],
      "products_found": 1
    }
  ]
}
```

## 🎯 Campos Essenciais para Dropshipping

### 1. Informações Básicas do Produto
**Localização:** `ae_item_base_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `subject` | string | Título do produto | "Mulheres chinelos coloridos..." |
| `product_id` | int | ID único do AliExpress | 1005009135748244 |
| `avg_evaluation_rating` | string | Avaliação média | "5.0" |
| `evaluation_count` | string | Número de avaliações | "6" |
| `sales_count` | string | Quantidade vendida | "31" |
| `product_status_type` | string | Status do produto | "onSelling" |
| `currency_code` | string | Moeda original | "CNY" |

### 2. Informações de Preço
**Localização:** `ae_item_sku_info_dtos.ae_item_sku_info_d_t_o[]`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `offer_sale_price` | string | Preço de venda atual | "42.79" |
| `sku_price` | string | Preço original | "91.04" |
| `offer_bulk_sale_price` | string | Preço para compra em massa | "42.79" |
| `currency_code` | string | Moeda | "BRL" |
| `price_include_tax` | boolean | Se inclui impostos | false |

### 3. Imagens
**Localização:** `ae_multimedia_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `image_urls` | string | URLs separadas por ponto e vírgula | "https://ae01.alicdn.com/kf/...;https://..." |

**Localização:** `ae_item_sku_info_dtos.ae_item_sku_info_d_t_o[].ae_sku_property_dtos.ae_sku_property_d_t_o[].sku_image`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `sku_image` | string | Imagem específica da variação | "https://ae01.alicdn.com/kf/..." |

### 4. Estoque e Variações
**Localização:** `ae_item_sku_info_dtos.ae_item_sku_info_d_t_o[]`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `sku_available_stock` | int | Estoque disponível | 67 |
| `sku_id` | string | ID da variação | "12000048043155838" |
| `buy_amount_limit_set_by_promotion` | string | Limite de compra | "5" |
| `sku_bulk_order` | int | Quantidade mínima para desconto | 2 |

**Variações:** `ae_sku_property_d_t_o[]`
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `sku_property_name` | string | Nome da propriedade | "cor" |
| `sku_property_value` | string | Valor da propriedade | "Bege" |
| `property_value_id` | int | ID do valor | 771 |

### 5. Informações da Loja
**Localização:** `ae_store_info`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `store_name` | string | Nome da loja | "BFCCQB Official Store" |
| `store_id` | int | ID da loja | 1103573036 |
| `store_country_code` | string | País da loja | "CN" |
| `communication_rating` | string | Avaliação da comunicação | "4.6" |
| `item_as_described_rating` | string | Avaliação do produto | "4.5" |
| `shipping_speed_rating` | string | Avaliação do frete | "4.7" |

### 6. Informações de Entrega
**Localização:** `logistics_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `delivery_time` | int | Tempo de entrega em dias | 7 |
| `ship_to_country` | string | País de destino | "BR" |

### 7. Informações do Pacote
**Localização:** `package_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `gross_weight` | string | Peso bruto em kg | "0.670" |
| `package_length` | int | Comprimento em cm | 30 |
| `package_width` | int | Largura em cm | 20 |
| `package_height` | int | Altura em cm | 10 |
| `package_type` | boolean | Tipo de pacote | false |
| `product_unit` | int | Unidade do produto | 100000013 |

### 8. Propriedades do Produto
**Localização:** `ae_item_properties.ae_item_property[]`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `attr_name` | string | Nome do atributo | "Nome da marca" |
| `attr_value` | string | Valor do atributo | "BFCCQB" |
| `attr_name_id` | int | ID do nome do atributo | 2 |
| `attr_value_id` | int | ID do valor do atributo | 1981179452 |

### 9. Categorização
**Localização:** `ae_item_base_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `category_id` | int | ID da categoria | 200001004 |

### 10. Conteúdo para SEO/Marketing
**Localização:** `ae_item_base_info_dto`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `detail` | string | Descrição HTML completa | "<div class=\"detailmodule_html\">..." |
| `mobile_detail` | string | Descrição para mobile | "{\"version\":\"2.0.0\",\"moduleList\":[...]}" |

## 🔄 Fluxo de 3 Etapas

### ETAPA 1: Buscar Nomes dos Feeds
- **Método:** `aliexpress.ds.feedname.get`
- **Resultado:** Lista de feeds disponíveis

### ETAPA 2: Buscar IDs dos Produtos
- **Método:** `aliexpress.ds.feed.itemids.get`
- **Parâmetros:** `feed_name`, `page_size`, `page_no`
- **Resultado:** Lista de IDs de produtos no feed

### ETAPA 3: Buscar Detalhes dos Produtos
- **Método:** `aliexpress.ds.product.get`
- **Parâmetros:** `product_id`, `ship_to_country`, `target_currency`, `target_language`
- **Resultado:** Dados completos de cada produto

## ⚠️ Limitações e Considerações

### Timeouts
- **Worker Timeout:** 30 segundos no Cloud Run
- **Request Timeout:** 5 segundos por requisição individual
- **Limites Seguros:** 1 feed, 1 produto por página para evitar timeouts

### Paginação
- **AliExpress Limite:** Máximo 8 produtos por página na API
- **Recomendação:** Usar `page_size=8` para melhor performance

### Estrutura de Dados
- **Formato:** `feedName{ idProduct{ DADOS} }`
- **Cache:** Implementar cache local para produtos já carregados
- **Incremental:** Usar paginação para carregar mais produtos

## 🚀 Próximos Passos

1. **Aumentar Limites:** Gradualmente aumentar `page_size` e `max_feeds`
2. **Interface Admin:** Criar UI para visualizar feeds
3. **Sincronização Firebase:** Implementar salvamento automático
4. **Sistema de Preços:** Calcular preços para dropshipping
5. **Cache Local:** Implementar cache para performance

## 📝 Notas de Implementação

- Sempre verificar tokens antes de fazer requisições
- Implementar retry automático para falhas de rede
- Logs detalhados para debug (ETAPA 1, 2, 3)
- Estrutura modular para facilitar manutenção
- Validação de dados antes de salvar no Firebase
