const express = require('express');
const cors = require('cors');
const axios = require('axios');
const crypto = require('crypto');
require('dotenv').config({ path: './config.env' });

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Configurações AliExpress
const APP_KEY = process.env.ALIEXPRESS_APP_KEY;
const APP_SECRET = process.env.ALIEXPRESS_APP_SECRET;
const CALLBACK_URL = 'https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback';

// Armazenar tokens
let aliexpressTokens = {};

// Função para gerar timestamp no formato correto
function aliTimestamp() {
    // Formato: YYYY-MM-DD HH:MM:SS (UTC+8)
    const now = new Date();
    const utc = new Date(now.getTime() + (8 * 60 * 60 * 1000)); // UTC+8
    return utc.toISOString().slice(0, 19).replace('T', ' ');
}

// Função para gerar assinatura MD5
function generateSign(params) {
    const sortedParams = Object.keys(params).sort().reduce((result, key) => {
        result[key] = params[key];
        return result;
    }, {});

    const paramString = Object.keys(sortedParams)
        .map(key => `${key}${sortedParams[key]}`)
        .join('');

    const signString = APP_SECRET + paramString + APP_SECRET;
    return crypto.createHash('md5').update(signString).digest('hex').toUpperCase();
}

// Gerar URL de autorização OAuth2
function generateAuthUrl() {
    const params = {
        response_type: 'code',
        client_id: APP_KEY,
        redirect_uri: CALLBACK_URL,
        state: 'xyz123',
        force_auth: 'true'
    };
    
    // Garantir que todos os parâmetros estão presentes
    if (!params.client_id) {
        throw new Error('APP_KEY não configurado');
    }
    
    const queryString = new URLSearchParams(params).toString();
    // Usar o endpoint correto baseado na documentação
    const authUrl = `https://oauth.aliexpress.com/authorize?${queryString}`;
    
    console.log('🔗 URL de autorização gerada:', authUrl);
    console.log('📝 Parâmetros:', params);
    return authUrl;
}

// Trocar código por access token
async function exchangeCodeForToken(code) {
    const timestamp = aliTimestamp();
    
    const params = {
        method: 'auth.token.create',
        app_key: APP_KEY,
        code: code,
        timestamp: timestamp,
        sign_method: 'md5',
        format: 'json',
        v: '2.0'
    };

    params.sign = generateSign(params);

    console.log('🔄 Fazendo requisição OAuth2...');
    console.log('📝 Dados:', params);

    try {
        const response = await axios.post('https://api-sg.aliexpress.com/rest', 
            new URLSearchParams(params), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        console.log('📊 Status Code:', response.status);
        console.log('📄 Response:', response.data);

        if (response.status === 200) {
            return response.data;
        } else {
            throw new Error(`HTTP ${response.status}: ${response.data}`);
        }
    } catch (error) {
        console.error('❌ Erro na requisição OAuth2:', error.message);
        throw error;
    }
}

// Endpoints

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        message: 'API funcionando!',
        app_key_configured: !!APP_KEY,
        app_secret_configured: !!APP_SECRET
    });
});

// Gerar URL de autorização
app.get('/api/aliexpress/oauth-url', (req, res) => {
    res.json({
        auth_url: generateAuthUrl()
    });
});

// Callback OAuth2
app.get('/api/aliexpress/oauth-callback', async (req, res) => {
    const { code } = req.query;
    
    if (!code) {
        return res.status(400).json({ error: 'Missing code parameter' });
    }

    try {
        const tokenData = await exchangeCodeForToken(code);
        
        // Armazenar tokens
        aliexpressTokens = {
            access_token: tokenData.access_token,
            refresh_token: tokenData.refresh_token,
            expires_in: tokenData.expires_in
        };

        console.log('✅ Tokens armazenados com sucesso!');
        console.log('🔑 Access Token:', tokenData.access_token ? tokenData.access_token.substring(0, 20) + '...' : 'N/A');

        res.json({
            success: true,
            message: 'OAuth2 autenticação realizada com sucesso!',
            token_data: tokenData
        });
    } catch (error) {
        console.error('❌ Erro na troca de código por token:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Buscar produtos
app.get('/api/aliexpress/products', async (req, res) => {
    const { keywords = '', page = 1, page_size = 20 } = req.query;
    
    if (!aliexpressTokens.access_token) {
        return res.status(401).json({
            success: false,
            error: 'OAuth2 não configurado',
            message: 'É necessário configurar OAuth2 para acessar produtos reais do AliExpress',
            auth_url: generateAuthUrl()
        });
    }

    try {
        const timestamp = aliTimestamp();
        const params = {
            method: 'aliexpress.ds.product.list',
            access_token: aliexpressTokens.access_token,
            app_key: APP_KEY,
            timestamp: timestamp,
            format: 'json',
            v: '2.0',
            keywords: keywords,
            page_no: page,
            page_size: page_size
        };

        params.sign = generateSign(params);

        const response = await axios.post('https://api-sg.aliexpress.com/sync', 
            new URLSearchParams(params), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const products = response.data.result?.products || [];
        
        res.json({
            success: true,
            products: products,
            raw: response.data
        });
    } catch (error) {
        console.error('❌ Erro na busca de produtos:', error.message);
        
        res.status(500).json({
            success: false,
            error: 'Erro na API do AliExpress',
            message: error.message
        });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log('🚀 API ALIEXPRESS NODE.JS iniciando...');
    console.log(`🌐 http://localhost:${PORT}`);
    console.log(`🔑 App Key configurado: ${APP_KEY ? '✅' : '❌'}`);
    console.log(`🔑 App Secret configurado: ${APP_SECRET ? '✅' : '❌'}`);
    console.log(`🔗 Callback URL: ${CALLBACK_URL}`);
});

module.exports = app; 