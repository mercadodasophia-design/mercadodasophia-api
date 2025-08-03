#!/usr/bin/env python3
"""
Teste simples da API AliExpress
"""

import sys
import os
from dotenv import load_dotenv

# Adicionar o path da biblioteca oficial (caminho correto)
sys.path.append('../exemplos/python-aliexpress-api-main')

# Carregar variáveis de ambiente
load_dotenv('./config.env')

# Configurações AliExpress
APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default_tracking_id')

print("🔑 App Key:", APP_KEY)
print("🔑 App Secret:", APP_SECRET)
print("🔗 Tracking ID:", TRACKING_ID)

try:
    from aliexpress_api import AliexpressApi, models
    print("✅ Biblioteca AliExpress importada com sucesso!")
    
    # Inicializar API AliExpress
    aliexpress = AliexpressApi(
        key=APP_KEY,
        secret=APP_SECRET,
        language=models.Language.PT,
        currency=models.Currency.BRL,
        tracking_id=TRACKING_ID
    )
    print("✅ API AliExpress inicializada com sucesso!")
    
    # Testar busca de produtos
    print("\n🔍 Testando busca de produtos...")
    response = aliexpress.get_products(
        keywords='smartphone',
        page_no=1,
        page_size=3,
        ship_to_country='BR'
    )
    
    print(f"✅ Encontrados {response.total_record_count} produtos!")
    
    for i, product in enumerate(response.products[:3]):
        print(f"\n📱 Produto {i+1}:")
        print(f"   ID: {product.product_id}")
        print(f"   Título: {product.product_title}")
        print(f"   Preço: R$ {product.target_sale_price / 100:.2f}")
        print(f"   Imagem: {product.product_main_image_url}")
        print(f"   Link: {product.promotion_link}")
    
except ImportError as e:
    print(f"❌ Erro ao importar biblioteca: {e}")
    print("📁 Verifique se a pasta '../exemplos/python-aliexpress-api-main' existe")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc() 