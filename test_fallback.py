import requests
import json

def test_fallback():
    """Teste para verificar se o fallback para Correios está funcionando"""
    
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste com produto que deve fazer fallback para Correios
    payload = {
        "destination_cep": "61771800",
        "product_id": "produto_sem_aliexpress",  # Produto sem AliExpress ID
        "items": [
            {"name": "Produto Local", "price": 50.0, "quantity": 1, "weight": 0.5}
        ]
    }
    
    print("=== TESTE: Fallback para Correios ===")
    print(f"CEP: {payload['destination_cep']}")
    print(f"Product ID: {payload['product_id']}")
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
                    print(f"     Source: {data.get('fulfillment', {}).get('source', 'N/A')}")
            else:
                print(f"\n❌ Erro: {data.get('message')}")
        else:
            print(f"\n❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_fallback()
