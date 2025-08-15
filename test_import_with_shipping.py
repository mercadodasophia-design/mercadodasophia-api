#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_import_product_with_shipping():
    """Testa a importação de produto com cálculo de frete"""
    
    # URL do servidor
    base_url = "https://service-api-aliexpress.mercadodasophia.com.br"
    import_url = f"{base_url}/api/aliexpress/import-product"
    
    # Dados de teste
    test_data = {
        "product_id": "1005001234567890",  # ID fictício para teste
        "weight": 0.8,  # 800g
        "dimensions": {
            "length": 25.0,  # cm
            "width": 18.0,   # cm
            "height": 8.0    # cm
        }
    }
    
    print("🚀 Testando importação de produto com cálculo de frete...")
    print(f"📦 Dados de teste: {json.dumps(test_data, indent=2)}")
    
    try:
        # Fazer requisição
        response = requests.post(import_url, json=test_data, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Produto importado com frete calculado:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se tem dados de frete
            if 'data' in data and 'product' in data['data']:
                product = data['data']['product']
                shipping_data = product.get('shipping_data', {})
                
                print(f"🚚 Dados de frete encontrados para {len(shipping_data)} CEPs:")
                for cep, options in shipping_data.items():
                    print(f"  📍 CEP {cep}:")
                    for option_type, option_data in options.items():
                        print(f"    - {option_type}: R$ {option_data.get('price', 0):.2f} ({option_data.get('days', 0)} dias)")
            
            return True
            
        else:
            print(f"❌ ERRO! Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ Erro: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Requisição demorou muito")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

def test_import_batch():
    """Testa a importação em lote"""
    
    # URL do servidor
    base_url = "https://service-api-aliexpress.mercadodasophia.com.br"
    batch_url = f"{base_url}/api/aliexpress/import-products-batch"
    
    # Dados de teste em lote
    test_data = {
        "products": [
            {
                "product_id": "1005001111111111",
                "weight": 0.5,
                "dimensions": {"length": 20.0, "width": 15.0, "height": 5.0}
            },
            {
                "product_id": "1005002222222222", 
                "weight": 1.2,
                "dimensions": {"length": 30.0, "width": 25.0, "height": 10.0}
            },
            {
                "product_id": "1005003333333333",
                "weight": 0.3,
                "dimensions": {"length": 15.0, "width": 10.0, "height": 3.0}
            }
        ]
    }
    
    print("\n🚀 Testando importação em lote...")
    print(f"📦 {len(test_data['products'])} produtos para importar")
    
    try:
        # Fazer requisição
        response = requests.post(batch_url, json=test_data, timeout=60)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Importação em lote concluída:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar resultados
            if 'data' in data and 'results' in data['data']:
                results = data['data']['results']
                success_count = sum(1 for r in results if r.get('success', False))
                print(f"📊 Resultado: {success_count}/{len(results)} produtos importados com sucesso")
                
                for i, result in enumerate(results):
                    status = "✅" if result.get('success', False) else "❌"
                    product_id = result.get('product_id', 'N/A')
                    error = result.get('error', '')
                    print(f"  {status} Produto {i+1} ({product_id}): {error if error else 'Sucesso'}")
            
            return True
            
        else:
            print(f"❌ ERRO! Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ Erro: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Requisição demorou muito")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

def test_shipping_calculation():
    """Testa apenas o cálculo de frete"""
    
    # URL do servidor
    base_url = "https://service-api-aliexpress.mercadodasophia.com.br"
    shipping_url = f"{base_url}/api/aliexpress/freight/calculate"
    
    # Dados de teste
    test_data = {
        "product_id": "1005001234567890",
        "destination_cep": "60731050",
        "weight": 0.8,
        "dimensions": {
            "length": 25.0,
            "width": 18.0,
            "height": 8.0
        }
    }
    
    print("\n🚀 Testando cálculo de frete...")
    print(f"📦 Dados de teste: {json.dumps(test_data, indent=2)}")
    
    try:
        # Fazer requisição
        response = requests.post(shipping_url, json=test_data, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Frete calculado:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar opções de frete
            if 'data' in data and 'shipping_options' in data['data']:
                options = data['data']['shipping_options']
                print(f"🚚 {len(options)} opções de frete encontradas:")
                
                for i, option in enumerate(options):
                    service = option.get('service_name', 'N/A')
                    price = option.get('price', 0)
                    days = option.get('estimated_days', 0)
                    print(f"  {i+1}. {service}: R$ {price:.2f} ({days} dias)")
            
            return True
            
        else:
            print(f"❌ ERRO! Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ Erro: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Requisição demorou muito")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTES DE IMPORTACAO COM FRETE")
    print("=" * 50)
    
    # Testar importação individual
    success1 = test_import_product_with_shipping()
    
    # Testar importação em lote
    success2 = test_import_batch()
    
    # Testar cálculo de frete
    success3 = test_shipping_calculation()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"  Importação individual: {'✅ PASSOU' if success1 else '❌ FALHOU'}")
    print(f"  Importação em lote: {'✅ PASSOU' if success2 else '❌ FALHOU'}")
    print(f"  Cálculo de frete: {'✅ PASSOU' if success3 else '❌ FALHOU'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
