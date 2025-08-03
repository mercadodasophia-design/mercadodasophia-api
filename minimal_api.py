from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from urllib.parse import urlencode

# Carregar variáveis de ambiente
config_path = os.path.join(os.path.dirname(__file__), 'config.env')
print(f"🔍 Procurando config.env em: {config_path}")
print(f"📁 Arquivo existe: {os.path.exists(config_path)}")

load_dotenv(config_path)

app = Flask(__name__)
CORS(app)

APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
API_BASE_URL = 'https://api-sg.aliexpress.com/sync'

RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL')
CALLBACK_URL = RENDER_EXTERNAL_URL + '/api/aliexpress/oauth-callback' if RENDER_EXTERNAL_URL else 'https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback'

print(f"🔑 APP_KEY carregado: {'✅' if APP_KEY else '❌'} - Valor: {APP_KEY}")
print(f"🔑 APP_SECRET carregado: {'✅' if APP_SECRET else '❌'} - Valor: {APP_SECRET[:10] if APP_SECRET else 'N/A'}...")

aliexpress_tokens = {}

def ali_timestamp():
    # Formato correto para AliExpress: YYYY-MM-DD HH:MM:SS (UTC+8)
    # AliExpress espera China timezone (UTC+8)
    utc_now = datetime.utcnow()
    china_time = utc_now + timedelta(hours=8)
    return china_time.strftime('%Y-%m-%d %H:%M:%S')

def generate_sign(params):
    sorted_params = sorted(params.items())
    param_string = ''.join(f"{k}{v}" for k,v in sorted_params)
    sign_string = f"{APP_SECRET}{param_string}{APP_SECRET}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def ali_request(method, access_token, extra_params=None):
    params = {
        'method': method,
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': ali_timestamp(),
        'format': 'json',
        'v': '2.0'
    }
    if extra_params:
        params.update(extra_params)
    params['sign'] = generate_sign(params)
    resp = requests.post(API_BASE_URL, data=params, timeout=30)
    print(f"📡 Request to AliExpress API method {method}: {params}")
    print(f"📄 Response status: {resp.status_code}")
    print(f"📄 Response body: {resp.text[:500]}...")
    resp.raise_for_status()
    return resp.json()

def generate_aliexpress_auth_url():
    params = {
        'response_type': 'code',
        'client_id': APP_KEY,
        'redirect_uri': CALLBACK_URL,
        'state': 'xyz123',
        'force_auth': 'true',  # Força nova autorização
    }
    return f"https://api-sg.aliexpress.com/oauth/authorize?{urlencode(params)}"

@app.route('/api/aliexpress/oauth-url')
def aliexpress_oauth_url():
    return jsonify({'auth_url': generate_aliexpress_auth_url()})

def exchange_code_for_token(code):
    """
    Troca código OAuth2 por access_token
    Baseado na documentação oficial do AliExpress
    """
    token_url = 'https://api-sg.aliexpress.com/rest'
    
    # Parâmetros obrigatórios para OAuth2 do AliExpress
    data = {
        'method': 'auth.token.create',
        'app_key': APP_KEY,
        'code': code,
        'timestamp': ali_timestamp(),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
    }
    
    # Gerar assinatura MD5
    sign = generate_sign(data)
    data['sign'] = sign
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    print(f"🔄 Fazendo requisição OAuth2...")
    print(f"📝 Dados: {data}")
    resp = requests.post(token_url, data=data, headers=headers, timeout=30)
    print(f"📊 Status Code: {resp.status_code}")
    print(f"📄 Response: {resp.text[:500]}...")

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")

