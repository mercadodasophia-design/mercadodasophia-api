warning: in the working copy of 'server.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/server.py b/server.py[m
[1mindex 4042ba1..079493c 100644[m
[1m--- a/server.py[m
[1m+++ b/server.py[m
[36m@@ -949,6 +949,101 @@[m [mdef tokens_status():[m
         } if tokens else None[m
     })[m
 [m
[32m+[m[32m@app.route('/api/aliexpress/product/<product_id>')[m
[32m+[m[32mdef product_details(product_id):[m
[32m+[m[32m    """Buscar detalhes completos de um produto"""[m
[32m+[m[32m    tokens = load_tokens()[m
[32m+[m[32m    if not tokens or not tokens.get('access_token'):[m
[32m+[m[32m        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        # Parâmetros para a API conforme documentação[m
[32m+[m[32m        params = {[m
[32m+[m[32m            "method": "aliexpress.ds.product.get",[m
[32m+[m[32m            "app_key": APP_KEY,[m
[32m+[m[32m            "timestamp": int(time.time() * 1000),[m
[32m+[m[32m            "sign_method": "md5",[m
[32m+[m[32m            "format": "json",[m
[32m+[m[32m            "v": "2.0",[m
[32m+[m[32m            "access_token": tokens['access_token'],[m
[32m+[m[32m            "product_id": product_id,[m
[32m+[m[32m            "ship_to_country": "BR",  # 👈 obrigatório para Brasil[m
[32m+[m[32m            "target_currency": "BRL",    # 👈 obrigatório para Brasil[m
[32m+[m[32m            "target_language": "pt",     # 👈 obrigatório para Brasil[m
[32m+[m[32m            "remove_personal_benefit": "false"[m
[32m+[m[32m        }[m
[32m+[m[41m        [m
[32m+[m[32m        # Gerar assinatura[m
[32m+[m[32m        params["sign"] = generate_api_signature(params, APP_SECRET)[m
[32m+[m[41m        [m
[32m+[m[32m        # Fazer requisição HTTP direta para /sync[m
[32m+[m[32m        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)[m
[32m+[m[32m        print(f'✅ Resposta detalhes produto {product_id}: {response.text[:500]}...')[m
[32m+[m[41m        [m
[32m+[m[32m        if response.status_code == 200:[m
[32m+[m[32m            data = response.json()[m
[32m+[m[32m            # Verificar se há dados na resposta[m
[32m+[m[32m            if 'aliexpress_ds_product_get_response' in data:[m
[32m+[m[32m                return jsonify({'success': True, 'data': data['aliexpress_ds_product_get_response']})[m
[32m+[m[32m            else:[m
[32m+[m[32m                return jsonify({'success': False, 'error': data}), 400[m
[32m+[m[32m        else:[m
[32m+[m[32m            return jsonify({'success': False, 'error': response.text}), response.status_code[m
[32m+[m
[32m+[m[32m    except Exception as e:[m
[32m+[m[32m        print(f'❌ Erro ao buscar detalhes do produto {product_id}: {e}')[m
[32m+[m[32m        return jsonify({'success': False, 'message': str(e)}), 500[m
[32m+[m
[32m+[m[32m@app.route('/api/aliexpress/freight/<product_id>')[m
[32m+[m[32mdef freight_calculation(product_id):[m
[32m+[m[32m    """Calcular frete para um produto"""[m
[32m+[m[32m    tokens = load_tokens()[m
[32m+[m[32m    if not tokens or not tokens.get('access_token'):[m
[32m+[m[32m        return jsonify({'success': False, 'message': 'Token não encontrado. Faça autorização primeiro.'}), 401[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        # Parâmetros para cálculo de frete conforme documentação[m
[32m+[m[32m        freight_params = {[m
[32m+[m[32m            "country_code": "BR",[m
[32m+[m[32m            "price": "10.00",  # Preço padrão para cálculo[m
[32m+[m[32m            "product_id": product_id,[m
[32m+[m[32m            "product_num": "1",[m
[32m+[m[32m            "send_goods_country_code": "CN",[m
[32m+[m[32m            "price_currency": "USD"[m
[32m+[m[32m        }[m
[32m+[m[41m        [m
[32m+[m[32m        params = {[m
[32m+[m[32m            "method": "aliexpress.logistics.buyer.freight.calculate",[m
[32m+[m[32m            "app_key": APP_KEY,[m
[32m+[m[32m            "timestamp": int(time.time() * 1000),[m
[32m+[m[32m            "sign_method": "md5",[m
[32m+[m[32m            "format": "json",[m
[32m+[m[32m            "v": "2.0",[m
[32m+[m[32m            "access_token": tokens['access_token'],[m
[32m+[m[32m            "param_aeop_freight_calculate_for_buyer_d_t_o": json.dumps(freight_params)[m
[32m+[m[32m        }[m
[32m+[m[41m        [m
[32m+[m[32m        # Gerar assinatura[m
[32m+[m[32m        params["sign"] = generate_api_signature(params, APP_SECRET)[m
[32m+[m[41m        [m
[32m+[m[32m        # Fazer requisição HTTP direta para /sync[m
[32m+[m[32m        response = requests.get('https://api-sg.aliexpress.com/sync', params=params)[m
[32m+[m[32m        print(f'✅ Resposta frete produto {product_id}: {response.text[:500]}...')[m
[32m+[m[41m        [m
[32m+[m[32m        if response.status_code == 200:[m
[32m+[m[32m            data = response.json()[m
[32m+[m[32m            # Verificar se há dados na resposta[m
[32m+[m[32m            if 'aliexpress_logistics_buyer_freight_calculate_response' in data:[m
[32m+[m[32m                return jsonify({'success': True, 'data': data['aliexpress_logistics_buyer_freight_calculate_response']})[m
[32m+[m[32m            else:[m
[32m+[m[32m                return jsonify({'success': False, 'error': data}), 400[m
[32m+[m[32m        else:[m
[32m+[m[32m            return jsonify({'success': False, 'error': response.text}), response.status_code[m
[32m+[m
[32m+[m[32m    except Exception as e:[m
[32m+[m[32m        print(f'❌ Erro ao calcular frete do produto {product_id}: {e}')[m
[32m+[m[32m        return jsonify({'success': False, 'message': str(e)}), 500[m
[32m+[m
 if __name__ == '__main__':[m
     print(f'🚀 Servidor rodando na porta {PORT}')[m
     print(f'APP_KEY: {"✅" if APP_KEY else "❌"} | APP_SECRET: {"✅" if APP_SECRET else "❌"} | REDIRECT_URI: {REDIRECT_URI}')[m
