const axios = require('axios');
const crypto = require('crypto');
require('dotenv').config({ path: './config.env' });

class AliExpressOAuthFlow {
  constructor() {
    this.appKey = process.env.ALIEXPRESS_APP_KEY;
    this.appSecret = process.env.ALIEXPRESS_APP_SECRET;
    this.redirectUri = 'https://mercadodasophia.com/callback'; // Voltando para o URI registrado
    this.oauthUrl = 'https://oauth.aliexpress.com';
    this.apiUrl = 'https://api-sg.aliexpress.com/sync';
  }

  // 1. Gerar URL de autorização
  generateAuthUrl() {
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.appKey,
      redirect_uri: this.redirectUri,
      state: 'xyz'
    });

    const authUrl = `${this.oauthUrl}/authorize?${params.toString()}`;
    
    console.log('🔗 URL de Autorização:');
    console.log(authUrl);
    console.log('\n📋 Instruções:');
    console.log('1. Abra esta URL no navegador');
    console.log('2. Faça login no AliExpress');
    console.log('3. Autorize o app');
    console.log('4. Copie o código da URL de retorno');
    console.log('5. Execute este script com o código\n');
    
    return authUrl;
  }

  // 2. Trocar code por access_token
  async exchangeCodeForToken(authorizationCode) {
    try {
      console.log('🔄 Trocando code por access_token...');
      
      const params = new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.appKey,
        client_secret: this.appSecret,
        redirect_uri: this.redirectUri,
        code: authorizationCode,
        need_refresh_token: 'true'
      });

      console.log('📤 Parâmetros OAuth2:', params.toString());

      const response = await axios.post(`${this.oauthUrl}/token`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('📥 Resposta OAuth2:', JSON.stringify(response.data, null, 2));

      if (response.data && response.data.access_token) {
        console.log('✅ Access token gerado com sucesso!');
        return response.data.access_token;
      } else {
        console.log('❌ Resposta não contém access_token:', response.data);
        throw new Error('Failed to generate access token - no token in response');
      }
    } catch (error) {
      console.error('❌ Error exchanging code for token:', error.message);
      if (error.response) {
        console.error('❌ Response data:', error.response.data);
        console.error('❌ Response status:', error.response.status);
      }
      throw error;
    }
  }

  // 3. Gerar assinatura MD5 para API de Dropshipping
  generateSign(params) {
    const sortedParams = Object.keys(params).sort().reduce((result, key) => {
      result[key] = params[key];
      return result;
    }, {});

    const paramString = Object.keys(sortedParams)
      .map(key => `${key}${sortedParams[key]}`)
      .join('');

    const signString = this.appSecret + paramString + this.appSecret;

    return crypto.createHash('md5').update(signString).digest('hex').toUpperCase();
  }

  // 4. Testar endpoint de dropshipping
  async testDropshippingAPI(accessToken) {
    try {
      console.log('🧪 Testando API de Dropshipping...');
      
      // Gerar timestamp correto (yyyy-MM-dd HH:mm:ss)
      const now = new Date();
      const timestamp = now.getFullYear() + '-' +
        String(now.getMonth()+1).padStart(2,'0') + '-' +
        String(now.getDate()).padStart(2,'0') + ' ' +
        String(now.getHours()).padStart(2,'0') + ':' +
        String(now.getMinutes()).padStart(2,'0') + ':' +
        String(now.getSeconds()).padStart(2,'0');

      const params = {
        method: 'aliexpress.ds.product.list',
        access_token: accessToken,
        app_key: this.appKey,
        timestamp: timestamp,
        format: 'json',
        v: '2.0',
        page_size: 5,
        page_no: 1,
        keywords: 'smartphone'
      };

      params.sign = this.generateSign(params);

      console.log('📤 Parâmetros Dropshipping:', JSON.stringify(params, null, 2));

      const response = await axios.post(this.apiUrl, new URLSearchParams(params), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('📥 Resposta Dropshipping:', JSON.stringify(response.data, null, 2));

      if (response.data && response.data.result) {
        console.log('✅ API de Dropshipping funcionando!');
        console.log(`📦 Produtos encontrados: ${response.data.result.total || 0}`);
        return response.data;
      } else {
        console.log('❌ Resposta inesperada da API:', response.data);
        return response.data;
      }
    } catch (error) {
      console.error('❌ Error testing dropshipping API:', error.message);
      if (error.response) {
        console.error('❌ Response data:', error.response.data);
        console.error('❌ Response status:', error.response.status);
      }
      throw error;
    }
  }

  // Fluxo completo
  async runCompleteFlow() {
    try {
      console.log('🚀 Iniciando fluxo OAuth2 completo para AliExpress Dropshipping\n');
      this.generateAuthUrl();
      console.log('⏳ Aguardando você gerar o authorization_code...');
      console.log('(Execute o script novamente com o código quando tiver)');
    } catch (error) {
      console.error('❌ Error no fluxo:', error.message);
    }
  }

  // Executar com code fornecido
  async runWithCode(authorizationCode) {
    try {
      console.log('🚀 Executando fluxo com authorization_code fornecido\n');
      const accessToken = await this.exchangeCodeForToken(authorizationCode);
      await this.testDropshippingAPI(accessToken);
      console.log('\n🎉 Fluxo OAuth2 completo executado com sucesso!');
    } catch (error) {
      console.error('❌ Error no fluxo:', error.message);
    }
  }
}

// Executar o script
async function main() {
  const oauthFlow = new AliExpressOAuthFlow();
  const authCode = process.argv[2];
  
  if (authCode) {
    console.log(`🔑 Authorization Code fornecido: ${authCode}`);
    await oauthFlow.runWithCode(authCode);
  } else {
    await oauthFlow.runCompleteFlow();
  }
}

main();
