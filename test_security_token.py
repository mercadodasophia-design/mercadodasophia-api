#!/usr/bin/env python3
"""
Script Python para testar o generateSecurityToken do AliExpress
Baseado na documentação oficial
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

class AliExpressSecurityToken:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print()

    def generate_auth_url(self):
        """Gerar URL de autorização OAuth"""
        print("🔗 Gerando URL de autorização...")
        
        params = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback'
        }
        
        auth_url = f"https://oauth.aliexpress.com/authorize?{urlencode(params)}"
        
        print("📋 URL de Autorização:")
        print(auth_url)
        print("\n📋 Instruções:")
        print("1. Abra esta URL no navegador")
        print("2. Faça login no AliExpress")
        print("3. Autorize o app")
        print("4. Copie o código da URL de retorno")
        print("5. Execute: python test_security_token.py SEU_CODIGO")
        print()
        
        return auth_url

    def generate_security_token(self, auth_code):
        """Gerar security token usando o endpoint oficial"""
        try:
            print(f"🔄 Gerando security token com code: {auth_code}")
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': 'auth.token.security.create',
                'app_key': self.app_key,
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5',
                'code': auth_code
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
                try:
                    result = response.json()
                    if 'auth_token_security_create_response' in result:
                        token_data = result['auth_token_security_create_response']['resp_result']['result']
                        access_token = token_data.get('access_token')
                        if access_token:
                            print("✅ Security token gerado com sucesso!")
                            print(f"🔑 Access Token: {access_token}")
                            print(f"⏰ Expires in: {token_data.get('expires_in')} segundos")
                            return access_token
                        else:
                            print("❌ Access token não encontrado na resposta")
                            return None
                    else:
                        print(f"❌ Resposta inesperada: {result}")
                        return None
                except Exception as e:
                    print(f"❌ Erro ao processar resposta: {str(e)}")
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
    
    token_gen = AliExpressSecurityToken()
    
    if len(sys.argv) > 1:
        auth_code = sys.argv[1]
        print(f"🔑 Authorization Code fornecido: {auth_code}")
        
        access_token = token_gen.generate_security_token(auth_code)
        if access_token:
            token_gen.test_product_api_with_token(access_token)
    else:
        token_gen.generate_auth_url()

if __name__ == "__main__":
    main() 