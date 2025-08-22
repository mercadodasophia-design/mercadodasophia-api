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

- DEBUG DO RESULTADO

{
  "feeds": [
    {
      "description": "AEB_ SummerProducts_EG",
      "display_name": "AEB_ SummerProducts_EG",
      "feed_id": "1",
      "feed_name": "AEB_ SummerProducts_EG",
      "item_ids": {
        "1005009135748244": {
          "ae_item_base_info_dto": {
            "avg_evaluation_rating": "5.0",
            "category_id": 200001004,
            "currency_code": "CNY",
            "detail": "\u003Cdiv class=\"detailmodule_html\"\u003E\u003Cdiv class=\"detail-desc-decorate-richtext\"\u003E\u003Cp style=\"text-align:left;margin:0;\"\u003E\u003Cimg data-id=\"ckeditor_img46\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/S54f8dee7dc1249c8a7c2663d8dd5edf3T.jpg?width=1340&height=1668&hash=3008\" style=\"width: 1340px; height: 1668px;\"\u003E\u003Cimg data-id=\"ckeditor_img47\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/Scc703fe827aa414dbbdbbb8d90f437b2I.jpg?width=1340&height=1340&hash=2680\" style=\"width: 1340px; height: 1340px;\"\u003E\u003Cimg data-id=\"ckeditor_img48\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/Saff5a95871b14ca9b66c46c41c5f8819p.jpg?width=1340&height=1340&hash=2680\" style=\"width: 1340px; height: 1340px;\"\u003E\u003Cimg data-id=\"ckeditor_img49\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/Sb22caa0ec77a478993487953cca8520dV.jpg?width=1343&height=1340&hash=2683\" style=\"width: 1343px; height: 1340px;\"\u003E\u003Cimg data-id=\"ckeditor_img50\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/S7afb7530c5464203bddafe535725c1a9j.jpg?width=1340&height=1340&hash=2680\" style=\"width: 1340px; height: 1340px;\"\u003E\u003Cimg data-id=\"ckeditor_img51\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/Sf203fada1db94898bf6f68aa55670e74l.jpg?width=1340&height=1340&hash=2680\" style=\"width: 1340px; height: 1340px;\"\u003E\u003Cimg data-id=\"ckeditor_img52\" referrerpolicy=\"no-referrer\" src=\"https://ae01.alicdn.com/kf/S74b03c80a3a64fe392116708b1d60ab7m.jpg?width=1340&height=1340&hash=2680\" style=\"width: 1340px; height: 1340px;\"\u003E\u003C/p\u003E\n\u003C/div\u003E\u003C/div\u003E\r\n",
            "evaluation_count": "6",
            "mobile_detail": "{\"version\":\"2.0.0\",\"moduleList\":[{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sd3337942abdb4e51b8c0710c409a948cw.jpg\",\"style\":{\"width\":1340,\"height\":1668}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sedff69e7bb3d42799743f51901fdbd8db.jpg\",\"style\":{\"width\":1340,\"height\":1340}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sabedf6cdd5494d028c34ad78611eaec3a.jpg\",\"style\":{\"width\":1340,\"height\":1340}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sefb08ffb95394a3aa4d8b43f0094c027E.jpg\",\"style\":{\"width\":1343,\"height\":1340}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S93cb9ae464d54abfb420f5efa4d428262.jpg\",\"style\":{\"width\":1340,\"height\":1340}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S1c46a6fc07e54782b1a50db7bf96e4909.jpg\",\"style\":{\"width\":1340,\"height\":1340}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S56ccd1a8d93944f3a6415e58492b7c5eY.jpg\",\"style\":{\"width\":1340,\"height\":1340}}}]}",
            "product_id": 1005009135748244,
            "product_status_type": "onSelling",
            "sales_count": "31",
            "subject": "Mulheres chinelos coloridos doces listra designer chinelos sola grossa sapatos 2025 nova praia ao ar livre estilo casual sandálias slides feminino"
          },
          "ae_item_properties": {
            "ae_item_property": [
              {
                "attr_name": "tenis de mujer",
                "attr_name_id": -1,
                "attr_value": "zapatos para mujeres",
                "attr_value_id": -1
              },
              {
                "attr_name": "zapatillas de mujer",
                "attr_name_id": -1,
                "attr_value": "shoes for woman",
                "attr_value_id": -1
              },
              {
                "attr_name": "shoesfor women",
                "attr_name_id": -1,
                "attr_value": "zapatillas de hombre",
                "attr_value_id": -1
              },
              {
                "attr_name": "sandalias de mujer verano 2024",
                "attr_name_id": -1,
                "attr_value": "chanclas",
                "attr_value_id": -1
              },
              {
                "attr_name": "Flip flops",
                "attr_name_id": -1,
                "attr_value": "heeled sandals",
                "attr_value_id": -1
              },
              {
                "attr_name": "tenis para hombre",
                "attr_name_id": -1,
                "attr_value": "tacones",
                "attr_value_id": -1
              },
              {
                "attr_name": "sandalias planas",
                "attr_name_id": -1,
                "attr_value": "zapatos mujer",
                "attr_value_id": -1
              },
              {
                "attr_name": "Women heels",
                "attr_name_id": -1,
                "attr_value": "shoes woman 2024 trend",
                "attr_value_id": -1
              },
              {
                "attr_name": "summer shoes women",
                "attr_name_id": -1,
                "attr_value": "Slippers women",
                "attr_value_id": -1
              },
              {
                "attr_name": "summer Slippers women",
                "attr_name_id": -1,
                "attr_value": "women Slippers",
                "attr_value_id": -1
              },
              {
                "attr_name": "Elemento de moda",
                "attr_name_id": 200000876,
                "attr_value": "Plataforma",
                "attr_value_id": 200004405
              },
              {
                "attr_name": "Nome da marca",
                "attr_name_id": 2,
                "attr_value": "BFCCQB",
                "attr_value_id": 1981179452
              },
              {
                "attr_name": "Nome do departamento",
                "attr_name_id": 200000043,
                "attr_value": "Adult",
                "attr_value_id": 4100
              },
              {
                "attr_name": "Material da sola",
                "attr_name_id": 200001154,
                "attr_value": "RUBBER",
                "attr_value_id": 123
              },
              {
                "attr_name": "Tipo de modelo",
                "attr_name_id": 200000329,
                "attr_value": "Sólida",
                "attr_value_id": 200001248
              },
              {
                "attr_name": "Estação",
                "attr_name_id": 281,
                "attr_value": "Verão",
                "attr_value_id": 366077
              },
              {
                "attr_name": "Altura do salto",
                "attr_name_id": 200000479,
                "attr_value": "Med (3 cm-5 cm)",
                "attr_value_id": 202115810
              },
              {
                "attr_name": "Material do Forro",
                "attr_name_id": 100004114,
                "attr_value": "NONE",
                "attr_value_id": 200003454
              },
              {
                "attr_name": "Método fixação superior",
                "attr_name_id": 400024206,
                "attr_value": "Outros (preencher por si mesmo)",
                "attr_value_id": 1982207216
              },
              {
                "attr_name": "Local de Aplicação",
                "attr_name_id": 200000874,
                "attr_value": "lado externo",
                "attr_value_id": 202225810
              },
              {
                "attr_name": "Sexo",
                "attr_name_id": 284,
                "attr_value": "Mulheres",
                "attr_value_id": 100006040
              },
              {
                "attr_name": "CN",
                "attr_name_id": 266081643,
                "attr_value": "Zhejiang",
                "attr_value_id": 100015203
              },
              {
                "attr_name": "Estilo",
                "attr_name_id": 326,
                "attr_value": "Conciso",
                "attr_value_id": 200004431
              },
              {
                "attr_name": "Tipo de Fecho",
                "attr_name_id": 200001153,
                "attr_value": "Puxe Em",
                "attr_value_id": 1981792210
              },
              {
                "attr_name": "Origem",
                "attr_name_id": 219,
                "attr_value": "CN (Origem)",
                "attr_value_id": 9441741844
              },
              {
                "attr_name": "Material de alta qualidade",
                "attr_name_id": 20698,
                "attr_value": "Plutônio",
                "attr_value_id": 452
              },
              {
                "attr_name": "Tipo de Item",
                "attr_name_id": 200000137,
                "attr_value": "Sapatilhas",
                "attr_value_id": 200002446
              },
              {
                "attr_name": "Número do modelo",
                "attr_name_id": 3,
                "attr_value": "shoes women",
                "attr_value_id": -1
              },
              {
                "attr_name": "Químico Hign-em causa",
                "attr_name_id": 400000603,
                "attr_value": "Nenhum",
                "attr_value_id": 23399591357
              },
              {
                "attr_name": "Tipo de salto",
                "attr_name_id": 200000480,
                "attr_value": "Plano com",
                "attr_value_id": 200004386
              },
              {
                "attr_name": "Ajuste",
                "attr_name_id": 200044261,
                "attr_value": "Se ajusta ao tamanho, use sei tamanho normal",
                "attr_value_id": 201632808
              },
              {
                "attr_name": "Com plataformas",
                "attr_name_id": 200001756,
                "attr_value": "Não",
                "attr_value_id": 349906
              },
              {
                "attr_name": "Material da palmilha",
                "attr_name_id": 20700,
                "attr_value": "Plutônio",
                "attr_value_id": 452
              },
              {
                "attr_name": "Tipo de sapato",
                "attr_name_id": 200198261,
                "attr_value": "Básico",
                "attr_value_id": 200000908
              }
            ]
          },
          "ae_item_sku_info_dtos": {
            "ae_item_sku_info_d_t_o": [
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 200000333,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "35"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:200000333",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:200000333",
                "sku_available_stock": 67,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155838",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 200000334,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "36"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:200000334",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:200000334",
                "sku_available_stock": 65,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155839",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 200000333,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "35"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:200000333",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:200000333",
                "sku_available_stock": 64,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155846",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 200000334,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "36"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:200000334",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:200000334",
                "sku_available_stock": 67,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155847",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 100010483,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "41"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:100010483",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:100010483",
                "sku_available_stock": 66,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155844",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 200000337,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "42"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:200000337",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:200000337",
                "sku_available_stock": 67,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155845",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 200000364,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "39"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:200000364",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:200000364",
                "sku_available_stock": 66,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155842",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 100013888,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "40"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:100013888",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:100013888",
                "sku_available_stock": 66,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155843",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 100010482,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "37"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:100010482",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:100010482",
                "sku_available_stock": 66,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155840",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 771,
                      "sku_image": "https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Bege"
                    },
                    {
                      "property_value_id": 200000898,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "38"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:771;200000124:200000898",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:771;200000124:200000898",
                "sku_available_stock": 67,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155841",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 100010483,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "41"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:100010483",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:100010483",
                "sku_available_stock": 65,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155852",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 200000337,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "42"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:200000337",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:200000337",
                "sku_available_stock": 67,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155853",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 200000364,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "39"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:200000364",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:200000364",
                "sku_available_stock": 62,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155850",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 100013888,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "40"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:100013888",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:100013888",
                "sku_available_stock": 64,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155851",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 100010482,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "37"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:100010482",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:100010482",
                "sku_available_stock": 65,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155848",
                "sku_price": "91.04"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 1052,
                      "sku_image": "https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Rosa"
                    },
                    {
                      "property_value_id": 200000898,
                      "sku_property_id": 200000124,
                      "sku_property_name": "Tamanho do sapato",
                      "sku_property_value": "38"
                    }
                  ]
                },
                "buy_amount_limit_set_by_promotion": "5",
                "currency_code": "BRL",
                "id": "14:1052;200000124:200000898",
                "offer_bulk_sale_price": "42.79",
                "offer_sale_price": "42.79",
                "price_include_tax": false,
                "sku_attr": "14:1052;200000124:200000898",
                "sku_available_stock": 66,
                "sku_bulk_order": 2,
                "sku_id": "12000048043155849",
                "sku_price": "91.04"
              }
            ]
          },
          "ae_multimedia_info_dto": {
            "image_urls": "https://ae01.alicdn.com/kf/S8e390a3d1abe4bf4b6ab8eb52f30ca67H.jpg;https://ae01.alicdn.com/kf/S7b7597f1b0f742808f79fb91250d3f919.jpg;https://ae01.alicdn.com/kf/S38637254f3ca4f208d51fd8d2854de6bK.jpg;https://ae01.alicdn.com/kf/Sce6f867047d94f01b7ad2c150feecab1p.jpg;https://ae01.alicdn.com/kf/S69011659fa104b9781509e04f6e5fbc2F.jpg;https://ae01.alicdn.com/kf/S6f257c7bba0e4fa0b20be4abea503e8b7.jpg"
          },
          "ae_store_info": {
            "communication_rating": "4.6",
            "item_as_described_rating": "4.5",
            "shipping_speed_rating": "4.7",
            "store_country_code": "CN",
            "store_id": 1103573036,
            "store_name": "BFCCQB Official Store"
          },
          "has_whole_sale": false,
          "logistics_info_dto": {
            "delivery_time": 7,
            "ship_to_country": "BR"
          },
          "package_info_dto": {
            "gross_weight": "0.670",
            "package_height": 10,
            "package_length": 30,
            "package_type": false,
            "package_width": 20,
            "product_unit": 100000013
          },
          "product_id_converter_result": {
            "main_product_id": 1005009135748244,
            "sub_product_id": "{\"US\":3256808949433492}"
          }
        }
      },
      "product_count": 16322,
      "products": [
        {
          "currency": "BRL",
          "main_image": "",
          "price": "0.00",
          "product_id": "1005009135748244",
          "title": ""
        }
      ],
      "products_found": 1
    },
    {
      "description": "AEB_AU_EbestSelectedItems_20240925",
      "display_name": "AEB_AU_EbestSelectedItems_20240925",
      "feed_id": "2",
      "feed_name": "AEB_AU_EbestSelectedItems_20240925",
      "item_ids": {
        "1005005454292177": {
          "ae_item_base_info_dto": {
            "avg_evaluation_rating": "4.8",
            "category_id": 440504,
            "currency_code": "CNY",
            "detail": "\u003Cdiv class=\"detailmodule_html\"\u003E\u003Cdiv class=\"detail-desc-decorate-richtext\"\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/Sc0b448160167430ab133b606f06be9f6M.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EExcelente qualidade 20W PD Carregamento rápido\u003C/p\u003E\u003Cdiv\u003E\u003Cimg style=\"margin-bottom:10px\" class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S1d067d52c78c4cca9773bd0fd41f87d3k.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S7bcabf1cc8e343ffaf0f48616105ea29p.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003E3X mais rápido, proteção da bateria\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EProjetado para carregamento rápido de dispositivos da série Apple 8-13\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S09bdc8594ee24591a63b6e86c9eb449dt.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003ECarregamento rápido Apple 13 Pro Max em velocidade total\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EO uso com um carregador Baseus 30W PD pode maximizar a potência de saída para 27W para seus telefones, tablets e Switches\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/Sb3cc766be2ee4b3ab613cc7b59f64e5au.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EPower-up em um Jiffy para seus tablets\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EBom para telefones e tablets, satisfazendo todas as suas necessidades de carregamento\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S89b028b51e5c4534b8098a62aeecdbb04.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EAntioxidante com maior durabilidade\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EO revestimento antioxidante protetor garante qualidade e durabilidade\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S8a730f883b034fadab8fbbf5c745a2461.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EMais que durável\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EMateriais e tecnologia atualizados\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S7de378651d6342938dc3ae1c79e73532b.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003ECarregamento estável sem superaquecimento\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EExcelente dissipação de calor oferece uma experiência de carregamento mais segura e suave.\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S4063064fe5964a28b9dcfd2c53e5a8c6z.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EDesign resistente a arranhões para proteger seu telefone\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EO design especial garante que não haja arranhões ao conectar e desconectar\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S34ddddd75ad140528a1f6aaefb2b15ddP.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003EAlta compatibilidade com vários dispositivos\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003ECarregamento rápido PD\u003Cbr\u003E\u003Cbr\u003ETelefones: 13/13 Pro/13 Pro Max/13 mini、12/12 Pro/12 Pro Max/12 mini、SE2/11/11 Pro/11 Max、Xs/Xs Max/XR/X、8/8 Plus\u003Cbr\u003ETablets: Novo Pad 9、Pad Pro 12,9 polegadas (segunda geração),Pad Pro 10,5 polegadas、Pad Air3 10,5 polegadas、Pad Mini5 7,9 polegadas\u003Cbr\u003E\u003Cbr\u003ECarregamento padrão\u003Cbr\u003E\u003Cbr\u003ETelefones:7/7 Plus、6s/6s Plus/6/6 Plus\u003Cbr\u003ETablets: Pad Pro 12.9 (primeira geração), Pad Pro 9,7 polegadas, Pad 9,7 polegadas, Pad mini 7,9 polegadas\u003Cbr\u003EOutros: Pods (Terceira Geração), Pods (Segunda Geração), Pods Pro、Pod touch\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S34f1fdeaf0164adda69a92bf9e56d078N.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cp style=\"font-family:OpenSans;font-size:20px;font-weight:900;line-height:28px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-title\"\u003ECarregamento e transmissão de dados, igualmente rápido\u003C/p\u003E\u003Cp style=\"font-family:OpenSans;font-size:14px;font-weight:300;line-height:20px;white-space:pre-wrap;color:rgb(0, 0, 0);margin-bottom:12px\" class=\"detail-desc-decorate-content\"\u003EVelocidade de transmissão de até 480 Mbps, 24 segundos por um gigabyte\u003C/p\u003E\u003Cdiv\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S6832e9d56a7841228ad811c66491fe24x.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"detailmodule_text-image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S382f8c613af447c4a41e9bcc36e7edeaK.jpg\" slate-data-type=\"image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/Sbc630f12b6754331aeb02d016ac2266eF.jpg\" slate-data-type=\"image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S5fdfaec839224e758ffab6e3d9b2b261Z.jpg\" slate-data-type=\"image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/See24350a83504445905af38d9468f48cx.jpg\" slate-data-type=\"image\"\u003E\u003Cimg class=\"detail-desc-decorate-image\" src=\"https://ae01.alicdn.com/kf/S3afbb4e1ebdf48cba61b3535360bc090c.jpg\" slate-data-type=\"image\"\u003E\u003C/div\u003E\u003Cp\u003E\u003Cbr\u003E\u003C/p\u003E\u003C/div\u003E\u003C/div\u003E\r\n",
            "evaluation_count": "38",
            "mobile_detail": "{\"version\":\"2.0.0\",\"moduleList\":[{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sc0b448160167430ab133b606f06be9f6M.jpg\",\"style\":{\"width\":930,\"height\":300}}},{\"type\":\"text\",\"data\":{\"content\":\"Carregamento rápido PD de 20 W de excelente qualidade\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S1d067d52c78c4cca9773bd0fd41f87d3k.jpg\",\"style\":{\"width\":930,\"height\":1417,\"paddingBottom\":10}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S7bcabf1cc8e343ffaf0f48616105ea29p.jpg\",\"style\":{\"width\":930,\"height\":745}}},{\"type\":\"text\",\"data\":{\"content\":\"3X mais rápido, proteção de bateria\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Projetado para carregamento rápido de dispositivos da série Apple 8-13\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S09bdc8594ee24591a63b6e86c9eb449dt.jpg\",\"style\":{\"width\":930,\"height\":1751}}},{\"type\":\"text\",\"data\":{\"content\":\"Carregamento rápido Apple 13 Pro Max em uma velocidade total\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Use com um carregador Baseus 30W PD pode maximizar a saída de energia de 27W para seus telefones, tablets e Switches\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sb3cc766be2ee4b3ab613cc7b59f64e5au.jpg\",\"style\":{\"width\":930,\"height\":1498}}},{\"type\":\"text\",\"data\":{\"content\":\"Continue em um Jiffy para seus tablets\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Bom para telefones e tablets, satisfaziando todas as suas necessidades de carregamento\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S89b028b51e5c4534b8098a62aeecdbb04.jpg\",\"style\":{\"width\":930,\"height\":1438}}},{\"type\":\"text\",\"data\":{\"content\":\"Antioxidante com durabilidade mais longa\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"O revestimento protetor antioxidante garante qualidade e durabilidade\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S8a730f883b034fadab8fbbf5c745a2461.jpg\",\"style\":{\"width\":930,\"height\":2073}}},{\"type\":\"text\",\"data\":{\"content\":\"Mais do que durável\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Materiais e tecnologia atualizados\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S7de378651d6342938dc3ae1c79e73532b.jpg\",\"style\":{\"width\":930,\"height\":1764}}},{\"type\":\"text\",\"data\":{\"content\":\"Carregamento estável sem superaquecimento\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Excelente dissipação de calor oferece uma experiência de carregamento mais segura e mais suave.\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S4063064fe5964a28b9dcfd2c53e5a8c6z.jpg\",\"style\":{\"width\":930,\"height\":2043}}},{\"type\":\"text\",\"data\":{\"content\":\"Design resistente a arranhões para proteger seu telefone\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"O design especial não garante arranhões quando você plug and desplugue\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S34ddddd75ad140528a1f6aaefb2b15ddP.jpg\",\"style\":{\"width\":930,\"height\":1541}}},{\"type\":\"text\",\"data\":{\"content\":\"Alta compatibilidade com vários dispositivos\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Carregamento rápido PD\\n\\nTelefones:13/13 Pro/13 Pro Max/13 mini、12/12 Pro/12 Pro Max/12 mini、SE2/11/11 Pro/11 Pro Max、Xs/Xs Max/XR/X、8/8 Plus\\nTablets: Novo Pad 9、 Pad Pro 12,9 polegadas (segundo GenislavPad Pro 10,5 polegadas, Pad Air3 10,5 polegadas, Pad Mini5 7,9 polegadas\\n\\nCarregamento padrão\\n\\nTelefones: 7/7 Plus、 6s/6s Plus/6/6 Plus\\nTablets: Pad Pro 12,9 (primeiro GenislavPad Pro 9,7 polegadas, Pad 9,7 polegadas, Pad mini 7,9 polegadas\\nOutros:Pods (Tecima Genza SimezPods (segundo Gen SimezPods Pro、Pod touch\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S34f1fdeaf0164adda69a92bf9e56d078N.jpg\",\"style\":{\"width\":930,\"height\":1793}}},{\"type\":\"text\",\"data\":{\"content\":\"Carregamento e transmissão de dados, equalmente rápido\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":16,\"fontWeight\":\"bold\",\"align\":\"left\",\"color\":\"#000000\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"text\",\"data\":{\"content\":\"Velocidade de transmissão de até 480Mbps, 24 segundos por um gigabyte\",\"style\":{\"paddingLeft\":16,\"paddingRight\":16,\"paddingTop\":10,\"paddingBottom\":10,\"fontSize\":14,\"fontWeight\":\"regular\",\"align\":\"left\",\"color\":\"#666666\",\"fontFamily\":\"OpenSans\",\"backgroundColor\":\"#FFFFFF\"}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S6832e9d56a7841228ad811c66491fe24x.jpg\",\"style\":{\"width\":930,\"height\":1582}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S382f8c613af447c4a41e9bcc36e7edeaK.jpg\",\"style\":{\"width\":930,\"height\":1172}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sbc630f12b6754331aeb02d016ac2266eF.jpg\",\"style\":{\"width\":930,\"height\":1056}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S5fdfaec839224e758ffab6e3d9b2b261Z.jpg\",\"style\":{\"width\":930,\"height\":1498}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/See24350a83504445905af38d9468f48cx.jpg\",\"style\":{\"width\":930,\"height\":1377}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S3afbb4e1ebdf48cba61b3535360bc090c.jpg\",\"style\":{\"width\":930,\"height\":1677}}}]}",
            "product_id": 1005005454292177,
            "product_status_type": "onSelling",
            "sales_count": "342",
            "subject": "Baseus pd 20w cabo usb c para iphone 13 12 11 pro max cabo iphone de carregamento rápido para iphone x xr 8 usb tipo c para cabo relâmpago"
          },
          "ae_item_properties": {
            "ae_item_property": [
              {
                "attr_name": "Nome da marca",
                "attr_name_id": 2,
                "attr_value": "BASEUS",
                "attr_value_id": 200005349
              },
              {
                "attr_name": "Corrente máxima",
                "attr_name_id": 1273,
                "attr_value": "3A",
                "attr_value_id": 200003393
              },
              {
                "attr_name": "Conector A",
                "attr_name_id": 200001065,
                "attr_value": "TYPE-C",
                "attr_value_id": 202452822
              },
              {
                "attr_name": "Conector B",
                "attr_name_id": 200001066,
                "attr_value": "LIGHTNING",
                "attr_value_id": 201447574
              },
              {
                "attr_name": "Químico Hign-em causa",
                "attr_name_id": 400000603,
                "attr_value": "Nenhum",
                "attr_value_id": 23399591357
              },
              {
                "attr_name": "Origem",
                "attr_name_id": 219,
                "attr_value": "CN (Origem)",
                "attr_value_id": 9441741844
              },
              {
                "attr_name": "Inclui embalagem avulsa",
                "attr_name_id": 200001037,
                "attr_value": "Sim",
                "attr_value_id": 350216
              },
              {
                "attr_name": "Certificado",
                "attr_name_id": 348,
                "attr_value": "CE",
                "attr_value_id": 351626
              },
              {
                "attr_name": "Certificado",
                "attr_name_id": 348,
                "attr_value": "FCC",
                "attr_value_id": 360587
              },
              {
                "attr_name": "Certificado",
                "attr_name_id": 348,
                "attr_value": "ROHS",
                "attr_value_id": 351628
              },
              {
                "attr_name": "Características",
                "attr_name_id": 100002145,
                "attr_value": "Charging & Data Sync Cable",
                "attr_value_id": 14971154387
              },
              {
                "attr_name": "Choice",
                "attr_name_id": -1,
                "attr_value": "yes"
              }
            ]
          },
          "ae_item_sku_info_dtos": {
            "ae_item_sku_info_d_t_o": [
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_id": 193,
                      "sku_image": "https://ae01.alicdn.com/kf/S96edc4ac84a645a1b8f9deb5c1bc02eaG.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Preto"
                    },
                    {
                      "property_value_id": 200746126,
                      "sku_property_id": 200001036,
                      "sku_property_name": "Comprimento",
                      "sku_property_value": "1m"
                    }
                  ]
                },
                "currency_code": "BRL",
                "id": "14:193;200001036:200746126",
                "offer_bulk_sale_price": "17.79",
                "offer_sale_price": "17.79",
                "price_include_tax": false,
                "sku_attr": "14:193;200001036:200746126",
                "sku_available_stock": 38,
                "sku_id": "12000033145756375",
                "sku_price": "59.30"
              }
            ]
          },
          "ae_multimedia_info_dto": {
            "image_urls": "https://ae01.alicdn.com/kf/S322b18fa72714a40ae502d32edc1b735f.jpg;https://ae01.alicdn.com/kf/S0333061b8bd741de9bdda24e66578ba1i.jpg;https://ae01.alicdn.com/kf/S1c05cf41b4d94b579f153ae1686d37181.jpg;https://ae01.alicdn.com/kf/Sbf27ce1b797c4056ba85d9b44a4186efJ.jpg;https://ae01.alicdn.com/kf/S15905f1f59c745e7a34643c1dc692bbfW.jpg;https://ae01.alicdn.com/kf/S13b76e3179d04112bf13922912bd98eeS.jpg"
          },
          "ae_store_info": {
            "communication_rating": "4.8",
            "item_as_described_rating": "4.8",
            "shipping_speed_rating": "4.9",
            "store_country_code": "CN",
            "store_id": 1102471236,
            "store_name": "BASEUS Official Store"
          },
          "has_whole_sale": false,
          "logistics_info_dto": {
            "delivery_time": 7,
            "ship_to_country": "BR"
          },
          "package_info_dto": {
            "gross_weight": "0.044",
            "package_height": 2,
            "package_length": 22,
            "package_type": false,
            "package_width": 18,
            "product_unit": 100000015
          },
          "product_id_converter_result": {
            "main_product_id": 1005005454292177,
            "sub_product_id": "{\"US\":3256805267977425}"
          }
        }
      },
      "product_count": 594778,
      "products": [
        {
          "currency": "BRL",
          "main_image": "",
          "price": "0.00",
          "product_id": "1005005454292177",
          "title": ""
        }
      ],
      "products_found": 1
    },
    {
      "description": "AEB_BR_DropiSelectedItems_20241106",
      "display_name": "AEB_BR_DropiSelectedItems_20241106",
      "feed_id": "3",
      "feed_name": "AEB_BR_DropiSelectedItems_20241106",
      "item_ids": {
        "1005007900819057": {
          "ae_item_base_info_dto": {
            "avg_evaluation_rating": "4.4",
            "category_id": 201375514,
            "currency_code": "CNY",
            "detail": "\u003Cdiv class=\"detailmodule_html\"\u003E\u003Cdiv class=\"detail-desc-decorate-richtext\"\u003E\u003Cdiv class=\"detailmodule_html\"\u003E\u003Cdiv class=\"detail-desc-decorate-richtext\"\u003E\u003Cp\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/Sa556ada700774eb69d8380bebe865cb7I.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/S783afe9cf9ba426382d07b48674b776dR.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/S147443c5280f4043846a6da97200f09b9.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/S74b2b81500bb47c4a3eebacb76938a17P.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/S0d78dd91b7b44d47a7bae1fddfee967cw.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/S105502d1463f427582e0d8f4f1d47fe9F.jpg\" slate-data-type=\"image\"/\u003E\u003Cimg src=\"https://ae01.alicdn.com/kf/Se5b8369e5eac494895cca5fbbb76076ah.jpg\" slate-data-type=\"image\"/\u003E\u003C/p\u003E\u003C/div\u003E\u003C/div\u003E\r\n\u003C/div\u003E\u003C/div\u003E\r\n",
            "evaluation_count": "94",
            "mobile_detail": "{\"version\":\"2.0.0\",\"moduleList\":[{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Sa556ada700774eb69d8380bebe865cb7I.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S783afe9cf9ba426382d07b48674b776dR.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S147443c5280f4043846a6da97200f09b9.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S74b2b81500bb47c4a3eebacb76938a17P.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S0d78dd91b7b44d47a7bae1fddfee967cw.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/S105502d1463f427582e0d8f4f1d47fe9F.jpg\",\"style\":{\"width\":800,\"height\":800}}},{\"type\":\"image\",\"data\":{\"url\":\"https://ae01.alicdn.com/kf/Se5b8369e5eac494895cca5fbbb76076ah.jpg\",\"style\":{\"width\":800,\"height\":800}}}]}",
            "product_id": 1005007900819057,
            "product_status_type": "onSelling",
            "sales_count": "498",
            "subject": "Protetor de lente de câmera traseira de metal de alumínio para Xiaomi 14T Pro Mi14T Mi14TPro Capa de lente Protetor de tela Filme de anel de lente"
          },
          "ae_item_properties": {
            "ae_item_property": [
              {
                "attr_name": "Nome da marca",
                "attr_name_id": 2,
                "attr_value": "MERCIVERRE",
                "attr_value_id": 23640886089
              },
              {
                "attr_name": "Químico Hign-em causa",
                "attr_name_id": 400000603,
                "attr_value": "Nenhum",
                "attr_value_id": 23399591357
              },
              {
                "attr_name": "Origem",
                "attr_name_id": 219,
                "attr_value": "CN (Origem)",
                "attr_value_id": 9441741844
              },
              {
                "attr_name": "Item",
                "attr_name_id": -1,
                "attr_value": "Camera Lens screen protector",
                "attr_value_id": -1
              },
              {
                "attr_name": "Compatible Models",
                "attr_name_id": -1,
                "attr_value": "For Xiaomi 14T/14T Pro",
                "attr_value_id": -1
              },
              {
                "attr_name": "Material",
                "attr_name_id": -1,
                "attr_value": "Aluminum Metal",
                "attr_value_id": -1
              },
              {
                "attr_name": "Features",
                "attr_name_id": -1,
                "attr_value": "Anti Scratch, Waterproof",
                "attr_value_id": -1
              },
              {
                "attr_name": "Color",
                "attr_name_id": -1,
                "attr_value": "Black",
                "attr_value_id": -1
              },
              {
                "attr_name": "Weight",
                "attr_name_id": -1,
                "attr_value": "5-10g",
                "attr_value_id": -1
              },
              {
                "attr_name": "Choice",
                "attr_name_id": -1,
                "attr_value": "yes"
              },
              {
                "attr_name": "semi_Choice",
                "attr_name_id": -2,
                "attr_value": "yes"
              }
            ]
          },
          "ae_item_sku_info_dtos": {
            "ae_item_sku_info_d_t_o": [
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_definition_name": "For Xiaomi 14T Pro",
                      "property_value_id": 200025551,
                      "sku_image": "https://ae01.alicdn.com/kf/S4acee062a19c4a9e838c9ac8c2439d1dQ.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Blue"
                    }
                  ]
                },
                "currency_code": "BRL",
                "id": "14:200025551#For Xiaomi 14T Pro",
                "offer_bulk_sale_price": "16.24",
                "offer_sale_price": "16.24",
                "price_include_tax": false,
                "sku_attr": "14:200025551#For Xiaomi 14T Pro",
                "sku_available_stock": 13,
                "sku_id": "12000042770245500",
                "sku_price": "17.76"
              },
              {
                "ae_sku_property_dtos": {
                  "ae_sku_property_d_t_o": [
                    {
                      "property_value_definition_name": "For Xiaomi 14T",
                      "property_value_id": 193,
                      "sku_image": "https://ae01.alicdn.com/kf/Saf0e9ab0bd5e43909b30dc175a919544H.jpg",
                      "sku_property_id": 14,
                      "sku_property_name": "cor",
                      "sku_property_value": "Preto"
                    }
                  ]
                },
                "currency_code": "BRL",
                "id": "14:193#For Xiaomi 14T",
                "offer_bulk_sale_price": "16.39",
                "offer_sale_price": "16.39",
                "price_include_tax": false,
                "sku_attr": "14:193#For Xiaomi 14T",
                "sku_available_stock": 27,
                "sku_id": "12000042770245499",
                "sku_price": "17.91"
              }
            ]
          },
          "ae_multimedia_info_dto": {
            "image_urls": "https://ae01.alicdn.com/kf/Sfb5a821dcdac4b3b9c11db714a4f61188.jpg;https://ae01.alicdn.com/kf/S2557ce985b954e3e8e1c60935e342623m.jpg;https://ae01.alicdn.com/kf/S75186cf833024a9eb34c1a76032ad528P.jpg;https://ae01.alicdn.com/kf/S48958b03eb35430093a0edf48cb9ac45n.jpg;https://ae01.alicdn.com/kf/Sba2ad593f4d54de78612de4302fc4e77h.jpg;https://ae01.alicdn.com/kf/S01aae21a2e6c480badf958216b43e835F.jpg"
          },
          "ae_store_info": {
            "communication_rating": "4.6",
            "item_as_described_rating": "4.6",
            "shipping_speed_rating": "4.7",
            "store_country_code": "CN",
            "store_id": 4233005,
            "store_name": "MERCIVERRE Official Store"
          },
          "has_whole_sale": false,
          "logistics_info_dto": {
            "delivery_time": 7,
            "ship_to_country": "BR"
          },
          "package_info_dto": {
            "gross_weight": "0.020",
            "package_height": 5,
            "package_length": 20,
            "package_type": false,
            "package_width": 10,
            "product_unit": 100000015
          },
          "product_id_converter_result": {
            "main_product_id": 1005007900819057,
            "sub_product_id": "{\"US\":3256807714504305}"
          }
        }
      },
      "product_count": 99872,
      "products": [
        {
          "currency": "BRL",
          "main_image": "",
          "price": "0.00",
          "product_id": "1005007900819057",
          "title": ""
        }
      ],
      "products_found": 1
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_feeds": 3
  },
  "success": true,
  "timestamp": "2025-08-22T15:33:37.287186"
}