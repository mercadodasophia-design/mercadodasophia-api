#!/usr/bin/env python3
"""
Script Python para debugar o problema do OAuth do AliExpress
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
CALLBACK_URL = 'https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback'

def test_oauth_exchange():
    """Teste manual do OAuth2"""
    
    # Simular um código de autorização (você precisa de um real)
    test_code = "3_517616_O7CHy8u8IkY9VFGUG9yD6u1f1494"  # Use o código real que você recebeu
    
    print("🔍 TESTE OAUTH2 DEBUG")
    print(f"📝 APP_KEY: {APP_KEY}")
    print(f"📝 APP_SECRET: {APP_SECRET[:10]}...")
    print(f"📝 CALLBACK_URL: {CALLBACK_URL}")
    print(f"📝 CODE: {test_code}")
    
    # Teste com o endpoint que estamos usando
    token_url = 'https://api-sg.aliexpress.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'redirect_uri': CALLBACK_URL,
        'code': test_code,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    print(f"\n🔄 Testando endpoint: {token_url}")
    print(f"📝 Dados enviados: {data}")
    print(f"📝 Headers: {headers}")
    
    try:
        resp = requests.post(token_url, data=data, headers=headers, timeout=30)
        
        print(f"\n📊 Status Code: {resp.status_code}")
        print(f"📄 Response Headers: {dict(resp.headers)}")
        print(f"📄 Response Text: {resp.text[:2000]}...")
        
        if resp.status_code == 200:
            try:
                json_response = resp.json()
                print(f"✅ JSON Response: {json_response}")
            except:
                print("❌ Não foi possível fazer parse do JSON")
        else:
            print(f"❌ Erro HTTP: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_oauth_exchange() 