#!/usr/bin/env python3
"""
Integração com Mercado Pago usando SDK oficial
Documentação oficial: https://www.mercadopago.com.br/developers/docs
"""

import mercadopago
import os
from datetime import datetime, timedelta

class MercadoPagoIntegration:
    """Classe para integração com Mercado Pago usando SDK oficial"""
    
    def __init__(self):
        # Configurações do Mercado Pago
        self.access_token = os.getenv('MP_ACCESS_TOKEN')
        self.public_key = os.getenv('MP_PUBLIC_KEY')
        self.sandbox_mode = os.getenv('MP_SANDBOX', 'true').lower() == 'true'
        
        # SDK será inicializado quando necessário
        self.sdk = None
    
    def _get_sdk(self):
        """Inicializar SDK apenas quando necessário"""
        if self.sdk is None:
            if not self.access_token:
                raise Exception('MP_ACCESS_TOKEN não encontrado nas variáveis de ambiente')
            try:
                self.sdk = mercadopago.SDK(self.access_token)
                print(f"✅ SDK Mercado Pago inicializado com sucesso")
                print(f"SDK type: {type(self.sdk)}")
                print(f"SDK attributes: {dir(self.sdk)}")
            except Exception as e:
                print(f"❌ Erro ao inicializar SDK: {e}")
                raise
        return self.sdk
    
    def create_preference(self, order_data):
        """
        Criar preferência de pagamento
        Documentação: https://www.mercadopago.com.br/developers/docs/checkout-api/reference/preferences
        """
        try:
            print(f"🔍 create_preference chamado com: {order_data}")
            print(f"🔍 self.access_token: {bool(self.access_token)}")
            print(f"🔍 self.sdk antes de _get_sdk(): {self.sdk}")
            print(f"🔍 Atributos da classe: {dir(self)}")
            # Estrutura da preferência
            preference_data = {
                "items": [
                    {
                        "title": f"Pedido {order_data['order_id']}",
                        "quantity": 1,
                        "unit_price": float(order_data['total_amount']),
                        "currency_id": "BRL"
                    }
                ],
                "external_reference": order_data['order_id'],
                "notification_url": f"{os.getenv('API_BASE_URL', 'https://service-api-aliexpress.mercadodasophia.com.br')}/api/payment/mp/webhook",
                "back_urls": {
                    "success": f"{os.getenv('API_BASE_URL', 'https://service-api-aliexpress.mercadodasophia.com.br')}/api/payment/mp/success",
                    "failure": f"{os.getenv('API_BASE_URL', 'https://service-api-aliexpress.mercadodasophia.com.br')}/api/payment/mp/failure",
                    "pending": f"{os.getenv('API_BASE_URL', 'https://service-api-aliexpress.mercadodasophia.com.br')}/api/payment/mp/pending"
                },
                "auto_return": "approved",
                "expires": True,
                "expiration_date_to": (datetime.now() + timedelta(hours=24)).isoformat() + "Z"
            }
            
            # Adicionar dados do pagador se fornecidos
            if 'payer' in order_data:
                preference_data["payer"] = order_data['payer']
            
            # Criar preferência usando SDK
            sdk = self._get_sdk()
            result = sdk.preference().create(preference_data)
            
            if result["status"] == 201:
                preference = result["response"]
                print(f"✅ Preferência Mercado Pago criada: {preference['id']}")
                return {
                    'success': True,
                    'preference_id': preference['id'],
                    'init_point': preference['init_point'],
                    'sandbox_init_point': preference.get('sandbox_init_point'),
                    'preference_data': preference
                }
            else:
                print(f"❌ Erro ao criar preferência: {result}")
                return {
                    'success': False,
                    'error': f"Erro {result['status']}: {result.get('response', {})}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao criar preferência: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_info(self, payment_id):
        """
        Obter informações de um pagamento
        Documentação: https://www.mercadopago.com.br/developers/docs/checkout-api/reference/payments
        """
        try:
            sdk = self._get_sdk()
            result = sdk.payment().get(payment_id)
            
            if result["status"] == 200:
                payment_data = result["response"]
                return {
                    'success': True,
                    'payment_data': payment_data
                }
            else:
                print(f"❌ Erro ao obter pagamento: {result}")
                return {
                    'success': False,
                    'error': f"Erro {result['status']}: {result.get('response', {})}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao obter pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, payment_id, amount=None, reason="Refund requested"):
        """
        Estornar pagamento
        Documentação: https://www.mercadopago.com.br/developers/docs/checkout-api/reference/payments
        """
        try:
            refund_data = {}
            
            if amount:
                refund_data["amount"] = float(amount)
            
            sdk = self._get_sdk()
            result = sdk.refund().create(payment_id, refund_data)
            
            if result["status"] == 201:
                refund_data = result["response"]
                print(f"✅ Estorno realizado: {refund_data['id']}")
                return {
                    'success': True,
                    'refund_id': refund_data['id'],
                    'status': refund_data['status'],
                    'refund_data': refund_data
                }
            else:
                print(f"❌ Erro ao estornar: {result}")
                return {
                    'success': False,
                    'error': f"Erro {result['status']}: {result.get('response', {})}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao estornar: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_payment(self, payment_data):
        """
        Criar pagamento direto (sem preferência)
        Documentação: https://www.mercadopago.com.br/developers/docs/checkout-api/reference/payments
        """
        try:
            sdk = self._get_sdk()
            result = sdk.payment().create(payment_data)
            
            if result["status"] == 201:
                payment = result["response"]
                print(f"✅ Pagamento criado: {payment['id']}")
                return {
                    'success': True,
                    'payment_id': payment['id'],
                    'status': payment['status'],
                    'payment_data': payment
                }
            else:
                print(f"❌ Erro ao criar pagamento: {result}")
                return {
                    'success': False,
                    'error': f"Erro {result['status']}: {result.get('response', {})}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao criar pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_preference(self, preference_id):
        """
        Obter detalhes de uma preferência
        Documentação: https://www.mercadopago.com.br/developers/docs/checkout-api/reference/preferences
        """
        try:
            sdk = self._get_sdk()
            result = sdk.preference().get(preference_id)
            
            if result["status"] == 200:
                preference = result["response"]
                return {
                    'success': True,
                    'preference_data': preference
                }
            else:
                print(f"❌ Erro ao obter preferência: {result}")
                return {
                    'success': False,
                    'error': f"Erro {result['status']}: {result.get('response', {})}"
                }
                
        except Exception as e:
            print(f"❌ Erro ao obter preferência: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sdk_info(self):
        """Obter informações do SDK"""
        return {
            'access_token': self.access_token[:20] + '...' if self.access_token else None,
            'public_key': self.public_key,
            'sandbox_mode': self.sandbox_mode
        }

# Instância global
mp_integration = MercadoPagoIntegration()
