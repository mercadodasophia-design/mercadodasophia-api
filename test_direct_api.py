#!/usr/bin/env python3
"""
Script Python para testar a API do AliExpress diretamente
"""

import requests
import hashlib
import time
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

class AliExpressDirectAPI:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print(f"   App Secret (primeiros 4): {self.app_secret[:4] + '...' if self.app_secret else 'N/A'}")
        print()

    def generate_sign(self, params):
        """Gerar assinatura MD5 para API"""
        # Ordenar parâmetros
        sorted_params = dict(sorted(params.items()))
        
        # Criar string de parâmetros
        param_string = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        
        # Gerar assinatura
        sign_string = self.app_secret + param_string + self.app_secret
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return sign

    def test_api_health(self):
        """Testar se a API está respondendo"""
        try:
            print("🏥 Testando saúde da API...")
            
            # Teste simples sem autenticação
            response = requests.get(self.api_url, timeout=10)
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ API está respondendo")
                return True
            else:
                print("❌ API não está respondendo corretamente")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {str(e)}")
            return False

    def test_without_auth(self):
        """Testar API sem autenticação"""
        try:
            print("🧪 Testando API sem autenticação...")
            
            # Gerar timestamp
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': 'aliexpress.ds.product.list',
                'app_key': self.app_key,
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5',  # Adicionando sign_method
                'page_size': '5',
                'page_no': '1',
                'keywords': 'smartphone'
            }
            
            # Gerar assinatura
            params['sign'] = self.generate_sign(params)
            
            print(f"📤 Parâmetros: {json.dumps(params, indent=2)}")
            
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resposta da API: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {str(e)}")
            return None

    def test_different_endpoints(self):
        """Testar diferentes endpoints da API"""
        endpoints = [
            'https://api.aliexpress.com/v2/product/get',
            'https://api-sg.aliexpress.com/sync',
            'https://api.aliexpress.com/sync'
        ]
        
        for endpoint in endpoints:
            try:
                print(f"🧪 Testando endpoint: {endpoint}")
                
                params = {
                    'method': 'aliexpress.ds.product.list',
                    'app_key': self.app_key,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'format': 'json',
                    'v': '2.0',
                    'sign_method': 'md5'  # Adicionando sign_method
                }
                
                params['sign'] = self.generate_sign(params)
                
                response = requests.post(
                    endpoint,
                    data=params,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=10
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                print()
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
                print()

    def run_tests(self):
        """Executar todos os testes"""
        print("🚀 Iniciando testes da API do AliExpress\n")
        
        # Teste 1: Saúde da API
        self.test_api_health()
        print()
        
        # Teste 2: API sem autenticação
        self.test_without_auth()
        print()
        
        # Teste 3: Diferentes endpoints
        print("🧪 Testando diferentes endpoints...")
        self.test_different_endpoints()

def main():
    api = AliExpressDirectAPI()
    api.run_tests()

if __name__ == "__main__":
    main() 