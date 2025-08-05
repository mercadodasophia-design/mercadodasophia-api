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

# ===================== CONFIGURAÇÕES =====================
APP_KEY = os.getenv('APP_KEY', '517616')  # Substitua pela sua APP_KEY
APP_SECRET = os.getenv('APP_SECRET', 'skAvaPWbGLkkx5TlKf8kvLmILQtTV2sq')
PORT = int(os.getenv('PORT', 5000))

REDIRECT_URI = "https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback"

TOKENS_FILE = 'tokens.json'

# ===================== FUNÇÕES AUXILIARES =====================
def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f)
    print('💾 Tokens salvos com sucesso!')

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    return None

def generate_gop_signature(params, app_secret):
    """Gera assinatura GOP para AliExpress API"""
    # Ordenar parâmetros alfabeticamente
    sorted_params = sorted(params.items())
    
    # Concatenar parâmetros
    param_string = ''
    for key, value in sorted_params:
        param_string += f'{key}{value}'
    
    # Adicionar app_secret no início e fim
    sign_string = f'{app_secret}{param_string}{app_secret}'
    
    # Gerar MD5
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    return signature

def generate_api_signature(params, app_secret):
    """Gerar assinatura para APIs de negócios do AliExpress"""
    # Ordenar parâmetros alfabeticamente
    sorted_params = dict(sorted(params.items()))
    
    # Concatenar chave=valor sem separadores
    param_string = ''.join(f"{k}{v}" for k, v in sorted_params.items())
    
    # Concatenar secret + params + secret
    to_sign = f"{app_secret}{param_string}{app_secret}"
    
    # Gerar MD5 em maiúsculo
    signature = hashlib.md5(to_sign.encode('utf-8')).hexdigest().upper()
    
    return signature

