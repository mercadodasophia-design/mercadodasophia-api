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
            f"{API_URL}/api/aliexpress/orders/{order_id}/status",
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                order_status = result.get('order_status', {})
                print("✅ Status do pedido obtido com sucesso!")
                print(f"📦 Status: {order_status.get('status', 'N/A')}")
                print(f"📝 Descrição: {order_status.get('status_desc', 'N/A')}")
                print(f"💰 Valor: {order_status.get('total_amount', 'N/A')} {order_status.get('currency', 'USD')}")
                print(f"🚚 Status Logística: {order_status.get('logistics_status', 'N/A')}")
                print(f"📦 Tracking: {order_status.get('logistics_tracking_no', 'N/A')}")
                print(f"📅 Criado: {order_status.get('created_time', 'N/A')}")
                print(f"📅 Modificado: {order_status.get('modified_time', 'N/A')}")
            else:
                print("❌ Erro ao obter status do pedido")
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
