#!/usr/bin/env python3
"""
Debug da criação de pedidos AliExpress
"""

import requests
import json

# URL da API
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def debug_order_creation():
    """Debug da criação de pedidos"""
    
    # Dados do pedido com endereço completo
    order_data = {
        "customer_id": "TEST_CUSTOMER_001",
        "items": [
            {
                "product_id": "1005007720304124",
                "quantity": 1,
                "sku_attr": "",
                "memo": "Teste de criação de pedido"
            }
        ],
        "address": {
            "country": "BR",
            "province": "Ceara",
            "city": "Fortaleza",
            "district": "Centro",
            "detail_address": "Rua Teste, 123 - Bloco 03, Apto 202",
            "zip": "61771880",
            "contact_person": "francisco adonay ferreira do nascimento",
            "phone": "+5585997640050"
        }
    }
    
    print("🛒 Debugando criação de pedido AliExpress...")
    print(f"📦 Dados do pedido: {json.dumps(order_data, indent=2)}")
    
    try:
        # Fazer requisição
        response = requests.post(
            f"{API_URL}/api/aliexpress/orders/create",
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        print(f"📡 Resposta completa: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📡 JSON parseado: {json.dumps(result, indent=2)}")
            except:
                print("❌ Não foi possível fazer parse do JSON")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    debug_order_creation()
