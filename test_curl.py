#!/usr/bin/env python3
import requests
import json

def test_shipping_curl():
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    data = {
        "destination_cep": "01001-000",
        "product_id": "3256802900954148",
        "items": [
            {
                "name": "Produto Teste",
                "price": 100.0,
                "quantity": 1,
                "weight": 1.0
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Testando endpoint: {url}")
    print(f"📦 Dados enviados: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCESSO! Cotações reais do AliExpress:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ ERRO {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_shipping_curl()
