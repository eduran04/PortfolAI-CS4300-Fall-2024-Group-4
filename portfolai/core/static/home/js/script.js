const themeToggleBtn = document.getElementById('theme-toggle');
const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
let chartInstance = null;

// CSRF token handling
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

if (
  localStorage.getItem('color-theme') === 'dark' ||
  (!('color-theme' in localStorage) &&
    window.matchMedia('(prefers-color-scheme: dark)').matches)
) {
  document.documentElement.classList.add('dark');
  themeToggleLightIcon.classList.remove('hidden');
} else {
  document.documentElement.classList.remove('dark');
  themeToggleDarkIcon.classList.remove('hidden');
}

themeToggleBtn.addEventListener('click', function () {
  themeToggleDarkIcon.classList.toggle('hidden');
  themeToggleLightIcon.classList.toggle('hidden');
  document.documentElement.classList.toggle('dark');
  const currentTheme = document.documentElement.classList.contains('dark')
    ? 'dark'
    : 'light';
  localStorage.setItem('color-theme', currentTheme);
  if (chartInstance) {
    const symbol =
      document.getElementById('stock-search').value.toUpperCase() || 'AAPL';
    renderChart(generateStockData(100), currentTheme, symbol);
  }
});

const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
mobileMenuButton.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
  const isExpanded =
    mobileMenuButton.getAttribute('aria-expanded') === 'true' || false;
  mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
  mobileMenuButton
    .querySelectorAll('svg')
    .forEach((icon) => icon.classList.toggle('hidden'));
});

const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const priceAlertModal = document.getElementById('priceAlertModal');

const loginBtnNav = document.getElementById('loginBtnNav');
const loginBtnMobile = document.getElementById('loginBtnMobile');
const closeLoginModalBtn = document.getElementById('closeLoginModal');
const switchToRegisterBtn = document.getElementById('switchToRegister');

const closeRegisterModalBtn = document.getElementById('closeRegisterModal');
const switchToLoginBtn = document.getElementById('switchToLogin');

const portfolaiAnalysisBtn = document.getElementById('portfolaiAnalysisBtn');
const closePriceAlertModalBtn = document.getElementById('closePriceAlertModal');

function openModal(modal) {
  modal.classList.add('active');
  setTimeout(() => {
    modal
      .querySelector('div[class*="bg-white"]')
      .classList.remove('scale-95', 'opacity-0');
    modal
      .querySelector('div[class*="bg-white"]')
      .classList.add('scale-100', 'opacity-100');
  }, 10);
  document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
  modal
    .querySelector('div[class*="bg-white"]')
    .classList.remove('scale-100', 'opacity-100');
  modal
    .querySelector('div[class*="bg-white"]')
    .classList.add('scale-95', 'opacity-0');
  setTimeout(() => {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }, 300);
}

