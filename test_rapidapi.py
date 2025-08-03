#!/usr/bin/env python3
"""
Teste da API RapidAPI AliExpress
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('./config.env')

# Configurações RapidAPI
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'aliexpress-api2.p.rapidapi.com'

print("🔑 RapidAPI Key:", RAPIDAPI_KEY)
print("🌐 RapidAPI Host:", RAPIDAPI_HOST)

if not RAPIDAPI_KEY:
    print("❌ RapidAPI Key não configurada!")
    print("📝 Adicione sua RapidAPI Key no arquivo config.env")
    exit(1)

# Headers para RapidAPI
headers = {
    'x-rapidapi-host': RAPIDAPI_HOST,
    'x-rapidapi-key': RAPIDAPI_KEY
}

def test_search_products():
    """Testar busca de produtos"""
    print("\n🔍 Testando busca de produtos...")
    
    url = "https://aliexpress-api2.p.rapidapi.com/search"
    params = {
        'q': 'smartphone',
        'page': 1,
        'limit': 3
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrados {len(data.get('products', []))} produtos!")
            
            for i, product in enumerate(data.get('products', [])[:3]):
                print(f"\n📱 Produto {i+1}:")
                print(f"   ID: {product.get('id', 'N/A')}")
                print(f"   Título: {product.get('title', 'N/A')}")
                print(f"   Preço: ${product.get('price', 0)}")
                print(f"   Imagem: {product.get('image', 'N/A')}")
                print(f"   URL: {product.get('url', 'N/A')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar busca: {e}")

def test_product_details():
    """Testar detalhes de produto"""
    print("\n📋 Testando detalhes de produto...")
    
    # URL de exemplo de um produto AliExpress
    product_url = "https://www.aliexpress.com/item/1005005640660666.html"
    
    url = "https://aliexpress-api2.p.rapidapi.com/product"
    params = {
        'url': product_url
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Detalhes do produto obtidos!")
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Preço: ${data.get('price', 0)}")
            print(f"   Avaliação: {data.get('rating', 0)}")
            print(f"   Avaliações: {data.get('reviews_count', 0)}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar detalhes: {e}")

def test_categories():
    """Testar categorias"""
    print("\n📂 Testando categorias...")
    
    url = "https://aliexpress-api2.p.rapidapi.com/categories"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            print(f"✅ Encontradas {len(categories)} categorias!")
            
            for i, category in enumerate(categories[:5]):
                print(f"   {i+1}. {category.get('name', 'N/A')} (ID: {category.get('id', 'N/A')})")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar categorias: {e}")

def test_hot_products():
    """Testar produtos em alta"""
    print("\n🔥 Testando produtos em alta...")
    
    url = "https://aliexpress-api2.p.rapidapi.com/hot-products"
    params = {
        'page': 1,
        'limit': 3
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ Encontrados {len(products)} produtos em alta!")
            
            for i, product in enumerate(products[:3]):
                print(f"\n🔥 Produto {i+1}:")
                print(f"   Título: {product.get('title', 'N/A')}")
                print(f"   Preço: ${product.get('price', 0)}")
                print(f"   URL: {product.get('url', 'N/A')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar produtos em alta: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando testes da API RapidAPI AliExpress...")
    
    test_search_products()
    test_product_details()
    test_categories()
    test_hot_products()
    
    print("\n✅ Testes concluídos!") 