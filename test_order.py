#!/usr/bin/env python3
import requests
import json

def test_order_creation():
    url = "https://service-api-aliexpress.mercadodasophia.com.br/api/aliexpress/orders/create"
    
    # Dados do pedido de teste com produto real
    data = {
        "customer_id": "CUSTOMER_001",
        "items": [
            {
                "product_id": "1005007720304124",  # Produto real do AliExpress
                "quantity": 1,
                "sku_attr": "",  # SKU vazio para usar o padrão
                "memo": "Pedido de teste da Loja da Sophia"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🛒 Testando criação de pedido: {url}")
    print(f"📦 Dados do pedido: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCESSO! Pedido criado no AliExpress:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ ERRO {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_order_creation()
