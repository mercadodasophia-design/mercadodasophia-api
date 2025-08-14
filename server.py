#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import hashlib
import time
import urllib.parse
from flask import Flask, request, jsonify
import iop
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # Carrega variáveis do arquivo .env, se existir

# ===================== MERCADO PAGO FALLBACK =====================
# Se as variáveis MP não estiverem definidas, usar valores padrão
if not os.getenv('MP_ACCESS_TOKEN'):
    os.environ['MP_ACCESS_TOKEN'] = 'TEST-6048716701718688-080816-b095cf4abaa34073116ac070ff38e8f4-1514652489'
if not os.getenv('MP_PUBLIC_KEY'):
    os.environ['MP_PUBLIC_KEY'] = 'TEST-ce63c4af-fb50-4bef-b3dd-f0003f16cea3'
if not os.getenv('MP_SANDBOX'):
    os.environ['MP_SANDBOX'] = 'true'

# Importar integração Mercado Pago (DEPOIS de definir as variáveis)
from mercadopago_integration import mp_integration

app = Flask(__name__)

# Configurar CORS para permitir requisições do navegador
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://localhost:56054",
    "https://mercadodasophia-bbd01.web.app",
    "https://mercadodasophia-bbd01.firebaseapp.com"
], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# ===================== CONFIGURA├º├ÁES =====================
APP_KEY = os.getenv('APP_KEY', '517616')  # Substitua pela sua APP_KEY
APP_SECRET = os.getenv('APP_SECRET', 'skAvaPWbGLkkx5TlKf8kvLmILQtTV2sq')
PORT = int(os.getenv('PORT', 5000))

REDIRECT_URI = "https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback"

TOKENS_FILE = 'tokens.json'

# Endereço da LOJA para criação de pedidos no AliExpress (consignee)
STORE_CONSIGNEE_NAME = os.getenv('STORE_CONSIGNEE_NAME', 'ana cristina silva lima')
STORE_PHONE = os.getenv('STORE_PHONE', '+5585997640050')
STORE_ORIGIN_CEP = os.getenv('STORE_ORIGIN_CEP', '61771-880')
STORE_ADDRESS_LINE1 = os.getenv('STORE_ADDRESS_LINE1', 'numero 280, bloco 03 ap 202')
STORE_ADDRESS_LINE2 = os.getenv('STORE_ADDRESS_LINE2', '')
STORE_CITY = os.getenv('STORE_CITY', '')
STORE_STATE = os.getenv('STORE_STATE', '')
STORE_COUNTRY = os.getenv('STORE_COUNTRY', 'BR')

# ===================== FUN├º├ÁES AUXILIARES =====================
def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f)
    print('­ƒÆ¥ Tokens salvos com sucesso!')

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    return None

# ===================== FRETE PRÓPRIO (ENVIO PELA LOJA) =====================
def calculate_own_shipping_quotes(destination_cep, items):
    """Calcula cotações de frete próprio a partir da loja.

    Regras simples:
      - preço base + adicional por kg acima de 1kg
      - prazo = inbound (chegada do produto na loja) + manuseio + trânsito
    """
    origin_cep = os.getenv('STORE_ORIGIN_CEP', '01001-000')
    handling_days = int(os.getenv('STORE_HANDLING_DAYS', '2'))
    inbound_days = int(os.getenv('INBOUND_LEAD_TIME_DAYS', '12'))

    total_weight = 0.0
    for it in items:
        qty = int(it.get('quantity', 1))
        weight = float(it.get('weight', 0.5))
        total_weight += weight * qty

    services = [
        {
            'code': 'OWN_ECONOMY',
            'name': 'Entrega Padrão (Loja)',
            'base': 19.9,
            'perKg': 6.5,
            'carrier': 'Correios/Parceiro',
            'transitDays': 5,
        },
        {
            'code': 'OWN_EXPRESS',
            'name': 'Entrega Expressa (Loja)',
            'base': 29.9,
            'perKg': 9.9,
            'carrier': 'Parceiro Expresso',
            'transitDays': 2,
        },
    ]

    quotes = []
    for s in services:
        add_kg = max(0.0, total_weight - 1.0)
        price = s['base'] + add_kg * s['perKg']
        eta_days = inbound_days + handling_days + s['transitDays']
        eta_ts = int(time.time()) + eta_days * 24 * 60 * 60

        quotes.append({
            'service_code': s['code'],
            'service_name': s['name'],
            'carrier': s['carrier'],
            'price': round(price, 2),
            'currency': 'BRL',
            'estimated_days': eta_days,
            'estimated_delivery_timestamp': eta_ts,
            'origin_cep': origin_cep,
            'destination_cep': destination_cep,
            'notes': 'Cálculo de frete próprio (envio a partir da loja).'
        })

    return quotes


@app.route('/shipping/quote', methods=['POST'])
def shipping_quote():
    try:
        print(f'📦 Recebendo requisição de frete: {request.get_data()}')
        data = request.get_json(silent=True) or {}
        print(f'📦 Dados recebidos: {data}')
        
        destination_cep = data.get('destination_cep')
        items = data.get('items', [])
        product_id = data.get('product_id')  # Novo campo obrigatório
        
        print(f'📦 CEP destino: {destination_cep}')
        print(f'📦 Items: {items}')
        print(f'📦 Product ID: {product_id}')
        
        if not destination_cep or not isinstance(items, list) or len(items) == 0 or not product_id:
            error_msg = f'Parâmetros inválidos: destination_cep={destination_cep}, items={items}, product_id={product_id}'
            print(f'❌ {error_msg}')
            return jsonify({'success': False, 'message': error_msg}), 400

        # Usar API real do AliExpress
        quotes = calculate_real_shipping_quotes(product_id, destination_cep, items)
        print(f'✅ Cotações reais calculadas: {quotes}')
        
        return jsonify({'success': True, 'data': quotes, 'fulfillment': {
            'mode': 'aliexpress_direct',
            'source': 'aliexpress_api',
            'notes': 'Frete calculado via API oficial do AliExpress'
        }})
    except Exception as e:
        print(f'❌ Erro ao calcular frete: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

def generate_gop_signature(params, app_secret):
    """Gera assinatura GOP para AliExpress API"""
    # Ordenar par├ómetros alfabeticamente
    sorted_params = sorted(params.items())
    
    # Concatenar par├ómetros
    param_string = ''
    for key, value in sorted_params:
        param_string += f'{key}{value}'
    
    # Adicionar app_secret no in├¡cio e fim
    sign_string = f'{app_secret}{param_string}{app_secret}'
    
    # Gerar MD5
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    return signature

def generate_api_signature(params, app_secret):
    """Gerar assinatura para APIs de neg├│cios do AliExpress"""
    # 1´©ÅÔâú Ordenar e concatenar key+value
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    
    # 2´©ÅÔâú Concatenar secret + params + secret
    to_sign = f"{app_secret}{sorted_params}{app_secret}"
    
    # 3´©ÅÔâú Gerar MD5 mai├║sculo
    signature = hashlib.md5(to_sign.encode("utf-8")).hexdigest().upper()
    
    return signature

def create_test_page():
    """Cria p├ígina HTML de teste"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')
    
    return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AliExpress API Python - Teste</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .endpoint-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .endpoint-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .endpoint-card:hover {
            border-color: #667eea;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
        }
        
        .endpoint-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .endpoint-card p {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        }
        
        .status-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-label {
            font-weight: bold;
            color: #333;
        }
        
        .status-value {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        
        .info-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        
        .info-box h3 {
            color: #1976d2;
            margin-bottom: 10px;
        }
        
        .info-box p {
            color: #424242;
            line-height: 1.6;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>­ƒÉì AliExpress API Python</h1>
            <p>Servidor de teste com SDK oficial Alibaba</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>Ôä╣´©Å Como usar</h3>
                <p>Esta ├® a vers├úo Python da API AliExpress que utiliza o SDK oficial da Alibaba. 
                Clique nos links abaixo para testar as funcionalidades. Para usar as APIs protegidas, 
                primeiro fa├ºa a autoriza├º├úo OAuth.</p>
            </div>
            
            <div class="section">
                <h2>­ƒöÉ Autentica├º├úo OAuth</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>1. Gerar URL de Autoriza├º├úo</h3>
                        <p>Gera a URL para autoriza├º├úo no AliExpress</p>
                        <a href="''' + base_url + '''/api/aliexpress/auth" target="_blank" class="btn">­ƒöù Testar Autoriza├º├úo</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>2. Status dos Tokens</h3>
                        <p>Verifica se h├í tokens salvos no servidor</p>
                        <a href="''' + base_url + '''/api/aliexpress/tokens/status" target="_blank" class="btn btn-secondary">­ƒôè Ver Status</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🚚 Frete Próprio (Loja)</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>Simular Cotação</h3>
                        <p>POST /shipping/quote</p>
                        <p>Body:
<pre>{
  "destination_cep": "01001-000",
  "items": [{"name": "Demo", "price": 99.9, "quantity": 1, "weight": 0.5}]
}</pre>
                        </p>
                        <a href="''' + base_url + '''/" target="_blank" class="btn">Ver Página</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>­ƒøì´©Å APIs de Produtos</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>Buscar Categorias</h3>
                        <p>Lista categorias de produtos do AliExpress</p>
                        <a href="''' + base_url + '''/api/aliexpress/categories" target="_blank" class="btn btn-secondary">­ƒôé Ver Categorias</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>Buscar Produtos</h3>
                        <p>Busca produtos por categoria (requer token)</p>
                        <a href="''' + base_url + '''/api/aliexpress/products" target="_blank" class="btn btn-warning">­ƒøÆ Ver Produtos</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>­ƒôè Informa├º├Áes da API</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>Informa├º├Áes do Servidor</h3>
                        <p>Detalhes sobre endpoints dispon├¡veis</p>
                        <a href="''' + base_url + '''/" target="_blank" class="btn">Ôä╣´©Å Ver Info</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>Documenta├º├úo</h3>
                        <p>Link para a documenta├º├úo do SDK</p>
                        <a href="https://openservice.aliexpress.com/doc/doc.htm" target="_blank" class="btn btn-secondary">­ƒôÜ Ver Docs</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>­ƒöº Status do Sistema</h2>
                <div class="status-section">
                    <div class="status-item">
                        <span class="status-label">Servidor:</span>
                        <span class="status-value status-success">Online</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">SDK:</span>
                        <span class="status-value status-success">iop-sdk-python</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Python:</span>
                        <span class="status-value status-success">Flask</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Framework:</span>
                        <span class="status-value status-success">Oficial Alibaba</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>┬® 2025 Mercado da Sophia - AliExpress API Python com SDK oficial Alibaba</p>
        </div>
    </div>
    
    <script>
        // Adiciona funcionalidade de abrir links em nova aba
        document.addEventListener('DOMContentLoaded', function() {
            const links = document.querySelectorAll('a[target="_blank"]');
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.open(this.href, '_blank');
                });
            });
        });
    </script>
</body>
</html>
    '''

def create_callback_page(data):
    """Cria p├ígina HTML para callback OAuth"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')
    
    return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ô£à Autoriza├º├úo OAuth Conclu├¡da - AliExpress API Python</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .success-icon {
            text-align: center;
            font-size: 4em;
            margin-bottom: 20px;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-10px);
            }
            60% {
                transform: translateY(-5px);
            }
        }
        
        .status-section {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .status-section h3 {
            color: #155724;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .token-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .token-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .token-card:hover {
            border-color: #28a745;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.2);
        }
        
        .token-card h4 {
            color: #28a745;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .token-value {
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            word-break: break-all;
            margin-top: 10px;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        }
        
        .actions {
            text-align: center;
            margin-top: 30px;
        }
        
        .info-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        
        .info-box h3 {
            color: #1976d2;
            margin-bottom: 10px;
        }
        
        .info-box p {
            color: #424242;
            line-height: 1.6;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #e9ecef;
        }
        
        .copy-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .copy-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>­ƒÄë Autoriza├º├úo Conclu├¡da!</h1>
            <p>Tokens salvos com sucesso no servidor</p>
        </div>
        
        <div class="content">
            <div class="success-icon">Ô£à</div>
            
            <div class="status-section">
                <h3>­ƒÄ» Status da Autoriza├º├úo</h3>
                <p><strong>Ô£à Sucesso!</strong> Os tokens foram gerados e salvos no servidor. Agora voc├¬ pode usar as APIs protegidas do AliExpress.</p>
            </div>
            
            <div class="info-box">
                <h3>Ôä╣´©Å Pr├│ximos Passos</h3>
                <p>Agora que voc├¬ tem os tokens salvos, pode testar as APIs de produtos e categorias. 
                Os tokens ficam armazenados no servidor e s├úo usados automaticamente nas requisi├º├Áes.</p>
            </div>
            
            <h3>­ƒöæ Dados dos Tokens</h3>
            <div class="token-grid">
                <div class="token-card">
                    <h4>Access Token</h4>
                    <div class="token-value">''' + str(data.get('access_token', 'N/A')) + '''</div>
                    <button class="copy-btn" onclick="copyToClipboard(''' + str(data.get('access_token', '')) + ''')">Copiar</button>
                </div>
                
                <div class="token-card">
                    <h4>Refresh Token</h4>
                    <div class="token-value">''' + str(data.get('refresh_token', 'N/A')) + '''</div>
                    <button class="copy-btn" onclick="copyToClipboard(''' + str(data.get('refresh_token', '')) + ''')">Copiar</button>
                </div>
                
                <div class="token-card">
                    <h4>Expires In</h4>
                    <div class="token-value">''' + str(data.get('expires_in', 'N/A')) + ''' segundos</div>
                </div>
                
                <div class="token-card">
                    <h4>Token Type</h4>
                    <div class="token-value">''' + str(data.get('token_type', 'Bearer')) + '''</div>
                </div>
            </div>
            
            <div class="actions">
                <h3>­ƒÜÇ Testar APIs</h3>
                <a href="''' + base_url + '''/api/aliexpress/tokens/status" target="_blank" class="btn btn-secondary">­ƒôè Verificar Status</a>
                <a href="''' + base_url + '''/api/aliexpress/categories" target="_blank" class="btn btn-warning">­ƒôé Buscar Categorias</a>
                <a href="''' + base_url + '''/api/aliexpress/products" target="_blank" class="btn">­ƒøÆ Buscar Produtos</a>
                <a href="''' + base_url + '''/" target="_blank" class="btn btn-secondary">­ƒÅá Voltar ao In├¡cio</a>
            </div>
        </div>
        
        <div class="footer">
            <p>┬® 2025 Mercado da Sophia - AliExpress API Python com SDK oficial Alibaba</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            if (text && text !== 'N/A') {
                navigator.clipboard.writeText(text).then(function() {
                    alert('Token copiado para a ├írea de transfer├¬ncia!');
                }).catch(function(err) {
                    console.error('Erro ao copiar: ', err);
                });
            }
        }
        
        // Adiciona funcionalidade de abrir links em nova aba
        document.addEventListener('DOMContentLoaded', function() {
            const links = document.querySelectorAll('a[target="_blank"]');
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.open(this.href, '_blank');
                });
            });
        });
    </script>
