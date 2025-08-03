from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys
import traceback

# Adicionar o path da biblioteca oficial (caminho correto)
sys.path.append('../exemplos/python-aliexpress-api-main')

try:
    from aliexpress_api import AliexpressApi, models
except ImportError:
    print("❌ Erro: Biblioteca AliExpress não encontrada")
    print("📁 Verifique se a pasta '../exemplos/python-aliexpress-api-main' existe")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv('./config.env')

app = Flask(__name__)
CORS(app)

# Configurações AliExpress
APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default_tracking_id')

# Inicializar API AliExpress
try:
    aliexpress = AliexpressApi(
        key=APP_KEY,
        secret=APP_SECRET,
        language=models.Language.PT,
        currency=models.Currency.BRL,
        tracking_id=TRACKING_ID
    )
    print("✅ API AliExpress inicializada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inicializar API AliExpress: {e}")
    aliexpress = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API funcionando!',
        'app_key_configured': bool(APP_KEY),
        'app_secret_configured': bool(APP_SECRET),
        'tracking_id_configured': bool(TRACKING_ID),
        'aliexpress_api_ready': aliexpress is not None
    })

@app.route('/api/aliexpress/products', methods=['GET'])
def get_products():
    """Buscar produtos do AliExpress"""
    if not aliexpress:
        return jsonify({
            'success': False,
            'error': 'API AliExpress não inicializada'
        }), 500

    try:
        # Parâmetros da requisição
        keywords = request.args.get('keywords', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        max_price = request.args.get('max_price')
        min_price = request.args.get('min_price')
        category_ids = request.args.get('category_ids')
        ship_to_country = request.args.get('ship_to_country', 'BR')

        # Converter preços para formato correto (centavos)
        if max_price:
            max_price = int(float(max_price) * 100)
        if min_price:
            min_price = int(float(min_price) * 100)

        # Buscar produtos
        response = aliexpress.get_products(
            keywords=keywords,
            page_no=page,
            page_size=page_size,
            max_sale_price=max_price,
            min_sale_price=min_price,
            ship_to_country=ship_to_country,
            sort=models.SortBy.SALE_PRICE_ASC
        )

        # Converter produtos para formato JSON
        products = []
        for product in response.products:
            products.append({
                'id': product.product_id,
                'title': product.product_title,
                'price': product.target_sale_price / 100,  # Converter de centavos
                'original_price': product.target_original_price / 100 if hasattr(product, 'target_original_price') else None,
                'image': product.product_main_image_url,
                'url': product.promotion_link,
                'rating': getattr(product, 'evaluate_rate', None),
                'reviews_count': getattr(product, 'evaluate_rate', None),
                'sales_count': getattr(product, 'sale_price', None),
                'store_name': getattr(product, 'shop_name', None),
                'shipping': getattr(product, 'logistics_cost', None),
                'aliexpress_id': product.product_id
            })

        return jsonify({
            'success': True,
            'products': products,
            'total': response.total_record_count,
            'current_page': page,
            'page_size': page_size
        })

    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/products/details', methods=['GET'])
def get_product_details():
    """Buscar detalhes de produtos específicos"""
    if not aliexpress:
        return jsonify({
            'success': False,
            'error': 'API AliExpress não inicializada'
        }), 500

    try:
        product_ids = request.args.get('product_ids', '')
        if not product_ids:
            return jsonify({
                'success': False,
            }), 400

        # Converter para lista
        if isinstance(product_ids, str):
            product_ids = [product_ids]

        # Buscar detalhes dos produtos
        products = aliexpress.get_products_details(product_ids)

        # Converter para formato JSON
        result = []
        for product in products:
            result.append({
                'id': product.product_id,
                'title': product.product_title,
                'price': product.target_sale_price / 100,
                'original_price': product.target_original_price / 100 if hasattr(product, 'target_original_price') else None,
                'image': product.product_main_image_url,
                'url': product.promotion_link,
                'rating': getattr(product, 'evaluate_rate', None),
                'reviews_count': getattr(product, 'evaluate_rate', None),
                'sales_count': getattr(product, 'sale_price', None),
                'store_name': getattr(product, 'shop_name', None),
                'shipping': getattr(product, 'logistics_cost', None),
                'aliexpress_id': product.product_id,
                'description': getattr(product, 'product_description', None),
                'images': getattr(product, 'product_images', []),
                'specifications': getattr(product, 'product_specifications', {})
            })

        return jsonify({
            'success': True,
            'products': result
        })

    except Exception as e:
        print(f"❌ Erro ao buscar detalhes dos produtos: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/categories', methods=['GET'])
def get_categories():
    """Buscar categorias do AliExpress"""
    if not aliexpress:
        return jsonify({
            'success': False,
            'error': 'API AliExpress não inicializada'
        }), 500

    try:
        parent_id = request.args.get('parent_id')
        
        if parent_id:
            # Buscar subcategorias
            categories = aliexpress.get_child_categories(int(parent_id))
        else:
            # Buscar categorias principais
            categories = aliexpress.get_parent_categories()

        # Converter para formato JSON
        result = []
        for category in categories:
            result.append({
                'id': category.category_id,
                'name': category.category_name,
                'level': getattr(category, 'category_level', 1),
                'parent_id': getattr(category, 'parent_category_id', None)
            })

        return jsonify({
            'success': True,
            'categories': result
        })

    except Exception as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/affiliate-links', methods=['POST'])
def generate_affiliate_links():
    """Gerar links de afiliado"""
    if not aliexpress:
        return jsonify({
            'success': False,
            'error': 'API AliExpress não inicializada'
        }), 500

    try:
        data = request.get_json()
        links = data.get('links', [])
        link_type = data.get('link_type', 'NORMAL')

        if not links:
            return jsonify({
                'success': False,
                'error': 'Links não fornecidos'
            }), 400

        # Converter tipo de link
        if link_type == 'HOT':
            link_type = models.LinkType.HOT
        else:
            link_type = models.LinkType.NORMAL

        # Gerar links de afiliado
        affiliate_links = aliexpress.get_affiliate_links(links, link_type)

        # Converter para formato JSON
        result = []
        for link in affiliate_links:
            result.append({
                'original_link': getattr(link, 'source_value', ''),
                'affiliate_link': link.promotion_link,
                'tracking_id': link.tracking_id
            })

        return jsonify({
            'success': True,
            'links': result
        })

    except Exception as e:
        print(f"❌ Erro ao gerar links de afiliado: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/aliexpress/hot-products', methods=['GET'])
def get_hot_products():
    """Buscar produtos em alta"""
    if not aliexpress:
        return jsonify({
            'success': False,
            'error': 'API AliExpress não inicializada'
        }), 500

    try:
        # Parâmetros da requisição
        keywords = request.args.get('keywords', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        max_price = request.args.get('max_price')
        min_price = request.args.get('min_price')
        category_ids = request.args.get('category_ids')
        ship_to_country = request.args.get('ship_to_country', 'BR')

        # Converter preços para formato correto (centavos)
        if max_price:
            max_price = int(float(max_price) * 100)
        if min_price:
            min_price = int(float(min_price) * 100)

        # Buscar produtos em alta
        response = aliexpress.get_hotproducts(
            keywords=keywords,
            page_no=page,
            page_size=page_size,
            max_sale_price=max_price,
            min_sale_price=min_price,
            ship_to_country=ship_to_country,
            sort=models.SortBy.SALE_PRICE_ASC
        )

        # Converter produtos para formato JSON
        products = []
        for product in response.products:
            products.append({
                'id': product.product_id,
                'title': product.product_title,
                'price': product.target_sale_price / 100,
                'original_price': product.target_original_price / 100 if hasattr(product, 'target_original_price') else None,
                'image': product.product_main_image_url,
                'url': product.promotion_link,
                'rating': getattr(product, 'evaluate_rate', None),
                'reviews_count': getattr(product, 'evaluate_rate', None),
                'sales_count': getattr(product, 'sale_price', None),
                'store_name': getattr(product, 'shop_name', None),
                'shipping': getattr(product, 'logistics_cost', None),
                'aliexpress_id': product.product_id
            })

        return jsonify({
            'success': True,
            'products': products,
            'total': response.total_record_count,
            'current_page': page,
            'page_size': page_size
        })

    except Exception as e:
        print(f"❌ Erro ao buscar produtos em alta: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 API ALIEXPRESS PYTHON iniciando na porta {port}...")
    print(f"🔑 App Key configurado: {'✅' if APP_KEY else '❌'}")
    print(f"🔑 App Secret configurado: {'✅' if APP_SECRET else '❌'}")
    print(f"🔗 Tracking ID configurado: {'✅' if TRACKING_ID else '❌'}")
    app.run(host='0.0.0.0', port=port, debug=True) 