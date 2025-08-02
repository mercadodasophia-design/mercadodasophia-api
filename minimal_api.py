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
CALLBACK_URL = RENDER_EXTERNAL_URL + '/api/aliexpress/oauth-callback' if RENDER_EXTERNAL_URL else 'https://mercadodasophia.com/callback'

print(f"🔑 APP_KEY carregado: {'✅' if APP_KEY else '❌'} - Valor: {APP_KEY}")
print(f"🔑 APP_SECRET carregado: {'✅' if APP_SECRET else '❌'} - Valor: {APP_SECRET[:10] if APP_SECRET else 'N/A'}...")

# Armazenamento simples de tokens em memória (pode ser trocado por banco depois)
aliexpress_tokens = {}

# SEM TOKENS FICTÍCIOS - APENAS TOKENS REAIS

def generate_sign(params):
    """Gerar assinatura MD5 para a API do AliExpress"""
    # Ordenar parâmetros
    sorted_params = sorted(params.items())
    
    # Concatenar parâmetros
    param_string = ''
    for key, value in sorted_params:
        param_string += f"{key}{value}"
    
    # Adicionar app_secret no início e fim
    sign_string = f"{APP_SECRET}{param_string}{APP_SECRET}"
    
    # Gerar MD5
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def search_aliexpress_official(query):
    """Buscar produtos usando a API oficial do AliExpress"""
    try:
        print(f"🔍 Buscando produtos reais via API oficial: {query}")
        
        # Parâmetros da requisição
        timestamp = str(int(time.time() * 1000))
        params = {
            'method': 'aliexpress.solution.product.list',  # Método correto para busca
            'app_key': APP_KEY,
            'timestamp': timestamp,
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5',
            'keywords': query,
            'page_size': '20',
            'page_no': '1',
        }
        
        # Gerar assinatura
        sign = generate_sign(params)
        params['sign'] = sign
        
        print(f"📡 Fazendo requisição para API oficial...")
        
        # Fazer requisição
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta da API: {data}")
            
            # Processar resposta real da API
            if 'result' in data and 'products' in data['result']:
                products = []
                for item in data['result']['products']:
                    product = {
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
                    products.append(product)
                
                print(f"🎯 Encontrados {len(products)} produtos reais")
                return products
            else:
                print(f"❌ Estrutura de resposta inesperada: {data}")
                # RETORNAR LISTA VAZIA - NADA DE FICTÍCIO
                return []
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            # RETORNAR LISTA VAZIA - NADA DE FICTÍCIO
            return []
            
    except Exception as e:
        print(f"❌ Erro na busca oficial: {e}")
        # RETORNAR LISTA VAZIA - NADA DE FICTÍCIO
        return []

# FUNÇÃO FICTÍCIA REMOVIDA - NADA DE PRODUTOS FALSOS

# === 1. Gerar URL de autorização OAuth2 ===
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
    url = generate_aliexpress_auth_url()
    return jsonify({'auth_url': url})

# === 2. Trocar código por access_token ===
def exchange_code_for_token(code):
    token_url = 'https://api-sg.aliexpress.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'redirect_uri': CALLBACK_URL,
        'code': code,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    try:
        print(f"🔄 Fazendo requisição para: {token_url}")
        print(f"📝 Dados: {data}")
        
        resp = requests.post(token_url, data=data, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response Headers: {dict(resp.headers)}")
        print(f"📄 Response Text: {resp.text[:1000]}...")
        
        if resp.status_code != 200:
            print(f"❌ Erro HTTP: {resp.status_code}")
            print(f"❌ Resposta: {resp.text}")
            raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")
        
        # Tentar fazer parse do JSON
        try:
            return resp.json()
        except Exception as json_error:
            print(f"❌ Erro ao fazer parse do JSON: {json_error}")
            print(f"📄 Conteúdo da resposta: {resp.text}")
            raise Exception(f"Resposta inválida do AliExpress: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        raise Exception(f"Erro de conexão com AliExpress: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        raise e

@app.route('/api/aliexpress/oauth-callback', methods=['GET', 'POST'])
def aliexpress_oauth_callback():
    # Tentar obter o código de diferentes formas
    code = None
    
    # Se for GET, pegar dos parâmetros da URL
    if request.method == 'GET':
        code = request.args.get('code')
    
    # Se for POST, tentar do JSON ou form data
    elif request.method == 'POST':
        if request.is_json:
            code = request.get_json().get('code')
        else:
            code = request.form.get('code')
    
    if not code:
        return jsonify({'error': 'Missing code parameter'}), 400
    
    try:
        print(f"🔄 Trocando código por token: {code}")
        token_data = exchange_code_for_token(code)
        
        # Armazenar tokens em memória (pode ser melhorado depois)
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

@app.route('/api/search')
def search():
    keywords = request.args.get('keywords', '').lower()
    
    if not keywords:
        return jsonify({
            'success': True,
            'products': []
        })
    
    # Buscar produtos via API oficial do AliExpress
    products = search_aliexpress_official(keywords)
    
    print(f"🎯 Retornando {len(products)} produtos reais para: {keywords}")
    
    return jsonify({
        'success': True,
        'products': products
    })

@app.route('/api/aliexpress/products')
def aliexpress_products():
    """
    Busca produtos reais do AliExpress usando OAuth2.
    Parâmetros: keywords, page, page_size
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    
    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    # Timestamp no formato yyyy-MM-dd HH:mm:ss
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    params = {
        'method': 'aliexpress.ds.product.list',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'page_size': page_size,
        'page_no': page,
        'keywords': keywords,
    }
    params['sign'] = generate_sign(params)
    
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Extrair produtos reais do resultado
        products = data.get('result', {}).get('products', [])
        return jsonify({'success': True, 'products': products, 'raw': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/import-product', methods=['POST'])
def aliexpress_import_product():
    """
    Importa um produto real do AliExpress para o catálogo local.
    Recebe: { "product_id": "..." }
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Faltando product_id'}), 400
    
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    params = {
        'method': 'aliexpress.solution.product.info.get',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'product_id': product_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        product_data = resp.json()
        # Simular persistência local (pode ser trocado por banco depois)
        # Exemplo: salvar em lista/dict em memória
        # local_catalog[product_id] = product_data
        return jsonify({'success': True, 'product': product_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/create-order', methods=['POST'])
def aliexpress_create_order():
    """
    Cria um pedido no AliExpress.
    Recebe: { ...dados do pedido... }
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    data = request.get_json() or {}
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.trade.create',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        **data
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/pay-order', methods=['POST'])
def aliexpress_pay_order():
    """
    Paga um pedido no AliExpress.
    Recebe: { "order_id": "..." }
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.trade.pay',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/order-status', methods=['GET'])
def aliexpress_order_status():
    """
    Consulta status/detalhes de um pedido no AliExpress.
    Parâmetro: order_id
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.trade.get',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/cancel-order', methods=['POST'])
def aliexpress_cancel_order():
    """
    Cancela um pedido no AliExpress.
    Recebe: { "order_id": "..." }
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.trade.cancel',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/refund-order', methods=['POST'])
def aliexpress_refund_order():
    """
    Solicita reembolso de um pedido no AliExpress.
    Recebe: { "order_id": "..." }
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.trade.refund.submit',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/track-order', methods=['GET'])
def aliexpress_track_order():
    """
    Rastreia um pedido no AliExpress.
    Parâmetro: order_id
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.logistics.buyer.tracking',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/logistics-info', methods=['GET'])
def aliexpress_logistics_info():
    """
    Obtém informações logísticas de um pedido no AliExpress.
    Parâmetro: order_id
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'Faltando order_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.logistics.get',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'order_id': order_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/shipping-methods', methods=['GET'])
def aliexpress_shipping_methods():
    """
    Obtém métodos de envio disponíveis no AliExpress.
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.logistics.redefining.getonlinelogisticsservicelist',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/categories', methods=['GET'])
def aliexpress_categories():
    """
    Obtém todas as categorias filhas do AliExpress.
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.category.redefining.getallchildattributesresult',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aliexpress/category-attributes', methods=['GET'])
def aliexpress_category_attributes():
    """
    Obtém atributos de uma categoria específica do AliExpress.
    Parâmetro: category_id
    """
    access_token = aliexpress_tokens.get('access_token')
    if not access_token:
        return jsonify({'error': 'AliExpress não autenticado. Faça login OAuth2 primeiro.'}), 401
    category_id = request.args.get('category_id')
    if not category_id:
        return jsonify({'error': 'Faltando category_id'}), 400
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = {
        'method': 'aliexpress.category.redefining.getchildattributesresult',
        'access_token': access_token,
        'app_key': APP_KEY,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'category_id': category_id,
    }
    params['sign'] = generate_sign(params)
    try:
        resp = requests.post(API_BASE_URL, data=params, timeout=30)
        resp.raise_for_status()
        return jsonify({'success': True, 'result': resp.json()})
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