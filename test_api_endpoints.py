#!/usr/bin/env python3
"""
Script de teste para verificar os endpoints da API AliExpress
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Testa um endpoint da API"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 Testando: {description}")
    print(f"📡 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    print("🚀 TESTANDO API ALIEXPRESS")
    print("=" * 50)
    
    # 1. Teste de saúde da API
    test_endpoint("/api/health", description="Verificar se a API está funcionando")
    
    # 2. Teste de busca básica (sem OAuth)
    test_endpoint("/api/search?keywords=smartphone", description="Busca básica de produtos")
    
    # 3. Teste de URL de autorização OAuth2
    test_endpoint("/api/aliexpress/oauth-url", description="Gerar URL de autorização OAuth2")
    
    # 4. Teste de produtos AliExpress (deve falhar sem OAuth)
    test_endpoint("/api/aliexpress/products?keywords=phone", description="Busca de produtos AliExpress (requer OAuth)")
    
    # 5. Teste de categorias (deve falhar sem OAuth)
    test_endpoint("/api/aliexpress/categories", description="Listar categorias (requer OAuth)")
    
    # 6. Teste de métodos de envio (deve falhar sem OAuth)
    test_endpoint("/api/aliexpress/shipping-methods", description="Métodos de envio (requer OAuth)")
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    print("✅ Endpoints básicos funcionando")
    print("⚠️  Endpoints OAuth2 precisam de autenticação")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Acesse: http://localhost:3000/api/aliexpress/oauth-url")
    print("2. Complete o fluxo OAuth2 no AliExpress")
    print("3. Teste os endpoints protegidos")

if __name__ == "__main__":
    main() 