const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const AliExpressAPI = require('./aliexpress-api');
require('dotenv').config({ path: './config.env' });

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());



// Cache para armazenar resultados de busca
const searchCache = new Map();
const productCache = new Map();

// Limpar cache
app.get('/api/clear-cache', (req, res) => {
  searchCache.clear();
  productCache.clear();
  console.log('🗑️ Cache limpo');
  res.json({ message: 'Cache limpo com sucesso' });
});

// Rotas
app.get('/', (req, res) => {
  res.json({
    message: 'API Mercado da Sophia - AliExpress Integration',
    version: '1.0.0',
    endpoints: {
      search: '/api/search?q=query&sort=rating&page=1',
      product: '/api/product?url=product_url',
      import: '/api/import',
      importBulk: '/api/import/bulk',
      trending: '/api/trending',
      categories: '/api/categories',
      stats: '/api/stats'
    }
  });
});

// Instanciar API do AliExpress
const aliExpressAPI = new AliExpressAPI();

// Buscar produtos no AliExpress
app.get('/api/search', async (req, res) => {
  try {
    const { q, sort = 'SALE_PRICE_ASC', page = 1, limit = 20 } = req.query;
    
    if (!q) {
      return res.status(400).json({ error: 'Query parameter "q" is required' });
    }

    console.log(`🔍 Searching for: ${q} (page: ${page}, sort: ${sort})`);
    
    // Verificar cache
    const cacheKey = `search_${q}_${sort}_${page}`;
    if (productCache.has(cacheKey)) {
      const cached = productCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log('📦 Returning cached results');
        return res.json(cached.data);
      }
    }
    
    let products = [];
    
    // Usar SÓ a API oficial
    if (aliExpressAPI.isConfigured()) {
      try {
        console.log('🚀 Using official AliExpress API');
        products = await aliExpressAPI.searchProducts(q, {
          page: parseInt(page),
          pageSize: parseInt(limit),
          sort: sort
        });
      } catch (apiError) {
        console.log('❌ AliExpress API Error:', apiError.message);
        products = [];
      }
    } else {
      console.log('❌ AliExpress API not configured');
      products = [];
    }
    
    // Se não encontrou produtos, retornar vazio
    if (products.length === 0) {
      console.log('⚠️ No products found in AliExpress');
      products = [];
    }
    
    const result = {
      query: q,
      total: products.length,
      page: parseInt(page),
      sort: sort,
      products: products
    };
    
    // Salvar no cache
    productCache.set(cacheKey, {
      data: result,
      timestamp: Date.now()
    });
    
    res.json(result);
    
  } catch (error) {
    console.error('❌ Search error:', error.message);
    res.status(500).json({ 
      error: 'Failed to search products',
      message: error.message,
      products: []
    });
  }
});



// Obter detalhes do produto via API oficial
app.get('/api/product', async (req, res) => {
  try {
    const { url } = req.query;
    
    if (!url) {
      return res.status(400).json({ error: 'URL parameter is required' });
    }
    
    console.log(`📦 Getting product details: ${url}`);
    
    // Verificar cache
    const cacheKey = `product_${url}`;
    if (productCache.has(cacheKey)) {
      const cached = productCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log('📦 Returning cached product details');
        return res.json(cached.data);
      }
    }
    
    // Usar SÓ a API oficial
    if (aliExpressAPI.isConfigured()) {
      try {
        const productId = extractProductId(url);
        const product = await aliExpressAPI.getProductDetails(productId);
        
        // Salvar no cache
        productCache.set(cacheKey, {
          data: product,
          timestamp: Date.now()
        });
        
        res.json(product);
      } catch (apiError) {
        console.log('❌ AliExpress API Error:', apiError.message);
        res.status(404).json({ 
          error: 'Product not found',
          message: 'Could not retrieve product details from AliExpress API'
        });
      }
    } else {
      console.log('❌ AliExpress API not configured');
      res.status(500).json({ 
        error: 'API not configured',
        message: 'AliExpress API credentials not found'
      });
    }
    
  } catch (error) {
    console.error('❌ Product details error:', error.message);
    res.status(500).json({ 
      error: 'Failed to get product details',
      message: error.message
    });
  }
});

// Importar produto individual
app.post('/api/import', async (req, res) => {
  try {
    const { url, categoryId, priceOverride, stockQuantity } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }
    
    console.log(`📦 Importing product: ${url}`);
    
    // Obter detalhes do produto via API oficial
    const productId = extractProductId(url);
    const productDetails = await aliExpressAPI.getProductDetails(productId);
    
    // Processar dados para importação
    const importData = {
      ...productDetails,
      categoryId: categoryId || 'general',
      priceOverride: priceOverride,
      stockQuantity: stockQuantity || 0,
      importedAt: new Date().toISOString(),
      status: 'pending'
    };
    
    res.json({
      success: true,
      message: 'Product imported successfully',
      product: importData
    });
    
  } catch (error) {
    console.error('❌ Import error:', error.message);
    res.status(500).json({ 
      error: 'Failed to import product',
      message: error.message
    });
  }
});