@app.route('/api/aliexpress/oauth-callback', methods=['GET'])
def aliexpress_oauth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Missing code parameter'}), 400
    
    try:
        token_data = exchange_code_for_token(code)
        aliexpress_tokens['access_token'] = token_data.get('access_token')
        aliexpress_tokens['refresh_token'] = token_data.get('refresh_token')
        aliexpress_tokens['expires_in'] = token_data.get('expires_in')
        
        print(f"✅ Tokens armazenados com sucesso!")
        print(f"🔑 Access Token: {token_data.get('access_token', '')[:20]}...")
        
        return jsonify({
            'success': True, 
            'message': 'OAuth2 autenticação realizada com sucesso!',
            'token_data': token_data
        })
    except Exception as e:
        print(f"❌ Erro na troca de código por token: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint genérico para ações de produto/pedido
@app.route('/api/aliexpress/action', methods=['POST'])
def aliexpress_action():
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401

    data = request.get_json() or {}
    method = data.get('method')
    extra_params = data.get('params', {})

    if not method:
        return jsonify({'error': 'Faltando parâmetro method'}), 400

    try:
        result = ali_request(method, access_token, extra_params)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        print(f"❌ Erro ao chamar API AliExpress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/products')
def aliexpress_products():
    access_token = aliexpress_tokens.get('access_token')
    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    # Se não tem token, retornar dados simulados
    if not access_token:
        print("⚠️  Sem token OAuth2, retornando dados simulados")
        simulated_products = get_simulated_products(keywords, page, page_size)
        return jsonify({
            'success': True, 
            'products': simulated_products,
            'message': 'Dados simulados (OAuth2 não configurado)',
            'total': len(simulated_products)
        })

    try:
        data = ali_request('aliexpress.ds.product.list', access_token, {
            'keywords': keywords,
            'page_no': page,
            'page_size': page_size
        })
        products = data.get('result', {}).get('products', [])
        return jsonify({'success': True, 'products': products, 'raw': data})
    except Exception as e:
        print(f"❌ Erro na API AliExpress: {e}")
        # Fallback para dados simulados
        simulated_products = get_simulated_products(keywords, page, page_size)
        return jsonify({
            'success': True, 
            'products': simulated_products,
            'message': 'Dados simulados (erro na API)',
            'error': str(e),
            'total': len(simulated_products)
        })

def get_simulated_products(keywords, page, page_size):
    """Retorna produtos simulados para teste"""
    base_products = [
        {
            'id': '1005005640660666',
            'name': f'Smartphone Case Premium - {keywords.title()}',
            'price': 'R$ 15,90',
            'originalPrice': 'R$ 29,90',
            'rating': '4.8',
            'reviewsCount': '2.5k',
            'salesCount': '15.2k',
            'image': 'https://via.placeholder.com/300x300/007bff/ffffff?text=Product',
            'url': 'https://www.aliexpress.com/item/1005005640660666.html',
            'shipping': 'Frete grátis',
            'store': 'TechStore Official',
            'aliexpressId': '1005005640660666'
        },
        {
            'id': '1005005640660667',
            'name': f'Wireless Headphones - {keywords.title()}',
            'price': 'R$ 89,90',
            'originalPrice': 'R$ 159,90',
            'rating': '4.6',
            'reviewsCount': '1.8k',
            'salesCount': '8.9k',
            'image': 'https://via.placeholder.com/300x300/28a745/ffffff?text=Headphones',
            'url': 'https://www.aliexpress.com/item/1005005640660667.html',
            'shipping': 'Frete grátis',
            'store': 'AudioPro Store',
            'aliexpressId': '1005005640660667'
        },
        {
            'id': '1005005640660668',
            'name': f'Smart Watch Fitness - {keywords.title()}',
            'price': 'R$ 129,90',
            'originalPrice': 'R$ 299,90',
            'rating': '4.7',
            'reviewsCount': '3.2k',
            'salesCount': '12.1k',
            'image': 'https://via.placeholder.com/300x300/dc3545/ffffff?text=SmartWatch',
            'url': 'https://www.aliexpress.com/item/1005005640660668.html',
            'shipping': 'Frete grátis',
            'store': 'TechGear Pro',
            'aliexpressId': '1005005640660668'
        }
    ]
    
    # Simular paginação
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return base_products[start_idx:end_idx]

@app.route('/api/health')
def health():
    return jsonify({
        'success': True,
        'message': 'API funcionando!',
        'app_key_configured': bool(APP_KEY),
        'app_secret_configured': bool(APP_SECRET)
    })

if __name__ == '__main__':
    print("🚀 API ALIEXPRESS OFICIAL iniciando...")
    port = int(os.environ.get('PORT', 3000))
    print(f"🌐 http://localhost:{port}")
    print(f"🔑 App Key configurado: {'✅' if APP_KEY else '❌'}")
    print(f"🔑 App Secret configurado: {'✅' if APP_SECRET else '❌'}")
    print(f"🔗 Callback URL: {CALLBACK_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)
