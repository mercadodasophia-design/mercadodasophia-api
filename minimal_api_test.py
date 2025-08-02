#!/usr/bin/env python3
"""
API de Teste - Funciona sem OAuth2 AliExpress
Usa dados simulados para testar a funcionalidade
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
import time
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

# Carregar variáveis de ambiente
config_path = os.path.join(os.path.dirname(__file__), 'config.env')
load_dotenv(config_path)

app = Flask(__name__)
CORS(app)

# Configurações da API oficial do AliExpress
APP_KEY = os.getenv('ALIEXPRESS_APP_KEY', '517616')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET', 'TTqNmTMs5Q0QiPbulDNenhXr2My18nN4')
API_BASE_URL = 'https://api-sg.aliexpress.com/sync'

print(f"🔑 APP_KEY: {APP_KEY}")
print(f"🔑 APP_SECRET: {APP_SECRET[:10]}...")

# Simular tokens autenticados para teste
aliexpress_tokens = {
    'access_token': 'test_access_token_123',
    'refresh_token': 'test_refresh_token_456',
    'expires_in': 7200
}

def generate_sign(params):
    """Gerar assinatura MD5 para a API do AliExpress"""
    sorted_params = sorted(params.items())
    param_string = ''
    for key, value in sorted_params:
        param_string += f"{key}{value}"
    sign_string = f"{APP_SECRET}{param_string}{APP_SECRET}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def get_simulated_products(keywords):
    """Produtos simulados para teste"""
    products = [
        {
            'id': '1005005640660666',
            'title': f'Produto Teste - {keywords}',
            'price': 'R$ 299,90',
            'original_price': 'R$ 399,90',
            'image': 'https://ae01.alicdn.com/kf/S1f8c8c8c8c8c8c8c8c8c8c8c8c8c8c8.jpg_640x640q90.jpg',
            'rating': 4.5,
            'reviews': 1234,
            'seller': 'Test Store',
            'aliexpress_url': 'https://www.aliexpress.com/item/1005005640660666.html',
            'aliexpress_id': '1005005640660666'
        },
        {
            'id': '1005005640660667',
            'title': f'Produto Premium - {keywords}',
            'price': 'R$ 599,90',
            'original_price': 'R$ 799,90',
            'image': 'https://ae01.alicdn.com/kf/S2f8c8c8c8c8c8c8c8c8c8c8c8c8c8c8.jpg_640x640q90.jpg',
            'rating': 4.8,
            'reviews': 567,
            'seller': 'Premium Store',
            'aliexpress_url': 'https://www.aliexpress.com/item/1005005640660667.html',
            'aliexpress_id': '1005005640660667'
        }
    ]
    return products

@app.route('/api/health')
def health():
    return jsonify({
        'success': True, 
        'message': 'API de TESTE funcionando!',
        'app_key_configured': bool(APP_KEY),
        'app_secret_configured': bool(APP_SECRET),
        'mode': 'TESTE - Dados simulados'
    })

@app.route('/api/search')
def search():
    keywords = request.args.get('keywords', '').lower()
    
    if not keywords:
        return jsonify({
            'success': True,
            'products': []
        })
    
    # Usar produtos simulados
    products = get_simulated_products(keywords)
    
    return jsonify({
        'success': True,
        'products': products,
        'mode': 'TESTE - Dados simulados'
    })

@app.route('/api/aliexpress/oauth-url')
def aliexpress_oauth_url():
    """URL de autorização simulada"""
    params = {
        'response_type': 'code',
        'client_id': APP_KEY,
        'redirect_uri': 'https://mercadodasophia.com/callback',
        'state': 'xyz123',
    }
    auth_url = f"https://oauth.aliexpress.com/authorize?{urlencode(params)}"
    return jsonify({
        'auth_url': auth_url,
        'warning': 'MODO TESTE - Use credenciais reais para produção'
    })

@app.route('/api/aliexpress/oauth-callback')
def aliexpress_oauth_callback():
    """Callback OAuth2 simulado"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Missing code'}), 400
    
    # Simular resposta de token
    token_data = {
        'access_token': 'test_access_token_123',
        'refresh_token': 'test_refresh_token_456',
        'expires_in': 7200,
        'token_type': 'Bearer'
    }
    
    aliexpress_tokens.update(token_data)
    return jsonify({
        'success': True, 
        'token_data': token_data,
        'mode': 'TESTE - Tokens simulados'
    })

@app.route('/api/aliexpress/products')
def aliexpress_products():
    """Busca produtos simulados"""
    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    products = get_simulated_products(keywords)
    
    return jsonify({
        'success': True, 
        'products': products,
        'page': page,
        'page_size': page_size,
        'mode': 'TESTE - Dados simulados'
    })

@app.route('/api/aliexpress/categories')
def aliexpress_categories():
    """Categorias simuladas"""
    categories = [
        {'id': '1', 'name': 'Electronics', 'parent_id': '0'},
        {'id': '2', 'name': 'Clothing', 'parent_id': '0'},
        {'id': '3', 'name': 'Home & Garden', 'parent_id': '0'},
        {'id': '4', 'name': 'Sports', 'parent_id': '0'},
        {'id': '5', 'name': 'Beauty', 'parent_id': '0'}
    ]
    
    return jsonify({
        'success': True,
        'categories': categories,
        'mode': 'TESTE - Dados simulados'
    })

@app.route('/api/aliexpress/shipping-methods')
def aliexpress_shipping_methods():
    """Métodos de envio simulados"""
    methods = [
        {'id': '1', 'name': 'Standard Shipping', 'price': 'R$ 15,90'},
        {'id': '2', 'name': 'Express Shipping', 'price': 'R$ 29,90'},
        {'id': '3', 'name': 'Premium Shipping', 'price': 'R$ 49,90'}
    ]
    
    return jsonify({
        'success': True,
        'methods': methods,
        'mode': 'TESTE - Dados simulados'
    })

@app.route('/api/aliexpress/create-order', methods=['POST'])
def aliexpress_create_order():
    """Criar pedido simulado"""
    data = request.get_json() or {}
    
    order_id = f"ORDER_{int(time.time())}"
    
    return jsonify({
        'success': True,
        'order_id': order_id,
        'order_data': data,
        'mode': 'TESTE - Pedido simulado'
    })

@app.route('/api/aliexpress/order-status', methods=['GET'])
def aliexpress_order_status():
    """Status do pedido simulado"""
    order_id = request.args.get('order_id', 'ORDER_123')
    
    return jsonify({
        'success': True,
        'order_id': order_id,
        'status': 'PROCESSING',
        'mode': 'TESTE - Status simulado'
    })

if __name__ == '__main__':
    print("🚀 API ALIEXPRESS TESTE iniciando...")
    print("🌐 http://localhost:3000")
    print("🔑 Modo: TESTE (dados simulados)")
    print("⚠️  Use para desenvolvimento apenas!")
    app.run(host='0.0.0.0', port=3000, debug=True) 