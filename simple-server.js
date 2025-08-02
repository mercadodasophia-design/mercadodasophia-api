const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Rota de teste
app.get('/', (req, res) => {
  res.json({
    message: 'API Mercado da Sophia - Teste',
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// Rota de busca simulada
app.get('/api/search', (req, res) => {
  const { q } = req.query;
  
  const products = [
    {
      id: 'test-1',
      name: `${q} - Produto Teste`,
      price: 'R$ 25,90',
      originalPrice: 'R$ 49,90',
      rating: '4.5',
      reviewsCount: '1.2k',
      salesCount: '5.3k',
      image: 'https://via.placeholder.com/300x300/007ACC/FFFFFF?text=Teste',
      url: 'https://www.aliexpress.com/item/test123.html',
      shipping: 'Frete grátis',
      store: 'Test Store'
    }
  ];
  
  res.json({
    query: q,
    total: products.length,
    products: products
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Simple Server running on port ${PORT}`);
  console.log(`📱 Test endpoint: http://localhost:${PORT}/api/search?q=test`);
});

module.exports = app; 