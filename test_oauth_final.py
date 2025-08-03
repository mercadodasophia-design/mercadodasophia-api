#!/usr/bin/env python3
"""
Teste final do OAuth2 baseado na documentação oficial do AliExpress
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
CALLBACK_URL = 'https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback'

def test_oauth_with_docs():
    """Teste baseado na documentação oficial"""
    
    # Use o código real que você recebeu do callback
    test_code = "3_517616_O7CHy8u8IkY9VFGUG9yD6u1f1494"  # Substitua pelo código real
    
    print("🔍 TESTE OAUTH2 FINAL - Baseado na documentação oficial")
    print(f"📝 APP_KEY: {APP_KEY}")
    print(f"📝 APP_SECRET: {APP_SECRET[:10]}...")
    print(f"📝 CALLBACK_URL: {CALLBACK_URL}")
    print(f"📝 CODE: {test_code}")
    
    # Teste 1: Endpoint da documentação
    print("\n🔄 TESTE 1: Endpoint da documentação")
    token_url = 'https://api-sg.aliexpress.com/rest'
    data = {
        'method': '/auth/token/create',
        'app_key': APP_KEY,
        'app_secret': APP_SECRET,
        'code': test_code,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sign_method': 'md5',
        'format': 'json',
        'v': '2.0',
    }
    
    # Gerar assinatura MD5
    def generate_sign(params):
        """Gerar assinatura MD5 para a API do AliExpress"""
        import hashlib
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
    
    sign = generate_sign(data)
    data['sign'] = sign
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        resp = requests.post(token_url, data=data, headers=headers, timeout=30)
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response Text: {resp.text[:500]}...")
        
        if resp.status_code == 200:
            try:
                json_response = resp.json()
                print(f"✅ JSON Response: {json_response}")
                return True
            except:
                print("❌ Não foi possível fazer parse do JSON")
        else:
            print(f"❌ Erro HTTP: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Sem parâmetros extras
    print("\n🔄 TESTE 2: Parâmetros mínimos")
    data_minimal = {
        'method': '/auth/token/create',
        'app_key': APP_KEY,
        'app_secret': APP_SECRET,
        'code': test_code,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sign_method': 'md5',
    }
    
    # Gerar assinatura MD5
    sign = generate_sign(data_minimal)
    data_minimal['sign'] = sign
    
    try:
        resp = requests.post(token_url, data=data_minimal, headers=headers, timeout=30)
        print(f"📊 Status Code: {resp.status_code}")
        print(f"📄 Response Text: {resp.text[:500]}...")
        
        if resp.status_code == 200:
            try:
                json_response = resp.json()
                print(f"✅ JSON Response: {json_response}")
                return True
            except:
                print("❌ Não foi possível fazer parse do JSON")
        else:
            print(f"❌ Erro HTTP: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False

if __name__ == "__main__":
    success = test_oauth_with_docs()
    if success:
        print("\n✅ OAuth2 funcionando!")
    else:
        print("\n❌ OAuth2 ainda com problemas") 