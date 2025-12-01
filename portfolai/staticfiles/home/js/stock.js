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

/** @type {number} Debounce delay for autocomplete search in milliseconds */
const AUTOCOMPLETE_DEBOUNCE_DELAY = 300;

/** @type {number|null} Reference to the debounce timeout */
let autocompleteTimeout = null;

/** @type {number} Currently selected index in autocomplete dropdown */
let selectedAutocompleteIndex = -1;

/** @type {string[]} List of common NYSE-listed stock symbols */
const NYSE_SYMBOLS = [
  'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'COF',         // Financials
  'XOM', 'CVX',                                    // Energy
  'KO', 'JNJ', 'PG', 'WMT', 'TGT', 'HD', 'LOW',   // Consumer
  'NKE', 'SBUX', 'MCD', 'DIS',                    // Retail/Food
  'V', 'MA', 'AXP', 'BRK.B',                      // Payments/Finance
  'GE', 'BA', 'CAT', 'DE',                        // Industrials
  'OKLO'                                           // Energy/Utilities
];

/** @type {string[]} List of NYSE Arca (AMEX) listed ETFs */
const NYSE_ARCA_ETFS = [
  'VOO', 'SPY', 'QQQ', 'VTI', 'IVV', 'IWM',      // Broad market ETFs
  'VEA', 'VWO', 'EFA', 'EEM',                     // International ETFs
  'BND', 'TLT', 'AGG',                            // Bond ETFs
  'GLD', 'SLV', 'USO',                            // Commodity ETFs
  'ARKK', 'ARKQ', 'ARKG',                         // ARK ETFs
  'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP',      // Sector ETFs
  'XLY', 'XLB', 'XLU', 'XME', 'XPH', 'XRT'       // More sector ETFs
];

// ============================================================================
// DOM Element References
// ============================================================================
// These are accessed via getter functions to ensure DOM is ready

function getSearchInput() {
  return document.getElementById('stock-search');
}

function getClearSearchButton() {
  return document.getElementById('clear-search-button');
}

function getStockDetailsDiv() {
  return document.getElementById('stock-details');
}

function getCompanyNameHeader() {
  return document.getElementById('company-name');
}

function getSearchErrorDiv() {
  return document.getElementById('search-error');
}

function getAddToWatchlistBtn() {
  return document.getElementById('addToWatchlistBtn');
}

function getPortfolaiAnalysisBtn() {
  return document.getElementById('portfolaiAnalysisBtn');
}

function getAutocompleteDropdown() {
  return document.getElementById('autocomplete-dropdown');
}

// ============================================================================
// Autocomplete Functions
// ============================================================================

/**
 * Fetch stock search suggestions from API
 * 
 * @async
 * @param {string} query - Search query (symbol or company name)
 * @returns {Promise<Array>} Array of stock suggestions
 */
async function fetchStockSuggestions(query) {
  if (!query || query.trim().length === 0) {
    return [];
  }
  
  try {
    const response = await fetch(`/api/stock-search/?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.results || [];
  } catch (error) {
    console.error('Error fetching stock suggestions:', error);
    return [];
  }
}

/**
 * Display autocomplete suggestions in dropdown
 * 
 * @param {Array} results - Array of stock objects from API
 */
function displayAutocompleteSuggestions(results) {
  const dropdown = getAutocompleteDropdown();
  if (!dropdown) return;
  
  // Reset selected index
  selectedAutocompleteIndex = -1;
  
  // Clear previous results
  dropdown.innerHTML = '';
  
  if (results.length === 0) {
    dropdown.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">No results found</div>';
    dropdown.classList.remove('hidden');
    return;
  }
  
  // Create result items
  results.forEach((stock, index) => {
    const item = document.createElement('div');
    item.className = 'px-4 py-3 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150';
    item.setAttribute('role', 'option');
    item.setAttribute('data-index', index);
    item.setAttribute('data-symbol', stock.symbol);
    
    // Format: Logo (if available) - Symbol (bold) - Description (gray) - Type
    const logoHtml = stock.logo 
      ? `<img src="${stock.logo}" alt="${stock.description || stock.symbol} logo" class="w-8 h-8 object-contain rounded mr-3 flex-shrink-0" onerror="this.style.display='none'">`
      : '';
    
    item.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center flex-1 min-w-0">
          ${logoHtml}
          <div class="min-w-0 flex-1">
            <span class="font-semibold text-gray-900 dark:text-gray-100">${stock.displaySymbol || stock.symbol}</span>
            <span class="text-sm text-gray-600 dark:text-gray-400 ml-2">${stock.description || ''}</span>
          </div>
        </div>
        <span class="text-xs text-gray-500 dark:text-gray-500 ml-2 flex-shrink-0">${stock.type || ''}</span>
      </div>
    `;
    
    // Click handler to select stock
    item.addEventListener('click', () => {
      selectAutocompleteItem(stock.symbol);
    });
    
    dropdown.appendChild(item);
  });
  
  dropdown.classList.remove('hidden');
}

