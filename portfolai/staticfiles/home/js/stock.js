/**
 * Stock Search & Chart Management
 * Handles stock search, data display, and chart rendering
 */

// Global chart instance for theme switching
let chartInstance = null;

// DOM references
const searchInput = document.getElementById('stock-search');
const searchButton = document.getElementById('search-button');
const stockDetailsDiv = document.getElementById('stock-details');
const companyNameHeader = document.getElementById('company-name');
const searchErrorDiv = document.getElementById('search-error');
const addToWatchlistBtn = document.getElementById('addToWatchlistBtn');
const portfolaiAnalysisBtn = document.getElementById('portfolaiAnalysisBtn');

/**
 * Perform stock search and update UI
 */
async function performSearch() {
  const searchTerm = searchInput.value.toUpperCase().trim();
  searchErrorDiv.classList.add('hidden');
  
  if (!searchTerm) {
    displayStockDetails(null);
    if (chartInstance) {
      chartInstance.remove();
      chartInstance = null;
      document.getElementById('chart-loader').classList.remove('hidden');
    }
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;
    return;
  }

  try {
    // Show loading state
    document.getElementById('chart-loader').classList.remove('hidden');
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;

    // Fetch stock data from API
    const stockData = await fetchStockData(searchTerm);

    // Display stock details
    displayStockDetails(stockData, searchTerm);
    
    // Show fallback notice if using fallback data
    if (stockData.fallback) {
      const fallbackNotice = document.createElement('div');
      fallbackNotice.className = 'bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-700 dark:text-yellow-300 px-4 py-3 rounded mb-4';
      fallbackNotice.innerHTML = '⚠️ Using demo data - API not configured or unavailable';
      stockDetailsDiv.parentNode.insertBefore(fallbackNotice, stockDetailsDiv);
      
      // Remove notice after 5 seconds
      setTimeout(() => {
        if (fallbackNotice.parentNode) {
          fallbackNotice.parentNode.removeChild(fallbackNotice);
        }
      }, 5000);
    }

    // Render chart with generated data
    renderChart(
      generateStockData(100),
      localStorage.getItem('color-theme') || 'light',
      searchTerm
    );

    // Enable buttons
    addToWatchlistBtn.disabled = false;
    portfolaiAnalysisBtn.disabled = false;
    addToWatchlistBtn.textContent = isStockInWatchlist(searchTerm)
      ? 'Remove from Watchlist'
      : 'Add to Watchlist';
    addToWatchlistBtn.classList.toggle(
      'bg-red-500',
      isStockInWatchlist(searchTerm)
    );
    addToWatchlistBtn.classList.toggle(
      'hover:bg-red-600',
      isStockInWatchlist(searchTerm)
    );
    addToWatchlistBtn.classList.toggle(
      'bg-green-500',
      !isStockInWatchlist(searchTerm)
    );
    addToWatchlistBtn.classList.toggle(
      'hover:bg-green-600',
      !isStockInWatchlist(searchTerm)
    );

  } catch (error) {
    console.error('Error fetching stock data:', error);
    searchErrorDiv.classList.remove('hidden');
    searchErrorDiv.textContent = `Error: ${error.message}`;
    
    if (chartInstance) {
      chartInstance.remove();
      chartInstance = null;
      document.getElementById('chart-loader').classList.remove('hidden');
    }
    addToWatchlistBtn.disabled = true;
    portfolaiAnalysisBtn.disabled = true;
  }
}

/**
 * Display stock details in the UI
 * @param {Object} stock - Stock data object
 * @param {string} symbol - Stock symbol
 */
function displayStockDetails(stock, symbol = 'N/A') {
  if (stock) {
    companyNameHeader.textContent = `${stock.name} (${symbol})`;
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
    companyNameHeader.textContent = 'Company Overview';
    stockDetailsDiv.innerHTML = `<p class="text-sm text-gray-600 dark:text-gray-400">Search for a stock to see details.</p>`;
  }
}

/**
 * Generate mock stock data for charting
 * @param {number} count - Number of data points to generate
 * @returns {Array} Array of candlestick data objects
 */
