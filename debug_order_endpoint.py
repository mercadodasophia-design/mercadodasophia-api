#!/usr/bin/env python3
"""
Debug endpoint para criação de pedidos
"""

import requests
import json

# URL da API
API_URL = "https://mercadodasophia-api.onrender.com"

def test_debug_endpoint():
    """Testa o endpoint de debug"""
    
    try:
        # Fazer requisição para endpoint de debug
        response = requests.get(
            f"{API_URL}/debug/order",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
