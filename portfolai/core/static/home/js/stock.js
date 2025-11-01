/**
 * Stock Search & Chart Management Module
 * 
 * Handles:
 * - Stock symbol search functionality
 * - Stock data display and formatting
 * - TradingView widget integration and rendering
 * 
 * @module StockManagement
 */

// ============================================================================
// Global Variables
// ============================================================================

/** @type {HTMLElement|null} Reference to the current TradingView widget container */
let tradingViewWidget = null;

/** @type {string} TradingView widget script URL */
const TRADINGVIEW_WIDGET_URL = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js';

/** @type {number} Delay in milliseconds before hiding the chart loader */
const CHART_LOADER_DELAY = 500;

/** @type {string[]} List of common NYSE-listed stock symbols */
const NYSE_SYMBOLS = [
  'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS',           // Financials
  'XOM', 'CVX',                                    // Energy
  'KO', 'JNJ', 'PG', 'WMT', 'TGT', 'HD', 'LOW',   // Consumer
  'NKE', 'SBUX', 'MCD', 'DIS',                    // Retail/Food
  'V', 'MA', 'AXP', 'BRK.B',                      // Payments/Finance
  'GE', 'BA', 'CAT', 'DE',                        // Industrials
  'OKLO'                                           // Energy/Utilities
];

// ============================================================================
// DOM Element References
// ============================================================================

const searchInput = document.getElementById('stock-search');
const searchButton = document.getElementById('search-button');
const stockDetailsDiv = document.getElementById('stock-details');
const companyNameHeader = document.getElementById('company-name');
const searchErrorDiv = document.getElementById('search-error');
const addToWatchlistBtn = document.getElementById('addToWatchlistBtn');
const portfolaiAnalysisBtn = document.getElementById('portfolaiAnalysisBtn');

/**
 * Perform stock search and update UI with results
 * 
 * Handles the complete search flow:
 * 1. Validates and normalizes the search input
 * 2. Fetches stock data from the API
 * 3. Displays stock information
 * 4. Renders TradingView chart widget
 * 5. Updates watchlist button state
 * 
 * @async
 * @function performSearch
 * @throws {Error} If stock data fetch fails
 */
async function performSearch() {
  const searchTerm = searchInput.value.toUpperCase().trim();
  searchErrorDiv.classList.add('hidden');
  
  // Handle empty search - reset UI to default state
  if (!searchTerm) {
    displayStockDetails(null);
    clearTradingViewWidget();
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;
    return;
  }

  try {
    // Show loading indicators
    document.getElementById('chart-loader').classList.remove('hidden');
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;

    // Fetch stock data from API
    const stockData = await fetchStockData(searchTerm);

    // Display stock details in the sidebar
    displayStockDetails(stockData, searchTerm);
    
    // Show fallback notice if API is unavailable (using demo data)
    if (stockData.fallback) {
      const fallbackNotice = document.createElement('div');
      fallbackNotice.className = 'bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-700 dark:text-yellow-300 px-4 py-3 rounded mb-4';
      fallbackNotice.innerHTML = '⚠️ Using demo data - API not configured or unavailable';
      stockDetailsDiv.parentNode.insertBefore(fallbackNotice, stockDetailsDiv);
      
      // Auto-remove notice after 5 seconds for better UX
      setTimeout(() => {
        if (fallbackNotice.parentNode) {
          fallbackNotice.parentNode.removeChild(fallbackNotice);
        }
      }, 5000);
    }

    // Render TradingView widget with the searched stock
    renderTradingViewWidget(searchTerm);

    // Update button states based on watchlist status
    addToWatchlistBtn.disabled = false;
    portfolaiAnalysisBtn.disabled = false;
    
    // Toggle watchlist button text and colors
    const isInWatchlist = isStockInWatchlist(searchTerm);
    addToWatchlistBtn.textContent = isInWatchlist
      ? 'Remove from Watchlist'
      : 'Add to Watchlist';
    
    // Update button styling based on watchlist status
    addToWatchlistBtn.classList.toggle('bg-red-500', isInWatchlist);
    addToWatchlistBtn.classList.toggle('hover:bg-red-600', isInWatchlist);
    addToWatchlistBtn.classList.toggle('bg-green-500', !isInWatchlist);
    addToWatchlistBtn.classList.toggle('hover:bg-green-600', !isInWatchlist);

  } catch (error) {
    console.error('Error fetching stock data:', error);
    searchErrorDiv.classList.remove('hidden');
    searchErrorDiv.textContent = `Error: ${error.message}`;
    
    // Reset UI on error
    clearTradingViewWidget();
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;
  }
}

