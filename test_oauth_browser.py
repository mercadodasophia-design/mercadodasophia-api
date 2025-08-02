#!/usr/bin/env python3
"""
Script Python para testar OAuth com sessão do navegador
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

class AliExpressOAuthBrowser:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.oauth_url = 'https://oauth.aliexpress.com'
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print()

    def generate_auth_urls(self):
        """Gerar URLs de autorização para testar no navegador"""
        print("🔗 URLs de autorização para testar no navegador:\n")
        
        # Teste 1: URL mais simples possível
        params1 = {
            'response_type': 'code',
            'client_id': self.app_key
        }
        url1 = f"{self.oauth_url}/authorize?{urlencode(params1)}"
        print("📋 Teste 1 - URL Simples:")
        print(url1)
        print()
        
        # Teste 2: Com redirect_uri
        params2 = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback'
        }
        url2 = f"{self.oauth_url}/authorize?{urlencode(params2)}"
        print("📋 Teste 2 - URL com redirect_uri:")
        print(url2)
        print()
        
        # Teste 3: Com state
        params3 = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback',
            'state': 'test123'
        }
        url3 = f"{self.oauth_url}/authorize?{urlencode(params3)}"
        print("📋 Teste 3 - URL com state:")
        print(url3)
        print()
        
        # Teste 4: Com scope
        params4 = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback',
            'scope': 'read'
        }
        url4 = f"{self.oauth_url}/authorize?{urlencode(params4)}"
        print("📋 Teste 4 - URL com scope:")
        print(url4)
        print()
        
        # Teste 5: Com display
        params5 = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback',
            'display': 'page'
        }
        url5 = f"{self.oauth_url}/authorize?{urlencode(params5)}"
        print("📋 Teste 5 - URL com display:")
        print(url5)
        print()
        
        print("🧪 Instruções:")
        print("1. Abra cada URL no navegador")
        print("2. Faça login no AliExpress se necessário")
        print("3. Veja se aparece a tela de autorização")
        print("4. Se funcionar, copie o código da URL de retorno")
        print("5. Execute: python test_oauth_browser.py SEU_CODIGO")
        print()

    def test_token_exchange(self, auth_code):
        """Testar troca de código por token"""
        try:
            print(f"🔄 Trocando code por access_token...")
            print(f"Code: {auth_code}")
            
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.app_key,
                'client_secret': self.app_secret,
                'redirect_uri': 'https://mercadodasophia.com/callback',
                'code': auth_code
            }
            
            print(f"📤 Parâmetros: {data}")
            
            response = requests.post(
                f"{self.oauth_url}/token",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if 'access_token' in result:
                        print("✅ Access token gerado com sucesso!")
                        return result['access_token']
                    else:
                        print(f"❌ Resposta não contém access_token: {result}")
                        return None
                except:
                    print("❌ Resposta não é JSON válido")
                    return None
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return None

    def test_product_api_with_token(self, access_token):
        """Testar API de produtos com access token"""
        try:
            print("🧪 Testando API de produtos com access token...")
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': 'aliexpress.ds.product.get',
                'access_token': access_token,
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
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resposta da API: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return None

def main():
    import sys
    
    oauth = AliExpressOAuthBrowser()
    
    if len(sys.argv) > 1:
        auth_code = sys.argv[1]
        print(f"🔑 Authorization Code fornecido: {auth_code}")
        
        access_token = oauth.test_token_exchange(auth_code)
        if access_token:
            oauth.test_product_api_with_token(access_token)
    else:
        oauth.generate_auth_urls()

if __name__ == "__main__":
    main() 