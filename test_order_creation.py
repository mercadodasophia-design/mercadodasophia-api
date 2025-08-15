#!/usr/bin/env python3
"""
Teste para criação de pedidos AliExpress
"""

import requests
import json

# URL da API
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def test_create_order():
    """Testa a criação de um pedido"""
    
    # Dados do pedido com endereço completo
    order_data = {
        "customer_id": "TEST_CUSTOMER_001",
        "items": [
            {
                "product_id": "1005007720304124",  # itemId válido encontrado
                "quantity": 1,
                "sku_attr": "",  # SKU padrão
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
    
    print("🛒 Testando criação de pedido AliExpress...")
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
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pedido criado com sucesso!")
            print(f"🆔 Order ID: {result.get('order_id')}")
            print(f"🆔 Out Order ID: {result.get('out_order_id')}")
        else:
            print("❌ Erro ao criar pedido")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_create_order()
