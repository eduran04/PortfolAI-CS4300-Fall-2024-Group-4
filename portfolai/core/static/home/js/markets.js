/**
 * Markets Page JavaScript
 * Handles market news fetching and display, and TradingView heatmap widget
 */

/** @type {string|null} Currently active heatmap type */
let currentHeatmapType = 'stock';

/** @type {Object} TradingView heatmap widget script URLs */
const TRADINGVIEW_HEATMAP_URLS = {
  stock: 'https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js',
  crypto: 'https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js',
  etf: 'https://s3.tradingview.com/external-embedding/embed-widget-etf-heatmap.js',
  forex: 'https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js'
};

/** @type {number} Delay in milliseconds before hiding the heatmap loader */
const HEATMAP_LOADER_DELAY = 500;

/**
 * Fetch market news from the API
 * @param {string} category - News category (general, forex, crypto, merger)
 * @param {number} minId - Minimum news ID for pagination
 * @returns {Promise<Object>} Market news data
 */
async function fetchMarketNews(category = 'general', minId = 0) {
  try {
    const url = `/api/market-news/?category=${category}&minId=${minId}`;
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

    return data;
  } catch (error) {
    console.error('Error fetching market news:', error);
    throw error;
  }
}

/**
 * Format timestamp to readable date
 * @param {string} isoString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(isoString) {
  if (!isoString) return 'Unknown date';
  
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    }
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Unknown date';
  }
}

/**
 * Display market news articles
 * @param {Array} articles - Array of news articles
 */
