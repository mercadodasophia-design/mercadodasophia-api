require('dotenv').config({ path: './config.env' });

console.log('🔧 Testando configuração do AliExpress:');
console.log('   App Key:', process.env.ALIEXPRESS_APP_KEY);
console.log('   App Secret:', process.env.ALIEXPRESS_APP_SECRET ? '✅ Configurado' : '❌ Não configurado');
console.log('   App Secret (primeiros 4 chars):', process.env.ALIEXPRESS_APP_SECRET ? process.env.ALIEXPRESS_APP_SECRET.substring(0, 4) + '...' : 'N/A');

// Testar se as credenciais estão corretas
if (process.env.ALIEXPRESS_APP_KEY === '517616') {
  console.log('✅ App Key correto');
} else {
  console.log('❌ App Key incorreto');
}

if (process.env.ALIEXPRESS_APP_SECRET && process.env.ALIEXPRESS_APP_SECRET.length > 10) {
  console.log('✅ App Secret parece válido');
} else {
  console.log('❌ App Secret inválido');
} 