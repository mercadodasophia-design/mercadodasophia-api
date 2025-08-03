#!/usr/bin/env python3
"""
Modelo completo e funcional para AliExpress API
Baseado na documentação oficial
"""

import requests
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')

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

def exchange_code_for_token(code):
    """
    Troca código OAuth2 por access_token
    Baseado na documentação oficial
    """
    token_url = 'https://api-sg.aliexpress.com/rest'
    
    # Parâmetros obrigatórios para OAuth2
    data = {
        'method': '/auth/token/create',
        'app_key': APP_KEY,
        'app_secret': APP_SECRET,
        'code': code,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
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
    
    try:
        resp = requests.post(token_url, data=data, headers=headers, timeout=30)
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response: {resp.text[:500]}...")
        
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise e

def search_products(access_token, keywords, page=1, page_size=20):
    """
    Busca produtos usando access_token
    Baseado na documentação oficial
    """
    api_url = 'https://api-sg.aliexpress.com/sync'
    
    # Parâmetros obrigatórios para busca de produtos
    params = {
        'method': 'aliexpress.solution.product.list',
        'app_key': APP_KEY,
        'access_token': access_token,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
        'page_size': str(page_size),
        'page_index': str(page),
        'keywords': keywords,
    }
    
    # Gerar assinatura MD5
    sign = generate_sign(params)
    params['sign'] = sign
    
    print(f"🔍 Buscando produtos: {keywords}")
    print(f"📝 Parâmetros: {params}")
    
    try:
        resp = requests.post(api_url, data=params, timeout=30)
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response: {resp.text[:500]}...")
        
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise e

def test_complete_flow():
    """
    Teste completo do fluxo OAuth2 + busca de produtos
    """
    print("🚀 TESTE COMPLETO ALIEXPRESS API")
    print(f"🔑 APP_KEY: {APP_KEY}")
    print(f"🔑 APP_SECRET: {APP_SECRET[:10]}...")
    
    # 1. Teste OAuth2 (use um código real)
    test_code = "3_517616_AQFGyoYBYbcvGb8brK2KVNwV1922"  # Substitua pelo código real
    
    print("\n=== 1. TESTE OAUTH2 ===")
    try:
        token_data = exchange_code_for_token(test_code)
        print(f"✅ OAuth2 funcionando!")
        print(f"🔑 Token data: {token_data}")
        
        # Extrair access_token
        access_token = token_data.get('access_token')
        if not access_token:
            print("❌ Access token não encontrado na resposta")
            return False
            
        print(f"🔑 Access Token: {access_token[:20]}...")
        
        # 2. Teste busca de produtos
        print("\n=== 2. TESTE BUSCA DE PRODUTOS ===")
        products_data = search_products(access_token, "phone")
        print(f"✅ Busca de produtos funcionando!")
        print(f"📦 Products data: {products_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 SUCESSO! API AliExpress funcionando!")
    else:
        print("\n❌ Falha no teste") 