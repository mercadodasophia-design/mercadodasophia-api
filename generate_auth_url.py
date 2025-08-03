from urllib.parse import urlencode

APP_KEY = "517616"
CALLBACK_URL = "https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback"

def generate_auth_url():
    params = {
        'response_type': 'code',
        'client_id': APP_KEY,
        'redirect_uri': CALLBACK_URL,
        'state': 'xyz123',
        'force_auth': 'true'
    }
    
    auth_url = f"https://api-sg.aliexpress.com/oauth/authorize?{urlencode(params)}"
    
    print("🔗 URL de Autorização AliExpress:")
    print("=" * 50)
    print(auth_url)
    print("=" * 50)
    print("\n📋 Instruções:")
    print("1. Acesse a URL acima")
    print("2. Faça login no AliExpress")
    print("3. Autorize o aplicativo")
    print("4. Copie o código da URL de callback")
    print("5. Use o código no teste OAuth2")
    
    return auth_url

if __name__ == "__main__":
    generate_auth_url() 