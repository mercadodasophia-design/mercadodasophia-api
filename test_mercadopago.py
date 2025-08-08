#!/usr/bin/env python3
"""
Teste para integração com Mercado Pago
"""

import requests
import json

# URL da API
API_URL = "https://mercadodasophia-api.onrender.com"

def test_mp_debug():
    """Testar debug do Mercado Pago"""
    
    print(f"🔍 Testando debug do Mercado Pago...")
    
    try:
        response = requests.get(
            f"{API_URL}/api/payment/mp/debug",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                sdk_info = result.get('sdk_info', {})
                print("✅ Debug do Mercado Pago obtido com sucesso!")
                print(f"🔑 Access Token: {sdk_info.get('access_token', 'N/A')}")
                print(f"🔑 Public Key: {sdk_info.get('public_key', 'N/A')}")
                print(f"🔧 Sandbox Mode: {sdk_info.get('sandbox_mode', 'N/A')}")
            else:
                print("❌ Erro ao obter debug do Mercado Pago")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_create_preference():
    """Testar criação de preferência"""
    
    print(f"🔍 Testando criação de preferência...")
    
    # Dados de teste
    test_data = {
        "order_id": "TEST_ORDER_001",
        "total_amount": 99.90,
        "payer": {
            "name": "João Silva",
            "email": "joao.silva@teste.com"
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/payment/mp/create-preference",
            json=test_data,
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Preferência criada com sucesso!")
                print(f"🆔 Preference ID: {result.get('preference_id', 'N/A')}")
                print(f"🔗 Init Point: {result.get('init_point', 'N/A')}")
                print(f"🔗 Sandbox Init Point: {result.get('sandbox_init_point', 'N/A')}")
            else:
                print("❌ Erro ao criar preferência")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_process_payment():
    """Testar processamento de pagamento completo"""
    
    print(f"🔍 Testando processamento de pagamento...")
    
    # Dados de teste
    test_data = {
        "order_id": "TEST_ORDER_002",
        "total_amount": 149.90,
        "items": [
            {
                "product_id": "1005007720304124",
                "quantity": 1,
                "price": 149.90
            }
        ],
        "customer_info": {
            "name": "Maria Santos",
            "email": "maria.santos@teste.com",
            "phone": "11987654321"
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/payment/process",
            json=test_data,
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Processamento iniciado com sucesso!")
                print(f"🆔 Preference ID: {result.get('preference_id', 'N/A')}")
                print(f"🔗 Init Point: {result.get('init_point', 'N/A')}")
                print(f"🔗 Sandbox Init Point: {result.get('sandbox_init_point', 'N/A')}")
            else:
                print("❌ Erro ao processar pagamento")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Testando Integração Mercado Pago")
    print("=" * 50)
    
    # Testar debug
    test_mp_debug()
    
    print("\n" + "=" * 50)
    
    # Testar criação de preferência
    test_create_preference()
    
    print("\n" + "=" * 50)
    
    # Testar processamento de pagamento
    test_process_payment()
