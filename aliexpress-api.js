const axios = require('axios');
const crypto = require('crypto');

class AliExpressAPI {
  constructor() {
    // Configurações da API de Dropshipping do AliExpress
    this.baseUrl = 'https://api-sg.aliexpress.com/sync'; // API de Dropshipping
    this.oauthUrl = 'https://oauth.aliexpress.com/token'; // Endpoint OAuth correto
    this.appKey = process.env.ALIEXPRESS_APP_KEY;
    this.appSecret = process.env.ALIEXPRESS_APP_SECRET;
    this.accessToken = null; // Será gerado dinamicamente
    
    // Debug: verificar se as credenciais estão sendo carregadas
    console.log('🔧 AliExpress Dropshipping API Debug:');
    console.log('   App Key:', this.appKey ? '✅ Configurado' : '❌ Não configurado');
    console.log('   App Secret:', this.appSecret ? '✅ Configurado' : '❌ Não configurado');
    console.log('   Access Token: Será gerado dinamicamente');
  }

  // Gerar assinatura MD5 para API de Dropshipping
  generateSign(params) {
    // Ordenar parâmetros alfabeticamente
    const sortedParams = Object.keys(params).sort().reduce((result, key) => {
      result[key] = params[key];
      return result;
    }, {});

    // Criar string de parâmetros
    const paramString = Object.keys(sortedParams)
      .map(key => `${key}${sortedParams[key]}`)
      .join('');

    // Adicionar app_secret no início e fim
    const signString = this.appSecret + paramString + this.appSecret;

    // Gerar MD5
    return crypto.createHash('md5').update(signString).digest('hex').toUpperCase();
  }

  // Buscar produtos via API de Dropshipping
  async searchProducts(query, options = {}) {
    try {
      const {
        page = 1,
        pageSize = 20,
        sort = 'SALE_PRICE_ASC',
        categoryId,
        minPrice,
        maxPrice
      } = options;

      const params = {
        method: 'aliexpress.ds.product.list', // Método de Dropshipping
        app_key: this.appKey,
        timestamp: new Date().toISOString().replace('T', ' ').replace('Z', ''),
        format: 'json',
        v: '2.0',
        keywords: query,
        page_no: page,
        page_size: pageSize,
        sort: sort
      };

      if (categoryId) params.category_id = categoryId;
      if (minPrice) params.min_price = minPrice;
      if (maxPrice) params.max_price = maxPrice;

      const accessToken = await this.getAccessToken();
      params.access_token = accessToken;

      // Gerar assinatura
      params.sign = this.generateSign(params);

      console.log('📤 Parâmetros Dropshipping:', JSON.stringify(params, null, 2));

      const response = await axios.post(this.baseUrl, new URLSearchParams(params), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('📥 Resposta Dropshipping:', JSON.stringify(response.data, null, 2));

      return this.formatProducts(response.data);
    } catch (error) {
      console.error('❌ AliExpress Dropshipping API Error:', error.message);
      throw error;
    }
  }

  // Obter detalhes do produto via API de Dropshipping
  async getProductDetails(productId) {
    try {
      const params = {
        method: 'aliexpress.ds.product.get', // Método de Dropshipping
        app_key: this.appKey,
        timestamp: new Date().toISOString().replace('T', ' ').replace('Z', ''),
        format: 'json',
        v: '2.0',
        product_id: productId
      };

      const accessToken = await this.getAccessToken();
      params.access_token = accessToken;

      // Gerar assinatura
      params.sign = this.generateSign(params);

      const response = await axios.post(this.baseUrl, new URLSearchParams(params), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      return this.formatProductDetails(response.data);
    } catch (error) {
      console.error('❌ Product Details Dropshipping API Error:', error.message);
      throw error;
    }
  }

  // Formatar produtos da resposta da API de Dropshipping
  formatProducts(apiResponse) {
    if (!apiResponse.result || !apiResponse.result.products) {
      return [];
    }

    return apiResponse.result.products.map(product => ({
      id: product.product_id,
      name: product.product_title,
      price: product.sale_price,
      originalPrice: product.original_price,
      rating: product.evaluate_rate,
      reviewsCount: product.evaluate_count,
      salesCount: product.sale_count,
      image: product.product_main_image,
      url: product.product_detail_url,
      shipping: product.shipping_info,
      store: product.store_name,
      aliexpressId: product.product_id
    }));
  }

  // Formatar detalhes do produto
  formatProductDetails(apiResponse) {
    if (!apiResponse.result) {
      throw new Error('Product not found');
    }

    const product = apiResponse.result;
    return {
      id: product.product_id,
      name: product.product_title,
      price: product.sale_price,
      originalPrice: product.original_price,
      rating: product.evaluate_rate,
      reviewsCount: product.evaluate_count,
      salesCount: product.sale_count,
      images: product.product_images || [],
      description: product.product_description,
      specifications: product.product_specifications || {},
      shipping: product.shipping_info,
      store: product.store_name,
      url: product.product_detail_url,
      aliexpressId: product.product_id
    };
  }

  // Gerar access token usando OAuth2
  async generateAccessToken() {
    try {
      console.log('🔧 Tentando gerar access token via OAuth2...');
      
      // Primeiro, precisamos obter o authorization_code
      // Isso normalmente é feito através de um fluxo OAuth2 no navegador
      // Por enquanto, vamos usar um código de exemplo
      const authorizationCode = '0_2DL4DV3jcU1UOT7WGI1A4rY91'; // Este código precisa ser obtido via OAuth2
      
      const params = new URLSearchParams({
        grant_type: 'authorization_code',
        need_refresh_token: 'true',
        client_id: this.appKey,
        client_secret: this.appSecret,
        redirect_uri: 'https://mercadodasophia.com/api/ali/status', // URL de callback configurada no AliExpress
        code: authorizationCode
      });

      console.log('📤 Parâmetros OAuth2:', params.toString());

      const response = await axios.post(this.oauthUrl, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('📥 Resposta OAuth2:', JSON.stringify(response.data, null, 2));

      if (response.data && response.data.access_token) {
        this.accessToken = response.data.access_token;
        console.log('✅ Access token gerado com sucesso:', this.accessToken.substring(0, 20) + '...');
        return this.accessToken;
      } else {
        console.log('❌ Resposta não contém access_token:', response.data);
        throw new Error('Failed to generate access token - no token in response');
      }
    } catch (error) {
      console.error('❌ Error generating access token:', error.message);
      if (error.response) {
        console.error('❌ Response data:', error.response.data);
        console.error('❌ Response status:', error.response.status);
      }
      throw error;
    }
  }

  // Verificar se as credenciais estão configuradas
  isConfigured() {
    return !!(this.appKey && this.appSecret);
  }

  // Obter token (gerar se necessário)
  async getAccessToken() {
    if (!this.accessToken) {
      await this.generateAccessToken();
    }
    return this.accessToken;
  }
}

module.exports = AliExpressAPI; 