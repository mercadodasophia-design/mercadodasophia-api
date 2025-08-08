#!/usr/bin/env python3
"""
Teste para tracking de pedidos AliExpress
"""

import requests
import json

# URL da API
API_URL = "https://mercadodasophia-api.onrender.com"

def test_order_tracking():
    """Testa o tracking de um pedido"""
    
    # Order ID do pedido que criamos anteriormente
    order_id = "8203955732372614"  # Pedido criado com sucesso
    
    print(f"📋 Testando tracking do pedido AliExpress...")
    print(f"🆔 Order ID: {order_id}")
    
    try:
        # Fazer requisição
        response = requests.get(
            f"{API_URL}/api/aliexpress/orders/{order_id}/tracking",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tracking_info = result.get('tracking_info', {})
                print("✅ Tracking do pedido obtido com sucesso!")
                print(f"📦 Order ID: {tracking_info.get('order_id', 'N/A')}")
                
                tracking_details = tracking_info.get('tracking_details', [])
                print(f"📦 Pacotes encontrados: {len(tracking_details)}")
                
                for i, package in enumerate(tracking_details):
                    print(f"\n📦 Pacote {i+1}:")
                    print(f"   🚚 Transportadora: {package.get('carrier_name', 'N/A')}")
                    print(f"   📦 Número de rastreio: {package.get('mail_no', 'N/A')}")
                    print(f"   📅 ETA: {package.get('eta_time', 'N/A')}")
                    
                    events = package.get('tracking_events', [])
                    print(f"   📋 Eventos de tracking: {len(events)}")
                    
                    for event in events:
                        print(f"      📅 {event.get('timestamp', 'N/A')} - {event.get('name', 'N/A')}")
                        print(f"      📝 {event.get('description', 'N/A')}")
            else:
                print("❌ Erro ao obter tracking do pedido")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_order_list():
    """Testa listagem de pedidos"""
    
    print(f"📋 Testando listagem de pedidos...")
    
    try:
        # Fazer requisição
        response = requests.get(
            f"{API_URL}/api/aliexpress/orders",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                orders = result.get('orders', [])
                print(f"✅ Encontrados {len(orders)} pedidos!")
                for order in orders:
                    print(f"🆔 {order.get('order_id')} - {order.get('status', 'N/A')}")
            else:
                print("❌ Erro ao listar pedidos")
        else:
            print("❌ Erro HTTP")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Testando Tracking de Pedidos AliExpress")
    print("=" * 50)
    
    # Testar tracking de um pedido específico
    test_order_tracking()
    
    print("\n" + "=" * 50)
    
    # Testar listagem de pedidos
    test_order_list()
