import requests
import json

def test_shipping_endpoint():
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste 1: Produto com AliExpress ID
    payload1 = {
        "destination_cep": "60731050",
        "product_id": "1MbtWCeNEscpGBAfWN6Z",
        "items": [
            {"name": "Test Product", "price": 33.8, "quantity": 1, "weight": 0.123}
        ]
    }
    
    print("=== TESTE 1: Produto com AliExpress ID ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload1, indent=2)}")
    
    try:
        response1 = requests.post(url, json=payload1, timeout=30)
        print(f"Status: {response1.status_code}")
        print(f"Response: {response1.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Produto sem AliExpress ID (deve usar Correios)
    payload2 = {
        "destination_cep": "60731050",
        "product_id": "produto_sem_aliexpress",
        "items": [
            {"name": "Produto Local", "price": 50.0, "quantity": 1, "weight": 0.5}
        ]
    }
    
    print("=== TESTE 2: Produto sem AliExpress ID ===")
    print(f"Payload: {json.dumps(payload2, indent=2)}")
    
    try:
        response2 = requests.post(url, json=payload2, timeout=30)
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 3: Produto com frete grátis
    payload3 = {
        "destination_cep": "60731050",
        "product_id": "produto_frete_gratis",
        "items": [
            {"name": "Produto Frete Grátis", "price": 100.0, "quantity": 1, "weight": 0.3, "has_free_shipping": True}
        ]
    }
    
    print("=== TESTE 3: Produto com frete grátis ===")
    print(f"Payload: {json.dumps(payload3, indent=2)}")
    
    try:
        response3 = requests.post(url, json=payload3, timeout=30)
        print(f"Status: {response3.status_code}")
        print(f"Response: {response3.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_shipping_endpoint()
