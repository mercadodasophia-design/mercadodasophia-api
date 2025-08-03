#!/usr/bin/env python3
"""
Teste simples e direto para AliExpress OAuth2
Baseado na documentação oficial
"""

import requests
import hashlib
import os
from datetime import datetime, timezone
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

def test_oauth_simple():
    """
    Teste simples do OAuth2
    """
    print("🚀 TESTE SIMPLES OAUTH2")
    print(f"🔑 APP_KEY: {APP_KEY}")
    print(f"🔑 APP_SECRET: {APP_SECRET[:10]}...")
    
    # Código real do callback
    test_code = "3_517616_AQFGyoYBYbcvGb8brK2KVNwV1922"
    
    # Endpoint correto
    token_url = 'https://api-sg.aliexpress.com/rest'
    
    # Parâmetros mínimos
    data = {
        'method': '/auth/token/create',
        'app_key': APP_KEY,
        'app_secret': APP_SECRET,
        'code': test_code,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
    }
    
    # Gerar assinatura
    sign = generate_sign(data)
    data['sign'] = sign
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    print(f"🔄 Fazendo requisição...")
    print(f"📝 URL: {token_url}")
    print(f"📝 Dados: {data}")
    print(f"📝 Sign: {sign}")
    
    try:
        resp = requests.post(token_url, data=data, headers=headers, timeout=30)
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response: {resp.text}")
        
        if resp.status_code == 200:
            try:
                json_data = resp.json()
                print(f"✅ JSON Response: {json_data}")
                
                if 'access_token' in json_data:
                    print(f"🎉 SUCESSO! Access token obtido!")
                    return True
                else:
                    print(f"❌ Access token não encontrado na resposta")
                    return False
            except:
                print(f"❌ Erro ao fazer parse do JSON")
                return False
        else:
            print(f"❌ Erro HTTP: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth_simple()
    if success:
        print("\n🎉 SUCESSO! OAuth2 funcionando!")
    else:
        print("\n❌ Falha no OAuth2") 