def create_test_page():
    """Cria página HTML de teste"""
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
            <h1>🐍 AliExpress API Python</h1>
            <p>Servidor de teste com SDK oficial Alibaba</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>ℹ️ Como usar</h3>
                <p>Esta é a versão Python da API AliExpress que utiliza o SDK oficial da Alibaba. 
                Clique nos links abaixo para testar as funcionalidades. Para usar as APIs protegidas, 
                primeiro faça a autorização OAuth.</p>
            </div>
            
            <div class="section">
                <h2>🔐 Autenticação OAuth</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>1. Gerar URL de Autorização</h3>
                        <p>Gera a URL para autorização no AliExpress</p>
                        <a href="''' + base_url + '''/api/aliexpress/auth" target="_blank" class="btn">🔗 Testar Autorização</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>2. Status dos Tokens</h3>
                        <p>Verifica se há tokens salvos no servidor</p>
                        <a href="''' + base_url + '''/api/aliexpress/tokens/status" target="_blank" class="btn btn-secondary">📊 Ver Status</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🛍️ APIs de Produtos</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>Buscar Categorias</h3>
                        <p>Lista categorias de produtos do AliExpress</p>
                        <a href="''' + base_url + '''/api/aliexpress/categories" target="_blank" class="btn btn-secondary">📂 Ver Categorias</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>Buscar Produtos</h3>
                        <p>Busca produtos por categoria (requer token)</p>
                        <a href="''' + base_url + '''/api/aliexpress/products" target="_blank" class="btn btn-warning">🛒 Ver Produtos</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Informações da API</h2>
                <div class="endpoint-grid">
                    <div class="endpoint-card">
                        <h3>Informações do Servidor</h3>
                        <p>Detalhes sobre endpoints disponíveis</p>
                        <a href="''' + base_url + '''/" target="_blank" class="btn">ℹ️ Ver Info</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>Documentação</h3>
                        <p>Link para a documentação do SDK</p>
                        <a href="https://openservice.aliexpress.com/doc/doc.htm" target="_blank" class="btn btn-secondary">📚 Ver Docs</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 Status do Sistema</h2>
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
            <p>© 2025 Mercado da Sophia - AliExpress API Python com SDK oficial Alibaba</p>
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
    """Cria página HTML para callback OAuth"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')
    
    return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✅ Autorização OAuth Concluída - AliExpress API Python</title>
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
            <h1>🎉 Autorização Concluída!</h1>
            <p>Tokens salvos com sucesso no servidor</p>
        </div>
        
        <div class="content">
            <div class="success-icon">✅</div>
            
            <div class="status-section">
                <h3>🎯 Status da Autorização</h3>
                <p><strong>✅ Sucesso!</strong> Os tokens foram gerados e salvos no servidor. Agora você pode usar as APIs protegidas do AliExpress.</p>
            </div>
            
            <div class="info-box">
                <h3>ℹ️ Próximos Passos</h3>
                <p>Agora que você tem os tokens salvos, pode testar as APIs de produtos e categorias. 
                Os tokens ficam armazenados no servidor e são usados automaticamente nas requisições.</p>
            </div>
            
            <h3>🔑 Dados dos Tokens</h3>
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
                <h3>🚀 Testar APIs</h3>
                <a href="''' + base_url + '''/api/aliexpress/tokens/status" target="_blank" class="btn btn-secondary">📊 Verificar Status</a>
                <a href="''' + base_url + '''/api/aliexpress/categories" target="_blank" class="btn btn-warning">📂 Buscar Categorias</a>
                <a href="''' + base_url + '''/api/aliexpress/products" target="_blank" class="btn">🛒 Buscar Produtos</a>
                <a href="''' + base_url + '''/" target="_blank" class="btn btn-secondary">🏠 Voltar ao Início</a>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 Mercado da Sophia - AliExpress API Python com SDK oficial Alibaba</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            if (text && text !== 'N/A') {
                navigator.clipboard.writeText(text).then(function() {
                    alert('Token copiado para a área de transferência!');
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
    """Página inicial com links de teste"""
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

@app.route('/api/aliexpress/oauth-callback')
def oauth_callback():
    """Callback OAuth"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Código de autorização não fornecido'}), 400

    print(f'🔍 Callback OAuth recebido com code: {code}')

    # Tentar diferentes abordagens
    attempts = [
        {
            'name': 'DS API Standard',
            'url': 'https://api-sg.aliexpress.com/oauth/token',
            'data': {
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            }
        },
        {
            'name': 'Seller OAuth',
            'url': 'https://api-sg.aliexpress.com/seller/oauth/token',
            'data': {
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            }
        },
        {
            'name': 'Alternative OAuth',
            'url': 'https://api-sg.aliexpress.com/oauth2/token',
            'data': {
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            }
        },
        {
            'name': 'Direct API',
            'url': 'https://api-sg.aliexpress.com/api/oauth/token',
            'data': {
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            }
        },
        {
            'name': 'Seller API with GOP',
            'url': 'https://api-sg.aliexpress.com/auth/token/create',
            'data': {
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
                "timestamp": str(int(time.time())),
                "format": "json",
                "v": "2.0",
                "sign_method": "md5"
            }
        },
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
        print(f'🔧 Tentativa: {attempt["name"]}')
        print(f'🔧 URL: {attempt["url"]}')
        
        # Gerar assinatura GOP se necessário
        data = attempt['data'].copy()
        if 'timestamp' in data:  # Se tem timestamp, precisa de assinatura GOP
            signature = generate_gop_signature(data, APP_SECRET)
            data['sign'] = signature
            print(f'🔧 Assinatura GOP gerada: {signature}')
        
        print(f'🔧 Data: {data}')
        
        try:
            if attempt['url'] == 'SDK_METHOD':
                # Usar SDK oficial do AliExpress - Método correto da documentação
                print(f'🔧 Usando SDK oficial do AliExpress (método correto)...')
                try:
                    # URL base correta conforme documentação
                    client = iop.IopClient('https://api-sg.aliexpress.com/rest', APP_KEY, APP_SECRET)
                    request_obj = iop.IopRequest('/auth/token/create')
                    request_obj.add_api_param('code', code)
                    # Não adicionar uuid conforme documentação
                    
                    response = client.execute(request_obj)
                    print(f'✅ SDK Response: {response.body}')
                    
                    if response.code == '0':
                        tokens = response.body
                        print(f'✅ Sucesso usando SDK oficial!')
                        save_tokens(tokens)
                        
                        if request.headers.get('Accept', '').find('text/html') != -1:
                            return create_callback_page(tokens)
                        else:
                            return jsonify({'success': True, 'tokens': tokens})
                    else:
                        print(f'❌ Erro no SDK: {response.body}')
                        continue
                        
                except Exception as sdk_error:
                    print(f'❌ Erro no SDK: {sdk_error}')
                    continue
            else:
                # Usar requisição HTTP normal
                response = requests.post(attempt['url'], headers=headers, data=data)
                print(f'✅ Status Code: {response.status_code}')
                print(f'✅ Content-Type: {response.headers.get("Content-Type")}')
                print(f'✅ Raw Response: {response.text[:300]}...')

                if response.status_code == 200:
                    try:
                        tokens = response.json()
                        
                        if 'error' in tokens:
                            print(f'❌ Erro na tentativa {attempt["name"]}: {tokens.get("error")}')
                            continue
                        
                        print(f'✅ Sucesso na tentativa {attempt["name"]}!')
                        save_tokens(tokens)
                        
                        # Retornar página HTML se a requisição aceita HTML
                        if request.headers.get('Accept', '').find('text/html') != -1:
                            return create_callback_page(tokens)
                        else:
                            # Retornar JSON para requisições programáticas
                            return jsonify({'success': True, 'tokens': tokens})
                            
                    except json.JSONDecodeError as json_error:
                        print(f'❌ Erro ao decodificar JSON na tentativa {attempt["name"]}: {json_error}')
                        continue
                else:
                    print(f'❌ Status code {response.status_code} na tentativa {attempt["name"]}')
                    continue
                
        except Exception as e:
            print(f'❌ Erro na tentativa {attempt["name"]}: {e}')
            continue

    # Se chegou aqui, nenhuma tentativa funcionou
    error_message = "Todas as tentativas falharam. Verifique a configuração da app no AliExpress."
    print(f'❌ {error_message}')
    return jsonify({
        'success': False,
        'message': error_message,
        'details': 'A API está retornando HTML em vez de JSON. Isso pode indicar: 1) App não configurada corretamente no AliExpress, 2) Tipo de app incorreto, 3) Permissões insuficientes'
    }), 400

@app.route('/api/aliexpress/products')
def products():
    """Buscar produtos"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401

    try:
        # Parâmetros para a API
        params = {
            "method": "aliexpress.ds.text.search",
            "app_key": APP_KEY,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "access_token": tokens['access_token'],
            "keyWord": request.args.get('q', 'electronics'),
            "local": "zh_CN",
            "countryCode": "US",
            "currency": "USD"
        }
        
        # Gerar assinatura
        params["sign"] = generate_api_signature(params, APP_SECRET)
        
        # Fazer requisição HTTP direta
        response = requests.get('https://api-sg.aliexpress.com/rest', params=params)
        print(f'✅ Resposta produtos: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                return jsonify({'success': True, 'data': data})
            else:
                return jsonify({'success': False, 'error': data}), 400
        else:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'❌ Erro ao buscar produtos: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/aliexpress/categories')
def categories():
    """Buscar categorias"""
    tokens = load_tokens()
    if not tokens or not tokens.get('access_token'):
        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401

    try:
        # Parâmetros para a API
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
        
        # Fazer requisição HTTP direta
        response = requests.get('https://api-sg.aliexpress.com/rest', params=params)
        print(f'✅ Resposta categorias: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                return jsonify({'success': True, 'data': data})
            else:
                return jsonify({'success': False, 'error': data}), 400
        else:
            return jsonify({'success': False, 'error': response.text}), response.status_code

    except Exception as e:
        print(f'❌ Erro ao buscar categorias: {e}')
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

if __name__ == '__main__':
    print(f'🚀 Servidor rodando na porta {PORT}')
    print(f'APP_KEY: {"✅" if APP_KEY else "❌"} | APP_SECRET: {"✅" if APP_SECRET else "❌"} | REDIRECT_URI: {REDIRECT_URI}')
    app.run(host='0.0.0.0', port=PORT, debug=False) 