/**
 * API Communication Layer
 * Handles all HTTP requests to the Django backend
 * Includes client-side caching to reduce API calls
 */

// Cache configuration
const CACHE_DURATIONS = {
  stockData: 60000,      // 1 minute for stock data
  marketMovers: 120000,  // 2 minutes for market movers
  news: 300000,          // 5 minutes for news
  analysis: 600000       // 10 minutes for AI analysis
};

/**
 * Get cached data from localStorage
 * @param {string} key - Cache key
 * @param {number} duration - Cache duration in milliseconds (optional, uses default if not provided)
 * @returns {Object|null} Cached data or null if expired/missing
 */
function getCachedData(key, duration = null) {
  try {
    const cached = localStorage.getItem(key);
    if (!cached) return null;
    
    const { data, timestamp } = JSON.parse(cached);
    const now = Date.now();
    
    // Determine cache duration
    let cacheDuration = duration;
    if (!cacheDuration) {
      // Try to infer from key
      if (key.startsWith('stock_')) {
        cacheDuration = CACHE_DURATIONS.stockData;
      } else if (key === 'marketMovers') {
        cacheDuration = CACHE_DURATIONS.marketMovers;
      } else if (key.startsWith('news_')) {
        cacheDuration = CACHE_DURATIONS.news;
      } else {
        cacheDuration = 60000; // Default 1 minute
      }
    }
    
    // Check if cache is still valid
    if (now - timestamp < cacheDuration) {
      return data;
    }
    
    // Cache expired, remove it
    localStorage.removeItem(key);
    return null;
  } catch (error) {
    console.warn('Error reading cache:', error);
    return null;
  }
}

/**
 * Store data in cache
 * @param {string} key - Cache key
 * @param {Object} data - Data to cache
 */
function setCachedData(key, data) {
  try {
    const cacheEntry = {
      data: data,
      timestamp: Date.now()
    };
    localStorage.setItem(key, JSON.stringify(cacheEntry));
  } catch (error) {
    console.warn('Error writing cache:', error);
  }
}

/**
 * Fetch stock data for a given symbol
 * @param {string} symbol - The stock symbol to fetch data for
 * @param {boolean} forceRefresh - Force refresh, bypass cache
 * @returns {Promise<Object>} Stock data object or error
 */
async function fetchStockData(symbol, forceRefresh = false) {
  // Check cache first (unless forcing refresh)
  if (!forceRefresh) {
    const cacheKey = `stock_${symbol}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();
        // Check if cache is still valid (1 minute)
        if (now - timestamp < CACHE_DURATIONS.stockData) {
          console.log(`Using cached stock data for ${symbol}`);
          return data;
        }
        // Cache expired, remove it
        localStorage.removeItem(cacheKey);
      } catch (e) {
        // Invalid cache, remove it
        localStorage.removeItem(cacheKey);
      }
    }
  }
  
  try {
    const response = await fetch(`/api/stock-data/?symbol=${symbol}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    // Cache the response
    const cacheKey = `stock_${symbol}`;
    setCachedData(cacheKey, data);
    
    return data;
  } catch (error) {
    console.error('Error fetching stock data:', error);
    // Try to return cached data even if expired as fallback
    const cacheKey = `stock_${symbol}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { data } = JSON.parse(cached);
        console.log(`Using expired cache as fallback for ${symbol}`);
        return data;
      } catch (e) {
        // Invalid cache
      }
    }
    throw error;
  }
}

/**
 * Fetch market movers (gainers and losers)
 * @param {boolean} forceRefresh - Force refresh, bypass cache
 * @returns {Promise<Object>} Object containing gainers and losers arrays
 */
async function fetchMarketMovers(forceRefresh = false) {
  const cacheKey = 'marketMovers';
  
  // Check cache first (unless forcing refresh)
  if (!forceRefresh) {
    const cached = getCachedData(cacheKey);
    if (cached) {
      console.log('Using cached market movers data');
      return cached;
    }
  }
  
  try {
    const response = await fetch('/api/market-movers/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    // Cache the response
    setCachedData(cacheKey, data);
    
    return data;
  } catch (error) {
    console.error('Error fetching market movers:', error);
    // Try to return cached data even if expired as fallback
    const cached = getCachedData(cacheKey);
    if (cached) {
      console.log('Using expired cache as fallback for market movers');
      return cached;
    }
    throw error;
  }
}

/**
 * Fetch PortfolAI analysis for a given symbol
 * @param {string} symbol - The stock symbol to analyze
 * @returns {Promise<Object>} Analysis data object
 */
async function fetchPortfolAIAnalysis(symbol) {
  try {
    const response = await fetch(`/api/portfolai-analysis/?symbol=${symbol}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching analysis:', error);
    throw error;
  }
}

/**
 * Fetch news articles, optionally filtered by symbol
 * @param {string} symbol - Optional stock symbol to filter news
 * @param {boolean} forceRefresh - Force refresh, bypass cache
 * @returns {Promise<Object>} News data object
 */
async function fetchNews(symbol = null, forceRefresh = false) {
  const cacheKey = `news_${symbol || 'general'}`;
  
  // Check cache first (unless forcing refresh)
  if (!forceRefresh) {
    const cached = getCachedData(cacheKey);
    if (cached) {
      console.log(`Using cached news data for ${symbol || 'general'}`);
      return cached;
    }
  }
  
  try {
    const url = symbol ? `/api/news/?symbol=${symbol}` : '/api/news/';
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    // Cache the response
    setCachedData(cacheKey, data);
    
    return data;
  } catch (error) {
    console.error('Error fetching news:', error);
    // Try to return cached data even if expired as fallback
    const cached = getCachedData(cacheKey);
    if (cached) {
      console.log(`Using expired cache as fallback for news ${symbol || 'general'}`);
      return cached;
    }
    throw error;
  }
}
