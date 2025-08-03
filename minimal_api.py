from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
import os
from datetime import datetime, timedelta
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
    return (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

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
    }
    return f"https://api-sg.aliexpress.com/oauth/authorize?{urlencode(params)}"

@app.route('/api/aliexpress/oauth-url')
def aliexpress_oauth_url():
    return jsonify({'auth_url': generate_aliexpress_auth_url()})

def exchange_code_for_token(code):
    token_url = 'https://api-sg.aliexpress.com/auth/token/create'
    data = {
        'method': 'auth.token.create',
        'app_key': APP_KEY,
        'code': code,
        'redirect_uri': CALLBACK_URL,
        'timestamp': ali_timestamp(),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
    }
    data['sign'] = generate_sign(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    print(f"🔄 Fazendo requisição OAuth2... Dados enviados: {data}")
    resp = requests.post(token_url, data=data, headers=headers, timeout=30)
    print(f"📊 Status Code: {resp.status_code}")
    print(f"📄 Response: {resp.text[:500]}...")

    resp.raise_for_status()
    return resp.json()

@app.route('/api/aliexpress/oauth-callback', methods=['GET', 'POST'])
def aliexpress_oauth_callback():
    code = request.args.get('code') if request.method=='GET' else (
        request.get_json().get('code') if request.is_json else request.form.get('code')
    )
    if not code:
        return jsonify({'error': 'Missing code parameter'}), 400
    try:
        token_data = exchange_code_for_token(code)
        aliexpress_tokens['access_token'] = token_data.get('access_token')
        aliexpress_tokens['refresh_token'] = token_data.get('refresh_token')
        aliexpress_tokens['expires_in'] = token_data.get('expires_in')
        return jsonify({'success': True,'message':'OAuth2 autenticação realizada com sucesso!','token_data': token_data})
    except Exception as e:
        print(f"❌ Erro ao trocar código por token: {e}")
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
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401

    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    try:
        data = ali_request('aliexpress.ds.product.list', access_token, {
            'keywords': keywords,
            'page_no': page,
            'page_size': page_size
        })
        products = data.get('result', {}).get('products', [])
        return jsonify({'success': True, 'products': products, 'raw': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