/**
 * Hide autocomplete dropdown
 */
function hideAutocompleteDropdown() {
  const dropdown = getAutocompleteDropdown();
  if (dropdown) {
    dropdown.classList.add('hidden');
    dropdown.innerHTML = '';
  }
  selectedAutocompleteIndex = -1;
}

/**
 * Select an autocomplete item and trigger search
 * 
 * @param {string} symbol - Stock symbol to search for
 */
function selectAutocompleteItem(symbol) {
  const searchInput = getSearchInput();
  if (searchInput) {
    searchInput.value = symbol.toUpperCase();
  }
  hideAutocompleteDropdown();
  toggleClearButton();
  performSearch();
}

/**
 * Handle keyboard navigation in autocomplete dropdown
 * 
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleAutocompleteKeyboard(event) {
  const dropdown = getAutocompleteDropdown();
  if (!dropdown || dropdown.classList.contains('hidden')) {
    return;
  }
  
  const items = dropdown.querySelectorAll('[role="option"]');
  if (items.length === 0) return;
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      selectedAutocompleteIndex = Math.min(selectedAutocompleteIndex + 1, items.length - 1);
      updateAutocompleteSelection(items);
      break;
      
    case 'ArrowUp':
      event.preventDefault();
      selectedAutocompleteIndex = Math.max(selectedAutocompleteIndex - 1, 0);
      updateAutocompleteSelection(items);
      break;
      
    case 'Enter':
      event.preventDefault();
      if (selectedAutocompleteIndex >= 0 && selectedAutocompleteIndex < items.length) {
        const selectedItem = items[selectedAutocompleteIndex];
        const symbol = selectedItem.getAttribute('data-symbol');
        selectAutocompleteItem(symbol);
      }
      break;
      
    case 'Escape':
      event.preventDefault();
      hideAutocompleteDropdown();
      break;
  }
}

/**
 * Update visual selection in autocomplete dropdown
 * 
 * @param {NodeList} items - List of dropdown items
 */
function updateAutocompleteSelection(items) {
  items.forEach((item, index) => {
    if (index === selectedAutocompleteIndex) {
      item.classList.add('bg-gray-100', 'dark:bg-gray-700');
      item.scrollIntoView({ block: 'nearest' });
    } else {
      item.classList.remove('bg-gray-100', 'dark:bg-gray-700');
    }
  });
}

/**
 * Toggle visibility of clear button based on input content
 */
function toggleClearButton() {
  const searchInput = getSearchInput();
  const clearButton = getClearSearchButton();
  
  if (searchInput && clearButton) {
    if (searchInput.value.trim().length > 0) {
      clearButton.classList.remove('hidden');
    } else {
      clearButton.classList.add('hidden');
    }
  }
}

/**
 * Clear search input and reset UI
 */
function clearSearch() {
  const searchInput = getSearchInput();
  if (searchInput) {
    searchInput.value = '';
    searchInput.focus();
  }
  
  hideAutocompleteDropdown();
  toggleClearButton();
  
  // Reset UI elements
  displayStockDetails(null);
  clearTradingViewWidget();
  
  const addToWatchlistBtn = getAddToWatchlistBtn();
  const portfolaiAnalysisBtn = getPortfolaiAnalysisBtn();
  if (addToWatchlistBtn) addToWatchlistBtn.disabled = true;
  if (portfolaiAnalysisBtn) portfolaiAnalysisBtn.disabled = true;
}

