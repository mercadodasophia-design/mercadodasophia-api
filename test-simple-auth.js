require('dotenv').config({ path: './config.env' });

const appKey = process.env.ALIEXPRESS_APP_KEY;
const appSecret = process.env.ALIEXPRESS_APP_SECRET;

console.log('🔧 Testando diferentes URLs de autorização...\n');

// Teste 1: URL básica
const basicUrl = `https://oauth.aliexpress.com/authorize?response_type=code&client_id=${appKey}`;
console.log('📋 Teste 1 - URL Básica:');
console.log(basicUrl);
console.log('');

// Teste 2: Com redirect_uri simples
const simpleUrl = `https://oauth.aliexpress.com/authorize?response_type=code&client_id=${appKey}&redirect_uri=https://mercadodasophia.com/callback`;
console.log('📋 Teste 2 - URL com redirect_uri:');
console.log(simpleUrl);
console.log('');

// Teste 3: Com state
const stateUrl = `https://oauth.aliexpress.com/authorize?response_type=code&client_id=${appKey}&redirect_uri=https://mercadodasophia.com/callback&state=test123`;
console.log('📋 Teste 3 - URL com state:');
console.log(stateUrl);
console.log('');

console.log('🧪 Teste estas URLs uma por vez para ver qual funciona.');
console.log('Se alguma funcionar, copie o código e execute:');
console.log('node test-oauth-flow.js SEU_CODIGO'); 