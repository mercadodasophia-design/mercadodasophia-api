const axios = require('axios');

async function testAPI() {
  try {
    console.log('🧪 Testing API connection...');
    
    // Teste 1: Endpoint principal
    const response1 = await axios.get('http://192.168.1.24:3000/');
    console.log('✅ Main endpoint:', response1.data);
    
    // Teste 2: Busca de produtos
    const response2 = await axios.get('http://192.168.1.24:3000/api/search?q=smartphone&limit=5');
    console.log('✅ Search endpoint:', response2.data);
    
    console.log('🎉 API is working correctly!');
    
  } catch (error) {
    console.error('❌ API test failed:', error.message);
    console.log('💡 Make sure:');
    console.log('   1. Server is running on port 3000');
    console.log('   2. Firewall allows connections on port 3000');
    console.log('   3. Both devices are on the same network');
  }
}

testAPI(); 