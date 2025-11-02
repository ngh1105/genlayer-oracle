/**
 * Proxy Service Example for Off-chain Proxy Pattern
 * 
 * This is a Node.js Express server that acts as a proxy between
 * GenLayer contracts and external APIs that require authentication.
 * 
 * The proxy holds API keys and adds them to requests.
 * Contracts never see or store API keys.
 * 
 * Setup:
 *   1. Install dependencies: npm install express axios dotenv
 *   2. Set API keys in .env file
 *   3. Run: node scripts/proxy-service-example.js
 * 
 * Usage:
 *   Contract calls: GET https://your-proxy.com/api/price/ETH
 *   Proxy adds API key and calls: GET https://api.coingecko.com/.../price?...
 */

const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// API keys stored in environment variables (never in code)
const COINGECKO_API_KEY = process.env.COINGECKO_API_KEY;
const BINANCE_API_KEY = process.env.BINANCE_API_KEY;

// Rate limiting (simple in-memory store - use Redis in production)
const rateLimitStore = new Map();
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 100; // 100 requests per window

function rateLimit(req, res, next) {
  const clientId = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  
  if (!rateLimitStore.has(clientId)) {
    rateLimitStore.set(clientId, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return next();
  }
  
  const limit = rateLimitStore.get(clientId);
  
  if (now > limit.resetTime) {
    // Reset window
    limit.count = 1;
    limit.resetTime = now + RATE_LIMIT_WINDOW;
    return next();
  }
  
  if (limit.count >= RATE_LIMIT_MAX) {
    return res.status(429).json({ 
      error: 'Rate limit exceeded',
      retryAfter: Math.ceil((limit.resetTime - now) / 1000)
    });
  }
  
  limit.count++;
  next();
}

// Apply rate limiting to all routes
app.use(rateLimit);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    timestamp: Date.now(),
    hasCoingeckoKey: !!COINGECKO_API_KEY,
    hasBinanceKey: !!BINANCE_API_KEY
  });
});

// Price endpoint
app.get('/api/price/:symbol', async (req, res) => {
  const symbol = symbolMap[req.params.symbol.toUpperCase()] || req.params.symbol.toLowerCase();
  
  try {
    // Try Coingecko first (if key available)
    if (COINGECKO_API_KEY) {
      try {
        const response = await axios.get(
          'https://api.coingecko.com/api/v3/simple/price',
          {
            params: { 
              ids: symbol,
              vs_currencies: 'usd'
            },
            headers: {
              'X-CG-Pro-API-Key': COINGECKO_API_KEY,  // API key added here
              'User-Agent': 'GenLayerProxy/1.0'
            },
            timeout: 5000
          }
        );
        
        const price = response.data[symbol]?.usd;
        
        if (price) {
          return res.json({
            price: price.toString(),
            source: 'coingecko-proxy',
            timestamp: Date.now(),
            symbol: req.params.symbol.toUpperCase()
          });
        }
      } catch (coingeckoError) {
        // Fallback to Binance if Coingecko fails
        console.log('Coingecko failed, trying Binance...', coingeckoError.message);
      }
    }
    
    // Fallback to Binance (if key available)
    if (BINANCE_API_KEY) {
      try {
        const binanceSymbol = `${req.params.symbol.toUpperCase()}USDT`;
        const response = await axios.get(
          `https://api.binance.com/api/v3/ticker/price`,
          {
            params: { symbol: binanceSymbol },
            headers: {
              'X-MBX-APIKEY': BINANCE_API_KEY,
              'User-Agent': 'GenLayerProxy/1.0'
            },
            timeout: 5000
          }
        );
        
        const price = parseFloat(response.data.price);
        
        if (price && price > 0) {
          return res.json({
            price: price.toString(),
            source: 'binance-proxy',
            timestamp: Date.now(),
            symbol: req.params.symbol.toUpperCase()
          });
        }
      } catch (binanceError) {
        console.log('Binance failed:', binanceError.message);
      }
    }
    
    // All sources failed
    res.status(503).json({ 
      error: 'All price sources unavailable',
      message: 'Coingecko and Binance both failed'
    });
    
  } catch (error) {
    console.error('Proxy error:', error.message);
    res.status(500).json({ 
      error: 'Proxy error',
      message: error.message
    });
  }
});

// Symbol mapping for common cryptocurrencies
const symbolMap = {
  'ETH': 'ethereum',
  'BTC': 'bitcoin',
  'SOL': 'solana',
  'MATIC': 'matic-network',
  'AVAX': 'avalanche-2',
  'ADA': 'cardano',
  'DOT': 'polkadot',
  'LINK': 'chainlink'
};

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log(`Proxy service running on http://${HOST}:${PORT}`);
  console.log(`Health check: http://${HOST}:${PORT}/health`);
  console.log(`Price endpoint: http://${HOST}:${PORT}/api/price/ETH`);
  
  if (!COINGECKO_API_KEY && !BINANCE_API_KEY) {
    console.warn('⚠️  WARNING: No API keys configured in .env file');
    console.warn('   Set COINGECKO_API_KEY or BINANCE_API_KEY in .env');
  }
});

module.exports = app;

