import requests
import json

def test_debug_shipping():
    """Teste para debugar a lógica de frete"""
    
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste com um product_id que parece ser um AliExpress ID real
    payload = {
        "destination_cep": "60731050",
        "product_id": "3256802900954148",  # ID que aparece no debug dos tokens
        "items": [
            {"name": "Test Product", "price": 33.8, "quantity": 1, "weight": 0.123}
        ]
    }
    
    print("=== TESTE DEBUG: Produto com AliExpress ID real ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_debug_shipping()
