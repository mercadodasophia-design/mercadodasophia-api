#!/usr/bin/env python3
"""
Debug da estrutura de produtos
"""

import requests
import json

# URL da API
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def debug_products():
    """Debug da estrutura de produtos"""
    
    try:
        # Buscar produtos
        response = requests.get(
            f"{API_URL}/api/aliexpress/products",
            params={
                "keywords": "phone",
                "limit": 1
            },
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Estrutura completa: {json.dumps(data, indent=2)}")
            
            # Tentar extrair product_id de diferentes campos
            if 'data' in data and 'aliexpress_ds_text_search_response' in data['data']:
                search_response = data['data']['aliexpress_ds_text_search_response']
                
                if 'data' in search_response and 'products' in search_response['data']:
                    products = search_response['data']['products']
                    
                    if 'selection_search_product' in products and len(products['selection_search_product']) > 0:
                        product = products['selection_search_product'][0]
                        print(f"🔍 Produto encontrado: {json.dumps(product, indent=2)}")
                        
                        # Tentar diferentes campos para product_id
                        possible_fields = ['product_id', 'productId', 'id', 'productid']
                        for field in possible_fields:
                            if field in product:
                                print(f"✅ Product ID encontrado em '{field}': {product[field]}")
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    debug_products()