/**
 * Display stock details in the UI sidebar
 * 
 * Formats and renders stock information including:
 * - Current price and daily change
 * - Market data (open, high, low, volume)
 * - Financial metrics (market cap, P/E ratio)
 * - 52-week high/low
 * 
 * @param {Object|null} stock - Stock data object containing price, change, metrics, etc.
 * @param {string} symbol - Stock symbol (e.g., 'AAPL', 'MSFT')
 */
function displayStockDetails(stock, symbol = 'N/A') {
  if (stock) {
    companyNameHeader.textContent = `${stock.name} (${symbol})`;
    
    // Determine color class based on price change direction
    const changeClass = stock.change >= 0
      ? 'text-green-500 dark:text-green-400'
      : 'text-red-500 dark:text-red-400';
    const changeSign = stock.change >= 0 ? '+' : '';
    
    stockDetailsDiv.innerHTML = `
      <div class="flex justify-between items-baseline">
          <p class="text-3xl font-bold">$${stock.price.toFixed(2)} <span class="text-xs text-gray-500 dark:text-gray-400">USD</span></p>
          <p class="text-lg ${changeClass}">${changeSign}${stock.change.toFixed(2)} (${changeSign}${stock.changePercent.toFixed(2)}%)</p>
      </div>
      <hr class="my-2 border-gray-200 dark:border-gray-600">
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
          <p><strong>Open:</strong> $${stock.open.toFixed(2)}</p>
          <p><strong>High:</strong> $${stock.high.toFixed(2)}</p>
          <p><strong>Low:</strong> $${stock.low.toFixed(2)}</p>
          <p><strong>Volume:</strong> ${stock.volume.toLocaleString()}</p>
          <p><strong>Mkt Cap:</strong> $${(stock.marketCap / 1000000000).toFixed(1)}B</p>
          <p><strong>P/E Ratio:</strong> ${stock.peRatio || 'N/A'}</p>
          <p><strong>52W H:</strong> $${stock.yearHigh.toFixed(2)}</p>
          <p><strong>52W L:</strong> $${stock.yearLow.toFixed(2)}</p>
      </div>
  `;
  } else {
    // Display default empty state
    companyNameHeader.textContent = 'Company Overview';
    stockDetailsDiv.innerHTML = `<p class="text-sm text-gray-600 dark:text-gray-400">Search for a stock to see details.</p>`;
  }
}

// ============================================================================
// TradingView Widget Helper Functions
// ============================================================================

/**
 * Detect the stock exchange for a given symbol
 * 
 * Determines the most likely exchange (NASDAQ or NYSE) based on known symbols.
 * TradingView supports auto-detection if the exchange is incorrect, but specifying
 * the correct exchange improves widget initialization speed.
 * 
 * @param {string} symbol - Stock symbol to detect exchange for
 * @returns {string} Exchange identifier ('NYSE' or 'NASDAQ')
 */
function detectExchange(symbol) {
  if (!symbol || symbol.length === 0) {
    return 'NASDAQ';
  }
  
  const upperSymbol = symbol.toUpperCase();
  return NYSE_SYMBOLS.includes(upperSymbol) ? 'NYSE' : 'NASDAQ';
}

/**
 * Get the current theme (light or dark) from localStorage or system preference
 * 
 * @returns {string} Theme identifier ('light' or 'dark')
 */
