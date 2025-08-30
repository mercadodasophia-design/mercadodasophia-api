import requests
import json

def test_real_aliexpress_id():
    """Teste com AliExpress ID real fornecido pelo usuário"""
    
    url = "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote"
    
    # Teste com diferentes CEPs
    ceps_to_test = ["60731050", "01001000", "20040020", "80000000"]
    
    for cep in ceps_to_test:
        payload = {
            "destination_cep": cep,
            "product_id": "1005008811362675",  # ID real fornecido pelo usuário
            "items": [
                {"name": "Produto Real AliExpress", "price": 50.0, "quantity": 1, "weight": 0.3}
            ]
        }
        
        print(f"\n=== TESTE: AliExpress ID Real - CEP {cep} ===")
        print(f"AliExpress ID: {payload['product_id']}")
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            print(f"Status: {response.status_code}")
            
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
    test_real_aliexpress_id()
