#!/usr/bin/env python3
"""
Debug script para tracking de pedidos AliExpress
"""

import requests
import json
import time

# URL da API
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def debug_tracking():
    """Debug do tracking com logs detalhados"""
    
    # Order ID do pedido que criamos anteriormente
    order_id = "8203955732372614"  # Pedido criado com sucesso
    
    print(f"🔍 Debug do tracking do pedido AliExpress...")
    print(f"🆔 Order ID: {order_id}")
    
    try:
        # Fazer requisição
        print(f"📡 Fazendo requisição para: {API_URL}/api/aliexpress/orders/{order_id}/tracking")
        
        response = requests.get(
            f"{API_URL}/api/aliexpress/orders/{order_id}/tracking",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Requisição bem-sucedida!")
            print(f"📋 Resultado: {json.dumps(result, indent=2)}")
        else:
            print("❌ Erro HTTP")
            if response.status_code == 500:
                print("🔍 Erro 500 - Verificando logs do servidor...")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_tokens():
    """Testar se os tokens estão funcionando"""
    
    print(f"🔍 Testando tokens...")
    
    try:
        response = requests.get(
            f"{API_URL}/debug/tokens",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Debug do Tracking de Pedidos AliExpress")
    print("=" * 50)
    
    # Testar tokens primeiro
    test_tokens()
    
    print("\n" + "=" * 50)
    
    # Testar tracking
    debug_tracking()
