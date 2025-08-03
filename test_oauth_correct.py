import requests
import hashlib
import time
from datetime import datetime, timezone

APP_KEY = "517616"
APP_SECRET = "TTqNmTMs5Q0QiPbulDNenhXr2My18nN4"
AUTH_CODE = "3_517616_AQFGyoYBYbcvGb8brK2KVNwV1922"

# 1️⃣ Gera timestamp UTC no formato aceito
def get_timestamp():
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕐 Timestamp UTC: {timestamp}")
    return timestamp

# 2️⃣ Gera assinatura MD5 correta
def generate_sign(params):
    # Ordenar parâmetros alfabeticamente
    sorted_params = dict(sorted(params.items()))
    
    # Concatenar parâmetros
    param_string = "".join(f"{k}{v}" for k, v in sorted_params.items())
    
    # Adicionar app_secret no início e fim
    sign_string = APP_SECRET + param_string + APP_SECRET
    
    # Gerar MD5 e converter para maiúsculo
    sign = hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper()
    
    print(f"🔐 String para assinatura: {sign_string}")
    print(f"🔐 Assinatura MD5: {sign}")
    
    return sign

# 3️⃣ Faz a requisição de token
def get_access_token(auth_code):
    url = "https://api-sg.aliexpress.com/rest"
    timestamp = get_timestamp()

    params = {
        "method": "/auth/token/create",
        "app_key": APP_KEY,
        "code": auth_code,
        "timestamp": timestamp,
        "sign_method": "md5",
        "format": "json",
        "v": "2.0"
    }

    # Gerar assinatura
    sign = generate_sign(params)
    params["sign"] = sign

    print("\n🔄 Fazendo requisição OAuth2...")
    print(f"📝 URL: {url}")
    print(f"📝 Parâmetros: {params}")

    try:
        response = requests.post(url, data=params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Access token gerado com sucesso!")
                print(f"🔑 Token: {data['access_token'][:20]}...")
                return data["access_token"]
            else:
                print("❌ Access token não encontrado na resposta")
                print(f"📄 Resposta completa: {data}")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

if __name__ == "__main__":
    print("🚀 TESTE OAUTH2 ALIEXPRESS")
    print(f"🔑 APP_KEY: {APP_KEY}")
    print(f"🔑 APP_SECRET: {APP_SECRET[:10]}...")
    print(f"🔑 AUTH_CODE: {AUTH_CODE}")
    print("=" * 50)
    
    token = get_access_token(AUTH_CODE)
    
    if token:
        print("\n🎉 SUCESSO! OAuth2 funcionando!")
    else:
        print("\n❌ Falha no OAuth2") 