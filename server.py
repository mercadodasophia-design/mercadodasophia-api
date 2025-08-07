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

app = Flask(__name__)

# ===================== CONFIGURA├º├ÁES =====================
APP_KEY = os.getenv('APP_KEY', '517616')  # Substitua pela sua APP_KEY
APP_SECRET = os.getenv('APP_SECRET', 'skAvaPWbGLkkx5TlKf8kvLmILQtTV2sq')
PORT = int(os.getenv('PORT', 5000))

REDIRECT_URI = "https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback"

TOKENS_FILE = 'tokens.json'

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
    """Gera URL de autoriza├º├úo"""
    auth_url = (
        f'https://api-sg.aliexpress.com/oauth/authorize?response_type=code'
        f'&force_auth=true&client_id={APP_KEY}&redirect_uri={REDIRECT_URI}'
    )
    print(f'­ƒöù URL de autoriza├º├úo gerada: {auth_url}')
    return jsonify({'success': True, 'auth_url': auth_url})

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
                print(f'­ƒöì AN├üLISE ESTRUTURA - BUSCA RESULT:')
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
        return jsonify({'success': False, 'message': 'Token n├úo encontrado. Fa├ºa autoriza├º├úo primeiro.'}), 401

    try:
        # Par├ómetros para a API conforme documenta├º├úo
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
        
        # Fazer requisi├º├úo HTTP direta para /sync
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
        return jsonify({'success': False, 'message': 'Token n├úo encontrado. Fa├ºa autoriza├º├úo primeiro.'}), 401

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
            return jsonify({'success': False, 'error': 'Dados do produto n├úo encontrados'}), 400
            
        # Extrair o primeiro skuId dispon├¡vel
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
        product_price = "10.00"  # Preço padrão
        
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
                print(f'­ƒöì AN├üLISE ESTRUTURA - FRETE RESULT:')
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
            
            # Padrões comuns: "29#Red;14#M" ou "13143:Red" ou "14"
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
                    # Formato: "13143:Red"
                    code, value = part.split(':', 1)
                    attributes.append({
                        'code': code.strip(),
                        'value': value.strip(),
                        'translated_code': translate_attribute_code(code.strip()),
                        'translated_value': translate_attribute_value(value.strip())
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

if __name__ == '__main__':
    print(f'­ƒÜÇ Servidor rodando na porta {PORT}')
    print(f'APP_KEY: {"Ô£à" if APP_KEY else "ÔØî"} | APP_SECRET: {"Ô£à" if APP_SECRET else "ÔØî"} | REDIRECT_URI: {REDIRECT_URI}')
    app.run(host='0.0.0.0', port=PORT, debug=False) 