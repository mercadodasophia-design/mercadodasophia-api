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

# Configurações da API oficial do AliExpress
APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
API_BASE_URL = 'https://api-sg.aliexpress.com/sync'

# URL de callback dinâmica para produção
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL')
CALLBACK_URL = RENDER_EXTERNAL_URL + '/api/aliexpress/oauth-callback' if RENDER_EXTERNAL_URL else 'https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback'

print(f"🔑 APP_KEY carregado: {'✅' if APP_KEY else '❌'} - Valor: {APP_KEY}")
print(f"🔑 APP_SECRET carregado: {'✅' if APP_SECRET else '❌'} - Valor: {APP_SECRET[:10] if APP_SECRET else 'N/A'}...")

# Armazenamento simples de tokens em memória
aliexpress_tokens = {}

# Função para timestamp correto (GMT+8)
def ali_timestamp():
    return (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

def generate_sign(params):
    """Gerar assinatura MD5 para a API do AliExpress"""
    sorted_params = sorted(params.items())
    param_string = ''.join(f"{k}{v}" for k,v in sorted_params)
    sign_string = f"{APP_SECRET}{param_string}{APP_SECRET}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def search_aliexpress_official(query):
    try:
        print(f"🔍 Buscando produtos reais via API oficial: {query}")
        access_token = aliexpress_tokens.get('access_token')
        if not access_token:
            print("❌ Sem access_token - precisa fazer OAuth2 primeiro")
            return []

        params = {
            'method': 'aliexpress.solution.product.list',
            'app_key': APP_KEY,
            'access_token': access_token,
            'timestamp': ali_timestamp(),
            'sign_method': 'md5',
            'page_size': '20',
            'page_index': '1',
            'keywords': query,
        }
        params['sign'] = generate_sign(params)
        print(f"📡 Fazendo requisição para API oficial...")
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta da API: {data}")
            if 'result' in data and 'products' in data['result']:
                products = [
                    {
                        'id': item.get('product_id', ''),
                        'title': item.get('product_title', ''),
                        'price': item.get('product_price', ''),
                        'original_price': item.get('product_original_price', ''),
                        'image': item.get('product_main_image', ''),
                        'rating': float(item.get('product_rating', 0)),
                        'reviews': int(item.get('product_review_count', 0)),
                        'seller': item.get('seller_name', 'AliExpress Seller'),
                        'aliexpress_url': item.get('product_url', ''),
                        'aliexpress_id': item.get('product_id', '')
                    }
                    for item in data['result']['products']
                ]
                print(f"🎯 Encontrados {len(products)} produtos reais")
                return products
            else:
                print(f"❌ Estrutura de resposta inesperada: {data}")
                return []
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erro na busca oficial: {e}")
        return []

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
        'timestamp': ali_timestamp(),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
    }
    data['sign'] = generate_sign(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    print(f"🔄 Fazendo requisição OAuth2...")
    print(f"📝 Dados: {data}")

    resp = requests.post(token_url, data=data, headers=headers, timeout=30)
    print(f"📊 Status Code: {resp.status_code}")
    print(f"📄 Response: {resp.text[:500]}...")

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")

@app.route('/api/aliexpress/oauth-callback', methods=['GET', 'POST'])
def aliexpress_oauth_callback():
    code = request.args.get('code') if request.method=='GET' else (
        request.get_json().get('code') if request.is_json else request.form.get('code')
    )
    if not code:
        return jsonify({'error': 'Missing code parameter'}), 400
    try:
        print(f"🔄 Trocando código por token: {code}")
        token_data = exchange_code_for_token(code)
        aliexpress_tokens['access_token'] = token_data.get('access_token')
        aliexpress_tokens['refresh_token'] = token_data.get('refresh_token')
        aliexpress_tokens['expires_in'] = token_data.get('expires_in')
        print(f"✅ Tokens armazenados com sucesso!")
        print(f"🔑 Access Token: {token_data.get('access_token', '')[:20]}...")
        return jsonify({'success': True,'message':'OAuth2 autenticação realizada com sucesso!','token_data': token_data})
    except Exception as e:
        print(f"❌ Erro na troca de código por token: {e}")
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
