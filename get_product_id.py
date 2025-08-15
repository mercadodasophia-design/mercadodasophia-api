#!/usr/bin/env python3
"""
Busca um product_id válido para teste
"""

import requests
import json

# URL da API
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def get_valid_product_id():
    """Busca um product_id válido"""
    
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
            
            if 'data' in data and 'aliexpress_ds_text_search_response' in data['data']:
                search_response = data['data']['aliexpress_ds_text_search_response']
                
                if 'data' in search_response and 'products' in search_response['data']:
                    products = search_response['data']['products']
                    
                    if 'selection_search_product' in products and len(products['selection_search_product']) > 0:
                        product = products['selection_search_product'][0]
                        product_id = product.get('product_id')
                        
                        print(f"✅ Produto encontrado!")
                        print(f"🆔 Product ID: {product_id}")
                        print(f"📦 Nome: {product.get('product_title', 'N/A')}")
                        print(f"💰 Preço: {product.get('product_price', 'N/A')}")
                        
                        return product_id
        
        print("❌ Nenhum produto encontrado")
        return None
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

if __name__ == "__main__":
    product_id = get_valid_product_id()
    if product_id:
        print(f"\n🎯 Use este product_id no teste: {product_id}")
