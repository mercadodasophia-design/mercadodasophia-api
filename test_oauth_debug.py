#!/usr/bin/env python3
"""
Script Python para debugar o problema do OAuth do AliExpress
"""

import requests
import hashlib
import time
import json
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

# Carregar variáveis de ambiente
load_dotenv('config.env')

class AliExpressOAuthDebug:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.oauth_url = 'https://oauth.aliexpress.com'
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print()

    def test_oauth_endpoint(self):
        """Testar se o endpoint OAuth está funcionando"""
        try:
            print("🧪 Testando endpoint OAuth...")
            
            # Teste simples do endpoint
            response = requests.get(f"{self.oauth_url}/authorize", timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ Endpoint OAuth está respondendo")
                return True
            else:
                print("❌ Endpoint OAuth não está respondendo corretamente")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar endpoint OAuth: {str(e)}")
            return False

    def test_different_app_keys(self):
        """Testar com diferentes formatos de App Key"""
        print("🧪 Testando diferentes formatos de App Key...\n")
        
        # Teste 1: App Key como string
        params1 = {
            'response_type': 'code',
            'client_id': str(self.app_key)
        }
        url1 = f"{self.oauth_url}/authorize?{urlencode(params1)}"
        print("📋 Teste 1 - App Key como string:")
        print(url1)
        print()
        
        # Teste 2: App Key com aspas
        params2 = {
            'response_type': 'code',
            'client_id': f'"{self.app_key}"'
        }
        url2 = f"{self.oauth_url}/authorize?{urlencode(params2)}"
        print("📋 Teste 2 - App Key com aspas:")
        print(url2)
        print()
        
        # Teste 3: App Key com zeros à esquerda
        params3 = {
            'response_type': 'code',
            'client_id': self.app_key.zfill(10)
        }
        url3 = f"{self.oauth_url}/authorize?{urlencode(params3)}"
        print("📋 Teste 3 - App Key com zeros à esquerda:")
        print(url3)
        print()

    def test_different_oauth_urls(self):
        """Testar diferentes URLs de OAuth"""
        print("🧪 Testando diferentes URLs de OAuth...\n")
        
        oauth_urls = [
            'https://oauth.aliexpress.com',
            'https://oauth.aliexpress.com/oauth',
            'https://api.aliexpress.com/oauth',
            'https://api-sg.aliexpress.com/oauth'
        ]
        
        for oauth_url in oauth_urls:
            try:
                print(f"🧪 Testando: {oauth_url}")
                
                params = {
                    'response_type': 'code',
                    'client_id': self.app_key
                }
                
                url = f"{oauth_url}/authorize?{urlencode(params)}"
                print(f"   URL: {url}")
                
                response = requests.get(url, timeout=10)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                print()
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
                print()

    def test_api_without_oauth(self):
        """Testar se conseguimos usar a API sem OAuth"""
        print("🧪 Testando API sem OAuth...")
        
        try:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': 'aliexpress.ds.category.get',
                'app_key': self.app_key,
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5'
            }
            
            # Gerar assinatura
            sorted_params = dict(sorted(params.items()))
            param_string = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
            sign_string = self.app_secret + param_string + self.app_secret
            sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
            params['sign'] = sign
            
            print(f"📤 Parâmetros: {json.dumps(params, indent=2)}")
            
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status: {response.status_code}")
            print(f"📥 Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                result = response.json()
                if 'error_response' not in result:
                    print("✅ API funcionando sem OAuth!")
                    return True
                else:
                    print(f"❌ Erro da API: {result['error_response']}")
                    return False
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False

    def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 Iniciando debug completo do OAuth\n")
        
        # Teste 1: Endpoint OAuth
        self.test_oauth_endpoint()
        print()
        
        # Teste 2: Diferentes App Keys
        self.test_different_app_keys()
        
        # Teste 3: Diferentes URLs OAuth
        self.test_different_oauth_urls()
        
        # Teste 4: API sem OAuth
        self.test_api_without_oauth()

def main():
    debug = AliExpressOAuthDebug()
    debug.run_all_tests()

if __name__ == "__main__":
    main() 