import requests
import json

def test_working_aliexpress_id():
    """Teste com AliExpress ID que funcionou anteriormente"""
    
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste com o AliExpress ID que funcionou anteriormente
    payload = {
        "destination_cep": "60731050",
        "product_id": "3256802900954148",  # ID que funcionou anteriormente
        "items": [
            {"name": "Produto Funcionando", "price": 50.0, "quantity": 1, "weight": 0.3}
        ]
    }
    
    print("=== TESTE: AliExpress ID que funcionou anteriormente ===")
    print(f"AliExpress ID: {payload['product_id']}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                quotes = data.get('data', [])
                print(f"✅ Sucesso! {len(quotes)} opções de frete encontradas:")
                for i, quote in enumerate(quotes, 1):
                    print(f"  {i}. {quote.get('service_name')} - R$ {quote.get('price')} - {quote.get('estimated_days')} dias")
            else:
                print(f"❌ Erro: {data.get('message')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_working_aliexpress_id()
