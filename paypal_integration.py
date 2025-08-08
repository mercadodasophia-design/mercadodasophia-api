#!/usr/bin/env python3
"""
Integração com PayPal para pagamentos internacionais
Documentação oficial: https://developer.paypal.com/docs/api/
"""

import requests
import json
import base64
import os
from datetime import datetime, timedelta

class PayPalIntegration:
    """Classe para integração com PayPal"""
    
    def __init__(self):
        # Configurações do PayPal
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.sandbox_mode = os.getenv('PAYPAL_SANDBOX', 'true').lower() == 'true'
        
        # URLs base
        if self.sandbox_mode:
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"
        
        self.access_token = None
        self.token_expires = None
    
    def get_access_token(self):
        """Obter token de acesso do PayPal"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        # Credenciais para autenticação
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
                print(f"✅ Token PayPal obtido com sucesso")
                return self.access_token
            else:
                print(f"❌ Erro ao obter token PayPal: {response.status_code} - {response.text}")
                raise Exception(f"Erro ao obter token PayPal: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na autenticação PayPal: {e}")
            raise e
    
    def create_order(self, order_data):
        """
        Criar ordem de pagamento no PayPal
        Documentação: https://developer.paypal.com/docs/api/orders/v2/
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Estrutura da ordem PayPal
        paypal_order = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": f"ORDER_{order_data['order_id']}",
                    "amount": {
                        "currency_code": "USD",
                        "value": str(order_data['total_amount'])
                    },
                    "description": f"Pedido {order_data['order_id']} - {order_data.get('description', 'Produtos AliExpress')}",
                    "custom_id": order_data['order_id']
                }
            ],
            "application_context": {
                "return_url": f"{os.getenv('API_BASE_URL', 'https://mercadodasophia-api.onrender.com')}/api/payment/paypal/return",
                "cancel_url": f"{os.getenv('API_BASE_URL', 'https://mercadodasophia-api.onrender.com')}/api/payment/paypal/cancel"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/checkout/orders",
                headers=headers,
                json=paypal_order,
                timeout=30
            )
            
            if response.status_code == 201:
                order_response = response.json()
                print(f"✅ Ordem PayPal criada: {order_response['id']}")
                return {
                    'success': True,
                    'paypal_order_id': order_response['id'],
                    'approval_url': order_response['links'][1]['href'],  # Link de aprovação
                    'order_data': order_response
                }
            else:
                print(f"❌ Erro ao criar ordem PayPal: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao criar ordem PayPal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def capture_payment(self, paypal_order_id):
        """
        Capturar pagamento após aprovação
        Documentação: https://developer.paypal.com/docs/api/orders/v2/
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                capture_data = response.json()
                print(f"✅ Pagamento capturado: {capture_data['id']}")
                return {
                    'success': True,
                    'capture_id': capture_data['id'],
                    'status': capture_data['status'],
                    'capture_data': capture_data
                }
            else:
                print(f"❌ Erro ao capturar pagamento: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao capturar pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_details(self, paypal_order_id):
        """
        Obter detalhes de uma ordem
        Documentação: https://developer.paypal.com/docs/api/orders/v2/
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/v2/checkout/orders/{paypal_order_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order_data = response.json()
                return {
                    'success': True,
                    'order_data': order_data
                }
            else:
                print(f"❌ Erro ao obter ordem: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao obter ordem: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, capture_id, amount=None, reason="Refund requested"):
        """
        Estornar pagamento
        Documentação: https://developer.paypal.com/docs/api/payments/v2/
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        refund_data = {
            "reason": reason
        }
        
        if amount:
            refund_data["amount"] = {
                "currency_code": "USD",
                "value": str(amount)
            }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/payments/captures/{capture_id}/refund",
                headers=headers,
                json=refund_data,
                timeout=30
            )
            
            if response.status_code == 201:
                refund_response = response.json()
                print(f"✅ Estorno realizado: {refund_response['id']}")
                return {
                    'success': True,
                    'refund_id': refund_response['id'],
                    'status': refund_response['status'],
                    'refund_data': refund_response
                }
            else:
                print(f"❌ Erro ao estornar: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao estornar: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Instância global
paypal = PayPalIntegration()
