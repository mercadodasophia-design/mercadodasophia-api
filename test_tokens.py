import requests
import json

def test_tokens():
    """Testa se os tokens estão sendo carregados corretamente"""
    
    # Teste 1: Verificar se o servidor está funcionando
    print("=== TESTE 1: Verificar se o servidor está funcionando ===")
    try:
        response = requests.get('https://service-api-aliexpress.mercadodasophia.com.br/test')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Verificar status dos tokens
    print("=== TESTE 2: Verificar status dos tokens ===")
    try:
        response = requests.get('https://service-api-aliexpress.mercadodasophia.com.br/api/aliexpress/token-status')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 3: Verificar tokens status (endpoint alternativo)
    print("=== TESTE 3: Verificar tokens status (alternativo) ===")
    try:
        response = requests.get('https://service-api-aliexpress.mercadodasophia.com.br/api/aliexpress/tokens/status')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 4: Debug tokens
    print("=== TESTE 4: Debug tokens ===")
    try:
        response = requests.get('https://service-api-aliexpress.mercadodasophia.com.br/debug/tokens')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 5: Tentar autorização
    print("=== TESTE 5: Tentar autorização ===")
    try:
        response = requests.get('https://service-api-aliexpress.mercadodasophia.com.br/api/aliexpress/auth')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_tokens()