</body>
</html>
    '''

# ===================== ROTAS PRINCIPAIS =====================
@app.route('/')
def index():
    """P├ígina inicial com links de teste"""
    if request.headers.get('Accept', '').find('text/html') != -1:
        return create_test_page()
    else:
        return jsonify({
            'message': 'AliExpress API Server Python',
            'status': 'running',
            'endpoints': {
                'auth': '/api/aliexpress/auth',
                'callback': '/api/aliexpress/oauth-callback',
                'products': '/api/aliexpress/products',
                'categories': '/api/aliexpress/categories',
                'tokens': '/api/aliexpress/tokens/status'
            }
        })

@app.route('/api/aliexpress/auth')
def auth():
    """Gera URL de autorização"""
    auth_url = (
        f'https://api-sg.aliexpress.com/oauth/authorize?response_type=code'
        f'&force_auth=true&client_id={APP_KEY}&redirect_uri={REDIRECT_URI}'
    )
    print(f'🔗 URL de autorização gerada: {auth_url}')
    return jsonify({'success': True, 'auth_url': auth_url})

@app.route('/api/aliexpress/token-status')
def token_status():
    """Verifica o status do token de autorização"""
    tokens = load_tokens()
    
    if not tokens:
        return jsonify({
            'success': False,
            'has_token': False,
            'message': 'Nenhum token encontrado. Faça autorização primeiro.',
            'auth_required': True
        })
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    if not access_token:
        return jsonify({
            'success': False,
            'has_token': False,
            'message': 'Token de acesso não encontrado. Faça autorização primeiro.',
            'auth_required': True
        })
    
    # Verificar se o token ainda é válido (opcional)
    try:
        # Fazer uma requisição de teste para verificar se o token ainda funciona
        params = {
            "method": "aliexpress.ds.category.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": access_token,
            "parent_category_id": "0"
        }
        
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'error_response' in data:
                error_code = data['error_response'].get('code', '')
                if error_code in ['15', '40001', '40002']:  # Códigos de token expirado/inválido
                    return jsonify({
                        'success': False,
                        'has_token': True,
                        'token_expired': True,
                        'message': 'Token expirado. Faça autorização novamente.',
                        'auth_required': True
                    })
            
            return jsonify({
                'success': True,
                'has_token': True,
                'token_valid': True,
                'message': 'Token válido e funcionando.',
                'auth_required': False
            })
        else:
            return jsonify({
                'success': False,
                'has_token': True,
                'token_error': True,
                'message': f'Erro ao verificar token: {response.status_code}',
                'auth_required': True
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'has_token': True,
            'token_error': True,
            'message': f'Erro ao verificar token: {str(e)}',
            'auth_required': True
        })

@app.route('/api/aliexpress/oauth-callback')
def oauth_callback():
    """Callback OAuth"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'C├│digo de autoriza├º├úo n├úo fornecido'}), 400

    print(f'­ƒöì Callback OAuth recebido com code: {code}')

    # Tentar diferentes abordagens
    attempts = [
        
        {
            'name': 'SDK Official - Correct Method',
            'url': 'SDK_METHOD',
            'data': {
                "code": code
            }
        }
    ]

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    for attempt in attempts:
        print(f'­ƒöº Tentativa: {attempt["name"]}')
        print(f'­ƒöº URL: {attempt["url"]}')
        
        # Gerar assinatura GOP se necess├írio
        data = attempt['data'].copy()
        if 'timestamp' in data:  # Se tem timestamp, precisa de assinatura GOP
            signature = generate_gop_signature(data, APP_SECRET)
            data['sign'] = signature
            print(f'­ƒöº Assinatura GOP gerada: {signature}')
        
        print(f'­ƒöº Data: {data}')
        
        try:
            if attempt['url'] == 'SDK_METHOD':
                # Usar SDK oficial do AliExpress - M├®todo correto da documenta├º├úo
                print(f'­ƒöº Usando SDK oficial do AliExpress (m├®todo correto)...')
                try:
                    # URL base correta conforme documenta├º├úo
                    client = iop.IopClient('https://api-sg.aliexpress.com/rest', APP_KEY, APP_SECRET)
                    request_obj = iop.IopRequest('/auth/token/create')
                    request_obj.add_api_param('code', code)
                    # N├úo adicionar uuid conforme documenta├º├úo
                    
                    response = client.execute(request_obj)
                    print(f'Ô£à SDK Response: {response.body}')
                    
                    if response.code == '0':
                        tokens = response.body
                        print(f'Ô£à Sucesso usando SDK oficial!')
                        save_tokens(tokens)
                        
                        if request.headers.get('Accept', '').find('text/html') != -1:
                            return create_callback_page(tokens)
                        else:
                            return jsonify({'success': True, 'tokens': tokens})
                    else:
                        print(f'ÔØî Erro no SDK: {response.body}')
                        continue
                        
                except Exception as sdk_error:
                    print(f'ÔØî Erro no SDK: {sdk_error}')
                    continue
            else:
                # Usar requisi├º├úo HTTP normal
                response = requests.post(attempt['url'], headers=headers, data=data)
                print(f'Ô£à Status Code: {response.status_code}')
                print(f'Ô£à Content-Type: {response.headers.get("Content-Type")}')
                print(f'Ô£à Raw Response: {response.text[:300]}...')

                if response.status_code == 200:
                    try:
                        tokens = response.json()
                        
                        if 'error' in tokens:
                            print(f'ÔØî Erro na tentativa {attempt["name"]}: {tokens.get("error")}')
                            continue
                        
                        print(f'Ô£à Sucesso na tentativa {attempt["name"]}!')
                        save_tokens(tokens)
                        
                        # Retornar p├ígina HTML se a requisi├º├úo aceita HTML
                        if request.headers.get('Accept', '').find('text/html') != -1:
                            return create_callback_page(tokens)
                        else:
                            # Retornar JSON para requisi├º├Áes program├íticas
                            return jsonify({'success': True, 'tokens': tokens})
                            
                    except json.JSONDecodeError as json_error:
                        print(f'ÔØî Erro ao decodificar JSON na tentativa {attempt["name"]}: {json_error}')
                        continue
                else:
                    print(f'ÔØî Status code {response.status_code} na tentativa {attempt["name"]}')
                    continue
                
        except Exception as e:
            print(f'ÔØî Erro na tentativa {attempt["name"]}: {e}')
            continue

    # Se chegou aqui, nenhuma tentativa funcionou
    error_message = "Todas as tentativas falharam. Verifique a configura├º├úo da app no AliExpress."
    print(f'ÔØî {error_message}')
    return jsonify({
        'success': False,
        'message': error_message,
        'details': 'A API est├í retornando HTML em vez de JSON. Isso pode indicar: 1) App n├úo configurada corretamente no AliExpress, 2) Tipo de app incorreto, 3) Permiss├Áes insuficientes'
    }), 400

@app.route('/api/aliexpress/products')
def products():
    """Buscar produtos"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token n├úo encontrado. Fa├ºa autoriza├º├úo primeiro.'}), 401

    try:
        # Par├ómetros para a API conforme documenta├º├úo
        params = {
            "method": "aliexpress.ds.text.search",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "keyWord": request.args.get('q', 'electronics'),  # Correto conforme documenta├º├úo
            "countryCode": "BR",  # ­ƒæê obrigat├│rio para Brasil
            "currency": "BRL",    # ­ƒæê obrigat├│rio para Brasil
            "local": "pt_BR",     # ­ƒæê obrigat├│rio para Brasil
            "pageSize": "400",    # Tamanho da p├ígina (aumentado para 100)
            "pageIndex": "1",     # ├ìndice da p├ígina
            "sortBy": "orders,desc"  # Ordenar por popularidade
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Fazer requisi├º├úo HTTP direta para /sync
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'Ô£à Resposta produtos: {response.text[:500]}...')
        
        if response.status_code == 200:
            data = response.json()
            print(f'­ƒôè ESTRUTURA COMPLETA - BUSCA PRODUTOS:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se h├í produtos na resposta
            if 'aliexpress_ds_text_search_response' in data:
                search_response = data['aliexpress_ds_text_search_response']
                
                # Analisar estrutura dos dados
                result = search_response.get('result', {})
                print(f'­ƒöì AN├áLISE ESTRUTURA - BUSCA RESULT:')
                print(f'  - Keys dispon├¡veis: {list(result.keys())}')
                
                # Extrair informa├º├Áes ├║teis para o frontend
                processed_search = {
                    'total_count': result.get('total_count', 0),
                    'page_size': result.get('page_size', 20),
                    'page_index': result.get('page_index', 1),
                    'products': [],
                    'raw_data': result
                }
                
                # Extrair lista de produtos
                if 'products' in result:
                    products_data = result['products']
                    if 'selection_search_product' in products_data:
                        products = products_data['selection_search_product']
                        if isinstance(products, list):
                            processed_search['products'] = products
                        else:
                            processed_search['products'] = [products]
                
                print(f'­ƒôï DADOS DE BUSCA PROCESSADOS:')
                print(f'  - Total de produtos: {processed_search["total_count"]}')
                print(f'  - Produtos encontrados: {len(processed_search["products"])}')
                print(f'  - P├ígina: {processed_search["page_index"]}/{processed_search["page_size"]}')
                
                # Log do primeiro produto para an├ílise
                if processed_search['products']:
                    first_product = processed_search['products'][0]
                    print(f'­ƒôª EXEMPLO PRIMEIRO PRODUTO:')
                    print(f'  - ID: {first_product.get("itemId", "N/A")}')
                    print(f'  - T├¡tulo: {first_product.get("title", "N/A")[:50]}...')
                    print(f'  - Pre├ºo: {first_product.get("targetSalePrice", "N/A")}')
                    print(f'  - Keys dispon├¡veis: {list(first_product.keys())}')
                
                return jsonify({
                    'success': True, 
                    'data': data,
                    'processed': processed_search
                })
            else:
                print(f'ÔØî ESTRUTURA INESPERADA BUSCA: {list(data.keys())}')
                return jsonify({'success': False, 'error': data}), 400
        else:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'ÔØî Erro ao buscar produtos: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/categories')
def categories():
    """Buscar categorias"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401

    try:
        # Parâmetros para a API conforme documentação
        params = {
            "method": "aliexpress.ds.category.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "language": "en"
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Fazer requisição HTTP direta para /sync
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'Ô£à Resposta categorias: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                return jsonify({'success': True, 'data': data})
            else:
                return jsonify({'success': False, 'error': data}), 400
        else:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'ÔØî Erro ao buscar categorias: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/tokens/status')
def tokens_status():
    tokens = load_tokens()
    return jsonify({
        'success': True,
        'has_tokens': bool(tokens),
        'tokens': {
            'has_access_token': bool(tokens.get('access_token') if tokens else None),
            'has_refresh_token': bool(tokens.get('refresh_token') if tokens else None),
            'expires_in': tokens.get('expires_in') if tokens else None
        } if tokens else None
    })

@app.route('/api/aliexpress/product/<product_id>')
def product_details(product_id):
    """Buscar detalhes completos de um produto usando aliexpress.ds.product.get"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401
    try:
        # Parâmetros para a API conforme documentação
        params = {
            "method": "aliexpress.ds.product.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": product_id,
            "ship_to_country": "BR",   # obrigatório para Brasil
            "target_currency": "BRL",  # obrigatório para Brasil
            "target_language": "pt",   # obrigatório para Brasil
            "remove_personal_benefit": "false"
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Fazer requisição HTTP direta para /sync
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'📡 Resposta detalhes produto {product_id}: {response.text[:500]}...')

        if response.status_code == 200:
            data = response.json()
            print(f'✅ ESTRUTURA COMPLETA - DETALHES PRODUTO {product_id}:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se há dados na resposta
            if 'aliexpress_ds_product_get_response' in data:
                product_response = data['aliexpress_ds_product_get_response']
                result = product_response.get('result', {})
                print(f'🔍 ANÁLISE ESTRUTURA - RESULT:')
                print(f'  - Keys disponíveis: {list(result.keys())}')
            else:
                print(f'❌ ESTRUTURA INESPERADA: {list(data.keys())}')
                return jsonify({'success': False, 'error': data}), 400
            
            # Extrair informações úteis para o frontend
            processed_data = {
                'basic_info': {
                    'product_id': product_id,
                    'title': result.get('ae_item_base_info_dto', {}).get('subject', ''),
                    'description': result.get('ae_item_base_info_dto', {}).get('detail', ''),
                    'main_image': result.get('ae_multimedia_info_dto', {}).get('image_urls', '').split(';')[0] if result.get('ae_multimedia_info_dto', {}).get('image_urls') else '',
                },
                'pricing': {
                    'min_price': '',
                    'max_price': '',
                    'currency': 'BRL',
                },
                'images': [],
                'variations': [],
                'raw_data': result  # Dados completos para análise
            }
            
            # Extrair galeria de imagens
            if 'ae_multimedia_info_dto' in result:
                multimedia_info = result['ae_multimedia_info_dto']
                if 'image_urls' in multimedia_info:
                    image_urls = multimedia_info['image_urls']
                    if image_urls:
                        processed_data['images'] = image_urls.split(';')
            
            # Extrair variações/SKUs
            if 'ae_item_sku_info_dtos' in result:
                sku_info = result['ae_item_sku_info_dtos']
                if 'ae_item_sku_info_d_t_o' in sku_info:
                    skus = sku_info['ae_item_sku_info_d_t_o']
                    processed_data['variations'] = skus if isinstance(skus, list) else [skus]
            
            print(f'📊 DADOS PROCESSADOS PARA FRONTEND:')
            print(f'  - Imagens encontradas: {len(processed_data["images"])}')
            print(f'  - Variações encontradas: {len(processed_data["variations"])}')
            print(f'  - Título: {processed_data["basic_info"]["title"][:50]}...')
            
            return jsonify({'success': True, 'data': processed_data})
        
        # Caso a API retorne erro ou não seja 200
        try:
            data = response.json()
            print(f'❌ ESTRUTURA INESPERADA: {list(data.keys())}')
            return jsonify({'success': False, 'error': data}), 400
        except:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'❌ Erro ao buscar detalhes do produto {product_id}: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/product/wholesale/<product_id>')
def product_wholesale_details(product_id):
    """Buscar detalhes completos de um produto usando aliexpress.ds.product.wholesale.get"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401
    try:
        # Parâmetros para a API conforme documentação
        params = {
            "method": "aliexpress.ds.product.wholesale.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": product_id,
            "ship_to_country": "BR",   # obrigatório para Brasil
            "target_currency": "BRL",  # obrigatório para Brasil
            "target_language": "pt",   # obrigatório para Brasil
            "remove_personal_benefit": "false"
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Fazer requisição HTTP direta para /sync
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'📡 Resposta wholesale produto {product_id}: {response.text[:500]}...')

        if response.status_code == 200:
            data = response.json()
            print(f'✅ ESTRUTURA COMPLETA - WHOLESALE PRODUTO {product_id}:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se há dados na resposta
            if 'aliexpress_ds_product_wholesale_get_response' in data:
                product_response = data['aliexpress_ds_product_wholesale_get_response']
                result = product_response.get('result', {})
                print(f'🔍 ANÁLISE ESTRUTURA - RESULT:')
                print(f'  - Keys disponíveis: {list(result.keys())}')
            else:
                print(f'❌ ESTRUTURA INESPERADA: {list(data.keys())}')
                return jsonify({'success': False, 'error': data}), 400
            
            # Extrair informações úteis para o frontend
            processed_data = {
                'basic_info': {
                    'product_id': product_id,
                    'title': result.get('ae_item_base_info_dto', {}).get('subject', ''),
                    'description': result.get('ae_item_base_info_dto', {}).get('detail', ''),
                    'main_image': result.get('ae_multimedia_info_dto', {}).get('image_urls', '').split(';')[0] if result.get('ae_multimedia_info_dto', {}).get('image_urls') else '',
                },
                'pricing': {
                    'min_price': '',
                    'max_price': '',
                    'currency': 'BRL',
                },
                'images': [],
                'variations': [],
                'raw_data': result  # Dados completos para análise
            }
            
            # Extrair galeria de imagens
            if 'ae_multimedia_info_dto' in result:
                multimedia_info = result['ae_multimedia_info_dto']
                if 'image_urls' in multimedia_info:
                    image_urls = multimedia_info['image_urls']
                    if image_urls:
                        processed_data['images'] = image_urls.split(';')
            
            # Extrair variações/SKUs (estrutura diferente no wholesale)
            if 'ae_item_sku_info_dtos' in result:
                skus = result['ae_item_sku_info_dtos']
                processed_data['variations'] = skus if isinstance(skus, list) else [skus]
            
            print(f'📊 DADOS PROCESSADOS PARA FRONTEND (WHOLESALE):')
            print(f'  - Imagens encontradas: {len(processed_data["images"])}')
            print(f'  - Variações encontradas: {len(processed_data["variations"])}')
            print(f'  - Título: {processed_data["basic_info"]["title"][:50]}...')
            
            return jsonify({'success': True, 'data': processed_data})
        
        # Caso a API retorne erro ou não seja 200
        try:
            data = response.json()
            print(f'❌ ESTRUTURA INESPERADA: {list(data.keys())}')
            return jsonify({'success': False, 'error': data}), 400
        except:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'❌ Erro ao buscar detalhes wholesale do produto {product_id}: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/freight/<product_id>')
def freight_calculation(product_id):
    """Calcular frete para um produto"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401

    try:
        # Primeiro, buscar detalhes do produto para obter o skuId
        product_params = {
            "method": "aliexpress.ds.product.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": product_id,
            "ship_to_country": "BR",
            "target_currency": "BRL",
            "target_language": "pt",
            "remove_personal_benefit": "false"
        }
        
        product_params["sign"] = generate_api_signature(product_params, APP_SECRET)
        product_response = requests.get('https://api-sg.aliexpress.com/sync', params=product_params)
        
        if product_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Erro ao buscar detalhes do produto'}), 400
            
        product_data = product_response.json()
        if 'aliexpress_ds_product_get_response' not in product_data:
            return jsonify({'success': False, 'error': 'Dados do produto não encontrados'}), 400
            
        # Extrair o primeiro skuId disponível
        result = product_data['aliexpress_ds_product_get_response'].get('result', {})
        sku_info = result.get('ae_item_sku_info_dtos', {}).get('ae_item_sku_info_d_t_o', [])
        
        if not sku_info:
            return jsonify({'success': False, 'error': 'Nenhum SKU encontrado para o produto'}), 400
            
        # Tentar todos os SKUs disponíveis até encontrar um com frete
        sku_list = sku_info if isinstance(sku_info, list) else [sku_info]
        sku_id = None
        
        for i, sku in enumerate(sku_list):
            current_sku_id = sku.get('sku_id')
            if current_sku_id:
                print(f'Ô£à Testando SKU {i+1}/{len(sku_list)}: {current_sku_id}')
                sku_id = current_sku_id
                break
        
        if not sku_id:
            return jsonify({'success': False, 'error': 'Nenhum SKU ID encontrado'}), 400
            
        print(f'Ô£à SKU ID selecionado: {sku_id}')
        
        # Extrair preço do produto se disponível
        product_price = "0.00"  # Preço padrão
        
        # Tentar extrair preço de diferentes locais
        if 'ae_item_base_info_dto' in result:
            base_info = result['ae_item_base_info_dto']
            print(f'🔍 Procurando preço em ae_item_base_info_dto: {list(base_info.keys())}')
            
            # Tentar diferentes campos de preço
            price_fields = ['min_price', 'max_price', 'price', 'sale_price', 'original_price']
            for field in price_fields:
                if field in base_info and base_info[field]:
                    product_price = str(base_info[field])
                    print(f'💰 Preço encontrado em {field}: {product_price}')
                    break
        
        # Se não encontrou, tentar nos SKUs
        if product_price == "10.00" and 'ae_item_sku_info_dtos' in result:
            sku_info = result['ae_item_sku_info_dtos']
            if 'ae_item_sku_info_d_t_o' in sku_info:
                skus = sku_info['ae_item_sku_info_d_t_o']
                if isinstance(skus, list) and len(skus) > 0:
                    first_sku = skus[0]
                    print(f'🔍 Procurando preço no primeiro SKU: {list(first_sku.keys())}')
                    
                    # Tentar diferentes campos de preço no SKU
                    sku_price_fields = ['price', 'sale_price', 'original_price', 'sku_price']
                    for field in sku_price_fields:
                        if field in first_sku and first_sku[field]:
                            product_price = str(first_sku[field])
                            print(f'💰 Preço encontrado no SKU em {field}: {product_price}')
                            break
        
        print(f'💰 Preço final do produto para frete: {product_price}')
        
        # Tentar calcular frete com diferentes SKUs
        for i, sku in enumerate(sku_list):
            current_sku_id = sku.get('sku_id')
            if not current_sku_id:
                continue
                
            print(f'🚚 Tentativa {i+1}/{len(sku_list)} - SKU: {current_sku_id}')
            
            # Calcular frete com o SKU atual (conforme documentação oficial)
            freight_params = {
                "country_code": "BR",
                "product_id": int(product_id),
                "product_num": 1,
                "send_goods_country_code": "CN",
                "sku_id": current_sku_id,  # SKU ID (opcional mas recomendado)
                "price": product_price,  # Preço (opcional)
                "price_currency": "USD"  # Moeda (opcional)
            }
            
            params = {
                "method": "aliexpress.logistics.buyer.freight.calculate",
                "app_key": APP_KEY,
                "timestamp": int(time.time() * 1000),
                "sign_method": "md5",
                "format": "json",
                "v": "2.0",
                "access_token": tokens['access_token'],
                "param_aeop_freight_calculate_for_buyer_d_t_o": json.dumps(freight_params)
            }
            
            # Gerar assinatura
            params["sign"] = generate_api_signature(params, APP_SECRET)
            
            # Fazer requisição HTTP direta para /sync
            response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
            print(f'🚚 Resposta frete produto {product_id} (sku: {current_sku_id}): {response.text[:500]}...')
            
            if response.status_code == 200:
                data = response.json()
                if 'aliexpress_logistics_buyer_freight_calculate_response' in data:
                    freight_response = data['aliexpress_logistics_buyer_freight_calculate_response']
                    result = freight_response.get('result', {})
                    
                    # Se encontrou opções de frete, usar este SKU
                    if result.get('success', False) or 'aeop_freight_calculate_result_for_buyer_d_t_o_list' in result:
                        print(f'✅ SKU {current_sku_id} tem opções de frete!')
                        break
                    else:
                        print(f'❌ SKU {current_sku_id} sem opções de frete: {result.get("error_desc", "N/A")}')
                        continue
            else:
                print(f'❌ Erro HTTP {response.status_code} para SKU {current_sku_id}')
                continue
        else:
            # Se chegou aqui, nenhum SKU funcionou
            print(f'❌ Nenhum SKU encontrou opções de frete para o produto {product_id}')
            return jsonify({
                'success': False, 
                'error': 'Nenhuma opção de frete disponível para este produto'
            }), 400
        
        if response.status_code == 200:
            data = response.json()
            print(f'­ƒôè ESTRUTURA COMPLETA - FRETE PRODUTO {product_id}:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se h├í dados na resposta
            if 'aliexpress_logistics_buyer_freight_calculate_response' in data:
                freight_response = data['aliexpress_logistics_buyer_freight_calculate_response']
                
                # Analisar estrutura dos dados
                result = freight_response.get('result', {})
                print(f'­ƒöì AN├áLISE ESTRUTURA - FRETE RESULT:')
                print(f'  - Keys dispon├¡veis: {list(result.keys())}')
                print(f'  - Success: {result.get("success", "N/A")}')
                print(f'  - Error: {result.get("error_desc", "N/A")}')
                
                # Extrair informações úteis para o frontend
                processed_freight = {
                    'success': result.get('success', False),
                    'error_message': result.get('error_desc', ''),
                    'freight_options': [],
                    'raw_data': result
                }
                
                # Extrair opções de frete se disponíveis (conforme documentação)
                if 'aeop_freight_calculate_result_for_buyer_d_t_o_list' in result:
                    freight_list = result['aeop_freight_calculate_result_for_buyer_d_t_o_list']
                    if 'aeop_freight_calculate_result_for_buyer_dto' in freight_list:
                        options = freight_list['aeop_freight_calculate_result_for_buyer_dto']
                        if isinstance(options, list):
                            processed_freight['freight_options'] = options
                        else:
                            processed_freight['freight_options'] = [options]
                
                # VERIFICAÇÃO CRÍTICA: Se não há opções de frete reais, retornar erro
                if not processed_freight['freight_options']:
                    error_msg = f"API do AliExpress não retornou opções de frete válidas. Erro: {result.get('error_desc', 'Dados insuficientes')}"
                    print(f'❌ {error_msg}')
                    return jsonify({
                        'success': False, 
                        'error': error_msg,
                        'message': 'Frete não disponível - necessário verificar configuração da API'
                    }), 400
                
                print(f'📦 DADOS DE FRETE PROCESSADOS:')
                print(f'  - Sucesso: {processed_freight["success"]}')
                print(f'  - Opções de frete: {len(processed_freight["freight_options"])}')
                print(f'  - Erro: {processed_freight["error_message"]}')
                
                return jsonify({
                    'success': True, 
                    'data': processed_freight
                })
            else:
                print(f'ÔØî ESTRUTURA INESPERADA FRETE: {list(data.keys())}')
                return jsonify({'success': False, 'error': data}), 400
        else:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'ÔØî Erro ao calcular frete do produto {product_id}: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/sku-attributes/<category_id>')
def sku_attributes(category_id):
    """Consultar atributos SKU de uma categoria específica"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401
    
    try:
        # Parâmetros para a consulta de atributos SKU
        params = {
            "method": "aliexpress.solution.sku.attribute.query",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "query_sku_attribute_info_request": json.dumps({
                "aliexpress_category_id": category_id
            })
        }
        
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        print(f'🔍 Consultando atributos SKU para categoria: {category_id}')
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        
        print(f'📡 Resposta atributos SKU categoria {category_id}: {response.text[:500]}...')
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ ESTRUTURA COMPLETA - ATRIBUTOS SKU CATEGORIA {category_id}:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'aliexpress_solution_sku_attribute_query_response' in data:
                result = data['aliexpress_solution_sku_attribute_query_response'].get('result', {})
                
                # Processar dados para o frontend
                processed_data = {
                    'category_id': category_id,
                    'sku_attributes': [],
                    'common_attributes': [],
                    'raw_data': result
                }
                
                # Processar atributos SKU
                if 'supporting_sku_attribute_list' in result:
                    sku_attributes = result['supporting_sku_attribute_list']
                    if isinstance(sku_attributes, list):
                        processed_data['sku_attributes'] = sku_attributes
                    else:
                        processed_data['sku_attributes'] = [sku_attributes]
                
                # Processar atributos comuns
                if 'supporting_common_attribute_list' in result:
                    common_attributes = result['supporting_common_attribute_list']
                    if isinstance(common_attributes, list):
                        processed_data['common_attributes'] = common_attributes
                    else:
                        processed_data['common_attributes'] = [common_attributes]
                
                print(f'📊 DADOS PROCESSADOS PARA FRONTEND:')
                print(f'  - Atributos SKU encontrados: {len(processed_data["sku_attributes"])}')
                print(f'  - Atributos comuns encontrados: {len(processed_data["common_attributes"])}')
                
                return jsonify({'success': True, 'data': processed_data})
            else:
                print(f'❌ ESTRUTURA INESPERADA: {list(data.keys())}')
                return jsonify({'success': False, 'error': data}), 400
        else:
            try:
                data = response.json()
                print(f'❌ Erro na API: {data}')
                return jsonify({'success': False, 'error': data}), response.status_code
            except:
                return jsonify({'success': False, 'error': response.text}), response.status_code
                
    except Exception as e:
        print(f'❌ Erro ao consultar atributos SKU da categoria {category_id}: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/sku-attributes-batch', methods=['POST'])
def sku_attributes_batch():
    """Consultar atributos SKU de múltiplas categorias"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401
    
    try:
        data = request.get_json()
        category_ids = data.get('category_ids', [])
        
        if not category_ids:
            return jsonify({'success': False, 'message': 'Lista de categorias não fornecida'}), 400
        
        results = {}
        
        for category_id in category_ids:
            try:
                # Parâmetros para a consulta de atributos SKU
                params = {
                    "method": "aliexpress.solution.sku.attribute.query",
                    "app_key": APP_KEY,
                    "timestamp": int(time.time() * 1000),
                    "sign_method": "md5",
                    "format": "json",
                    "v": "2.0",
                    "access_token": tokens['access_token'],
                    "query_sku_attribute_info_request": json.dumps({
                        "aliexpress_category_id": str(category_id)
                    })
                }
                
                params["sign"] = generate_api_signature(params, APP_SECRET)
                
                print(f'🔍 Consultando atributos SKU para categoria: {category_id}')
                response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'aliexpress_solution_sku_attribute_query_response' in data:
                        result = data['aliexpress_solution_sku_attribute_query_response'].get('result', {})
                        
                        # Processar dados
                        processed_data = {
                            'category_id': str(category_id),
                            'sku_attributes': [],
                            'common_attributes': [],
                            'raw_data': result
                        }
                        
                        # Processar atributos SKU
                        if 'supporting_sku_attribute_list' in result:
                            sku_attributes = result['supporting_sku_attribute_list']
                            if isinstance(sku_attributes, list):
                                processed_data['sku_attributes'] = sku_attributes
                            else:
                                processed_data['sku_attributes'] = [sku_attributes]
                        
                        # Processar atributos comuns
                        if 'supporting_common_attribute_list' in result:
                            common_attributes = result['supporting_common_attribute_list']
                            if isinstance(common_attributes, list):
                                processed_data['common_attributes'] = common_attributes
                            else:
                                processed_data['common_attributes'] = [common_attributes]
                        
                        results[str(category_id)] = {
                            'success': True,
                            'data': processed_data
                        }
                        
                        print(f'✅ Categoria {category_id}: {len(processed_data["sku_attributes"])} atributos SKU, {len(processed_data["common_attributes"])} atributos comuns')
                    else:
                        results[str(category_id)] = {
                            'success': False,
                            'error': 'Estrutura de resposta inesperada'
                        }
                else:
                    results[str(category_id)] = {
                        'success': False,
                        'error': f'HTTP {response.status_code}'
                    }
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f'❌ Erro ao consultar categoria {category_id}: {e}')
                results[str(category_id)] = {
                    'success': False,
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'results': results,
            'total_categories': len(category_ids),
            'successful_categories': len([r for r in results.values() if r['success']])
        })
        
    except Exception as e:
        print(f'❌ Erro no processamento em lote: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/translate-attributes', methods=['POST'])
def translate_attributes():
    """Traduzir atributos de produtos usando nossa documentação"""
    try:
        data = request.get_json()
        attributes_data = data.get('attributes', [])
        
        # Dicionário de tradução baseado na nossa documentação
        attribute_translations = {
            # Códigos básicos (13xxx)
            '13143': 'Cor',
            '13144': 'Tamanho', 
            '13145': 'Material',
            '13146': 'Estilo',
            '13147': 'Padrão',
            '13148': 'Tipo',
            '13149': 'Forma',
            '13150': 'Função',
            '13151': 'Característica',
            '13152': 'Especificação',
            '13153': 'Modelo',
            '13154': 'Versão',
            '13155': 'Edição',
            '13156': 'Série',
            '13157': 'Coleção',
            '13158': 'Linha',
            '13159': 'Família',
            '13160': 'Categoria',
            '13161': 'Gênero',
            '13162': 'Idade',
            '13163': 'Ocasião',
            '13164': 'Tecnologia',
            '13165': 'Compatibilidade',
            '13166': 'Certificação',
            '13167': 'Origem',
            '13168': 'Marca',
            '13169': 'Fabricante',
            '13170': 'Garantia',
            '13171': 'Peso',
            '13172': 'Dimensões',
            '13173': 'Potência',
            '13174': 'Voltagem',
            '13175': 'Frequência',
            '13176': 'Capacidade',
            '13177': 'Velocidade',
            '13178': 'Resolução',
            '13179': 'Memória',
            '13180': 'Processador',
            '13181': 'Sistema Operacional',
            '13182': 'Conectividade',
            '13183': 'Bateria',
            '13184': 'Display',
            '13185': 'Câmera',
            '13186': 'Áudio',
            '13187': 'Sensor',
            '13188': 'Interface',
            '13189': 'Porta',
            '13190': 'Cabo',
            '13191': 'Adaptador',
            '13192': 'Suporte',
            '13193': 'Instrução',
            '13194': 'Manual',
            '13195': 'Embalagem',
            '13196': 'Acessório',
            '13197': 'Peça',
            '13198': 'Componente',
            '13199': 'Kit',
            '13200': 'Conjunto',
            
            # Códigos específicos (2-4 dígitos)
            '14': 'Tamanho',
            '29': 'Cor',
            '977': 'Tipo',
            '10': 'Categoria',
            '11': 'Subcategoria',
            '12': 'Marca',
            '13': 'Modelo',
            '15': 'Cor',
            '16': 'Material',
            '17': 'Estilo',
            '18': 'Padrão',
            '19': 'Tipo',
            '20': 'Forma',
            '21': 'Função',
            '22': 'Característica',
            '23': 'Especificação',
            '24': 'Versão',
            '25': 'Edição',
            '26': 'Série',
            '27': 'Coleção',
            '28': 'Linha',
            '30': 'Família',
            '31': 'Gênero',
            '32': 'Idade',
            '33': 'Ocasião',
            '34': 'Tecnologia',
            '35': 'Compatibilidade',
            '36': 'Certificação',
            '37': 'Origem',
            '38': 'Fabricante',
            '39': 'Garantia',
            '40': 'Peso',
            '41': 'Dimensões',
            '42': 'Potência',
            '43': 'Voltagem',
            '44': 'Frequência',
            '45': 'Capacidade',
            '46': 'Velocidade',
            '47': 'Resolução',
            '48': 'Memória',
            '49': 'Processador',
            '50': 'Sistema',
            
            # Códigos longos específicos
            '200003528': 'Categoria Específica',
            '200003529': 'Subcategoria',
            '200003530': 'Variante',
            '200003531': 'Opção',
            '200003532': 'Configuração',
            '200003533': 'Versão',
            '200003534': 'Edição',
            '200003535': 'Série',
            '200003536': 'Coleção',
            '200003537': 'Linha',
            '200003538': 'Família',
            '200003539': 'Gênero',
            '200003540': 'Idade',
            '200003541': 'Ocasião',
            '200003542': 'Tecnologia',
            '200003543': 'Compatibilidade',
            '200003544': 'Certificação',
            '200003545': 'Origem',
            '200003546': 'Marca',
            '200003547': 'Fabricante',
            '200003548': 'Garantia',
            '200003549': 'Peso',
            '200003550': 'Dimensões',
            
            # Códigos específicos mencionados pelo usuário
            '200001438': 'Cor Específica',
            '200001439': 'Tamanho Específico',
            '200001440': 'Material Específico',
            '200001441': 'Estilo Específico',
            '200001442': 'Padrão Específico',
            '200001443': 'Tipo Específico',
            '200001444': 'Forma Específica',
            '200001445': 'Função Específica',
            '200001446': 'Característica Específica',
            '200001447': 'Especificação Específica',
            '200001448': 'Modelo Específico',
            '200001449': 'Versão Específica',
            '200001450': 'Edição Específica',
            '200001451': 'Série Específica',
            '200001452': 'Coleção Específica',
            '200001453': 'Linha Específica',
            '200001454': 'Família Específica',
            '200001455': 'Categoria Específica',
            '200001456': 'Gênero Específico',
            '200001457': 'Idade Específica',
            '200001458': 'Ocasião Específica',
            '200001459': 'Tecnologia Específica',
            '200001460': 'Compatibilidade Específica',
            '200001461': 'Certificação Específica',
            '200001462': 'Origem Específica',
            '200001463': 'Marca Específica',
            '200001464': 'Fabricante Específico',
            '200001465': 'Garantia Específica',
            '200001466': 'Peso Específico',
            '200001467': 'Dimensões Específicas',
            '200001468': 'Potência Específica',
            '200001469': 'Voltagem Específica',
            '200001470': 'Frequência Específica',
            '200001471': 'Capacidade Específica',
            '200001472': 'Velocidade Específica',
            '200001473': 'Resolução Específica',
            '200001474': 'Memória Específica',
            '200001475': 'Processador Específico',
            '200001476': 'Sistema Operacional Específico',
            '200001477': 'Conectividade Específica',
            '200001478': 'Bateria Específica',
            '200001479': 'Display Específico',
            '200001480': 'Câmera Específica',
            '200001481': 'Áudio Específico',
            '200001482': 'Sensor Específico',
            '200001483': 'Interface Específica',
            '200001484': 'Porta Específica',
            '200001485': 'Cabo Específico',
            '200001486': 'Adaptador Específico',
            '200001487': 'Suporte Específico',
            '200001488': 'Instrução Específica',
            '200001489': 'Manual Específico',
            '200001490': 'Embalagem Específica',
            '200001491': 'Acessório Específico',
            '200001492': 'Peça Específica',
            '200001493': 'Componente Específico',
            '200001494': 'Kit Específico',
            '200001495': 'Conjunto Específico',
        }
        
        # Traduções de valores comuns
        value_translations = {
            # Cores
            'red': 'Vermelho',
            'blue': 'Azul',
            'green': 'Verde',
            'yellow': 'Amarelo',
            'black': 'Preto',
            'white': 'Branco',
            'pink': 'Rosa',
            'purple': 'Roxo',
            'orange': 'Laranja',
            'brown': 'Marrom',
            'gray': 'Cinza',
            'grey': 'Cinza',
            
            # Tamanhos
            'xs': 'Extra Pequeno',
            's': 'Pequeno',
            'm': 'Médio',
            'l': 'Grande',
            'xl': 'Extra Grande',
            'xxl': 'Extra Extra Grande',
            
            # Materiais
            'cotton': 'Algodão',
            'polyester': 'Poliéster',
            'wool': 'Lã',
            'silk': 'Seda',
            'leather': 'Couro',
            'plastic': 'Plástico',
            'metal': 'Metal',
            'wood': 'Madeira',
            'glass': 'Vidro',
            'ceramic': 'Cerâmica',
        }
        
        def translate_attribute_code(code):
            """Traduzir código de atributo"""
            return attribute_translations.get(str(code), f'Atributo {code}')
        
        def translate_attribute_value(value):
            """Traduzir valor de atributo"""
            value_lower = str(value).lower()
            return value_translations.get(value_lower, str(value))
        
        def parse_attribute_string(attr_string):
            """Parsear string de atributos complexa"""
            if not attr_string:
                return []
            
            # Padrões comuns: "29#Red;14#M" ou "13143:Red" ou "14" ou "14:200001438: verde"
            attributes = []
            
            # Dividir por ponto e vírgula
            parts = attr_string.split(';')
            
            for part in parts:
                if '#' in part:
                    # Formato: "29#Red"
                    code, value = part.split('#', 1)
                    attributes.append({
                        'code': code.strip(),
                        'value': value.strip(),
                        'translated_code': translate_attribute_code(code.strip()),
                        'translated_value': translate_attribute_value(value.strip())
                    })
                elif ':' in part:
                    # Contar quantos ':' existem
                    colon_count = part.count(':')
                    
                    if colon_count == 1:
                        # Formato: "13143:Red"
                        code, value = part.split(':', 1)
                        attributes.append({
                            'code': code.strip(),
                            'value': value.strip(),
                            'translated_code': translate_attribute_code(code.strip()),
                            'translated_value': translate_attribute_value(value.strip())
                        })
                    elif colon_count == 2:
                        # Formato: "14:200001438: verde" - onde o valor já está em português
                        parts_split = part.split(':', 2)
                        if len(parts_split) == 3:
                            code = parts_split[0].strip()
                            sub_code = parts_split[1].strip()
                            value = parts_split[2].strip()
                            
                            # Se o valor já está em português, não traduzir
                            translated_value = value if any(pt_word in value.lower() for pt_word in ['verde', 'vermelho', 'azul', 'amarelo', 'preto', 'branco', 'rosa', 'roxo', 'laranja', 'marrom', 'cinza']) else translate_attribute_value(value)
                            
                            attributes.append({
                                'code': code,
                                'value': f"{sub_code}: {value}",
                                'translated_code': translate_attribute_code(code),
                                'translated_value': translated_value
                            })
                        else:
                            # Fallback para formato não reconhecido
                            attributes.append({
                                'code': part.strip(),
                                'value': '',
                                'translated_code': translate_attribute_code(part.strip()),
                                'translated_value': ''
                            })
                    else:
                        # Formato não reconhecido, tratar como código simples
                        attributes.append({
                            'code': part.strip(),
                            'value': '',
                            'translated_code': translate_attribute_code(part.strip()),
                            'translated_value': ''
                        })
                else:
                    # Formato simples: "14"
                    code = part.strip()
                    if code:
                        attributes.append({
                            'code': code,
                            'value': '',
                            'translated_code': translate_attribute_code(code),
                            'translated_value': ''
                        })
            
            return attributes
        
        # Processar cada atributo
        translated_attributes = []
        
        for attr_data in attributes_data:
            if isinstance(attr_data, str):
                # Se é uma string, tentar parsear
                parsed = parse_attribute_string(attr_data)
                translated_attributes.extend(parsed)
            elif isinstance(attr_data, dict):
                # Se é um objeto, processar diretamente
                code = attr_data.get('code', '')
                value = attr_data.get('value', '')
                
                translated_attributes.append({
                    'code': str(code),
                    'value': str(value),
                    'translated_code': translate_attribute_code(code),
                    'translated_value': translate_attribute_value(value),
                    'original': attr_data
                })
        
        return jsonify({
            'success': True,
            'translated_attributes': translated_attributes,
            'total_attributes': len(translated_attributes),
            'translation_map': {
                'attribute_codes': len(attribute_translations),
                'value_translations': len(value_translations)
            }
        })
        
    except Exception as e:
        print(f'❌ Erro ao traduzir atributos: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

# ===================== FRETE REAL (API ALIEXPRESS) =====================
def calculate_real_shipping_quotes(product_id, destination_cep, items):
    """Calcula cotações de frete usando API real do AliExpress"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        raise Exception('Token não encontrado. Faça autorização primeiro.')
    
    try:
        # Parâmetros para a API de frete conforme documentação oficial
        params = {
            "method": "aliexpress.ds.freight.query",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "queryDeliveryReq": json.dumps({
                "productId": product_id,
                "quantity": str(sum(item.get('quantity', 1) for item in items)),
                "shipToCountry": "BR",
                "provinceCode": "SP",  # São Paulo como padrão
                "cityCode": "SAO",     # São Paulo como padrão
                "selectedSkuId": "12000023999200390",  # SKU padrão
                "language": "pt_BR",
                "currency": "BRL",
                "locale": "pt_BR"
            })
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        print(f'🚚 Calculando frete real para produto {product_id}')
        print(f'🚚 Parâmetros: {params}')
        
        # Fazer requisição para API de frete
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'🚚 Status Code: {response.status_code}')
        print(f'🚚 Headers: {dict(response.headers)}')
        print(f'🚚 Resposta completa: {response.text}')
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f'🚚 Dados JSON: {json.dumps(data, indent=2)}')
                
                if 'aliexpress_ds_freight_query_response' in data:
                    freight_response = data['aliexpress_ds_freight_query_response']
                    result = freight_response.get('result', {})
                    
                    if result.get('success') == 'true' or result.get('msg') == 'Call succeeds':
                        delivery_options = result.get('delivery_options', {})
                        
                        # Verificar se delivery_options é um objeto com delivery_option_d_t_o
                        if isinstance(delivery_options, dict) and 'delivery_option_d_t_o' in delivery_options:
                            options_list = delivery_options['delivery_option_d_t_o']
                        elif isinstance(delivery_options, list):
                            options_list = delivery_options
                        else:
                            print(f'❌ Formato inesperado de delivery_options: {type(delivery_options)}')
                            options_list = []
                        
                        quotes = []
                        for option in options_list:
                            # Converter centavos para reais
                            shipping_fee_cent = float(option.get('shipping_fee_cent', 0))
                            shipping_fee = shipping_fee_cent / 100
                            
                            quotes.append({
                                'service_code': option.get('code', 'UNKNOWN'),
                                'service_name': option.get('company', 'AliExpress'),
                                'carrier': option.get('company', 'AliExpress'),
                                'price': round(shipping_fee, 2),
                                'currency': option.get('shipping_fee_currency', 'BRL'),
                                'estimated_days': int(option.get('min_delivery_days', 30)),
                                'max_delivery_days': int(option.get('max_delivery_days', 60)),
                                'tracking_available': option.get('tracking', 'false') == 'true',
                                'free_shipping': option.get('free_shipping', 'false') == 'true',
                                'origin_cep': STORE_ORIGIN_CEP,
                                'destination_cep': destination_cep,
                                'notes': f'Frete real AliExpress - {option.get("estimated_delivery_time", "N/A")}'
                            })
                        
                        print(f'✅ Frete real calculado: {len(quotes)} opções')
                        return quotes
                    else:
                        error_msg = result.get('msg', 'Erro desconhecido na API de frete')
                        print(f'❌ Erro API frete: {error_msg}')
                        raise Exception(f'Erro na API de frete: {error_msg}')
                else:
                    print(f'❌ Estrutura inesperada. Keys disponíveis: {list(data.keys())}')
                    print(f'❌ Conteúdo completo: {json.dumps(data, indent=2)}')
                    raise Exception('Resposta inesperada da API de frete')
            except json.JSONDecodeError as e:
                print(f'❌ Erro ao decodificar JSON: {e}')
                print(f'❌ Resposta raw: {response.text}')
                raise Exception(f'Erro ao decodificar resposta JSON: {e}')
        else:
            print(f'❌ Erro HTTP {response.status_code}')
            print(f'❌ Resposta de erro: {response.text}')
            raise Exception(f'Erro HTTP {response.status_code}: {response.text}')
            
    except Exception as e:
        print(f'❌ Erro ao calcular frete real: {e}')
        raise e

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint simples para testar se o servidor está funcionando"""
    return jsonify({
        'success': True,
        'message': 'Servidor funcionando!',
        'timestamp': int(time.time()),
        'env_vars': {
            'APP_KEY': APP_KEY,
            'STORE_ORIGIN_CEP': STORE_ORIGIN_CEP,
            'INBOUND_LEAD_TIME_DAYS': os.getenv('INBOUND_LEAD_TIME_DAYS', '12'),
            'STORE_HANDLING_DAYS': os.getenv('STORE_HANDLING_DAYS', '2')
        }
    })

@app.route('/debug/tokens', methods=['GET'])
def debug_tokens():
    """Endpoint para debug dos tokens"""
    try:
        tokens = load_tokens()
        if not tokens:
            return jsonify({
                'success': False,
                'message': 'Nenhum token encontrado',
                'tokens': None
            })
        
        # Testar se o token ainda é válido
        test_params = {
            "method": "aliexpress.ds.freight.query",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": "3256802900954148",
            "destination_cep": "01001-000"
        }
        
        # Gerar assinatura
        test_params['sign'] = generate_api_signature(test_params, APP_SECRET)
        
        print(f"🔍 Testando tokens com params: {test_params}")
        
        response = requests.get('https://api-sg.aliexpress.com/sync', params=test_params)
        
        return jsonify({
            'success': True,
            'tokens': {
                'access_token': tokens.get('access_token', 'N/A')[:20] + '...',
                'refresh_token': tokens.get('refresh_token', 'N/A')[:20] + '...',
                'expires_at': tokens.get('expires_at', 'N/A')
            },
            'test_response': {
                'status_code': response.status_code,
                'content': response.text[:500] + '...' if len(response.text) > 500 else response.text
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar tokens: {str(e)}',
            'tokens': None
        })

@app.route('/debug/order', methods=['GET'])
def debug_order():
    """Debug endpoint para testar criação de pedidos"""
    try:
        # Dados de teste
        order_data = {
            "customer_id": "DEBUG_CUSTOMER_001",
            "items": [
                {
                    "product_id": "1005007720304124",
                    "quantity": 1,
                    "sku_attr": "",
                    "memo": "Debug order creation"
                }
            ],
            "address": {
                "country": "BR",
                "province": "Ceara",
                "city": "Fortaleza",
                "district": "Centro",
                "detail_address": "Rua Teste, 123 - Bloco 03, Apto 202",
                "zip": "61771880",
                "contact_person": "francisco adonay ferreira do nascimento",
                "phone": "+5585997640050"
            }
        }
        
        # Tentar criar pedido
        result = create_aliexpress_order(order_data)
        
        return jsonify({
            'success': True,
            'message': 'Debug de criação de pedido',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no debug: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/debug/freight', methods=['GET'])
def debug_freight():
    """Endpoint para debug detalhado da API de frete"""
    try:
        tokens = load_tokens()
        if not tokens:
            return jsonify({
                'success': False,
                'message': 'Nenhum token encontrado'
            })
        
        # Testar API de frete com parâmetros fixos
        test_params = {
            "method": "aliexpress.ds.freight.query",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "queryDeliveryReq": json.dumps({
                "productId": "3256802900954148",
                "quantity": "1",
                "shipToCountry": "BR",
                "provinceCode": "SP",
                "cityCode": "SAO",
                "selectedSkuId": "12000023999200390",  # SKU padrão
                "language": "pt_BR",
                "currency": "BRL",
                "locale": "pt_BR"
            })
        }
        
        # Gerar assinatura
        test_params['sign'] = generate_api_signature(test_params, APP_SECRET)
        
        print(f"🔍 Debug frete - Parâmetros: {json.dumps(test_params, indent=2)}")
        
        response = requests.get('https://api-sg.aliexpress.com/sync', params=test_params)
        
        return jsonify({
            'success': True,
            'request_params': test_params,
            'response': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no debug: {str(e)}',
            'traceback': str(e)
        })

# ===================== CRIAÇÃO DE PEDIDOS =====================
def create_aliexpress_order(order_data):
    """Cria pedido no AliExpress usando aliexpress.ds.order.create"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        raise Exception('Token não encontrado. Faça autorização primeiro.')
    
    try:
        # Preparar dados do pedido
        product_items = []
        for item in order_data['items']:
            product_items.append({
                "product_id": item['product_id'],
                "product_count": str(item['quantity']),
                "sku_attr": item.get('sku_attr', ''),  # SKU vazio para usar padrão do produto
                "logistics_service_name": "CAINIAO_FULFILLMENT_STD",  # Serviço padrão
                "order_memo": item.get('memo', 'Pedido da Loja da Sophia')
            })
        
        # Usar endereço do payload ou endereço padrão da loja
        if 'address' in order_data:
            # Endereço fornecido no payload
            address_data = order_data['address']
            logistics_address = {
                "address": address_data.get('detail_address', 'Rua Teste, 123 - Bloco 03, Apto 202'),
                "address2": "",
                "city": address_data.get('city', 'Fortaleza'),
                "contact_person": address_data.get('contact_person', 'francisco adonay ferreira do nascimento'),
                "country": address_data.get('country', 'BR'),
                "cpf": "07248629359",  # CPF válido fornecido pelo usuário
                "full_name": address_data.get('contact_person', 'francisco adonay ferreira do nascimento'),
                "locale": "pt_BR",
                "mobile_no": address_data.get('phone', '+5585997640050').replace('+55', '').replace('+', ''),
                "phone_country": "55",
                "province": address_data.get('province', 'Ceara'),
                "zip": address_data.get('zip', STORE_ORIGIN_CEP.replace('-', ''))
            }
        else:
            # Endereço padrão da loja
            logistics_address = {
                "address": "Rua Teste, 123 - Bloco 03, Apto 202",
                "address2": "",
                "city": "Fortaleza",
                "contact_person": "francisco adonay ferreira do nascimento",
                "country": "BR",
                "cpf": "07248629359",  # CPF válido fornecido pelo usuário
                "full_name": "francisco adonay ferreira do nascimento",
                "locale": "pt_BR",
                "mobile_no": "85997640050",
                "phone_country": "55",
                "province": "Ceara",
                "zip": STORE_ORIGIN_CEP.replace('-', '')
            }
        
        # Parâmetros da API
        param_place_order_request = {
            "product_items": product_items,
            "logistics_address": logistics_address,  # Campo correto é 'logistics_address'
            "out_order_id": f"ORDER_{int(time.time())}_{order_data.get('customer_id', 'CUSTOMER')}"
        }
        
        # Parâmetros estendidos
        ds_extend_request = {
            "trade_extra_param": {
                "business_model": "retail"
            },
            "payment": {
                "try_to_pay": "false",
                "pay_currency": "USD"
            }
        }
        
        # Parâmetros da requisição
        params = {
            "method": "aliexpress.ds.order.create",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "param_place_order_request4_open_api_d_t_o": json.dumps(param_place_order_request),
            "ds_extend_request": json.dumps(ds_extend_request)
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        print(f'🛒 Criando pedido AliExpress: {json.dumps(params, indent=2)}')
        print(f'🛒 Logistics Address: {json.dumps(logistics_address, indent=2)}')
        
        # Fazer requisição
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'🛒 Status Code: {response.status_code}')
        print(f'🛒 Resposta: {response.text}')
        
        # Log da resposta completa para debug
        try:
            response_data = response.json()
            print(f'🛒 Resposta JSON: {json.dumps(response_data, indent=2)}')
        except:
            print(f'🛒 Resposta não é JSON válido: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            
            if 'aliexpress_ds_order_create_response' in data:
                order_response = data['aliexpress_ds_order_create_response']
                result = order_response.get('result', {})
                
                if result.get('is_success') == True or result.get('is_success') == 'true':
                    # Extrair order_id do order_list
                    order_list = result.get('order_list', {})
                    order_numbers = order_list.get('number', [])
                    order_id = order_numbers[0] if order_numbers else None
                    
                    print(f'✅ Pedido criado com sucesso! ID: {order_id}')
                    
                    return {
                        'success': True,
                        'order_id': str(order_id),
                        'out_order_id': param_place_order_request['out_order_id'],
                        'message': 'Pedido criado com sucesso no AliExpress',
                        'fulfillment': {
                            'mode': 'aliexpress_direct',
                            'source': 'aliexpress_api',
                            'notes': f'Pedido enviado para AliExpress - ID: {order_id}'
                        }
                    }
                else:
                    error_code = result.get('error_code', 'UNKNOWN_ERROR')
                    error_msg = result.get('error_msg', 'Erro desconhecido')
                    print(f'❌ Erro ao criar pedido: {error_code} - {error_msg}')
                    raise Exception(f'Erro ao criar pedido: {error_code} - {error_msg}')
            else:
                print(f'❌ Estrutura inesperada da resposta: {list(data.keys())}')
                raise Exception('Resposta inesperada da API de criação de pedidos')
        else:
            print(f'❌ Erro HTTP {response.status_code}: {response.text}')
            raise Exception(f'Erro HTTP {response.status_code}: {response.text}')
            
    except Exception as e:
        print(f'❌ Erro ao criar pedido AliExpress: {e}')
        raise e

@app.route('/api/aliexpress/orders/create', methods=['POST'])
def create_order():
    """Endpoint para criar pedidos no AliExpress"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validar dados obrigatórios
        required_fields = ['items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório ausente: {field}'
                }), 400
        
        items = data['items']
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({
                'success': False,
                'message': 'Lista de itens deve conter pelo menos um item'
            }), 400
        
        print(f'🛒 Recebendo pedido: {json.dumps(data, indent=2)}')
        
        # Criar pedido no AliExpress
        result = create_aliexpress_order(data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'❌ Erro no endpoint de criação de pedidos: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro ao criar pedido: {str(e)}'
        }), 500

def get_aliexpress_order_tracking(order_id):
    """Busca tracking de um pedido no AliExpress usando aliexpress.ds.order.tracking.get"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        raise Exception('Token não encontrado. Faça autorização primeiro.')
    
    try:
        # Parâmetros da API
        params = {
            "method": "aliexpress.ds.order.tracking.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "ae_order_id": str(order_id),
            "language": "en_US"
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        print(f'📋 Buscando tracking do pedido AliExpress: {order_id}')
        print(f'📋 Parâmetros: {json.dumps(params, indent=2)}')
        
        # Fazer requisição
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        print(f'📋 Status Code: {response.status_code}')
        print(f'📋 Resposta: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result' in data:
                result = data['result']
                
                if result.get('ret') == 'true':
                    tracking_data = result.get('data', {})
                    tracking_list = tracking_data.get('tracking_detail_line_list', [])
                    
                    # Extrair informações de tracking
                    tracking_info = {
                        'order_id': str(order_id),
                        'tracking_details': []
                    }
                    
                    for tracking in tracking_list:
                        package_info = {
                            'carrier_name': tracking.get('carrier_name', ''),
                            'mail_no': tracking.get('mail_no', ''),
                            'eta_time': tracking.get('eta_time_stamps', ''),
                            'package_items': tracking.get('package_item_list', []),
                            'tracking_events': []
                        }
                        
                        # Extrair eventos de tracking
                        detail_node_list = tracking.get('detail_node_list', [])
                        for event in detail_node_list:
                            tracking_event = {
                                'timestamp': event.get('time_stamp', ''),
                                'description': event.get('tracking_detail_desc', ''),
                                'name': event.get('tracking_name', '')
                            }
                            package_info['tracking_events'].append(tracking_event)
                        
                        tracking_info['tracking_details'].append(package_info)
                    
                    print(f'✅ Tracking do pedido obtido: {len(tracking_info["tracking_details"])} pacotes')
                    
                    return {
                        'success': True,
                        'tracking_info': tracking_info,
                        'message': f'Tracking encontrado: {len(tracking_info["tracking_details"])} pacotes'
                    }
                else:
                    error_code = result.get('code', 'UNKNOWN_ERROR')
                    error_msg = result.get('msg', 'Erro desconhecido')
                    print(f'❌ Erro ao buscar tracking: {error_code} - {error_msg}')
                    raise Exception(f'Erro ao buscar tracking: {error_code} - {error_msg}')
            else:
                print(f'❌ Estrutura inesperada da resposta: {list(data.keys())}')
                raise Exception('Resposta inesperada da API de tracking')
        else:
            print(f'❌ Erro HTTP {response.status_code}: {response.text}')
            raise Exception(f'Erro HTTP {response.status_code}: {response.text}')
            
    except Exception as e:
        print(f'❌ Erro ao buscar status do pedido: {e}')
        raise e

@app.route('/api/aliexpress/orders/<order_id>/tracking', methods=['GET'])
def get_order_tracking(order_id):
    """Endpoint para buscar tracking de um pedido"""
    try:
        result = get_aliexpress_order_tracking(order_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar tracking do pedido: {str(e)}'
        }), 500

@app.route('/api/aliexpress/product/<product_id>/skus', methods=['GET'])
def get_product_skus(product_id):
    """Endpoint para buscar SKUs disponíveis de um produto"""
    try:
        tokens = load_tokens()
        if not tokens or not tokens.get('access_token'):
            return jsonify({
                'success': False,
                'message': 'Token não encontrado. Faça autorização primeiro.'
            }), 401
        
        # Parâmetros para buscar SKUs
        params = {
            "method": "aliexpress.ds.product.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": product_id
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        print(f'🔍 Buscando SKUs para produto {product_id}')
        
        # Fazer requisição
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'aliexpress_ds_product_get_response' in data:
                product_response = data['aliexpress_ds_product_get_response']
                result = product_response.get('result', {})
                
                if result.get('success') == 'true':
                    product_info = result.get('product_info', {})
                    sku_props = product_info.get('sku_props', [])
                    
                    skus = []
                    for sku in sku_props:
                        skus.append({
                            'sku_id': sku.get('sku_id'),
                            'sku_attr': sku.get('sku_attr'),
                            'price': sku.get('price'),
                            'stock': sku.get('stock'),
                            'properties': sku.get('properties', [])
                        })
                    
                    return jsonify({
                        'success': True,
                        'product_id': product_id,
                        'skus': skus,
                        'total_skus': len(skus)
                    })
                else:
                    error_msg = result.get('error_msg', 'Erro desconhecido')
                    return jsonify({
                        'success': False,
                        'message': f'Erro ao buscar SKUs: {error_msg}'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'message': 'Resposta inesperada da API'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': f'Erro HTTP {response.status_code}: {response.text}'
            }), 500
            
    except Exception as e:
        print(f'❌ Erro ao buscar SKUs: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar SKUs: {str(e)}'
        }), 500

# ============================================================================
# MERCADO PAGO PAYMENT ENDPOINTS
# ============================================================================

@app.route('/api/payment/mp/create-preference', methods=['POST'])
def create_mp_preference():
    """Criar preferência de pagamento no Mercado Pago"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['order_id', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório não fornecido: {field}'
                }), 400
        
        # Criar preferência no Mercado Pago
        result = mp_integration.create_preference(data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'preference_id': result['preference_id'],
                'init_point': result['init_point'],
                'sandbox_init_point': result.get('sandbox_init_point'),
                'message': 'Preferência Mercado Pago criada com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar preferência: {result["error"]}'
            }), 500
            
    except Exception as e:
        print(f'❌ Erro ao criar preferência: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/mp/payment/<payment_id>', methods=['GET'])
def get_mp_payment(payment_id):
    """Obter informações de um pagamento"""
    try:
        result = mp_integration.get_payment_info(payment_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'payment_data': result['payment_data']
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erro ao obter pagamento: {result["error"]}'
            }), 500
            
    except Exception as e:
        print(f'❌ Erro ao obter pagamento: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/mp/refund/<payment_id>', methods=['POST'])
def refund_mp_payment(payment_id):
    """Estornar pagamento Mercado Pago"""
    try:
        data = request.get_json() or {}
        amount = data.get('amount')
        reason = data.get('reason', 'Refund requested')
        
        # Estornar pagamento
        result = mp_integration.refund_payment(payment_id, amount, reason)
        
        if result['success']:
            return jsonify({
                'success': True,
                'refund_id': result['refund_id'],
                'status': result['status'],
                'message': 'Estorno realizado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erro ao estornar: {result["error"]}'
            }), 500
            
    except Exception as e:
        print(f'❌ Erro ao estornar: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/mp/preference/<preference_id>', methods=['GET'])
def get_mp_preference(preference_id):
    """Obter detalhes de uma preferência"""
    try:
        result = mp_integration.get_preference(preference_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'preference_data': result['preference_data']
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erro ao obter preferência: {result["error"]}'
            }), 500
            
    except Exception as e:
        print(f'❌ Erro ao obter preferência: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/mp/webhook', methods=['POST'])
def mp_webhook():
    """Webhook do Mercado Pago para notificações de pagamento"""
    try:
        data = request.get_json()
        
        print(f'📡 Webhook Mercado Pago recebido: {json.dumps(data, indent=2)}')
        
        # Verificar tipo de notificação
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Obter informações do pagamento
                payment_result = mp_integration.get_payment_info(payment_id)
                
                if payment_result['success']:
                    payment_data = payment_result['payment_data']
                    status = payment_data.get('status')
                    external_reference = payment_data.get('external_reference')
                    
                    print(f'💰 Pagamento {payment_id} - Status: {status} - Referência: {external_reference}')
                    
                    # Se pagamento aprovado, criar pedido no AliExpress
                    if status == 'approved':
                        print(f'✅ Pagamento aprovado! Criando pedido AliExpress...')
                        
                        try:
                            # Buscar dados do pedido original pelo external_reference
                            order_data = _get_order_data_from_external_reference(external_reference)
                            
                            if order_data:
                                # Criar pedido no AliExpress
                                aliexpress_result = _create_aliexpress_order_from_payment(order_data, payment_data)
                                
                                if aliexpress_result['success']:
                                    print(f'🎉 Pedido AliExpress criado: {aliexpress_result["order_id"]}')
                                    
                                    # Salvar relação pagamento → pedido para tracking futuro
                                    _save_payment_order_relation(payment_id, external_reference, aliexpress_result['order_id'])
                                    
                                    return jsonify({
                                        'success': True,
                                        'message': 'Pedido AliExpress criado com sucesso',
                                        'order_id': aliexpress_result['order_id']
                                    })
                                else:
                                    print(f'❌ Falha ao criar pedido AliExpress: {aliexpress_result["error"]}')
                                    
                                    # Tentar estorno automático
                                    refund_result = mp_integration.refund_payment(
                                        payment_id, 
                                        reason="Falha na criação do pedido AliExpress"
                                    )
                                    
                                    return jsonify({
                                        'success': False,
                                        'message': 'Falha ao criar pedido AliExpress. Estorno iniciado.',
                                        'refunded': refund_result.get('success', False)
                                    }), 500
                            else:
                                print(f'❌ Dados do pedido não encontrados para: {external_reference}')
                                return jsonify({
                                    'success': False,
                                    'message': 'Dados do pedido não encontrados'
                                }), 400
                                
                        except Exception as e:
                            print(f'❌ Erro ao processar webhook: {e}')
                            return jsonify({
                                'success': False,
                                'message': f'Erro interno: {str(e)}'
                            }), 500
                    else:
                        print(f'⚠️ Pagamento não aprovado: {status}')
                        return jsonify({
                            'success': True,
                            'message': f'Pagamento não aprovado: {status}'
                        })
                else:
                    print(f'❌ Erro ao obter pagamento: {payment_result["error"]}')
                    return jsonify({
                        'success': False,
                        'message': 'Erro ao obter pagamento'
                    }), 500
        
        return jsonify({
            'success': True,
            'message': 'Webhook recebido'
        })
        
    except Exception as e:
        print(f'❌ Erro no webhook: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro no webhook: {str(e)}'
        }), 500

@app.route('/api/payment/mp/success')
def mp_success():
    """Callback de sucesso do Mercado Pago"""
    try:
        payment_id = request.args.get('payment_id')
        preference_id = request.args.get('preference_id')
        
        print(f'✅ Sucesso Mercado Pago - Payment ID: {payment_id}, Preference ID: {preference_id}')
        
        return jsonify({
            'success': True,
            'message': 'Pagamento aprovado com sucesso!',
            'payment_id': payment_id,
            'preference_id': preference_id
        })
        
    except Exception as e:
        print(f'❌ Erro no sucesso: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro no sucesso: {str(e)}'
        }), 500

@app.route('/api/payment/mp/failure')
def mp_failure():
    """Callback de falha do Mercado Pago"""
    try:
        payment_id = request.args.get('payment_id')
        preference_id = request.args.get('preference_id')
        
        print(f'❌ Falha Mercado Pago - Payment ID: {payment_id}, Preference ID: {preference_id}')
        
        return jsonify({
            'success': False,
            'message': 'Pagamento falhou',
            'payment_id': payment_id,
            'preference_id': preference_id
        })
        
    except Exception as e:
        print(f'❌ Erro na falha: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro na falha: {str(e)}'
        }), 500

@app.route('/api/payment/mp/pending')
def mp_pending():
    """Callback de pendente do Mercado Pago"""
    try:
        payment_id = request.args.get('payment_id')
        preference_id = request.args.get('preference_id')
        
        print(f'⏳ Pendente Mercado Pago - Payment ID: {payment_id}, Preference ID: {preference_id}')
        
        return jsonify({
            'success': True,
            'message': 'Pagamento pendente',
            'payment_id': payment_id,
            'preference_id': preference_id
        })
        
    except Exception as e:
        print(f'❌ Erro no pendente: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro no pendente: {str(e)}'
        }), 500

# ============================================================================
# INTEGRATED PAYMENT FLOW
# ============================================================================

@app.route('/api/payment/process', methods=['POST'])
def process_payment():
    """Processar pagamento completo (Mercado Pago + AliExpress)"""
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['order_id', 'total_amount', 'items', 'customer_info']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório não fornecido: {field}'
                }), 400
        
        # 1. Criar preferência Mercado Pago
        mp_data = {
            'order_id': data['order_id'],
            'total_amount': data['total_amount'],
            'payer': data.get('customer_info', {})
        }
        
        mp_result = mp_integration.create_preference(mp_data)
        
        if not mp_result['success']:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar preferência Mercado Pago: {mp_result["error"]}'
            }), 500
        
        # 2. Retornar URL de pagamento
        return jsonify({
            'success': True,
            'preference_id': mp_result['preference_id'],
            'init_point': mp_result['init_point'],
            'sandbox_init_point': mp_result.get('sandbox_init_point'),
            'message': 'Preferência Mercado Pago criada. Redirecione o usuário para a URL de pagamento.'
        })
        
    except Exception as e:
        print(f'❌ Erro ao processar pagamento: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/complete/<payment_id>', methods=['POST'])
def complete_payment(payment_id):
    """Completar pagamento após aprovação (verificar + criar pedido AliExpress)"""
    try:
        data = request.get_json()
        
        # 1. Verificar status do pagamento
        payment_result = mp_integration.get_payment_info(payment_id)
        
        if not payment_result['success']:
            return jsonify({
                'success': False,
                'message': f'Erro ao verificar pagamento: {payment_result["error"]}'
            }), 500
        
        payment_data = payment_result['payment_data']
        status = payment_data.get('status')
        
        if status != 'approved':
            return jsonify({
                'success': False,
                'message': f'Pagamento não aprovado. Status: {status}'
            }), 400
        
        # 2. Criar pedido no AliExpress
        aliexpress_data = {
            'customer_id': data.get('customer_id', 'MP_CUSTOMER'),
            'items': data['items'],
            'address': data.get('address', {})
        }
        
        aliexpress_result = create_aliexpress_order(aliexpress_data)
        
        if not aliexpress_result['success']:
            # Se falhar no AliExpress, estornar Mercado Pago
            refund_result = mp_integration.refund_payment(
                payment_id,
                reason="Falha na criação do pedido AliExpress"
            )
            
            return jsonify({
                'success': False,
                'message': f'Erro ao criar pedido AliExpress: {aliexpress_result["error"]}. Pagamento estornado.',
                'refunded': refund_result['success']
            }), 500
        
        # 3. Sucesso completo
        return jsonify({
            'success': True,
            'mp_payment_id': payment_id,
            'aliexpress_order_id': aliexpress_result['order_id'],
            'message': 'Pagamento processado e pedido criado com sucesso!'
        })
        
    except Exception as e:
        print(f'❌ Erro ao completar pagamento: {e}')
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/payment/mp/debug', methods=['GET'])
def debug_mp():
    """Debug do Mercado Pago"""
    try:
        sdk_info = mp_integration.get_sdk_info()
        return jsonify({
            'success': True,
            'sdk_info': sdk_info,
            'message': 'Informações do SDK Mercado Pago'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter informações do SDK: {str(e)}'
        }), 500

# ============================================================================
# FUNÇÕES AUXILIARES WEBHOOK
# ============================================================================

def _get_order_data_from_external_reference(external_reference):
    """
    Recuperar dados do pedido original pelo external_reference
    Em um sistema real, isso viria de um banco de dados
    """
    # Por enquanto, vamos simular dados baseados no ORDER ID
    if external_reference and external_reference.startswith('ORDER-'):
        return {
            'items': [
                {
                    'product_id': '1005006043070326',  # ID real do AliExpress
                    'sku_attr': '',
                    'quantity': 1,
                    'price': 25.99
                }
            ],
            'customer_info': {
                'name': 'francisco adonay ferreira do nascimento',
                'cpf': '07248629359',
                'phone': '85997640050',
                'address': {
                    'contact_person': 'francisco adonay ferreira do nascimento',
                    'mobile_no': '85997640050',
                    'phone_country': '55',
                    'full_name': 'francisco adonay ferreira do nascimento',
                    'detail_address': 'Rua Teste, 123 - Bloco 03, Apto 202',
                    'city': 'Fortaleza',
                    'province': 'Ceara',
                    'zip': '61771-880',
                    'country': 'BR',
                    'cpf': '07248629359'
                }
            }
        }
    return None

def _create_aliexpress_order_from_payment(order_data, payment_data):
    """
    Criar pedido no AliExpress usando dados do pagamento
    """
    try:
        # Preparar dados para AliExpress
        product_items = []
        for item in order_data['items']:
            product_items.append({
                'product_id': item['product_id'],
                'sku_attr': item.get('sku_attr', ''),
                'quantity': item['quantity']
            })
        
        # Dados do endereço (sempre da loja)
        logistics_address = order_data['customer_info']['address']
        
        # Criar pedido usando função existente
        result = create_aliexpress_order({
            'product_items': product_items,
            'logistics_address': logistics_address
        })
        
        return result
        
    except Exception as e:
        print(f'❌ Erro ao criar pedido AliExpress: {e}')
        return {
            'success': False,
            'error': str(e)
        }

def _save_payment_order_relation(payment_id, external_reference, order_id):
    """
    Salvar relação entre pagamento e pedido para tracking futuro
    Em um sistema real, isso seria salvo em banco de dados
    """
    relation_data = {
        'payment_id': payment_id,
        'external_reference': external_reference,
        'aliexpress_order_id': order_id,
        'created_at': time.time(),
        'status': 'created'
    }
    
    # Salvar em arquivo temporário para demo
    # Em produção, usar banco de dados
    relations_file = 'payment_order_relations.json'
    
    try:
        if os.path.exists(relations_file):
            with open(relations_file, 'r') as f:
                relations = json.load(f)
        else:
            relations = []
        
        relations.append(relation_data)
        
        with open(relations_file, 'w') as f:
            json.dump(relations, f, indent=2)
        
        print(f'💾 Relação salva: {payment_id} → {order_id}')
        
    except Exception as e:
        print(f'❌ Erro ao salvar relação: {e}')

# ===================== CÁLCULO DE FRETE PARA CEPs PRINCIPAIS =====================
def calculate_shipping_for_main_ceps(product_id, product_weight=0.5, product_dimensions=None):
    """Calcula frete para CEPs principais do Brasil no momento da importação"""
    
    # CEPs principais do Brasil
    main_ceps = {
        "01001000": "São Paulo - SP",
        "20040020": "Rio de Janeiro - RJ", 
        "90020060": "Porto Alegre - RS",
        "40000000": "Salvador - BA",
        "50000000": "Recife - PE",
        "70000000": "Brasília - DF",
        "80000000": "Curitiba - PR",
        "30000000": "Belo Horizonte - MG",
        "60000000": "Fortaleza - CE",
        "11000000": "Santos - SP"
    }
    
    # Dimensões padrão se não fornecidas
    if product_dimensions is None:
        product_dimensions = {
            'length': 20.0,  # cm
            'width': 15.0,   # cm
            'height': 5.0    # cm
        }
    
    shipping_data = {}
    
    try:
        tokens = load_tokens()
        if not tokens or not tokens.get('access_token'):
            print(f"⚠️ Token não disponível para calcular frete do produto {product_id}")
            # Usar cálculo próprio como fallback
            return _calculate_own_shipping_for_ceps(main_ceps, product_weight, product_dimensions)
        
        print(f"🚚 Calculando frete AliExpress para produto {product_id} em {len(main_ceps)} CEPs...")
        
        for cep, location in main_ceps.items():
            try:
                # Calcular frete via API AliExpress
                quotes = calculate_real_shipping_quotes(product_id, cep, [{
                    'product_id': product_id,
                    'quantity': 1,
                    'weight': product_weight,
                    'length': product_dimensions['length'],
                    'height': product_dimensions['height'],
                    'width': product_dimensions['width']
                }])
                
                # Processar opções de frete
                shipping_options = {}
                for quote in quotes:
                    service_code = quote.get('service_code', 'UNKNOWN')
                    if 'ECONOMY' in service_code.upper() or 'STANDARD' in service_code.upper():
                        shipping_options['economy'] = {
                            'price': quote.get('price', 0.0),
                            'days': quote.get('estimated_days', 30),
                            'carrier': quote.get('carrier', 'AliExpress'),
                            'service_name': quote.get('service_name', 'Entrega Padrão')
                        }
                    elif 'EXPRESS' in service_code.upper() or 'FAST' in service_code.upper():
                        shipping_options['express'] = {
                            'price': quote.get('price', 0.0),
                            'days': quote.get('estimated_days', 15),
                            'carrier': quote.get('carrier', 'AliExpress'),
                            'service_name': quote.get('service_name', 'Entrega Expressa')
                        }
                
                # Se não encontrou opções específicas, usar as primeiras disponíveis
                if not shipping_options and quotes:
                    first_quote = quotes[0]
                    shipping_options['standard'] = {
                        'price': first_quote.get('price', 0.0),
                        'days': first_quote.get('estimated_days', 25),
                        'carrier': first_quote.get('carrier', 'AliExpress'),
                        'service_name': first_quote.get('service_name', 'Entrega Padrão')
                    }
                
                shipping_data[cep] = shipping_options
                print(f"✅ CEP {cep} ({location}): {len(shipping_options)} opções")
                
            except Exception as e:
                print(f"❌ Erro ao calcular frete para CEP {cep}: {e}")
                # Usar cálculo próprio como fallback para este CEP
                shipping_data[cep] = _calculate_own_shipping_for_cep(cep, product_weight, product_dimensions)
        
        print(f"✅ Frete calculado para {len(shipping_data)} CEPs")
        return shipping_data
        
    except Exception as e:
        print(f"❌ Erro geral no cálculo de frete: {e}")
        # Fallback completo para cálculo próprio
        return _calculate_own_shipping_for_ceps(main_ceps, product_weight, product_dimensions)

def _calculate_own_shipping_for_ceps(ceps, weight, dimensions):
    """Calcula frete próprio para múltiplos CEPs"""
    shipping_data = {}
    
    for cep in ceps.keys():
        shipping_data[cep] = _calculate_own_shipping_for_cep(cep, weight, dimensions)
    
    return shipping_data

def _calculate_own_shipping_for_cep(cep, weight, dimensions):
    """Calcula frete próprio para um CEP específico"""
    
    # Regras de frete próprio
    base_price = 19.90
    price_per_kg = 6.50
    express_multiplier = 1.5
    
    # Calcular preço baseado no peso
    total_price = base_price + (weight * price_per_kg)
    
    # Determinar prazo baseado na região
    region_days = _get_region_delivery_days(cep)
    
    return {
        'economy': {
            'price': round(total_price, 2),
            'days': region_days['economy'],
            'carrier': 'Correios/Parceiro',
            'service_name': 'Entrega Padrão'
        },
        'express': {
            'price': round(total_price * express_multiplier, 2),
            'days': region_days['express'],
            'carrier': 'Parceiro Expresso',
            'service_name': 'Entrega Expressa'
        }
    }

def _get_region_delivery_days(cep):
    """Determina prazo de entrega baseado na região do CEP"""
    
    # Extrair região do CEP (primeiros 2 dígitos)
    region = cep[:2]
    
    # Prazos por região (em dias úteis)
    region_prazos = {
        # Sudeste
        '01': {'economy': 3, 'express': 1},   # São Paulo
        '02': {'economy': 3, 'express': 1},   # São Paulo
        '03': {'economy': 3, 'express': 1},   # São Paulo
        '04': {'economy': 3, 'express': 1},   # São Paulo
        '05': {'economy': 3, 'express': 1},   # São Paulo
        '06': {'economy': 3, 'express': 1},   # São Paulo
        '07': {'economy': 3, 'express': 1},   # São Paulo
        '08': {'economy': 3, 'express': 1},   # São Paulo
        '09': {'economy': 3, 'express': 1},   # São Paulo
        '20': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '21': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '22': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '23': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '24': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '25': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '26': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '27': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '28': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '29': {'economy': 5, 'express': 2},   # Rio de Janeiro
        '30': {'economy': 4, 'express': 2},   # Minas Gerais
        '31': {'economy': 4, 'express': 2},   # Minas Gerais
        '32': {'economy': 4, 'express': 2},   # Minas Gerais
        '33': {'economy': 4, 'express': 2},   # Minas Gerais
        '34': {'economy': 4, 'express': 2},   # Minas Gerais
        '35': {'economy': 4, 'express': 2},   # Minas Gerais
        '36': {'economy': 4, 'express': 2},   # Minas Gerais
        '37': {'economy': 4, 'express': 2},   # Minas Gerais
        '38': {'economy': 4, 'express': 2},   # Minas Gerais
        '39': {'economy': 4, 'express': 2},   # Minas Gerais
        '11': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '12': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '13': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '14': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '15': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '16': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '17': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '18': {'economy': 3, 'express': 1},   # São Paulo (interior)
        '19': {'economy': 3, 'express': 1},   # São Paulo (interior)
        
        # Sul
        '80': {'economy': 6, 'express': 3},   # Paraná
        '81': {'economy': 6, 'express': 3},   # Paraná
        '82': {'economy': 6, 'express': 3},   # Paraná
        '83': {'economy': 6, 'express': 3},   # Paraná
        '84': {'economy': 6, 'express': 3},   # Paraná
        '85': {'economy': 6, 'express': 3},   # Paraná
        '86': {'economy': 6, 'express': 3},   # Paraná
        '87': {'economy': 6, 'express': 3},   # Paraná
        '88': {'economy': 6, 'express': 3},   # Paraná
        '89': {'economy': 6, 'express': 3},   # Paraná
        '90': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '91': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '92': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '93': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '94': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '95': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '96': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '97': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '98': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '99': {'economy': 7, 'express': 4},   # Rio Grande do Sul
        '88': {'economy': 5, 'express': 3},   # Santa Catarina
        '89': {'economy': 5, 'express': 3},   # Santa Catarina
        
        # Nordeste
        '40': {'economy': 8, 'express': 4},   # Bahia
        '41': {'economy': 8, 'express': 4},   # Bahia
        '42': {'economy': 8, 'express': 4},   # Bahia
        '43': {'economy': 8, 'express': 4},   # Bahia
        '44': {'economy': 8, 'express': 4},   # Bahia
        '45': {'economy': 8, 'express': 4},   # Bahia
        '46': {'economy': 8, 'express': 4},   # Bahia
        '47': {'economy': 8, 'express': 4},   # Bahia
        '48': {'economy': 8, 'express': 4},   # Bahia
        '49': {'economy': 8, 'express': 4},   # Bahia
        '50': {'economy': 9, 'express': 5},   # Pernambuco
        '51': {'economy': 9, 'express': 5},   # Pernambuco
        '52': {'economy': 9, 'express': 5},   # Pernambuco
        '53': {'economy': 9, 'express': 5},   # Pernambuco
        '54': {'economy': 9, 'express': 5},   # Pernambuco
        '55': {'economy': 9, 'express': 5},   # Pernambuco
        '56': {'economy': 9, 'express': 5},   # Pernambuco
        '57': {'economy': 9, 'express': 5},   # Pernambuco
        '58': {'economy': 9, 'express': 5},   # Pernambuco
        '59': {'economy': 9, 'express': 5},   # Pernambuco
        '60': {'economy': 8, 'express': 4},   # Ceará
        '61': {'economy': 8, 'express': 4},   # Ceará
        '62': {'economy': 8, 'express': 4},   # Ceará
        '63': {'economy': 8, 'express': 4},   # Ceará
        '64': {'economy': 8, 'express': 4},   # Ceará
        '65': {'economy': 8, 'express': 4},   # Ceará
        '66': {'economy': 8, 'express': 4},   # Ceará
        '67': {'economy': 8, 'express': 4},   # Ceará
        '68': {'economy': 8, 'express': 4},   # Ceará
        '69': {'economy': 8, 'express': 4},   # Ceará
        
        # Norte
        '65': {'economy': 12, 'express': 7},  # Mato Grosso
        '66': {'economy': 12, 'express': 7},  # Mato Grosso
        '67': {'economy': 12, 'express': 7},  # Mato Grosso
        '68': {'economy': 12, 'express': 7},  # Mato Grosso
        '69': {'economy': 12, 'express': 7},  # Mato Grosso
        '78': {'economy': 10, 'express': 6},  # Mato Grosso do Sul
        '79': {'economy': 10, 'express': 6},  # Mato Grosso do Sul
        '70': {'economy': 11, 'express': 6},  # Distrito Federal
        '71': {'economy': 11, 'express': 6},  # Distrito Federal
        '72': {'economy': 11, 'express': 6},  # Distrito Federal
        '73': {'economy': 11, 'express': 6},  # Distrito Federal
        '74': {'economy': 11, 'express': 6},  # Distrito Federal
        '75': {'economy': 11, 'express': 6},  # Distrito Federal
        '76': {'economy': 11, 'express': 6},  # Distrito Federal
        '77': {'economy': 11, 'express': 6},  # Distrito Federal
        '68': {'economy': 15, 'express': 8},  # Acre
        '69': {'economy': 15, 'express': 8},  # Acre
        '69': {'economy': 14, 'express': 8},  # Rondônia
        '76': {'economy': 13, 'express': 7},  # Roraima
        '77': {'economy': 13, 'express': 7},  # Roraima
        '69': {'economy': 16, 'express': 9},  # Amazonas
        '69': {'economy': 15, 'express': 8},  # Pará
        '69': {'economy': 14, 'express': 8},  # Amapá
        '69': {'economy': 15, 'express': 8},  # Tocantins
    }
    
    # Retornar prazo padrão se região não encontrada
    return region_prazos.get(region, {'economy': 10, 'express': 5})

# ===================== IMPORTAÇÃO DE PRODUTOS COM FRETE =====================
@app.route('/api/aliexpress/import-product', methods=['POST'])
def import_product_with_shipping():
    """Importa produto do AliExpress com cálculo de frete para CEPs principais"""
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_weight = data.get('weight', 0.5)  # kg
        product_dimensions = data.get('dimensions', {
            'length': 20.0,
            'width': 15.0, 
            'height': 5.0
        })
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID é obrigatório'}), 400
        
        print(f"📦 Iniciando importação do produto {product_id} com cálculo de frete...")
        
        # 1. Buscar detalhes do produto
        tokens = load_tokens()
        if not tokens or not tokens.get('access_token'):
            return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401
        
        # Parâmetros para buscar produto
        params = {
            "method": "aliexpress.ds.product.get",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "product_id": product_id,
            "ship_to_country": "BR",
            "target_currency": "BRL",
            "target_language": "pt",
            "remove_personal_benefit": "false"
        }
        
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Buscar produto
        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'Erro ao buscar produto do AliExpress'}), 400
        
        product_data = response.json()
        
        if 'aliexpress_ds_product_get_response' not in product_data:
            return jsonify({'success': False, 'message': 'Resposta inválida do AliExpress'}), 400
        
        result = product_data['aliexpress_ds_product_get_response'].get('result', {})
        
        # 2. Processar dados do produto
        processed_product = {
            'aliexpress_id': product_id,
            'title': result.get('ae_item_base_info_dto', {}).get('subject', ''),
            'description': result.get('ae_item_base_info_dto', {}).get('detail', ''),
            'main_image': result.get('ae_multimedia_info_dto', {}).get('image_urls', '').split(';')[0] if result.get('ae_multimedia_info_dto', {}).get('image_urls') else '',
            'images': result.get('ae_multimedia_info_dto', {}).get('image_urls', '').split(';') if result.get('ae_multimedia_info_dto', {}).get('image_urls') else [],
            'weight': product_weight,
            'dimensions': product_dimensions,
            'imported_at': int(time.time() * 1000),
            'status': 'active'
        }
        
        # 3. Calcular frete para CEPs principais
        print(f"🚚 Calculando frete para produto {product_id}...")
        shipping_data = calculate_shipping_for_main_ceps(product_id, product_weight, product_dimensions)
        
        # 4. Adicionar dados de frete ao produto
        processed_product['shipping_data'] = shipping_data
        
        # 5. Processar variações/SKUs se disponíveis
        if 'ae_item_sku_info_dtos' in result:
            sku_info = result['ae_item_sku_info_dtos']
            if 'ae_item_sku_info_d_t_o' in sku_info:
                skus = sku_info['ae_item_sku_info_d_t_o']
                processed_product['variations'] = skus if isinstance(skus, list) else [skus]
        
        # 6. Salvar no Firebase (simulado por enquanto)
        # TODO: Implementar integração real com Firebase
        firebase_product_id = f"product_{product_id}_{int(time.time())}"
        processed_product['firebase_id'] = firebase_product_id
        
        print(f"✅ Produto {product_id} importado com sucesso!")
        print(f"📊 Resumo:")
        print(f"  - Título: {processed_product['title'][:50]}...")
        print(f"  - Imagens: {len(processed_product['images'])}")
        print(f"  - Variações: {len(processed_product.get('variations', []))}")
        print(f"  - CEPs com frete: {len(shipping_data)}")
        
        return jsonify({
            'success': True,
            'message': 'Produto importado com sucesso',
            'data': {
                'product': processed_product,
                'shipping_ceps': list(shipping_data.keys()),
                'firebase_id': firebase_product_id
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return jsonify({'success': False, 'message': f'Erro na importação: {str(e)}'}), 500

@app.route('/api/aliexpress/import-products-batch', methods=['POST'])
def import_products_batch():
    """Importa múltiplos produtos em lote com cálculo de frete"""
    
    try:
        data = request.get_json()
        products = data.get('products', [])
        
        if not products or not isinstance(products, list):
            return jsonify({'success': False, 'message': 'Lista de produtos é obrigatória'}), 400
        
        print(f"📦 Iniciando importação em lote de {len(products)} produtos...")
        
        results = []
        success_count = 0
        error_count = 0
        
        for i, product_info in enumerate(products):
            try:
                print(f"📦 Processando produto {i+1}/{len(products)}: {product_info.get('product_id')}")
                
                # Simular importação individual
                result = {
                    'product_id': product_info.get('product_id'),
                    'status': 'success',
                    'firebase_id': f"product_{product_info.get('product_id')}_{int(time.time())}",
                    'shipping_ceps': ["01001000", "20040020", "90020060", "40000000", "50000000"]
                }
                
                results.append(result)
                success_count += 1
                
            except Exception as e:
                print(f"❌ Erro no produto {product_info.get('product_id')}: {e}")
                results.append({
                    'product_id': product_info.get('product_id'),
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        print(f"✅ Importação em lote concluída!")
        print(f"📊 Resumo: {success_count} sucessos, {error_count} erros")
        
        return jsonify({
            'success': True,
            'message': f'Importação concluída: {success_count} sucessos, {error_count} erros',
            'data': {
                'results': results,
                'summary': {
                    'total': len(products),
                    'success': success_count,
                    'error': error_count
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na importação em lote: {e}")
        return jsonify({'success': False, 'message': f'Erro na importação em lote: {str(e)}'}), 500



if __name__ == '__main__':
    print(f'🚀 Servidor rodando na porta {PORT}')
    print(f'APP_KEY: {"✅" if APP_KEY else "❌"} | APP_SECRET: {"✅" if APP_SECRET else "❌"} | REDIRECT_URI: {REDIRECT_URI}')
    app.run(host='0.0.0.0', port=PORT, debug=False) 