// Importar produtos em lote
app.post('/api/import/bulk', async (req, res) => {
  try {
    const { urls, categoryId, priceMultiplier = 1.5 } = req.body;
    
    if (!urls || !Array.isArray(urls)) {
      return res.status(400).json({ error: 'URLs array is required' });
    }
    
    console.log(`📦 Bulk importing ${urls.length} products`);
    
    const results = [];
    const errors = [];
    
    for (let i = 0; i < urls.length; i++) {
      try {
        const url = urls[i];
        console.log(`📦 Processing ${i + 1}/${urls.length}: ${url}`);
        
                 const productId = extractProductId(url);
         const productDetails = await aliExpressAPI.getProductDetails(productId);
        
        // Aplicar multiplicador de preço
        if (priceMultiplier && productDetails.price) {
          const priceValue = parseFloat(productDetails.price.replace(/[^\d.,]/g, '').replace(',', '.'));
          if (!isNaN(priceValue)) {
            productDetails.price = `R$ ${(priceValue * priceMultiplier).toFixed(2).replace('.', ',')}`;
          }
        }
        
        const importData = {
          ...productDetails,
          categoryId: categoryId || 'general',
          importedAt: new Date().toISOString(),
          status: 'pending'
        };
        
        results.push(importData);
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        console.error(`❌ Error importing ${urls[i]}:`, error.message);
        errors.push({
          url: urls[i],
          error: error.message
        });
      }
    }
    
    res.json({
      success: true,
      message: `Imported ${results.length} products successfully`,
      imported: results.length,
      errors: errors.length,
      results: results,
      errors: errors
    });
    
  } catch (error) {
    console.error('❌ Bulk import error:', error.message);
    res.status(500).json({ 
      error: 'Failed to import products',
      message: error.message
    });
  }
});

// Estatísticas da API
app.get('/api/stats', async (req, res) => {
  try {
    const stats = {
      cacheSize: productCache.size,
      cacheKeys: Array.from(productCache.keys()),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      timestamp: new Date().toISOString()
    };
    
    res.json(stats);
  } catch (error) {
    console.error('❌ Stats error:', error.message);
    res.status(500).json({ error: 'Failed to get stats' });
  }
});

// Produtos em tendência
app.get('/api/trending', async (req, res) => {
  try {
    const trendingProducts = getTrendingProducts();
    res.json({
      total: trendingProducts.length,
      products: trendingProducts
    });
  } catch (error) {
    console.error('❌ Trending error:', error.message);
    res.status(500).json({ error: 'Failed to get trending products' });
  }
});

// Categorias populares
app.get('/api/categories', async (req, res) => {
  try {
    const categories = [
      { id: 'electronics', name: 'Electronics', icon: '📱', count: 1250 },
      { id: 'clothing', name: 'Clothing & Accessories', icon: '👕', count: 890 },
      { id: 'home', name: 'Home & Garden', icon: '🏠', count: 670 },
      { id: 'beauty', name: 'Beauty & Health', icon: '💄', count: 450 },
      { id: 'sports', name: 'Sports & Outdoor', icon: '⚽', count: 320 },
      { id: 'toys', name: 'Toys & Hobbies', icon: '🎮', count: 280 },
      { id: 'automotive', name: 'Automotive', icon: '🚗', count: 190 },
      { id: 'jewelry', name: 'Jewelry & Watches', icon: '💍', count: 150 }
    ];
    
    res.json({
      total: categories.length,
      categories: categories
    });
  } catch (error) {
    console.error('❌ Categories error:', error.message);
    res.status(500).json({ error: 'Failed to get categories' });
  }
});



// Funções auxiliares
function getTrendingProducts() {
  return [];
}

function extractProductId(url) {
  const match = url.match(/item\/(\d+)\.html/);
  return match ? match[1] : 'unknown';
}

// Error handling
app.use((error, req, res, next) => {
  console.error('❌ Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 API Server running on port ${PORT}`);
  console.log(`🌐 Accessible at:`);
  console.log(`   Local: http://localhost:${PORT}`);
  console.log(`   Network: http://192.168.1.24:${PORT}`);
  console.log(`📱 Endpoints:`);
  console.log(`   GET  /api/search?q=query&sort=rating&page=1`);
  console.log(`   GET  /api/product?url=product_url`);
  console.log(`   POST /api/import`);
  console.log(`   POST /api/import/bulk`);
  console.log(`   GET  /api/trending`);
  console.log(`   GET  /api/categories`);
  console.log(`   GET  /api/stats`);
});

module.exports = app; 