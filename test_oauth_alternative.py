#!/usr/bin/env python3
"""
Script Python para testar abordagens alternativas do OAuth
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

class AliExpressOAuthAlternative:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.oauth_url = 'https://oauth.aliexpress.com'
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print()

    def test_oauth_with_session(self):
        """Testar OAuth com sessão/cookies"""
        try:
            print("🧪 Testando OAuth com sessão...")
            
            session = requests.Session()
            
            # Primeiro, acessar a página de login
            login_url = "https://login.aliexpress.com/"
            response = session.get(login_url)
            print(f"📥 Login page status: {response.status_code}")
            
            # Agora tentar OAuth
            params = {
                'response_type': 'code',
                'client_id': self.app_key,
                'redirect_uri': 'https://mercadodasophia.com/callback'
            }
            
            auth_url = f"{self.oauth_url}/authorize?{urlencode(params)}"
            print(f"📤 Auth URL: {auth_url}")
            
            response = session.get(auth_url)
            print(f"📥 Auth status: {response.status_code}")
            print(f"📥 Auth response: {response.text[:200]}...")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

    def test_different_oauth_flows(self):
        """Testar diferentes fluxos OAuth"""
        print("🧪 Testando diferentes fluxos OAuth...\n")
        
        # Teste 1: OAuth com implicit flow
        params1 = {
            'response_type': 'token',
            'client_id': self.app_key,
            'redirect_uri': 'https://mercadodasophia.com/callback'
        }
        url1 = f"{self.oauth_url}/authorize?{urlencode(params1)}"
        print("📋 Teste 1 - Implicit Flow:")
        print(url1)
        print()
        
        # Teste 2: OAuth com client credentials
        print("📋 Teste 2 - Client Credentials Flow:")
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.app_key,
                'client_secret': self.app_secret
            }
            
            response = requests.post(
                f"{self.oauth_url}/token",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status: {response.status_code}")
            print(f"📥 Response: {response.text}")
            print()
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            print()

    def test_api_with_categories(self):
        """Testar se conseguimos extrair produtos das categorias"""
        print("🧪 Testando extração de produtos das categorias...")
        
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
            
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'aliexpress_ds_category_get_response' in result:
                    categories = result['aliexpress_ds_category_get_response']['resp_result']['result']['categories']['category']
                    print(f"✅ Encontradas {len(categories)} categorias!")
                    
                    # Mostrar algumas categorias
                    print("\n📦 Categorias disponíveis:")
                    for i, cat in enumerate(categories[:10]):
                        print(f"   {i+1}. {cat.get('category_name', 'N/A')} (ID: {cat.get('category_id', 'N/A')})")
                    
                    return categories
                else:
                    print("❌ Resposta inesperada da API")
                    return None
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return None

    def test_product_search_by_category(self):
        """Testar busca de produtos por categoria"""
        print("🧪 Testando busca de produtos por categoria...")
        
        try:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Testar diferentes métodos de busca
            methods = [
                'aliexpress.ds.product.list',
                'aliexpress.ds.product.search',
                'aliexpress.ds.product.query'
            ]
            
            for method in methods:
                print(f"\n📋 Testando método: {method}")
                
                params = {
                    'method': method,
                    'app_key': self.app_key,
                    'timestamp': timestamp,
                    'format': 'json',
                    'v': '2.0',
                    'sign_method': 'md5',
                    'page_size': '5',
                    'page_no': '1'
                }
                
                # Gerar assinatura
                sorted_params = dict(sorted(params.items()))
                param_string = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
                sign_string = self.app_secret + param_string + self.app_secret
                sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
                params['sign'] = sign
                
                response = requests.post(
                    self.api_url,
                    data=params,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                print(f"   📥 Status: {response.status_code}")
                print(f"   📥 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

    def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 Testando abordagens alternativas\n")
        
        # Teste 1: OAuth com sessão
        self.test_oauth_with_session()
        print()
        
        # Teste 2: Diferentes fluxos OAuth
        self.test_different_oauth_flows()
        
        # Teste 3: API com categorias
        categories = self.test_api_with_categories()
        print()
        
        # Teste 4: Busca de produtos por categoria
        if categories:
            self.test_product_search_by_category()

def main():
    alt = AliExpressOAuthAlternative()
    alt.run_all_tests()

if __name__ == "__main__":
    main() 