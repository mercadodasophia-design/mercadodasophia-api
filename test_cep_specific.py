import requests
import json

def test_specific_cep():
    """Teste com CEP específico fornecido pelo usuário"""
    
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste com o CEP específico fornecido
    payload = {
        "destination_cep": "61771800",
        "product_id": "1005008811362675",  # ID real fornecido pelo usuário
        "items": [
            {"name": "Produto Real AliExpress", "price": 50.0, "quantity": 1, "weight": 0.3}
        ]
    }
    
    print("=== TESTE: CEP Específico ===")
    print(f"CEP: {payload['destination_cep']}")
    print(f"AliExpress ID: {payload['product_id']}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                quotes = data.get('data', [])
                print(f"\n✅ Sucesso! {len(quotes)} opções de frete encontradas:")
                for i, quote in enumerate(quotes, 1):
                    print(f"  {i}. {quote.get('service_name')} - R$ {quote.get('price')} - {quote.get('estimated_days')} dias")
            else:
                print(f"\n❌ Erro: {data.get('message')}")
        else:
            print(f"\n❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_specific_cep()