function displayMarketNews(articles) {
  const newsFeedDiv = document.getElementById('market-news-feed');
  if (!newsFeedDiv) {
    console.warn('Market news feed element not found');
    return;
  }

  if (!articles || articles.length === 0) {
    newsFeedDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No market news available at this time.</p>';
    return;
  }

  newsFeedDiv.innerHTML = articles.map(article => {
    // Handle image URL - check multiple possible field names and ensure it's a valid URL
    let imageUrl = article.image || article.image_url || '';
    // If image URL is empty or invalid, use placeholder
    if (!imageUrl || imageUrl.trim() === '' || imageUrl === '#' || !imageUrl.startsWith('http')) {
      imageUrl = 'https://via.placeholder.com/400x200?text=News';
    }
    const publishedAt = formatDate(article.publishedAt || article.published_at);
    const description = article.description || article.snippet || article.title || 'No description available';
    const truncatedDescription = description.length > 150 
      ? description.substring(0, 150) + '...' 
      : description;
    const source = article.source || 'Unknown source';

    return `
      <article class="news-card bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="md:w-1/3">
            <img 
              src="${imageUrl}" 
              alt="${article.title || 'News image'}"
              class="w-full h-48 object-cover rounded-md"
              onerror="this.onerror=null; this.src='https://via.placeholder.com/400x200?text=News'"
              loading="lazy"
            />
          </div>
          <div class="md:w-2/3 flex flex-col justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                <a 
                  href="${article.url || '#'}" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  ${article.title || 'No title'}
                </a>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                ${truncatedDescription}
              </p>
            </div>
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center gap-2">
                <span class="font-medium">${source}</span>
                <span>•</span>
                <span>${publishedAt}</span>
                ${article.category ? `<span>•</span><span class="capitalize">${article.category}</span>` : ''}
              </div>
              <a 
                href="${article.url || '#'}" 
                target="_blank" 
                rel="noopener noreferrer"
                class="text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Read more →
              </a>
            </div>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

/**
 * Populate market news feed
 * @param {string} category - News category
 */
async function populateMarketNews(category = 'general') {
  const newsFeedDiv = document.getElementById('market-news-feed');
  if (!newsFeedDiv) {
    console.warn('Market news feed element not found');
    return;
  }

  // Show loading state
  newsFeedDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">Loading market news...</p>';

  try {
    const data = await fetchMarketNews(category, 0);
    const articles = data.articles || [];
    // Backend already limits to 3, but ensure we don't exceed
    const limitedArticles = articles.slice(0, 3);
    displayMarketNews(limitedArticles);
  } catch (error) {
    console.error('Error populating market news:', error);
    newsFeedDiv.innerHTML = '<p class="text-sm text-red-500 dark:text-red-400">Error loading market news. Please try again later.</p>';
  }
}

/**
 * Initialize market news functionality
 */
function initializeMarketNews() {
  // Set up category buttons
  const categoryButtons = document.querySelectorAll('.news-category-btn');
  let currentCategory = 'general';

  categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
      const category = button.getAttribute('data-category');
      
      // Update active state
      categoryButtons.forEach(btn => {
        btn.classList.remove('active', 'bg-indigo-600', 'text-white');
        btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
      });
      
      button.classList.add('active', 'bg-indigo-600', 'text-white');
      button.classList.remove('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
      
      // Load news for selected category
      currentCategory = category;
      populateMarketNews(category);
    });
  });

  // Load initial news
  populateMarketNews(currentCategory);
}

/**
 * Create TradingView stock heatmap widget configuration
 * @returns {Object} TradingView stock heatmap widget configuration
 */
function createStockHeatmapConfig() {
  const theme = getCurrentTheme();
  const isDark = theme === 'dark';
  
  return {
    "dataSource": "SPX500",
    "blockSize": "market_cap_basic",
    "blockColor": "change",
    "grouping": "sector",
    "locale": "en",
    "symbolUrl": "",
    "colorTheme": isDark ? "dark" : "light",
    "exchanges": [],
    "hasTopBar": false,
    "isDataSetEnabled": false,
    "isZoomEnabled": true,
    "hasSymbolTooltip": true,
    "isMonoSize": false,
    "width": "100%",
    "height": "100%"
  };
}

/**
 * Create TradingView crypto heatmap widget configuration
 * @returns {Object} TradingView crypto heatmap widget configuration
 */
function createCryptoHeatmapConfig() {
  const theme = getCurrentTheme();
  const isDark = theme === 'dark';
  
  return {
    "dataSource": "Crypto",
    "blockSize": "market_cap_calc",
    "blockColor": "24h_close_change|5",
    "locale": "en",
    "symbolUrl": "",
    "colorTheme": isDark ? "dark" : "light",
    "hasTopBar": false,
    "isDataSetEnabled": false,
    "isZoomEnabled": true,
    "hasSymbolTooltip": true,
    "isMonoSize": false,
    "width": "100%",
    "height": "100%"
  };
}

/**
 * Create TradingView ETF heatmap widget configuration
 * @returns {Object} TradingView ETF heatmap widget configuration
 */
function createETFHeatmapConfig() {
  const theme = getCurrentTheme();
  const isDark = theme === 'dark';
  
  return {
    "dataSource": "AllUSEtf",
    "blockSize": "volume",
    "blockColor": "change",
    "grouping": "asset_class",
    "locale": "en",
    "symbolUrl": "",
    "colorTheme": isDark ? "dark" : "light",
    "hasTopBar": false,
    "isDataSetEnabled": false,
    "isZoomEnabled": true,
    "hasSymbolTooltip": true,
    "isMonoSize": false,
    "width": "100%",
    "height": "100%"
  };
}

/**
 * Get current theme from localStorage or system preference
 * @returns {string} Current theme ('dark' or 'light')
 */
function getCurrentTheme() {
  const storedTheme = localStorage.getItem('color-theme');
  if (storedTheme) {
    return storedTheme;
  }
  
  // Fallback to system preference
  return document.documentElement.classList.contains('dark') 
    ? 'dark' 
    : (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

/**
 * Create TradingView forex heatmap widget configuration
 * @returns {Object} TradingView forex heatmap widget configuration
 */
function createForexHeatmapConfig() {
  const theme = getCurrentTheme();
  const isDark = theme === 'dark';
  
  return {
    "colorTheme": isDark ? "dark" : "light",
    "isTransparent": false,
    "locale": "en",
    "currencies": [
      "EUR",
      "USD",
      "JPY",
      "GBP",
      "CHF",
      "AUD",
      "CAD",
      "NZD",
      "CNY"
    ],
    "backgroundColor": isDark ? "#1F2937" : "#F9FAFB",
    "width": "100%",
    "height": "100%"
  };
}

/**
 * Get copyright HTML for heatmap type
 * @param {string} type - Heatmap type (stock, crypto, etf, forex)
 * @returns {string} Copyright HTML
 */
function getHeatmapCopyright(type) {
  const copyrights = {
    stock: '<a href="https://www.tradingview.com/heatmap/stock/" rel="noopener nofollow" target="_blank"><span class="blue-text">Stock Heatmap</span></a><span class="trademark"> by TradingView</span>',
    crypto: '<a href="https://www.tradingview.com/heatmap/crypto/" rel="noopener nofollow" target="_blank"><span class="blue-text">Crypto Heatmap</span></a><span class="trademark"> by TradingView</span>',
    etf: '<a href="https://www.tradingview.com/heatmap/etf/" rel="noopener nofollow" target="_blank"><span class="blue-text">ETF Heatmap</span></a><span class="trademark"> by TradingView</span>',
    forex: '<a href="https://www.tradingview.com/markets/currencies/cross-rates-overview-heat-map/" rel="noopener nofollow" target="_blank"><span class="blue-text">Forex Heatmap</span></a><span class="trademark"> by TradingView</span>'
  };
  return copyrights[type] || copyrights.stock;
}

/**
 * Clear all TradingView heatmap widgets
 */
function clearAllHeatmaps() {
  const containers = ['stock', 'crypto', 'etf', 'forex'];
  containers.forEach(type => {
    const container = document.getElementById(`tradingview-heatmap-${type}`);
    if (container) {
      container.innerHTML = '';
    }
  });
}

/**
 * Render a TradingView heatmap widget
 * @param {string} type - Heatmap type (stock, crypto, etf, forex)
 * @param {boolean} force - Force re-render even if widget exists (for theme changes)
 */
function renderTradingViewHeatmap(type = 'stock', force = false) {
  const widgetContainer = document.getElementById(`tradingview-heatmap-${type}`);
  const loader = document.getElementById('heatmap-loader');
  
  if (!widgetContainer) {
    console.error(`TradingView heatmap container not found for type: ${type}`);
    return;
  }

  // Clear all heatmaps first
  clearAllHeatmaps();

  // Hide all heatmap containers first
  ['stock', 'crypto', 'etf', 'forex'].forEach(t => {
    const container = document.getElementById(`tradingview-heatmap-${t}`);
    if (container) {
      container.classList.add('hidden');
    }
  });

  // Show selected heatmap container (must be visible before script loads)
  widgetContainer.classList.remove('hidden');

  // Show loader
  if (loader) {
    loader.classList.remove('hidden');
  }

  // Check if widget already exists and is loaded in this container
  // Skip this check if force is true (for theme changes)
  if (!force) {
    const existingScript = widgetContainer.querySelector('script[src]');
    if (existingScript && widgetContainer.querySelector('.tradingview-widget-container__widget')) {
      // Widget already loaded, just show it and hide loader
      if (loader) {
        setTimeout(() => {
          loader.classList.add('hidden');
        }, 100);
      }
      return;
    }
  }

  try {
    // Get configuration based on type
    let config;
    switch (type) {
      case 'crypto':
        config = createCryptoHeatmapConfig();
        break;
      case 'etf':
        config = createETFHeatmapConfig();
        break;
      case 'forex':
        config = createForexHeatmapConfig();
        break;
      case 'stock':
      default:
        config = createStockHeatmapConfig();
        break;
    }

    // Create widget container div (required by TradingView)
    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    
    // Create and configure TradingView embed script
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = TRADINGVIEW_HEATMAP_URLS[type];
    script.async = true;
    
    // Set the script content with the configuration
    // TradingView expects the config as textContent of the script tag
    script.textContent = JSON.stringify(config);
    
    // Create copyright attribution (required by TradingView)
    const copyrightDiv = document.createElement('div');
    copyrightDiv.className = 'tradingview-widget-copyright';
    copyrightDiv.innerHTML = getHeatmapCopyright(type);
    
    // Append elements to container in correct order
    widgetContainer.appendChild(widgetDiv);
    widgetContainer.appendChild(script);
    widgetContainer.appendChild(copyrightDiv);
    
    // Hide loader after delay (give widget time to render)
    // Increase delay for better widget loading
    if (loader) {
      setTimeout(() => {
        loader.classList.add('hidden');
      }, HEATMAP_LOADER_DELAY * 2);
    }
    
    // Also listen for script load event
    script.onload = () => {
      console.log(`TradingView ${type} heatmap script loaded`);
      if (loader) {
        setTimeout(() => {
          loader.classList.add('hidden');
        }, HEATMAP_LOADER_DELAY);
      }
    };
    
    script.onerror = () => {
      console.error(`Failed to load TradingView ${type} heatmap script`);
      if (loader) {
        loader.innerHTML = '<p class="text-red-500 dark:text-red-400">Error loading heatmap. Please refresh the page.</p>';
      }
    };
    
    console.log(`TradingView ${type} heatmap widget rendered`);
  } catch (error) {
    console.error(`Error rendering TradingView ${type} heatmap:`, error);
    if (loader) {
      loader.innerHTML = '<p class="text-red-500 dark:text-red-400">Error loading heatmap. Please refresh the page.</p>';
    }
  }
}

/**
 * Switch heatmap type
 * @param {string} type - Heatmap type (stock, crypto, etf, forex)
 */
function switchHeatmap(type) {
  if (!['stock', 'crypto', 'etf', 'forex'].includes(type)) {
    console.error(`Invalid heatmap type: ${type}`);
    return;
  }

  currentHeatmapType = type;

  // Update tab buttons
  const tabButtons = document.querySelectorAll('.heatmap-tab-btn');
  tabButtons.forEach(btn => {
    const btnType = btn.getAttribute('data-heatmap');
    if (btnType === type) {
      btn.classList.add('active', 'bg-indigo-600', 'text-white');
      btn.classList.remove('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
    } else {
      btn.classList.remove('active', 'bg-indigo-600', 'text-white');
      btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
    }
  });

  // Render the selected heatmap
  renderTradingViewHeatmap(type);
}

/**
 * Initialize TradingView heatmap with tab switching
 */
function initializeHeatmap() {
  // Set up tab buttons
  const tabButtons = document.querySelectorAll('.heatmap-tab-btn');
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const type = button.getAttribute('data-heatmap');
      switchHeatmap(type);
    });
  });

  // Render initial heatmap (stock)
  renderTradingViewHeatmap('stock');
  
  // Listen for theme changes and re-render the current heatmap
  window.addEventListener('theme-changed', (event) => {
    // Only re-render if we're currently showing a heatmap
    if (currentHeatmapType) {
      console.log(`Theme changed to ${event.detail.theme}, re-rendering ${currentHeatmapType} heatmap`);
      // Force re-render the current heatmap with new theme
      renderTradingViewHeatmap(currentHeatmapType, true);
    }
  });
}

