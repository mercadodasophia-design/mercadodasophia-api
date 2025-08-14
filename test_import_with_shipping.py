#!/usr/bin/env python3
"""
Teste da importação de produtos com cálculo de frete
Testa se o sistema calcula frete no momento da importação
"""

import requests
import json

def test_import_product_with_shipping():
    """Testa a importação de produto com cálculo de frete"""
    
    # URL do servidor
    base_url = "https://mercadodasophia-api.onrender.com"
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
    base_url = "https://mercadodasophia-api.onrender.com"
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
            
            # Verificar resumo
            if 'data' in data and 'summary' in data['data']:
                summary = data['data']['summary']
                print(f"📊 Resumo: {summary['success']} sucessos, {summary['error']} erros de {summary['total']} produtos")
            
            return True
            
        else:
            print(f"❌ ERRO! Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

def main():
    """Função principal de teste"""
    
    print("=" * 60)
    print("🧪 TESTE DE IMPORTAÇÃO COM CÁLCULO DE FRETE")
    print("=" * 60)
    
    # Teste 1: Importação individual
    print("\n1️⃣ Testando importação individual...")
    success1 = test_import_product_with_shipping()
    
    # Teste 2: Importação em lote
    print("\n2️⃣ Testando importação em lote...")
    success2 = test_import_batch()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Importação individual: {'SUCESSO' if success1 else 'FALHOU'}")
    print(f"✅ Importação em lote: {'SUCESSO' if success2 else 'FALHOU'}")
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Sistema de importação com frete está funcionando!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os logs acima para identificar problemas")

if __name__ == "__main__":
    main()
