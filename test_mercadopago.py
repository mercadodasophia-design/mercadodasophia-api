#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Configurações
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"

def test_create_preference():
    """Testa a criação de preferência de pagamento"""
    
    url = f"{API_URL}/api/payment/mp/create-preference"
    
    # Dados de teste
    test_data = {
        "order_id": "TEST_ORDER_123",
        "total_amount": 150.00,
        "customer_email": "teste@exemplo.com",
        "customer_name": "Cliente Teste",
        "customer_phone": "+5511999999999",
        "items": [
            {
                "title": "Produto Teste",
                "quantity": 2,
                "unit_price": 75.00
            }
        ],
        "shipping_address": {
            "cep": "01234-567",
            "street": "Rua Teste",
            "number": "123",
            "complement": "Apto 1",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP"
        }
    }
    
    print("🚀 Testando criação de preferência de pagamento...")
    print(f"📦 Dados: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Preferência criada:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'data' in data and 'preference_id' in data['data']:
                preference_id = data['data']['preference_id']
                init_point = data['data'].get('init_point', '')
                print(f"🎯 Preference ID: {preference_id}")
                print(f"🔗 Init Point: {init_point}")
            
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
        print(f"❌ ERRO: {e}")
        return False

def test_debug_endpoint():
    """Testa o endpoint de debug"""
    
    url = f"{API_URL}/api/payment/mp/debug"
    
    print("\n🔍 Testando endpoint de debug...")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Debug info:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ ERRO! Status: {response.status_code}")
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_webhook_simulation():
    """Simula um webhook do Mercado Pago"""
    
    url = f"{API_URL}/api/payment/mp/webhook"
    
    # Dados simulados de webhook
    webhook_data = {
        "type": "payment",
        "data": {
            "id": "1234567890"
        }
    }
    
    print("\n🔄 Testando simulação de webhook...")
    print(f"📦 Dados: {json.dumps(webhook_data, indent=2)}")
    
    try:
        response = requests.post(url, json=webhook_data, timeout=30)
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Webhook processado:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
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
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTES DO MERCADO PAGO")
    print("=" * 50)
    
    # Testar criação de preferência
    success1 = test_create_preference()
    
    # Testar endpoint de debug
    success2 = test_debug_endpoint()
    
    # Testar webhook
    success3 = test_webhook_simulation()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"  Criação de preferência: {'✅ PASSOU' if success1 else '❌ FALHOU'}")
    print(f"  Endpoint de debug: {'✅ PASSOU' if success2 else '❌ FALHOU'}")
    print(f"  Simulação de webhook: {'✅ PASSOU' if success3 else '❌ FALHOU'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")

