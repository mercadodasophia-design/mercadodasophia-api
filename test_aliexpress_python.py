#!/usr/bin/env python3
"""
Script Python para testar a API do AliExpress
"""

import requests
import hashlib
import time
import json
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

class AliExpressPythonAPI:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.redirect_uri = 'https://mercadodasophia.com/callback'
        self.oauth_url = 'https://oauth.aliexpress.com'
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print(f"   App Secret (primeiros 4): {self.app_secret[:4] + '...' if self.app_secret else 'N/A'}")
        print()

    def generate_auth_url(self):
        """Gerar URL de autorização OAuth2"""
        params = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': self.redirect_uri,
            'state': 'xyz'
        }
        
        auth_url = f"{self.oauth_url}/authorize?{urlencode(params)}"
        
        print("🔗 URL de Autorização:")
        print(auth_url)
        print("\n📋 Instruções:")
        print("1. Abra esta URL no navegador")
        print("2. Faça login no AliExpress")
        print("3. Autorize o app")
        print("4. Copie o código da URL de retorno")
        print("5. Execute: python test_aliexpress_python.py SEU_CODIGO")
        print()
        
        return auth_url

    def exchange_code_for_token(self, authorization_code):
        """Trocar authorization code por access token"""
        try:
            print("🔄 Trocando code por access_token...")
            
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.app_key,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': authorization_code,
                'need_refresh_token': 'true'
            }
            
            print(f"📤 Parâmetros OAuth2: {data}")
            
            response = requests.post(
                f"{self.oauth_url}/token",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    print("✅ Access token gerado com sucesso!")
                    return token_data['access_token']
                else:
                    print(f"❌ Resposta não contém access_token: {token_data}")
                    return None
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao trocar code por token: {str(e)}")
            return None

    def generate_sign(self, params):
        """Gerar assinatura MD5 para API de Dropshipping"""
        # Ordenar parâmetros
        sorted_params = dict(sorted(params.items()))
        
        # Criar string de parâmetros
        param_string = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        
        # Gerar assinatura
        sign_string = self.app_secret + param_string + self.app_secret
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return sign

    def test_dropshipping_api(self, access_token):
        """Testar endpoint de dropshipping"""
        try:
            print("🧪 Testando API de Dropshipping...")
            
            # Gerar timestamp
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': 'aliexpress.ds.product.list',
                'access_token': access_token,
                'app_key': self.app_key,
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'page_size': '5',
                'page_no': '1',
                'keywords': 'smartphone'
            }
            
            # Gerar assinatura
            params['sign'] = self.generate_sign(params)
            
            print(f"📤 Parâmetros Dropshipping: {json.dumps(params, indent=2)}")
            
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    print("✅ API de Dropshipping funcionando!")
                    print(f"📦 Produtos encontrados: {result.get('result', {}).get('total', 0)}")
                    return result
                else:
                    print(f"❌ Resposta inesperada da API: {result}")
                    return result
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao testar API de dropshipping: {str(e)}")
            return None

    def run_complete_flow(self):
        """Executar fluxo completo"""
        print("🚀 Iniciando fluxo OAuth2 completo para AliExpress Dropshipping\n")
        self.generate_auth_url()
        print("⏳ Aguardando você gerar o authorization_code...")
        print("(Execute o script novamente com o código quando tiver)")

    def run_with_code(self, authorization_code):
        """Executar com code fornecido"""
        print("🚀 Executando fluxo com authorization_code fornecido\n")
        access_token = self.exchange_code_for_token(authorization_code)
        
        if access_token:
            result = self.test_dropshipping_api(access_token)
            if result:
                print("\n🎉 Fluxo OAuth2 completo executado com sucesso!")
            else:
                print("\n❌ Falha ao testar API de dropshipping")
        else:
            print("\n❌ Falha ao gerar access token")

def main():
    import sys
    
    api = AliExpressPythonAPI()
    
    if len(sys.argv) > 1:
        auth_code = sys.argv[1]
        print(f"🔑 Authorization Code fornecido: {auth_code}")
        api.run_with_code(auth_code)
    else:
        api.run_complete_flow()

if __name__ == "__main__":
    main() 