/**
 * Handle search input changes with debouncing
 * 
 * @param {Event} event - Input event
 */
async function handleSearchInput(event) {
  const query = event.target.value.trim();
  
  // Toggle clear button visibility
  toggleClearButton();
  
  // Clear existing timeout
  if (autocompleteTimeout) {
    clearTimeout(autocompleteTimeout);
  }
  
  // Hide dropdown if query is empty
  if (!query || query.length === 0) {
    hideAutocompleteDropdown();
    return;
  }
  
  // Debounce the API call
  autocompleteTimeout = setTimeout(async () => {
    const results = await fetchStockSuggestions(query);
    displayAutocompleteSuggestions(results);
  }, AUTOCOMPLETE_DEBOUNCE_DELAY);
}

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
  console.log('performSearch called');
  const searchInput = getSearchInput();
  const searchErrorDiv = getSearchErrorDiv();
  const addToWatchlistBtn = getAddToWatchlistBtn();
  const portfolaiAnalysisBtn = getPortfolaiAnalysisBtn();
  
  if (!searchInput || !searchErrorDiv) {
    console.error('Required DOM elements not found for search', { searchInput, searchErrorDiv });
    return;
  }
  
  const searchTerm = searchInput.value.toUpperCase().trim();
  console.log('Search term:', searchTerm);
  searchErrorDiv.classList.add('hidden');
  
  // Update clear button visibility
  toggleClearButton();
  
  // Handle empty search - reset UI to default state
  if (!searchTerm) {
    displayStockDetails(null);
    clearTradingViewWidget();
    if (addToWatchlistBtn) addToWatchlistBtn.disabled = true;
    if (portfolaiAnalysisBtn) portfolaiAnalysisBtn.disabled = true;
    return;
  }

  try {
    // Show loading indicators
    const chartLoader = document.getElementById('chart-loader');
    if (chartLoader) chartLoader.classList.remove('hidden');
    if (addToWatchlistBtn) addToWatchlistBtn.disabled = true;
    if (portfolaiAnalysisBtn) portfolaiAnalysisBtn.disabled = true;

    // Fetch stock data from API - always force refresh for search to ensure accurate data
    console.log('Fetching stock data for:', searchTerm, '(force refresh)');
    const stockData = await fetchStockData(searchTerm, true); // Force refresh for search
    console.log('Stock data received:', stockData);

    // Display stock details in the sidebar
    displayStockDetails(stockData, searchTerm);
    
    // Show fallback notice if API is unavailable (using demo data)
    const stockDetailsDiv = getStockDetailsDiv();
    if (stockData.fallback && stockDetailsDiv) {
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
    
    // Update news feed with stock-specific news (limit to 3 articles)
    // Force refresh to get latest news for the searched stock
    if (typeof populateNewsFeed === 'function') {
      console.log('Updating news feed for symbol:', searchTerm, '(force refresh)');
      // Explicitly pass the symbol to force refresh and update news
      await populateNewsFeed(searchTerm);
    } else {
      console.warn('populateNewsFeed function not available');
    }
    
    // Fetch and display company overview
    try {
      const overviewData = await fetchCompanyOverview(searchTerm);
      displayCompanyOverview(overviewData, searchTerm);
    } catch (error) {
      console.error('Error fetching company overview:', error);
      // Hide overview section on error
      const overviewDiv = document.getElementById('company-overview');
      const viewOverviewBtn = document.getElementById('viewOverviewBtn');
      if (overviewDiv) overviewDiv.classList.add('hidden');
      if (viewOverviewBtn) viewOverviewBtn.classList.add('hidden');
    }
    
    // Safety timeout to ensure loader is hidden even if widget fails
    setTimeout(() => {
      const chartLoader = document.getElementById('chart-loader');
      if (chartLoader && !chartLoader.classList.contains('hidden')) {
        console.warn('Chart loader still visible after timeout, hiding it');
        chartLoader.classList.add('hidden');
      }
    }, 5000); // 5 second timeout

    // Update button states based on watchlist status
    if (addToWatchlistBtn) {
      addToWatchlistBtn.disabled = false;
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
    }
    if (portfolaiAnalysisBtn) {
      portfolaiAnalysisBtn.disabled = false;
    }

  } catch (error) {
    console.error('Error fetching stock data:', error);
    if (searchErrorDiv) {
      searchErrorDiv.classList.remove('hidden');
      searchErrorDiv.textContent = `Error: ${error.message}`;
    }
    
    // Reset UI on error - ensure loader is hidden
    const chartLoader = document.getElementById('chart-loader');
    if (chartLoader) chartLoader.classList.add('hidden');
    clearTradingViewWidget();
    if (addToWatchlistBtn) addToWatchlistBtn.disabled = true;
    if (portfolaiAnalysisBtn) portfolaiAnalysisBtn.disabled = true;
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
  const companyNameHeader = getCompanyNameHeader();
  const stockDetailsDiv = getStockDetailsDiv();
  
  if (!companyNameHeader || !stockDetailsDiv) {
    console.warn('DOM elements not found for displaying stock details');
    return;
  }
  
  if (stock) {
    // Display stock information (logo removed from card section)
    companyNameHeader.textContent = `${stock.name} (${symbol})`;
    
    // Determine color class based on price change direction
    const changeClass = stock.change >= 0
      ? 'text-green-500 dark:text-green-400'
      : 'text-red-500 dark:text-red-400';
    const changeSign = stock.change >= 0 ? '+' : '';
    
    // Format market cap (API returns in millions)
    // Convert to billions or trillions for display
    let marketCapDisplay = 'N/A';
    if (stock.marketCap && stock.marketCap > 0) {
      const marketCapInBillions = stock.marketCap / 1000;
      if (marketCapInBillions >= 1000) {
        // Display in trillions for large caps
        marketCapDisplay = `$${(marketCapInBillions / 1000).toFixed(2)}T`;
      } else if (marketCapInBillions >= 1) {
        // Display in billions
        marketCapDisplay = `$${marketCapInBillions.toFixed(2)}B`;
      } else {
        // Display in millions for small caps
        marketCapDisplay = `$${stock.marketCap.toFixed(2)}M`;
      }
    }
    
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
          <p><strong>Mkt Cap:</strong> ${marketCapDisplay}</p>
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
  
  // Hide company overview section when stock details are cleared
  const overviewDiv = document.getElementById('company-overview');
  const viewOverviewBtn = document.getElementById('viewOverviewBtn');
  if (overviewDiv) overviewDiv.classList.add('hidden');
  if (viewOverviewBtn) viewOverviewBtn.classList.add('hidden');
}

/**
 * Format large numbers to billions/trillions
 * @param {number|null} value - Number to format
 * @returns {string} Formatted string
 */
function formatLargeNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  if (value >= 1_000_000_000_000) {
    return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  } else if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  } else if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }
  return `$${value.toFixed(2)}`;
}