function getCurrentTheme() {
  const storedTheme = localStorage.getItem('color-theme');
  if (storedTheme) {
    return storedTheme;
  }
  
  // Fallback to system preference
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Create TradingView widget configuration object
 * 
 * Generates the configuration JSON for the TradingView Symbol Overview widget
 * with theme-appropriate colors and settings.
 * 
 * @param {string} symbol - Stock symbol to display
 * @param {string} exchange - Exchange identifier (e.g., 'NASDAQ', 'NYSE')
 * @param {string} theme - Theme identifier ('light' or 'dark')
 * @returns {Object} TradingView widget configuration object
 */
function createWidgetConfig(symbol, exchange, theme) {
  const isDark = theme === 'dark';
  
  // Theme-specific color schemes
  const colorScheme = isDark ? {
    fontColor: 'rgb(106, 109, 120)',
    gridLineColor: 'rgba(242, 242, 242, 0.06)',
    volumeUpColor: 'rgba(34, 171, 148, 0.5)',
    volumeDownColor: 'rgba(247, 82, 95, 0.5)',
    backgroundColor: '#0F0F0F',
    widgetFontColor: '#DBDBDB',
    upColor: '#22ab94',
    downColor: '#f7525f',
    borderUpColor: '#22ab94',
    borderDownColor: '#f7525f',
    wickUpColor: '#22ab94',
    wickDownColor: '#f7525f'
  } : {
    fontColor: 'rgb(106, 109, 120)',
    gridLineColor: 'rgba(230, 230, 230, 0.8)',
    volumeUpColor: 'rgba(34, 171, 148, 0.3)',
    volumeDownColor: 'rgba(247, 82, 95, 0.3)',
    backgroundColor: '#FFFFFF',
    widgetFontColor: '#1F2937',
    upColor: '#22c55e',
    downColor: '#ef4444',
    borderUpColor: '#22c55e',
    borderDownColor: '#ef4444',
    wickUpColor: '#22c55e',
    wickDownColor: '#ef4444'
  };
  
  return {
    // Chart appearance
    lineWidth: 2,
    lineType: 0,
    chartType: 'area',
    
    // Color scheme
    ...colorScheme,
    
    // Widget settings
    colorTheme: theme,
    isTransparent: false,
    locale: 'en',
    chartOnly: false,
    scalePosition: 'right',
    scaleMode: 'Normal',
    fontFamily: '-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif',
    valuesTracking: '1',
    changeMode: 'price-and-percent',
    
    // Symbol configuration - single stock display
    symbols: [
      [
        symbol,
        `${exchange}:${symbol}|1D`  // Format: EXCHANGE:SYMBOL|INTERVAL
      ]
    ],
    
    // Available date range selectors
    dateRanges: [
      '1d|1',      // 1 day, 1 minute intervals
      '1m|30',     // 1 month, 30 minute intervals
      '3m|60',     // 3 months, 60 minute intervals
      '12m|1D',    // 12 months, daily intervals
      '60m|1W',    // 60 months (5 years), weekly intervals
      'all|1M'     // All time, monthly intervals
    ],
    
    // Typography
    fontSize: '10',
    headerFontSize: 'medium',
    
    // Responsive sizing
    autosize: true,
    width: '100%',
    height: '100%',
    
    // UI elements visibility
    noTimeScale: false,
    hideDateRanges: false,
    hideMarketStatus: false,
    hideSymbolLogo: false
  };
}

/**
 * Create the TradingView widget DOM structure
 * 
 * Builds the required DOM elements for the TradingView widget including
 * the container div, script tag, and copyright attribution.
 * 
 * @param {HTMLElement} container - Container element to append widget to
 * @param {string} symbol - Stock symbol being displayed
 * @param {string} exchange - Exchange identifier
 * @param {Object} config - Widget configuration object
 * @returns {Object} Object containing widget div and copyright div references
 */
function createWidgetStructure(container, symbol, exchange, config) {
  // Create widget div
  const widgetDiv = document.createElement('div');
  widgetDiv.className = 'tradingview-widget-container__widget';
  
  // Create and configure TradingView embed script
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = TRADINGVIEW_WIDGET_URL;
  script.async = true;
  script.innerHTML = JSON.stringify(config);
  
  widgetDiv.appendChild(script);
  container.appendChild(widgetDiv);
  
  // Create copyright attribution (required by TradingView)
  const copyrightDiv = document.createElement('div');
  copyrightDiv.className = 'tradingview-widget-copyright';
  copyrightDiv.innerHTML = `<a href="https://www.tradingview.com/symbols/${exchange}-${symbol}/" rel="noopener nofollow" target="_blank"><span class="blue-text">${symbol}</span></a><span class="trademark"> by TradingView</span>`;
  container.appendChild(copyrightDiv);
  
  return { widgetDiv, copyrightDiv };
}

/**
 * Hide the chart loader with error handling
 * 
 * Attempts to hide the loading spinner after the widget has initialized.
 * Uses a timeout to allow TradingView script to load and render.
 * 
 * @param {HTMLElement|null} chartLoader - Chart loader element
 */
function hideChartLoader(chartLoader) {
  if (!chartLoader) {
    return;
  }
  
  setTimeout(() => {
    try {
      chartLoader.classList.add('hidden');
    } catch (error) {
      console.warn('Error hiding chart loader:', error);
    }
  }, CHART_LOADER_DELAY);
}

/**
 * Clear the TradingView widget and reset to loading state
 * 
 * Removes the current widget instance and shows the loading spinner.
 * Called when:
 * - User clears the search
 * - An error occurs during search
 * - Switching between stocks
 * 
 * @function clearTradingViewWidget
 */
function clearTradingViewWidget() {
  const widgetContainer = document.getElementById('tradingview-widget-container');
  if (widgetContainer) {
    widgetContainer.innerHTML = '';
  }
  
  // Show loading spinner
  const chartLoader = document.getElementById('chart-loader');
  if (chartLoader) {
    chartLoader.classList.remove('hidden');
  }
  
  // Clear global reference
  tradingViewWidget = null;
}

/**
 * Render or update the TradingView widget for a given stock symbol
 * 
 * Creates and configures a TradingView Symbol Overview widget with:
 * - Theme-aware styling (light/dark) matching the application aesthetic
 * - Single stock symbol display
 * - Interactive chart with date range selectors
 * - Proper exchange detection (NASDAQ/NYSE)
 * 
 * TradingView Widget Support:
 * - US Exchanges: NASDAQ, NYSE, AMEX
 * - International: LSE (London), TSE (Tokyo), SSE (Shanghai), ASX, TSX, etc.
 * - Auto-detection: TradingView can find symbols across exchanges if specified incorrectly
 * 
 * @param {string} symbol - Stock symbol to display (e.g., 'AAPL', 'MSFT', 'NFLX')
 * @throws {Error} If widget container element is not found in DOM
 */
function renderTradingViewWidget(symbol) {
  const widgetContainer = document.getElementById('tradingview-widget-container');
  const chartLoader = document.getElementById('chart-loader');
  
  // Validate container exists
  if (!widgetContainer) {
    console.error('TradingView widget container not found');
    return;
  }

  // Validate symbol
  if (!symbol || symbol.trim().length === 0) {
    console.warn('Empty symbol provided to renderTradingViewWidget');
    clearTradingViewWidget();
    return;
  }

  try {
    // Clear any previous widget instance
    widgetContainer.innerHTML = '';
    
    // Detect exchange and theme
    const exchange = detectExchange(symbol);
    const theme = getCurrentTheme();
    
    // Create widget configuration
    const config = createWidgetConfig(symbol, exchange, theme);
    
    // Build widget DOM structure
    createWidgetStructure(widgetContainer, symbol, exchange, config);
    
    // Hide loading spinner after widget initializes
    hideChartLoader(chartLoader);
    
    // Store reference for potential cleanup
    tradingViewWidget = widgetContainer;
    
  } catch (error) {
    console.error('Error rendering TradingView widget:', error);
    
    // Show error to user
    if (chartLoader) {
      chartLoader.classList.remove('hidden');
      chartLoader.innerHTML = '<span class="text-red-500">Error loading chart. Please try again.</span>';
    }
    
    // Reset global reference
    tradingViewWidget = null;
  }
}

/**
 * Re-render the TradingView widget when theme changes
 * 
 * If a widget is currently displayed, re-renders it with the new theme.
 * This ensures the chart matches the application's theme.
 * 
 * @function updateWidgetTheme
 */
function updateWidgetTheme() {
  const currentSymbol = searchInput.value.toUpperCase().trim();
  if (currentSymbol && tradingViewWidget) {
    renderTradingViewWidget(currentSymbol);
  }
}

/**
 * Initialize stock search functionality
 * 
 * Sets up event listeners for:
 * - Search button click
 * - Enter key press in search input
 * - Theme changes (to update chart theme)
 * 
 * @function initializeStockSearch
 */
function initializeStockSearch() {
  // Search button click handler
  searchButton.addEventListener('click', performSearch);
  
  // Enter key handler for search input
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  });
  
  // Listen for theme changes to update chart
  // Use a custom event dispatched by the theme toggle
  window.addEventListener('theme-changed', () => {
    updateWidgetTheme();
  });
  
  // Also listen for localStorage changes (works across tabs)
  window.addEventListener('storage', (e) => {
    if (e.key === 'color-theme') {
      updateWidgetTheme();
    }
  });
  
  // Monitor DOM for class changes on document element
  const themeObserver = new MutationObserver(() => {
    // Debounce to avoid multiple updates
    clearTimeout(window._themeUpdateTimeout);
    window._themeUpdateTimeout = setTimeout(() => {
      updateWidgetTheme();
    }, 100);
  });
  
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  });
}

