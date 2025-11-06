/**
 * API Communication Layer
 * Handles all HTTP requests to the Django backend
 */

/**
 * Fetch stock data for a given symbol
 * @param {string} symbol - The stock symbol to fetch data for
 * @returns {Promise<Object>} Stock data object or error
 */
async function fetchStockData(symbol) {
  try {
    const response = await fetch(`/api/stock-data/?symbol=${symbol}`, {
      method: 'GET',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
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
    console.error('Error fetching stock data:', error);
    throw error;
  }
}

/**
 * Fetch market movers (gainers and losers)
 * @returns {Promise<Object>} Object containing gainers and losers arrays
 */
async function fetchMarketMovers() {
  try {
    const response = await fetch('/api/market-movers/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
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
    console.error('Error fetching market movers:', error);
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
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
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
 * @returns {Promise<Object>} News data object
 */
async function fetchNews(symbol = null) {
  try {
    const url = symbol ? `/api/news/?symbol=${symbol}` : '/api/news/';
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
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
    console.error('Error fetching news:', error);
    throw error;
  }
}