/**
 * Format percentage values
 * @param {number|null} value - Percentage value (0-1 or 0-100)
 * @param {boolean} isDecimal - Whether value is already a decimal (0-1)
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, isDecimal = false) {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  const percent = isDecimal ? value * 100 : value;
  return `${percent.toFixed(2)}%`;
}

/**
 * Format number with 2 decimal places
 * @param {number|null} value - Number to format
 * @returns {string} Formatted string
 */
function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  return value.toFixed(2);
}

/**
 * Display company overview in the UI
 * @param {Object} overview - Company overview data object
 * @param {string} symbol - Stock symbol
 */
function displayCompanyOverview(overview, symbol) {
  const overviewDiv = document.getElementById('company-overview');
  const viewOverviewBtn = document.getElementById('viewOverviewBtn');
  
  if (!overviewDiv) {
    console.warn('Company overview div not found');
    return;
  }
  
  if (!overview || overview.error) {
    overviewDiv.innerHTML = '<p class="text-sm text-red-500 dark:text-red-400">Unable to load company overview.</p>';
    if (viewOverviewBtn) viewOverviewBtn.classList.add('hidden');
    return;
  }
  
  // Build HTML for company overview
  let html = '';
  
  // Company Description (expandable)
  if (overview.description) {
    const shortDesc = overview.description.substring(0, 200);
    const isLong = overview.description.length > 200;
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">About</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          <span id="desc-short">${shortDesc}${isLong ? '...' : ''}</span>
          ${isLong ? `<span id="desc-full" class="hidden">${overview.description}</span>` : ''}
        </p>
        ${isLong ? `<button onclick="this.previousElementSibling.querySelector('#desc-short').classList.toggle('hidden'); this.previousElementSibling.querySelector('#desc-full').classList.toggle('hidden'); this.textContent = this.textContent === 'Show More' ? 'Show Less' : 'Show More';" class="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm mt-1">Show More</button>` : ''}
      </div>
    `;
  }
  
  // Key Information
  html += `
    <div class="mb-4">
      <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Key Information</h3>
      <div class="grid grid-cols-2 gap-2 text-sm">
        ${overview.sector ? `<p><strong>Sector:</strong> ${overview.sector}</p>` : ''}
        ${overview.industry ? `<p><strong>Industry:</strong> ${overview.industry}</p>` : ''}
        ${overview.exchange ? `<p><strong>Exchange:</strong> ${overview.exchange}</p>` : ''}
        ${overview.country ? `<p><strong>Country:</strong> ${overview.country}</p>` : ''}
        ${overview.currency ? `<p><strong>Currency:</strong> ${overview.currency}</p>` : ''}
        ${overview.fiscalYearEnd ? `<p><strong>Fiscal Year End:</strong> ${overview.fiscalYearEnd}</p>` : ''}
      </div>
    </div>
  `;
  
  // Financial Metrics
  if (overview.financials) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Financial Metrics</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.financials.marketCap !== null ? `<p><strong>Market Cap:</strong> ${formatLargeNumber(overview.financials.marketCap)}</p>` : ''}
          ${overview.financials.ebitda !== null ? `<p><strong>EBITDA:</strong> ${formatLargeNumber(overview.financials.ebitda)}</p>` : ''}
          ${overview.financials.revenueTTM !== null ? `<p><strong>Revenue (TTM):</strong> ${formatLargeNumber(overview.financials.revenueTTM)}</p>` : ''}
          ${overview.financials.grossProfitTTM !== null ? `<p><strong>Gross Profit (TTM):</strong> ${formatLargeNumber(overview.financials.grossProfitTTM)}</p>` : ''}
          ${overview.financials.bookValue !== null ? `<p><strong>Book Value:</strong> $${formatNumber(overview.financials.bookValue)}</p>` : ''}
          ${overview.financials.eps !== null ? `<p><strong>EPS:</strong> $${formatNumber(overview.financials.eps)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Valuation Ratios
  if (overview.valuation) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Valuation</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.valuation.peRatio !== null ? `<p><strong>P/E Ratio:</strong> ${formatNumber(overview.valuation.peRatio)}</p>` : ''}
          ${overview.valuation.pegRatio !== null ? `<p><strong>PEG Ratio:</strong> ${formatNumber(overview.valuation.pegRatio)}</p>` : ''}
          ${overview.valuation.priceToBook !== null ? `<p><strong>Price/Book:</strong> ${formatNumber(overview.valuation.priceToBook)}</p>` : ''}
          ${overview.valuation.priceToSales !== null ? `<p><strong>Price/Sales:</strong> ${formatNumber(overview.valuation.priceToSales)}</p>` : ''}
          ${overview.valuation.evToRevenue !== null ? `<p><strong>EV/Revenue:</strong> ${formatNumber(overview.valuation.evToRevenue)}</p>` : ''}
          ${overview.valuation.evToEbitda !== null ? `<p><strong>EV/EBITDA:</strong> ${formatNumber(overview.valuation.evToEbitda)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Profitability
  if (overview.profitability) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Profitability</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.profitability.profitMargin !== null ? `<p><strong>Profit Margin:</strong> ${formatPercentage(overview.profitability.profitMargin, true)}</p>` : ''}
          ${overview.profitability.operatingMargin !== null ? `<p><strong>Operating Margin:</strong> ${formatPercentage(overview.profitability.operatingMargin, true)}</p>` : ''}
          ${overview.profitability.returnOnAssets !== null ? `<p><strong>ROA:</strong> ${formatPercentage(overview.profitability.returnOnAssets, true)}</p>` : ''}
          ${overview.profitability.returnOnEquity !== null ? `<p><strong>ROE:</strong> ${formatPercentage(overview.profitability.returnOnEquity, true)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Growth
  if (overview.growth) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Growth</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.growth.earningsGrowthYOY !== null ? `<p><strong>Earnings Growth (YoY):</strong> ${formatPercentage(overview.growth.earningsGrowthYOY, true)}</p>` : ''}
          ${overview.growth.revenueGrowthYOY !== null ? `<p><strong>Revenue Growth (YoY):</strong> ${formatPercentage(overview.growth.revenueGrowthYOY, true)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Analyst Ratings
  if (overview.analyst) {
    const ratings = overview.analyst.ratings;
    const totalRatings = ratings.strongBuy + ratings.buy + ratings.hold + ratings.sell + ratings.strongSell;
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Analyst Ratings</h3>
        ${overview.analyst.targetPrice !== null ? `<p class="text-sm mb-2"><strong>Target Price:</strong> $${formatNumber(overview.analyst.targetPrice)}</p>` : ''}
        ${totalRatings > 0 ? `
          <div class="space-y-1 text-sm">
            <div class="flex justify-between"><span>Strong Buy:</span><span class="text-green-600 dark:text-green-400">${ratings.strongBuy}</span></div>
            <div class="flex justify-between"><span>Buy:</span><span class="text-green-500 dark:text-green-400">${ratings.buy}</span></div>
            <div class="flex justify-between"><span>Hold:</span><span class="text-yellow-500 dark:text-yellow-400">${ratings.hold}</span></div>
            <div class="flex justify-between"><span>Sell:</span><span class="text-red-500 dark:text-red-400">${ratings.sell}</span></div>
            <div class="flex justify-between"><span>Strong Sell:</span><span class="text-red-600 dark:text-red-400">${ratings.strongSell}</span></div>
            <div class="flex justify-between mt-2 pt-2 border-t border-gray-300 dark:border-gray-600"><span><strong>Total:</strong></span><span><strong>${totalRatings}</strong></span></div>
          </div>
        ` : '<p class="text-sm text-gray-500 dark:text-gray-400">No analyst ratings available</p>'}
      </div>
    `;
  }
  
  // Technical Indicators
  if (overview.technical) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Technical Indicators</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.technical['52WeekHigh'] !== null && overview.technical['52WeekHigh'] !== undefined ? `<p><strong>52W High:</strong> $${formatNumber(overview.technical['52WeekHigh'])}</p>` : ''}
          ${overview.technical['52WeekLow'] !== null && overview.technical['52WeekLow'] !== undefined ? `<p><strong>52W Low:</strong> $${formatNumber(overview.technical['52WeekLow'])}</p>` : ''}
          ${overview.technical['50DayMA'] !== null ? `<p><strong>50-Day MA:</strong> $${formatNumber(overview.technical['50DayMA'])}</p>` : ''}
          ${overview.technical['200DayMA'] !== null ? `<p><strong>200-Day MA:</strong> $${formatNumber(overview.technical['200DayMA'])}</p>` : ''}
          ${overview.technical.beta !== null ? `<p><strong>Beta:</strong> ${formatNumber(overview.technical.beta)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Shares & Ownership
  if (overview.shares) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Shares & Ownership</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.shares.outstanding !== null ? `<p><strong>Outstanding:</strong> ${(overview.shares.outstanding / 1_000_000).toFixed(2)}M</p>` : ''}
          ${overview.shares.float !== null ? `<p><strong>Float:</strong> ${(overview.shares.float / 1_000_000).toFixed(2)}M</p>` : ''}
          ${overview.shares.percentInsiders !== null ? `<p><strong>Insider %:</strong> ${formatPercentage(overview.shares.percentInsiders)}</p>` : ''}
          ${overview.shares.percentInstitutions !== null ? `<p><strong>Institution %:</strong> ${formatPercentage(overview.shares.percentInstitutions)}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  // Dividend Information
  if (overview.dividend) {
    html += `
      <div class="mb-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Dividend</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          ${overview.dividend.perShare !== null ? `<p><strong>Dividend/Share:</strong> $${formatNumber(overview.dividend.perShare)}</p>` : ''}
          ${overview.dividend.yield !== null ? `<p><strong>Yield:</strong> ${formatPercentage(overview.dividend.yield, true)}</p>` : ''}
          ${overview.dividend.date ? `<p><strong>Dividend Date:</strong> ${overview.dividend.date}</p>` : ''}
          ${overview.dividend.exDate ? `<p><strong>Ex-Dividend Date:</strong> ${overview.dividend.exDate}</p>` : ''}
        </div>
      </div>
    `;
  }
  
  overviewDiv.innerHTML = html;
  // Keep overview hidden by default - user clicks button to show it
  overviewDiv.classList.add('hidden');
  
  // Show the button to toggle overview
  if (viewOverviewBtn) {
    viewOverviewBtn.classList.remove('hidden');
    viewOverviewBtn.textContent = 'View Full Overview';
  }
}

/**
 * Initialize company overview button functionality
 * 
 * Sets up the view overview button to toggle company overview display
 * 
 * @function initializeCompanyOverview
 */
function initializeCompanyOverview() {
  const viewOverviewBtn = document.getElementById('viewOverviewBtn');
  if (!viewOverviewBtn) {
    console.warn('View overview button not found');
    return;
  }
  
  viewOverviewBtn.addEventListener('click', () => {
    const overviewDiv = document.getElementById('company-overview');
    if (!overviewDiv) {
      console.warn('Company overview div not found');
      return;
    }
    
    if (overviewDiv.classList.contains('hidden')) {
      overviewDiv.classList.remove('hidden');
      viewOverviewBtn.textContent = 'Hide Overview';
    } else {
      overviewDiv.classList.add('hidden');
      viewOverviewBtn.textContent = 'View Full Overview';
    }
  });
}

// ============================================================================
// TradingView Widget Helper Functions
// ============================================================================

/**
 * Detect the stock exchange for a given symbol
 * 
 * Determines the most likely exchange (NASDAQ, NYSE, or AMEX/NYSE Arca) based on known symbols.
 * Supports both stocks and ETFs. TradingView supports auto-detection if the 
 * exchange is incorrect, but specifying the correct exchange improves widget 
 * initialization speed.
 * 
 * Note: NYSE Arca (where many ETFs like VOO trade) is represented as "AMEX" in TradingView.
 * 
 * @param {string} symbol - Stock or ETF symbol to detect exchange for
 * @returns {string} Exchange identifier ('NYSE', 'AMEX', or 'NASDAQ')
 */
function detectExchange(symbol) {
  if (!symbol || symbol.length === 0) {
    return 'NASDAQ';
  }
  
  const upperSymbol = symbol.toUpperCase();
  
  // Check NYSE Arca ETFs first (many ETFs trade on NYSE Arca, represented as AMEX in TradingView)
  if (NYSE_ARCA_ETFS.includes(upperSymbol)) {
    return 'AMEX';
  }
  
  // Check NYSE stocks
  if (NYSE_SYMBOLS.includes(upperSymbol)) {
    return 'NYSE';
  }
  
  // Default to NASDAQ
  return 'NASDAQ';
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
 * @param {string} symbol - Stock or ETF symbol to display
 * @param {string} exchange - Exchange identifier (e.g., 'NASDAQ', 'NYSE', 'AMEX')
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
    
    // Exchanges to search across
    // Includes: NASDAQ, NASDAQ GIDS, NYSE, NYSE Arca, Cboe CFE, OTC Markets
    exchanges: [
      'NASDAQ',      // NASDAQ Stock Market (Cboe One - Delayed Stocks)
      'NYSE',        // New York Stock Exchange (Cboe One - Delayed Stocks)
      'AMEX',        // NYSE Arca (Cboe One - Delayed Stocks) - TradingView uses AMEX for Arca
      'OTC',         // OTC Markets (OTC - Delayed Stocks)
      'CBOE'         // Cboe Futures Exchange (CBOE - Delayed Futures)
    ],
    
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
function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

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
  const safeSymbol = escapeHTML(symbol);
  const safeExchange = escapeHTML(exchange);
  copyrightDiv.innerHTML = `<a href="https://www.tradingview.com/symbols/${safeExchange}-${safeSymbol}/" rel="noopener nofollow" target="_blank"><span class="blue-text">${safeSymbol}</span></a><span class="trademark"> by TradingView</span>`;
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
 * - US Exchanges: NASDAQ, NYSE, AMEX (NYSE Arca/American)
 * - International: LSE (London), TSE (Tokyo), SSE (Shanghai), ASX, TSX, etc.
 * - Auto-detection: TradingView can find symbols across exchanges if specified incorrectly
 * - Note: NYSE Arca ETFs (like VOO, SPY) use "AMEX" as the exchange identifier
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
  const searchInput = getSearchInput();
  if (!searchInput) return;
  
  const currentSymbol = searchInput.value.toUpperCase().trim();
  if (currentSymbol && tradingViewWidget) {
    renderTradingViewWidget(currentSymbol);
  }
}

/**
 * Initialize stock search functionality
 * 
 * Sets up event listeners for:
 * - Clear button click
 * - Enter key press in search input
 * - Autocomplete input changes
 * - Keyboard navigation in autocomplete
 * - Click outside to close dropdown
 * - Theme changes (to update chart theme)
 * 
 * @function initializeStockSearch
 */
function initializeStockSearch() {
  const searchInput = getSearchInput();
  const clearButton = getClearSearchButton();
  
  if (!searchInput) {
    console.error('Search input not found during initialization');
    return;
  }
  
  // Clear button click handler
  if (clearButton) {
    clearButton.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      clearSearch();
    });
  }
  
  // Input change handler for autocomplete
  searchInput.addEventListener('input', handleSearchInput);
  
  // Keyboard handler for search input
  searchInput.addEventListener('keydown', (e) => {
    const dropdown = getAutocompleteDropdown();
    const isDropdownVisible = dropdown && !dropdown.classList.contains('hidden');
    
    if (isDropdownVisible) {
      // Handle autocomplete keyboard navigation
      handleAutocompleteKeyboard(e);
    } else if (e.key === 'Enter') {
      // Perform search when Enter is pressed and dropdown is hidden
      hideAutocompleteDropdown();
      performSearch();
    }
  });
  
  // Click outside handler to close autocomplete dropdown
  document.addEventListener('click', (e) => {
    const dropdown = getAutocompleteDropdown();
    const clearBtn = getClearSearchButton();
    if (!dropdown) return;
    
    // Check if click is outside search input and dropdown (but not the clear button)
    const isClickInsideSearch = searchInput.contains(e.target);
    const isClickInsideDropdown = dropdown.contains(e.target);
    const isClickOnClearButton = clearBtn && clearBtn.contains(e.target);
    
    if (!isClickInsideSearch && !isClickInsideDropdown && !isClickOnClearButton) {
      hideAutocompleteDropdown();
    }
  });
  
  // Scroll handler to close autocomplete dropdown
  // Prevents dropdown from appearing in wrong position when scrolling
  window.addEventListener('scroll', () => {
    const dropdown = getAutocompleteDropdown();
    if (dropdown && !dropdown.classList.contains('hidden')) {
      hideAutocompleteDropdown();
    }
  }, { passive: true });
  
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
  const portfolaiAnalysisBtn = getPortfolaiAnalysisBtn();
  if (!portfolaiAnalysisBtn) {
    console.error('PortfolAI analysis button not found');
    return;
  }
  
  portfolaiAnalysisBtn.addEventListener('click', async () => {
    const searchInput = getSearchInput();
    if (!searchInput) {
      alert('Search input not found');
      return;
    }
    
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
