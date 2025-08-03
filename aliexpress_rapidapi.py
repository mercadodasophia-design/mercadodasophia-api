from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import traceback

# Carregar variáveis de ambiente
load_dotenv('./config.env')

app = Flask(__name__)
CORS(app)

# Configurações RapidAPI
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'aliexpress-api2.p.rapidapi.com'

# Headers padrão para RapidAPI
def get_headers():
    return {
        'x-rapidapi-host': RAPIDAPI_HOST,
        'x-rapidapi-key': RAPIDAPI_KEY
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API RapidAPI AliExpress funcionando!',
        'rapidapi_key_configured': bool(RAPIDAPI_KEY),
        'rapidapi_host': RAPIDAPI_HOST
    })

@app.route('/api/aliexpress/products', methods=['GET'])
def get_products():
    """Buscar produtos do AliExpress via RapidAPI"""
    if not RAPIDAPI_KEY:
        return jsonify({
            'success': False,
            'error': 'RapidAPI Key não configurada'
        }), 500

    try:
        # Parâmetros da requisição
        keywords = request.args.get('keywords', '')
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 20)
        
        # URL da API RapidAPI para busca de produtos
        url = "https://aliexpress-api2.p.rapidapi.com/search"
        
        # Parâmetros da busca
        params = {
            'q': keywords,
            'page': page,
            'limit': limit
        }
        
        # Fazer requisição para RapidAPI
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Converter resposta para formato padrão
            products = []
            if 'products' in data:
                for product in data['products']:
                    products.append({
                        'id': product.get('id', ''),
                        'title': product.get('title', ''),
                        'price': product.get('price', 0),
                        'original_price': product.get('original_price', 0),
                        'image': product.get('image', ''),
                        'url': product.get('url', ''),
                        'rating': product.get('rating', 0),
                        'reviews_count': product.get('reviews_count', 0),
                        'sales_count': product.get('sales_count', 0),
                        'store_name': product.get('store_name', ''),
                        'shipping': product.get('shipping', ''),
                        'aliexpress_id': product.get('id', '')
                    })
            
            return jsonify({
                'success': True,
                'products': products,
                'total': data.get('total', len(products)),
                'current_page': int(page),
                'page_size': int(limit)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro na API RapidAPI: {response.status_code}',
                'message': response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/product/details', methods=['GET'])
def get_product_details():
    """Buscar detalhes de um produto específico"""
    if not RAPIDAPI_KEY:
        return jsonify({
            'success': False,
            'error': 'RapidAPI Key não configurada'
        }), 500

    try:
        product_url = request.args.get('url', '')
        if not product_url:
            return jsonify({
                'success': False,
                'error': 'URL do produto não fornecida'
            }), 400

        # URL da API RapidAPI para detalhes do produto
        url = "https://aliexpress-api2.p.rapidapi.com/product"
        
        # Parâmetros
        params = {
            'url': product_url
        }
        
        # Fazer requisição para RapidAPI
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Converter resposta para formato padrão
            product = {
                'id': data.get('id', ''),
                'title': data.get('title', ''),
                'price': data.get('price', 0),
                'original_price': data.get('original_price', 0),
                'image': data.get('image', ''),
                'url': data.get('url', ''),
                'rating': data.get('rating', 0),
                'reviews_count': data.get('reviews_count', 0),
                'sales_count': data.get('sales_count', 0),
                'store_name': data.get('store_name', ''),
                'shipping': data.get('shipping', ''),
                'aliexpress_id': data.get('id', ''),
                'description': data.get('description', ''),
                'images': data.get('images', []),
                'specifications': data.get('specifications', {})
            }
            
            return jsonify({
                'success': True,
                'product': product
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro na API RapidAPI: {response.status_code}',
                'message': response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do produto: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/categories', methods=['GET'])
def get_categories():
    """Buscar categorias do AliExpress via RapidAPI"""
    if not RAPIDAPI_KEY:
        return jsonify({
            'success': False,
            'error': 'RapidAPI Key não configurada'
        }), 500

    try:
        # URL da API RapidAPI para categorias
        url = "https://aliexpress-api2.p.rapidapi.com/categories"
        
        # Fazer requisição para RapidAPI
        response = requests.get(url, headers=get_headers())
        
        if response.status_code == 200:
            data = response.json()
            
            # Converter resposta para formato padrão
            categories = []
            if 'categories' in data:
                for category in data['categories']:
                    categories.append({
                        'id': category.get('id', ''),
                        'name': category.get('name', ''),
                        'level': category.get('level', 1),
                        'parent_id': category.get('parent_id', None)
                    })
            
            return jsonify({
                'success': True,
                'categories': categories
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro na API RapidAPI: {response.status_code}',
                'message': response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/hot-products', methods=['GET'])
def get_hot_products():
    """Buscar produtos em alta via RapidAPI"""
    if not RAPIDAPI_KEY:
        return jsonify({
            'success': False,
            'error': 'RapidAPI Key não configurada'
        }), 500

    try:
        # Parâmetros da requisição
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 20)
        
        # URL da API RapidAPI para produtos em alta
        url = "https://aliexpress-api2.p.rapidapi.com/hot-products"
        
        # Parâmetros
        params = {
            'page': page,
            'limit': limit
        }
        
        # Fazer requisição para RapidAPI
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Converter resposta para formato padrão
            products = []
            if 'products' in data:
                for product in data['products']:
                    products.append({
                        'id': product.get('id', ''),
                        'title': product.get('title', ''),
                        'price': product.get('price', 0),
                        'original_price': product.get('original_price', 0),
                        'image': product.get('image', ''),
                        'url': product.get('url', ''),
                        'rating': product.get('rating', 0),
                        'reviews_count': product.get('reviews_count', 0),
                        'sales_count': product.get('sales_count', 0),
                        'store_name': product.get('store_name', ''),
                        'shipping': product.get('shipping', ''),
                        'aliexpress_id': product.get('id', '')
                    })
            
            return jsonify({
                'success': True,
                'products': products,
                'total': data.get('total', len(products)),
                'current_page': int(page),
                'page_size': int(limit)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro na API RapidAPI: {response.status_code}',
                'message': response.text
            }), response.status_code

    except Exception as e:
        print(f"❌ Erro ao buscar produtos em alta: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 API RAPIDAPI ALIEXPRESS iniciando na porta {port}...")
    print(f"🔑 RapidAPI Key configurado: {'✅' if RAPIDAPI_KEY else '❌'}")
    print(f"🌐 RapidAPI Host: {RAPIDAPI_HOST}")
    app.run(host='0.0.0.0', port=port, debug=True) 