/**
 * Initialize PortfolAI analysis functionality
 * 
 * Sets up the AI analysis button to:
 * - Fetch AI-powered stock analysis
 * - Display results in a modal dialog
 * - Handle loading states and errors
 * 
 * @function initializePortfolAIAnalysis
 */
function initializePortfolAIAnalysis() {
  portfolaiAnalysisBtn.addEventListener('click', async () => {
    const currentSymbol = searchInput.value.toUpperCase().trim();
    
    // Validate symbol exists
    if (!currentSymbol) {
      alert('Please search for a stock first');
      return;
    }
    
    // Update button to show loading state
    portfolaiAnalysisBtn.disabled = true;
    portfolaiAnalysisBtn.textContent = 'Analyzing...';
    
    try {
      // Fetch AI analysis from API
      const data = await fetchPortfolAIAnalysis(currentSymbol);
      
      // Display analysis in modal with formatted content
      showAnalysisModal(currentSymbol, data.analysis, data.fallback);
      
    } catch (error) {
      console.error('Error fetching analysis:', error);
      alert(`Error getting analysis: ${error.message}`);
    } finally {
      // Always restore button state regardless of success/failure
      portfolaiAnalysisBtn.disabled = false;
      portfolaiAnalysisBtn.textContent = 'PortfolAI Analysis';
    }
  });
}
