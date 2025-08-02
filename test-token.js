const AliExpressAPI = require('./aliexpress-api');
require('dotenv').config({ path: './config.env' });

async function testToken() {
  try {
    console.log('🧪 Testando geração de token...');
    
    const api = new AliExpressAPI();
    
    console.log('📋 Credenciais:');
    console.log('   App Key:', api.appKey);
    console.log('   App Secret:', api.appSecret);
    
    console.log('\n🔧 Gerando token...');
    const token = await api.generateAccessToken();
    
    console.log('✅ Token gerado:', token);
    
  } catch (error) {
    console.error('❌ Erro:', error.message);
    if (error.response) {
      console.error('📥 Response:', error.response.data);
    }
  }
}

testToken(); 