function showAnalysisModal(symbol, analysis, isFallback) {
  // Create modal if it doesn't exist
  let analysisModal = document.getElementById('analysisModal');
  if (!analysisModal) {
    analysisModal = document.createElement('div');
    analysisModal.id = 'analysisModal';
    analysisModal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300 ease-in-out';
    analysisModal.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-5xl w-full mx-4 max-h-[85vh] overflow-hidden transform transition-all duration-300 ease-in-out scale-95 opacity-0">
        <div class="bg-gradient-to-r from-purple-900 to-indigo-900 text-white p-6">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h2 class="text-2xl font-bold">PortfolAI Analysis</h2>
                <p class="text-purple-200 text-sm">AI-Powered Stock Analysis for <span id="analysisSymbol" class="font-semibold">${symbol}</span></p>
              </div>
            </div>
            <button id="closeAnalysisModal" class="text-white hover:text-purple-200 transition-colors duration-200 p-2 rounded-lg hover:bg-white hover:bg-opacity-10">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div class="p-6 overflow-y-auto max-h-[65vh]">
          <div id="analysisContent" class="text-gray-700 dark:text-gray-300 prose prose-lg max-w-none"></div>
          ${isFallback ? '<div class="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 border-l-4 border-yellow-400 rounded-r-lg"><div class="flex items-center"><svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg><span class="text-yellow-800 dark:text-yellow-200 font-medium">Demo Analysis</span></div><p class="text-yellow-700 dark:text-yellow-300 text-sm mt-1">OpenAI API not configured - showing sample analysis for demonstration purposes.</p></div>' : ''}
        </div>
      </div>
    `;
    document.body.appendChild(analysisModal);
    
    // Add close button event listener
    document.getElementById('closeAnalysisModal').addEventListener('click', () => {
      closeAnalysisModal();
    });
    
    // Close modal when clicking outside
    analysisModal.addEventListener('click', (e) => {
      if (e.target === analysisModal) {
        closeAnalysisModal();
      }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && analysisModal.classList.contains('active')) {
        closeAnalysisModal();
      }
    });
  }
  
  // Update content
  document.getElementById('analysisSymbol').textContent = symbol;
  const analysisContent = document.getElementById('analysisContent');
  analysisContent.innerHTML = formatAnalysisContent(analysis);
  
  // Show modal with animation
  analysisModal.classList.add('active');
  setTimeout(() => {
    const modalContent = analysisModal.querySelector('div[class*="bg-white"]');
    modalContent.classList.remove('scale-95', 'opacity-0');
    modalContent.classList.add('scale-100', 'opacity-100');
  }, 10);
  document.body.style.overflow = 'hidden';
}

function closeAnalysisModal() {
  const analysisModal = document.getElementById('analysisModal');
  if (analysisModal) {
    const modalContent = analysisModal.querySelector('div[class*="bg-white"]');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
      analysisModal.classList.remove('active');
      document.body.style.overflow = 'auto';
    }, 300);
  }
}

function formatAnalysisContent(analysis) {
  // Convert markdown-style formatting to HTML with more robust patterns
  let formatted = analysis
    // Bold text (**text** or __text__) - more flexible matching
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/__([^_]+)__/g, '<strong>$1</strong>')
    // Italic text (*text* or _text_) - more flexible matching
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    // Headers (#### Header, ### Header, ## Header)
    .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    // Bullet points (- item or • item)
    .replace(/^[-•] (.*$)/gm, '<li>$1</li>')
    // Numbered lists (1. item, 2. item, etc.)
    .replace(/^(\d+)\. (.*$)/gm, '<li>$1. $2</li>')
    // Line breaks - handle multiple newlines
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br>');
  
  // Wrap in paragraphs
  formatted = '<p>' + formatted + '</p>';
  
  // Convert list items to proper lists
  formatted = formatted.replace(/(<li>.*<\/li>)/g, (match) => {
    return '<ul>' + match + '</ul>';
  });
  
  // Clean up duplicate list wrappers
  formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
  
  // Clean up empty paragraphs
  formatted = formatted.replace(/<p><\/p>/g, '');
  formatted = formatted.replace(/<p><br><\/p>/g, '');
  
  return formatted;
}

[loginBtnNav, loginBtnMobile].forEach((btn) =>
  btn.addEventListener('click', () => openModal(loginModal))
);
closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
switchToRegisterBtn.addEventListener('click', (e) => {
  e.preventDefault();
  closeModal(loginModal);
  openModal(registerModal);
});

closeRegisterModalBtn.addEventListener('click', () =>
  closeModal(registerModal)
);
switchToLoginBtn.addEventListener('click', (e) => {
  e.preventDefault();
  closeModal(registerModal);
  openModal(loginModal);
});

portfolaiAnalysisBtn.addEventListener('click', async () => {
  const currentSymbol = document.getElementById('stock-search').value.toUpperCase();
  
  if (!currentSymbol) {
    alert('Please search for a stock first');
    return;
  }
  
  // Disable button and show loading
  portfolaiAnalysisBtn.disabled = true;
  portfolaiAnalysisBtn.textContent = 'Analyzing...';
  
  try {
    const response = await fetch(`/api/portfolai-analysis/?symbol=${currentSymbol}`, {
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
closePriceAlertModalBtn.addEventListener('click', () =>
  closeModal(priceAlertModal)
);

// Dummy data removed - now using real API data

const tickerMove = document.querySelector('.ticker-move');
let tickerData = [];

async function populateTicker() {
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

    // Combine gainers and losers for ticker
    tickerData = [...data.gainers, ...data.losers];
    
    let tickerHTML = '';
    // Display each stock twice for continuous scrolling
    for (let i = 0; i < 2; i++) {
      tickerData.forEach((stock) => {
        const changeClass = stock.change >= 0
          ? 'text-green-400'
          : 'text-red-400';
        const changeSign = stock.change >= 0 ? '+' : '';
        
        tickerHTML += `
        <div class="ticker-item inline-flex items-center">
            <span class="font-semibold">${stock.symbol}</span>
            <span class="ml-2 text-sm">$${stock.price.toFixed(2)}</span>
            <span class="ml-1 text-xs ${changeClass}">${changeSign}${stock.change.toFixed(2)} (${changeSign}${stock.changePercent.toFixed(2)}%)</span>
        </div>
    `;
      });
    }
    tickerMove.innerHTML = tickerHTML;

  } catch (error) {
    console.error('Error fetching ticker data:', error);
    tickerMove.innerHTML = '<div class="ticker-item text-gray-400">Loading market data...</div>';
  }
}

populateTicker();
// Update ticker every 30 seconds
setInterval(populateTicker, 30000);

const searchInput = document.getElementById('stock-search');
const searchButton = document.getElementById('search-button');
const stockDetailsDiv = document.getElementById('stock-details');
const companyNameHeader = document.getElementById('company-name');
const searchErrorDiv = document.getElementById('search-error');
const addToWatchlistBtn = document.getElementById('addToWatchlistBtn');

searchButton.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    performSearch();
  }
});

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
    const response = await fetch(`/api/stock-data/?symbol=${searchTerm}`, {
      method: 'GET',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const stockData = await response.json();
    
    if (stockData.error) {
      throw new Error(stockData.error);
    }

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

renderChart(
  generateStockData(100),
  localStorage.getItem('color-theme') || 'light',
  'AAPL'
);

const topGainersList = document.getElementById('top-gainers-list');
const topLosersList = document.getElementById('top-losers-list');

async function populateMarketMovers() {
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

    const { gainers, losers } = data;

    // Display gainers
    topGainersList.innerHTML = gainers.length
      ? gainers
          .map(
            (stock) => `
                  <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="searchInput.value='${
                    stock.symbol
                  }'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
                  <div>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">${
                            stock.symbol
                          }</span>
                          <span class="text-xs text-gray-500 dark:text-gray-400 block">${stock.name.substring(
                            0,
                            20
                          )}${stock.name.length > 20 ? '...' : ''}</span>
                          </div>
                          <div class="text-right">
                          <span class="font-medium text-gray-800 dark:text-gray-200">$${stock.price.toFixed(
                            2
                          )}</span>
                          <span class="block text-sm text-green-500 dark:text-green-400">+${stock.changePercent.toFixed(2)}%</span>
                          </div>
                  </li>
              `
          )
          .join('')
      : '<li class="text-sm text-gray-500 dark:text-gray-400">No significant gainers today.</li>';

    // Display losers
    topLosersList.innerHTML = losers.length
      ? losers
          .map(
            (stock) => `
            <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="searchInput.value='${
              stock.symbol
            }'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
                <div>
                    <span class="font-semibold text-gray-800 dark:text-gray-200">${
                      stock.symbol
                    }</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400 block">${stock.name.substring(
                            0,
                            20
                          )}${stock.name.length > 20 ? '...' : ''}</span>
                          </div>
                          <div class="text-right">
                              <span class="font-medium text-gray-800 dark:text-gray-200">$${stock.price.toFixed(
                                2
                              )}</span>
                              <span class="block text-sm text-red-500 dark:text-red-400">${stock.changePercent.toFixed(2)}%</span>
                          </div>
                      </li>
              `
          )
          .join('')
      : '<li class="text-sm text-gray-500 dark:text-gray-400">No significant losers today.</li>';

  } catch (error) {
    console.error('Error fetching market movers:', error);
    topGainersList.innerHTML = '<li class="text-sm text-red-500 dark:text-red-400">Error loading market data</li>';
    topLosersList.innerHTML = '<li class="text-sm text-red-500 dark:text-red-400">Error loading market data</li>';
  }
}
populateMarketMovers();
setInterval(populateMarketMovers, 15000);

const watchlistItemsDiv = document.getElementById('watchlist-items');
const emptyWatchlistMessage = document.getElementById(
  'empty-watchlist-message'
);
let watchlist = JSON.parse(localStorage.getItem('stockWatchlist')) || [];

async function renderWatchlist() {
  if (watchlist.length === 0) {
    watchlistItemsDiv.innerHTML = '';
    emptyWatchlistMessage.classList.remove('hidden');
    return;
  }
  emptyWatchlistMessage.classList.add('hidden');
  
  // Fetch data for each symbol in watchlist
  const watchlistItems = await Promise.all(
    watchlist.map(async (symbol) => {
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

        const stockData = await response.json();
        
        if (stockData.error) {
          throw new Error(stockData.error);
        }

        const changeClass = stockData.change >= 0
          ? 'text-green-500 dark:text-green-400'
          : 'text-red-500 dark:text-red-400';
        const changeSign = stockData.change >= 0 ? '+' : '';

        return `
        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg shadow hover:shadow-md transition-all duration-200 cursor-pointer" onclick="searchInput.value='${symbol}'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
        <div class="flex justify-between items-start mb-2">
            <div>
                <h4 class="text-lg font-semibold text-gray-800 dark:text-gray-100">${symbol}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">${stockData.name}</p>
            </div>
             <button class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-xs p-1" onclick="event.stopPropagation(); toggleWatchlist('${symbol}');" title="Remove from watchlist">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
        <div class="flex justify-between items-baseline">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">$${stockData.price.toFixed(2)}</p>
            <p class="text-md ${changeClass}">${changeSign}${stockData.changePercent.toFixed(2)}%</p>
        </div>
    </div>
  `;
      } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        return `
        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg shadow">
        <div class="flex justify-between items-start mb-2">
            <div>
                <h4 class="text-lg font-semibold text-gray-800 dark:text-gray-100">${symbol}</h4>
                <p class="text-xs text-red-500">Error loading data</p>
            </div>
             <button class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-xs p-1" onclick="event.stopPropagation(); toggleWatchlist('${symbol}');" title="Remove from watchlist">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    </div>
  `;
      }
    })
  );

  watchlistItemsDiv.innerHTML = watchlistItems.join('');
}

function isStockInWatchlist(symbol) {
  return watchlist.includes(symbol);
}

function toggleWatchlist(symbol) {
  if (!symbol) return;

  const index = watchlist.indexOf(symbol);
  if (index > -1) {
    watchlist.splice(index, 1);
  } else {
    watchlist.push(symbol);
  }
  localStorage.setItem('stockWatchlist', JSON.stringify(watchlist));
  renderWatchlist();

  const currentSearchSymbol = searchInput.value.toUpperCase().trim();
  if (currentSearchSymbol === symbol) {
    addToWatchlistBtn.textContent = isStockInWatchlist(symbol)
      ? 'Remove from Watchlist'
      : 'Add to Watchlist';
    addToWatchlistBtn.classList.toggle(
      'bg-red-500',
      isStockInWatchlist(symbol)
    );
    addToWatchlistBtn.classList.toggle(
      'hover:bg-red-600',
      isStockInWatchlist(symbol)
    );
    addToWatchlistBtn.classList.toggle(
      'bg-green-500',
      !isStockInWatchlist(symbol)
    );
    addToWatchlistBtn.classList.toggle(
      'hover:bg-green-600',
      !isStockInWatchlist(symbol)
    );
  }
}

addToWatchlistBtn.addEventListener('click', () => {
  const symbol = searchInput.value.toUpperCase().trim();
  toggleWatchlist(symbol);
});

const newsFeedDiv = document.getElementById('news-feed');
async function populateNewsFeed() {
  const currentSymbol = searchInput.value.toUpperCase().trim();
  
  try {
    const url = currentSymbol ? `/api/news/?symbol=${currentSymbol}` : '/api/news/';
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

    const articles = data.articles || [];
    
    // Show fallback notice if using fallback data
    let fallbackNotice = '';
    if (data.fallback) {
      fallbackNotice = '<div class="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-700 dark:text-yellow-300 px-4 py-3 rounded mb-4">⚠️ Using demo news - API not configured or unavailable</div>';
    }

    newsFeedDiv.innerHTML = fallbackNotice + (articles.length
      ? articles
          .map(
            (news) => `
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg shadow hover:shadow-md transition-shadow duration-200">
            <a href="${news.url}" target="_blank" rel="noopener noreferrer" class="block hover:text-indigo-600 dark:hover:text-indigo-400">
                <h4 class="text-md font-semibold text-gray-800 dark:text-gray-100 mb-1">${news.title}</h4>
                ${news.description ? `<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${news.description.substring(0, 100)}${news.description.length > 100 ? '...' : ''}</p>` : ''}
            </a>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>${news.source}</span>
                <span>${news.time}</span>
            </div>
        </div>
              `
          )
          .join('')
      : '<p class="text-sm text-gray-500 dark:text-gray-400">No news available at the moment.</p>');

  } catch (error) {
    console.error('Error fetching news:', error);
    newsFeedDiv.innerHTML = '<p class="text-sm text-red-500 dark:text-red-400">Error loading news. Please try again later.</p>';
  }
}

searchButton.addEventListener('click', populateNewsFeed);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    populateNewsFeed();
  }
});

document.getElementById('currentYear').textContent = new Date().getFullYear();

document.addEventListener('DOMContentLoaded', () => {
  renderWatchlist();
  populateNewsFeed();
  displayStockDetails(null);
  if (!searchInput.value) {
    searchInput.value = 'AAPL';
    performSearch();
  }

  document.querySelectorAll('nav a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        const navbarHeight = document.querySelector('nav').offsetHeight;
        const tickerHeight =
          document.querySelector('.ticker-wrap').offsetHeight;
        const offsetPosition =
          targetElement.offsetTop - navbarHeight - tickerHeight - 20;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth',
        });

        if (!mobileMenu.classList.contains('hidden')) {
          mobileMenu.classList.add('hidden');
          mobileMenuButton.setAttribute('aria-expanded', 'false');
          mobileMenuButton
            .querySelectorAll('svg')
            .forEach((icon) => icon.classList.toggle('hidden'));
        }
      }
    });
  });
});