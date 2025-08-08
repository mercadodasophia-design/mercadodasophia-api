#!/usr/bin/env python3
import requests
import json

def test_shipping_endpoint():
    url = "https://mercadodasophia-api.onrender.com/shipping/quote"
    
    # Usando um product_id real do AliExpress para teste
    data = {
        "destination_cep": "01001-000",
        "product_id": "3256802900954148",  # Product ID real do AliExpress
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
    
    try:
        print(f"Enviando requisição para: {url}")
        print(f"Dados: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Cotações reais do AliExpress: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_shipping_endpoint()
