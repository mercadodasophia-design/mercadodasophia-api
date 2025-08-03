#!/usr/bin/env python3
"""
Script para testar o fluxo OAuth2 completo da API AliExpress
"""

import requests
import json

# Configurações
API_BASE_URL = "https://mercadodasophia-api.onrender.com"
AUTH_CODE = "SEU_CODIGO_AQUI"  # Substitua pelo código que você recebeu

def test_oauth_flow():
    """Testa o fluxo OAuth2 completo"""
    
    print("🚀 TESTANDO FLUXO OAUTH2 COMPLETO")
    print("=" * 50)
    
    # 1. Gerar URL de autorização
    print("\n1️⃣ Gerando URL de autorização...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/aliexpress/oauth-url")
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ URL de autorização: {auth_data['auth_url']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 2. Se temos o código de autorização, testar callback
    if AUTH_CODE != "SEU_CODIGO_AQUI":
        print(f"\n2️⃣ Testando callback com código: {AUTH_CODE}")
        try:
            response = requests.get(f"{API_BASE_URL}/api/aliexpress/oauth-callback?code={AUTH_CODE}")
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            if response.status_code == 200:
                print("✅ OAuth2 callback funcionando!")
                
                # 3. Testar busca de produtos
                print("\n3️⃣ Testando busca de produtos...")
                response = requests.get(f"{API_BASE_URL}/api/aliexpress/products?keywords=phone&page=1&page_size=5")
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    products = response.json()
                    print(f"✅ Produtos encontrados: {len(products.get('products', []))}")
                    print(f"📦 Primeiro produto: {products.get('products', [{}])[0].get('name', 'N/A')}")
                else:
                    print(f"❌ Erro na busca: {response.text}")
            else:
                print("❌ Erro no callback OAuth2")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    else:
        print("\n⚠️  Para testar completamente:")
        print("1. Acesse a URL de autorização acima")
        print("2. Complete o fluxo OAuth2")
        print("3. Copie o código de autorização")
        print("4. Substitua 'SEU_CODIGO_AQUI' no script")
        print("5. Execute novamente")
    
    print("\n" + "=" * 50)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Complete o OAuth2 no navegador")
    print("2. Atualize o código no script")
    print("3. Execute novamente para testar produtos")

if __name__ == "__main__":
    test_oauth_flow() 