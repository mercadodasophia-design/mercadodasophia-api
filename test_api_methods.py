#!/usr/bin/env python3
"""
Script Python para testar diferentes métodos da API do AliExpress
"""

import requests
import hashlib
import time
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

class AliExpressAPIMethods:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.api_url = 'https://api-sg.aliexpress.com/sync'
        
        print(f"🔧 Configuração:")
        print(f"   App Key: {self.app_key}")
        print(f"   App Secret: {'✅ Configurado' if self.app_secret else '❌ Não configurado'}")
        print()

    def generate_sign(self, params):
        """Gerar assinatura MD5 para API"""
        sorted_params = dict(sorted(params.items()))
        param_string = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        sign_string = self.app_secret + param_string + self.app_secret
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return sign

    def test_method(self, method_name):
        """Testar um método específico da API"""
        try:
            print(f"🧪 Testando método: {method_name}")
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            params = {
                'method': method_name,
                'app_key': self.app_key,
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5'
            }
            
            params['sign'] = self.generate_sign(params)
            
            print(f"   📤 Parâmetros: {json.dumps(params, indent=4)}")
            
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"   📥 Status: {response.status_code}")
            print(f"   📥 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if 'error_response' in result:
                        print(f"   ❌ Erro: {result['error_response'].get('msg', 'Unknown error')}")
                    else:
                        print(f"   ✅ Sucesso!")
                except:
                    print(f"   ⚠️ Resposta não é JSON válido")
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
            
            print()
            return response.status_code == 200
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            print()
            return False

    def run_tests(self):
        """Executar testes com diferentes métodos"""
        print("🚀 Testando diferentes métodos da API do AliExpress\n")
        
        # Lista de métodos para testar
        methods = [
            'aliexpress.ds.product.list',
            'aliexpress.ds.product.get',
            'aliexpress.ds.product.search',
            'aliexpress.ds.category.get',
            'aliexpress.ds.product.detail.get',
            'aliexpress.ds.product.info.get',
            'aliexpress.ds.product.query',
            'aliexpress.ds.product.search.list',
            'aliexpress.ds.product.list.get',
            'aliexpress.ds.product.detail',
            'aliexpress.ds.product.info',
            'aliexpress.ds.product.search.list',
            'aliexpress.ds.product.list.get',
            'aliexpress.ds.product.detail.get',
            'aliexpress.ds.product.info.get',
            'aliexpress.ds.product.query.get',
            'aliexpress.ds.product.search.get',
            'aliexpress.ds.product.list.get',
            'aliexpress.ds.product.detail.get',
            'aliexpress.ds.product.info.get'
        ]
        
        successful_methods = []
        
        for method in methods:
            if self.test_method(method):
                successful_methods.append(method)
        
        print("📊 Resumo dos testes:")
        print(f"   ✅ Métodos que funcionaram: {len(successful_methods)}")
        print(f"   ❌ Métodos que falharam: {len(methods) - len(successful_methods)}")
        
        if successful_methods:
            print("\n🎉 Métodos funcionais:")
            for method in successful_methods:
                print(f"   - {method}")
        else:
            print("\n❌ Nenhum método funcionou. Pode ser necessário:")
            print("   1. Verificar se o app está ativo no painel")
            print("   2. Verificar permissões de API")
            print("   3. Verificar se precisa de OAuth primeiro")

def main():
    api = AliExpressAPIMethods()
    api.run_tests()

if __name__ == "__main__":
    main() 