# Documentação dos Parâmetros da API AliExpress

## Estrutura Principal do JSON Retornado

```json
{
  "success": true,
  "data": {
    // Dados principais do produto
  }
}
```

## Parâmetros Principais em `data`

### Informações Básicas
- `id`: ID do produto (ex: "1005009702513437")
- `title`: Título do produto
- `currency`: Moeda (ex: "BRL")
- `description`: Descrição HTML do produto
- `rating`: Avaliação média (ex: "0.0")
- `price`: Preço (pode estar vazio)
- `sales`: Número de vendas (ex: "0")

### Imagens e Mídia
- `images`: Array de URLs das imagens do produto
- `videos`: Array de vídeos (geralmente vazio)

### Dados Raw (`raw`)
#### `ae_item_base_info_dto`
- `product_id`: ID do produto
- `subject`: Título do produto
- `avg_evaluation_rating`: Avaliação média
- `evaluation_count`: Número de avaliações
- `sales_count`: Número de vendas
- `product_status_type`: Status do produto (ex: "onSelling")
- `category_id`: ID da categoria
- `currency_code`: Código da moeda
- `detail`: Descrição detalhada HTML
- `mobile_detail`: Descrição para mobile (JSON)

#### `ae_item_properties`
- `ae_item_property`: Array de propriedades do produto
  - `attr_name`: Nome do atributo
  - `attr_value`: Valor do atributo
  - `attr_name_id`: ID do nome do atributo
  - `attr_value_id`: ID do valor do atributo

#### `ae_item_sku_info_dtos`
- `ae_item_sku_info_d_t_o`: Array de SKUs disponíveis
  - `sku_id`: ID do SKU
  - `offer_sale_price`: Preço de venda
  - `offer_bulk_sale_price`: Preço em atacado
  - `sku_price`: Preço original do SKU
  - `sku_available_stock`: Estoque disponível
  - `currency_code`: Moeda
  - `ae_sku_property_dtos`: Propriedades do SKU
    - `ae_sku_property_d_t_o`: Array de propriedades
      - `sku_property_name`: Nome da propriedade (ex: "cor", "Tamanho")
      - `sku_property_value`: Valor da propriedade (ex: "CINZA", "XXXL")
      - `sku_image`: Imagem do SKU

#### `ae_multimedia_info_dto`
- `image_urls`: String com URLs das imagens separadas por ";"

#### `ae_store_info`
- `store_name`: Nome da loja
- `store_id`: ID da loja
- `store_country_code`: Código do país da loja

#### `package_info_dto`
- `gross_weight`: Peso bruto (ex: "0.500")
- `package_length`: Comprimento da embalagem
- `package_width`: Largura da embalagem
- `package_height`: Altura da embalagem
- `package_type`: Tipo de embalagem
- `product_unit`: Unidade do produto

#### `logistics_info_dto`
- `delivery_time`: Tempo de entrega em dias
- `ship_to_country`: País de destino

#### `skus`
- `ae_item_sku_info_d_t_o`: Array de SKUs (mesma estrutura de `ae_item_sku_info_dtos`)

## Exemplo de Uso no Frontend

```dart
// Acessar dados básicos
final productId = data['id'];
final title = data['title'];
final images = data['images'] as List<String>;

// Acessar dados raw
final raw = data['raw'];
final baseInfo = raw['ae_item_base_info_dto'];
final skuInfo = raw['ae_item_sku_info_dtos'];
final storeInfo = raw['ae_store_info'];
final packageInfo = raw['package_info_dto'];

// Acessar SKUs
final skus = raw['skus']['ae_item_sku_info_d_t_o'] as List;
final firstSku = skus.first;
final skuPrice = firstSku['offer_sale_price'];
final skuProperties = firstSku['ae_sku_property_dtos']['ae_sku_property_d_t_o'];
```

## Observações Importantes

1. **Preços**: Os preços estão em `offer_sale_price` dentro dos SKUs
2. **Imagens**: Estão em `images` (array) e também em `raw.ae_multimedia_info_dto.image_urls` (string)
3. **Propriedades**: Estão em `raw.ae_item_properties.ae_item_property`
4. **SKUs**: Contêm as variações do produto (cores, tamanhos, etc.)
5. **Avaliações**: Estão em `rating` e também em `raw.ae_item_base_info_dto.avg_evaluation_rating`
