#!/usr/bin/env python3
"""
Teste do cálculo de frete com fallback
Testa se o sistema funciona mesmo sem tokens AliExpress
"""

import requests
import json

def test_shipping_fallback():
    """Testa o cálculo de frete com fallback"""
    
    # URL do servidor
    base_url = "https://service-api-aliexpress.mercadodasophia.com.br"
    shipping_url = f"{base_url}/shipping/quote"
    
    # Dados de teste
    test_data = {
        "destination_cep": "01001000",  # São Paulo
        "product_id": "1005001234567890",  # ID fictício
        "items": [
            {
                "product_id": "1005001234567890",
                "quantity": 1,
                "weight": 0.5,  # 500g
                "price": 99.90,
                "length": 15.0,
                "height": 5.0,
                "width": 10.0
            }
        ]
    }
    
    print("🚚 Testando cálculo de frete com fallback...")
    print(f"📦 Dados de teste: {json.dumps(test_data, indent=2)}")
    
    try:
        # Fazer requisição
        response = requests.post(
            shipping_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Resposta: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                quotes = data.get('data', [])
                fulfillment = data.get('fulfillment', {})
                
                print(f"\n📦 {len(quotes)} opções de frete encontradas:")
                for i, quote in enumerate(quotes, 1):
                    print(f"  {i}. {quote.get('service_name', 'N/A')}")
                    print(f"     Preço: R$ {quote.get('price', 0):.2f}")
                    print(f"     Prazo: {quote.get('estimated_days', 0)} dias")
                    print(f"     Transportadora: {quote.get('carrier', 'N/A')}")
                    print()
                
                print(f"🔧 Modo: {fulfillment.get('mode', 'N/A')}")
                print(f"📡 Fonte: {fulfillment.get('source', 'N/A')}")
                print(f"📝 Notas: {fulfillment.get('notes', 'N/A')}")
                
                return True
            else:
                print(f"❌ Erro: {data.get('message', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        print(f"❌ Resposta raw: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_multiple_ceps():
    """Testa com diferentes CEPs"""
    
    ceps = [
        "01001000",  # São Paulo
        "20040020",  # Rio de Janeiro
        "90020060",  # Porto Alegre
        "40000000",  # Salvador
        "50000000",  # Recife
    ]
    
    print("\n🌍 Testando múltiplos CEPs...")
    
    for cep in ceps:
        print(f"\n📍 Testando CEP: {cep}")
        
        test_data = {
            "destination_cep": cep,
            "product_id": "1005001234567890",
            "items": [
                {
                    "product_id": "1005001234567890",
                    "quantity": 1,
                    "weight": 0.5,
                    "price": 99.90,
                    "length": 15.0,
                    "height": 5.0,
                    "width": 10.0
                }
            ]
        }
        
        try:
            response = requests.post(
                "https://service-api-aliexpress.mercadodasophia.com.br/shipping/quote",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    quotes = data.get('data', [])
                    if quotes:
                        first_quote = quotes[0]
                        print(f"  ✅ R$ {first_quote.get('price', 0):.2f} - {first_quote.get('estimated_days', 0)} dias")
                    else:
                        print(f"  ⚠️ Nenhuma opção de frete")
                else:
                    print(f"  ❌ {data.get('message', 'Erro')}")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {e}")

if __name__ == "__main__":
    print("🧪 TESTE DE CÁLCULO DE FRETE COM FALLBACK")
    print("=" * 50)
    
    # Teste principal
    success = test_shipping_fallback()
    
    if success:
        print("\n✅ Teste principal PASSOU!")
        # Teste com múltiplos CEPs
        test_multiple_ceps()
    else:
        print("\n❌ Teste principal FALHOU!")
    
    print("\n🏁 Teste concluído!")