function generateStockData(count) {
  const data = [];
  let lastClose = 50 + Math.random() * 150;
  let time = new Date();
  time.setDate(time.getDate() - count);

  for (let i = 0; i < count; i++) {
    time.setDate(time.getDate() + 1);
    const open = lastClose + (Math.random() - 0.5) * 5;
    const high = Math.max(open, lastClose) + Math.random() * 5;
    const low = Math.min(open, lastClose) - Math.random() * 5;
    const close = low + Math.random() * (high - low);
    lastClose = close;

    data.push({
      time: time.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
    });
  }
  return data;
}

/**
 * Render or update the stock chart
 * @param {Array} data - Chart data array
 * @param {string} theme - Current theme ('light' or 'dark')
 * @param {string} symbol - Stock symbol for watermark
 */
function renderChart(data, theme, symbol) {
  const chartContainer = document.getElementById('chart-container');
  const chartLoader = document.getElementById('chart-loader');

  if (chartInstance) {
    chartInstance.remove();
  }

  chartInstance = LightweightCharts.createChart(chartContainer, {
    width: chartContainer.clientWidth,
    height: chartContainer.clientHeight,
    layout: {
      backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
      textColor: theme === 'dark' ? '#d1d5db' : '#111827',
    },
    grid: {
      vertLines: { color: theme === 'dark' ? '#374151' : '#e5e7eb' },
      horzLines: { color: theme === 'dark' ? '#374151' : '#e5e7eb' },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    priceScale: {
      borderColor: theme === 'dark' ? '#4b5563' : '#cccccc',
    },
    timeScale: {
      borderColor: theme === 'dark' ? '#4b5563' : '#cccccc',
      timeVisible: true,
      secondsVisible: false,
    },
    watermark: {
      color:
        theme === 'dark' ? 'rgba(209, 213, 219, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      visible: true,
      text: symbol,
      fontSize: 48,
      horzAlign: 'center',
      vertAlign: 'center',
    },
  });

  const candleSeries = chartInstance.addCandlestickSeries({
    upColor: theme === 'dark' ? '#10b981' : '#22c55e',
    downColor: theme === 'dark' ? '#ef4444' : '#dc2626',
    borderDownColor: theme === 'dark' ? '#ef4444' : '#dc2626',
    borderUpColor: theme === 'dark' ? '#10b981' : '#22c55e',
    wickDownColor: theme === 'dark' ? '#ef4444' : '#dc2626',
    wickUpColor: theme === 'dark' ? '#10b981' : '#22c55e',
  });

  candleSeries.setData(data);
  chartInstance.timeScale().fitContent();
  chartLoader.classList.add('hidden');

  window.addEventListener('resize', () => {
    if (
      chartInstance &&
      chartContainer.clientWidth > 0 &&
      chartContainer.clientHeight > 0
    ) {
      chartInstance.resize(
        chartContainer.clientWidth,
        chartContainer.clientHeight
      );
    }
  });
}

/**
 * Initialize stock search functionality
 */
function initializeStockSearch() {
  searchButton.addEventListener('click', performSearch);
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  });
}

/**
 * Initialize PortfolAI analysis functionality
 */
function initializePortfolAIAnalysis() {
  portfolaiAnalysisBtn.addEventListener('click', async () => {
    const currentSymbol = searchInput.value.toUpperCase();
    
    if (!currentSymbol) {
      alert('Please search for a stock first');
      return;
    }
    
    // Disable button and show loading
    portfolaiAnalysisBtn.disabled = true;
    portfolaiAnalysisBtn.textContent = 'Analyzing...';
    
    try {
      const data = await fetchPortfolAIAnalysis(currentSymbol);
      
      // Display the analysis in a modal
      showAnalysisModal(currentSymbol, data.analysis, data.fallback);
      
    } catch (error) {
      console.error('Error fetching analysis:', error);
      alert(`Error getting analysis: ${error.message}`);
    } finally {
      // Re-enable button
      portfolaiAnalysisBtn.disabled = false;
      portfolaiAnalysisBtn.textContent = 'PortfolAI Analysis';
    }
  });
}
