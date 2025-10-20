// Dashboard Charts - Adapted from admin-dashboard

// BAR CHART - Portfolio Performance
const barChartOptions = {
  series: [
    {
      name: 'Portfolio Value',
      data: [44, 55, 57, 56, 61, 58, 63, 60, 66],
    },
    {
      name: 'Market Index',
      data: [76, 85, 101, 98, 87, 105, 91, 114, 94],
    },
    {
      name: 'Benchmark',
      data: [35, 41, 36, 26, 45, 48, 52, 53, 41],
    },
  ],
  chart: {
    type: 'bar',
    height: 350,
    toolbar: {
      show: false,
    },
  },
  colors: ['#2e7d32', '#2962ff', '#d50000'],
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      endingShape: 'rounded',
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    show: true,
    width: 2,
    colors: ['transparent'],
  },
  xaxis: {
    categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    labels: {
      style: {
        colors: '#f5f7ff',
      },
    },
  },
  yaxis: {
    title: {
      text: 'Value ($)',
      style: {
        color: '#f5f7ff',
      },
    },
    labels: {
      style: {
        colors: '#f5f7ff',
      },
    },
  },
  fill: {
    opacity: 1,
  },
  grid: {
    borderColor: '#55596e',
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: true,
      },
    },
  },
  legend: {
    labels: {
      colors: '#f5f7ff',
    },
    show: true,
    position: 'bottom',
  },
  tooltip: {
    theme: 'dark',
    y: {
      formatter: function (val) {
        return '$ ' + val + 'K';
      },
    },
  },
};

const barChart = new ApexCharts(
  document.querySelector('#bar-chart'),
  barChartOptions
);
barChart.render();

// AREA CHART - Stock Analysis Trends
const areaChartOptions = {
  series: [
    {
      name: 'Buy Signals',
      data: [31, 40, 28, 51, 42, 109, 100],
    },
    {
      name: 'Sell Signals',
      data: [11, 32, 45, 32, 34, 52, 41],
    },
  ],
  chart: {
    type: 'area',
    background: 'transparent',
    height: 350,
    stacked: false,
    toolbar: {
      show: false,
    },
  },
  colors: ['#00ab57', '#d50000'],
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
  dataLabels: {
    enabled: false,
  },
  fill: {
    gradient: {
      opacityFrom: 0.4,
      opacityTo: 0.1,
      shadeIntensity: 1,
      stops: [0, 100],
      type: 'vertical',
    },
    type: 'gradient',
  },
  grid: {
    borderColor: '#55596e',
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: true,
      },
    },
  },
  legend: {
    labels: {
      colors: '#f5f7ff',
    },
    show: true,
    position: 'bottom',
  },
  markers: {
    size: 6,
    strokeColors: '#1b2635',
    strokeWidth: 3,
  },
  stroke: {
    curve: 'smooth',
  },
  xaxis: {
    axisBorder: {
      color: '#55596e',
      show: true,
    },
    axisTicks: {
      color: '#55596e',
      show: true,
    },
    labels: {
      offsetY: 5,
      style: {
        colors: '#f5f7ff',
      },
    },
  },
  yaxis: [
    {
      title: {
        text: 'Buy Signals',
        style: {
          color: '#f5f7ff',
        },
      },
      labels: {
        style: {
          colors: ['#f5f7ff'],
        },
      },
    },
    {
      opposite: true,
      title: {
        text: 'Sell Signals',
        style: {
          color: '#f5f7ff',
        },
      },
      labels: {
        style: {
          colors: ['#f5f7ff'],
        },
      },
    },
  ],
  tooltip: {
    shared: true,
    intersect: false,
    theme: 'dark',
  },
};

const areaChart = new ApexCharts(
  document.querySelector('#area-chart'),
  areaChartOptions
);
areaChart.render();

// Dashboard initialization
document.addEventListener('DOMContentLoaded', function() {
  console.log('PortfolAI Dashboard initialized');
  
  // Initialize dashboard
  initializeDashboard();
  setupSearchFunctionality();
  setupWatchlistFunctionality();
  loadMarketStatus();
  loadWatchlist();
  initializeTradingViewWidget();
  loadTopStockCards();
  setupChartTabs();
  loadTrendingStocks();
});

// Global variables
let watchlist = [];
let selectedStock = null;

// Initialize dashboard
function initializeDashboard() {
  updateWatchlistCount();
  updateSelectedStock();
  updatePriceChange();
}

// Setup search functionality
function setupSearchFunctionality() {
  const searchInput = document.getElementById('stock-search');
  const searchBtn = document.getElementById('search-btn');
  const searchResults = document.getElementById('search-results');
  
  // Search button click
  searchBtn.addEventListener('click', performSearch);
  
  // Enter key press
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      performSearch();
    }
  });
  
  // Input change (for real-time search)
  searchInput.addEventListener('input', function() {
    if (this.value.length > 2) {
      performSearch();
    } else {
      searchResults.style.display = 'none';
    }
  });
}

// Perform stock search
async function performSearch() {
  const searchInput = document.getElementById('stock-search');
  const searchResults = document.getElementById('search-results');
  const query = searchInput.value.trim();
  
  if (!query) {
    searchResults.style.display = 'none';
    return;
  }
  
  // Show loading state
  searchResults.innerHTML = '<div class="loading">Searching stocks...</div>';
  searchResults.style.display = 'block';
  
  try {
    const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    
    if (data.error) {
      searchResults.innerHTML = `<div class="error">Error: ${data.error}</div>`;
      return;
    }
    
    displaySearchResults(data.result || []);
  } catch (error) {
    console.error('Search error:', error);
    searchResults.innerHTML = '<div class="error">Failed to search stocks. Please try again.</div>';
  }
}

// Display search results
function displaySearchResults(results) {
  const searchResults = document.getElementById('search-results');
  
  if (results.length === 0) {
    searchResults.innerHTML = '<div class="loading">No stocks found</div>';
    return;
  }
  
  const resultsHTML = results.map(stock => {
    const isInWatchlist = watchlist.some(item => item.symbol === stock.symbol);
    return `
      <div class="search-result-item">
        <div onclick="selectStock('${stock.symbol}', '${stock.description}')" style="flex: 1; cursor: pointer;">
          <div class="search-result-symbol">${stock.symbol}</div>
          <div class="search-result-description">${stock.description}</div>
          <div class="search-result-exchange">${stock.type || 'Stock'}</div>
        </div>
        <button class="add-to-watchlist-btn ${isInWatchlist ? 'added' : ''}" 
                onclick="event.stopPropagation(); toggleWatchlist('${stock.symbol}', '${stock.description}')">
          <span class="material-icons-outlined">${isInWatchlist ? 'star' : 'star_border'}</span>
          ${isInWatchlist ? 'Added' : 'Add'}
        </button>
      </div>
    `;
  }).join('');
  
  searchResults.innerHTML = resultsHTML;
}

// Select a stock
async function selectStock(symbol, description) {
  selectedStock = { symbol, description };
  updateSelectedStock();
  
  // Hide search results
  document.getElementById('search-results').style.display = 'none';
  document.getElementById('stock-search').value = '';
  
  // Show stock info section
  document.getElementById('stock-info-section').style.display = 'block';
  
  // Load stock data
  await loadStockData(symbol);
  
  // Load company profile
  await loadCompanyProfile(symbol);
  
  // Update chart with real data
  await updateChartWithStockData(symbol);
}

// Load stock data
async function loadStockData(symbol) {
  try {
    const response = await fetch(`/api/quote/?symbol=${encodeURIComponent(symbol)}`);
    const data = await response.json();
    
    if (data.error) {
      console.error('Error loading stock data:', data.error);
      return;
    }
    
    updatePriceChange(data);
    updateStockInfo(data);
  } catch (error) {
    console.error('Error loading stock data:', error);
  }
}

// Load company profile
async function loadCompanyProfile(symbol) {
  try {
    const response = await fetch(`/api/profile/?symbol=${encodeURIComponent(symbol)}`);
    const data = await response.json();
    
    if (data.error) {
      console.error('Error loading company profile:', data.error);
      return;
    }
    
    updateCompanyInfo(data);
  } catch (error) {
    console.error('Error loading company profile:', error);
  }
}

// Update stock information display
function updateStockInfo(quoteData) {
  if (!quoteData) return;
  
  // Update current price
  const currentPrice = quoteData.c || 0;
  document.getElementById('current-price-display').textContent = `$${currentPrice.toFixed(2)}`;
  
  // Update price change
  const change = quoteData.d || 0;
  const changePercent = quoteData.dp || 0;
  const priceChangeElement = document.getElementById('price-change-display');
  
  priceChangeElement.textContent = `${change >= 0 ? '+' : ''}$${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
  priceChangeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
  
  // Update stock details
  document.getElementById('stock-high').textContent = `$${(quoteData.h || 0).toFixed(2)}`;
  document.getElementById('stock-low').textContent = `$${(quoteData.l || 0).toFixed(2)}`;
  document.getElementById('stock-open').textContent = `$${(quoteData.o || 0).toFixed(2)}`;
  document.getElementById('stock-prev-close').textContent = `$${(quoteData.pc || 0).toFixed(2)}`;
}

// Update company information
function updateCompanyInfo(profileData) {
  if (!profileData) return;
  
  document.getElementById('stock-company-display').textContent = profileData.name || selectedStock.description;
}

// Update chart with real stock data
async function updateChartWithStockData(symbol) {
  try {
    // Update chart title
    document.getElementById('chart-stock-symbol').textContent = symbol;
    
    // Show loading state
    const chartContainer = document.getElementById('area-chart');
    chartContainer.innerHTML = '<div class="loading">Loading historical data...</div>';
    
    // Fetch real historical data
    const historicalData = await fetchHistoricalData(symbol);
    
    if (historicalData && historicalData.c && historicalData.c.length > 0) {
      updateAreaChartWithRealData(historicalData);
    } else {
      // Fallback to mock data if real data is not available
      const mockData = generateMockStockData(symbol);
      updateAreaChart(mockData);
    }
    
  } catch (error) {
    console.error('Error updating chart with stock data:', error);
    // Fallback to mock data on error
    const mockData = generateMockStockData(symbol);
    updateAreaChart(mockData);
  }
}

// Fetch historical data from API
async function fetchHistoricalData(symbol) {
  try {
    const response = await fetch(`/api/candles/?symbol=${encodeURIComponent(symbol)}&resolution=D&count=30`);
    const data = await response.json();
    
    if (data.error) {
      console.error('Error fetching historical data:', data.error);
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching historical data:', error);
    return null;
  }
}

// Generate mock stock data for demonstration
function generateMockStockData(symbol) {
  const basePrice = Math.random() * 200 + 50; // Random base price between 50-250
  const data = [];
  const dates = [];
  
  // Generate 30 days of data
  const today = new Date();
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    dates.push(date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    }));
    
    const variation = (Math.random() - 0.5) * 20; // Random variation
    const price = Math.max(0, basePrice + variation + (Math.random() - 0.5) * 10);
    data.push(parseFloat(price.toFixed(2)));
  }
  
  return { prices: data, dates: dates };
}

// Update area chart with real historical data
function updateAreaChartWithRealData(historicalData) {
  const prices = historicalData.c || []; // Close prices
  const timestamps = historicalData.t || []; // Timestamps
  
  if (prices.length === 0) {
    console.error('No price data available');
    return;
  }
  
  // Convert timestamps to dates and format them
  const dates = timestamps.map(timestamp => {
    const date = new Date(timestamp * 1000); // Convert Unix timestamp to milliseconds
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  });
  
  // Calculate price range for better Y-axis scaling
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const padding = priceRange * 0.1; // 10% padding
  
  const areaChartOptions = {
    series: [
      {
        name: 'Stock Price',
        data: prices,
      },
    ],
    chart: {
      type: 'area',
      background: 'transparent',
      height: 350,
      stacked: false,
      toolbar: {
        show: false,
      },
    },
    colors: ['#334be9'],
    labels: dates,
    dataLabels: {
      enabled: false,
    },
    fill: {
      gradient: {
        opacityFrom: 0.4,
        opacityTo: 0.1,
        shadeIntensity: 1,
        stops: [0, 100],
        type: 'vertical',
      },
      type: 'gradient',
    },
    grid: {
      borderColor: '#55596e',
      yaxis: {
        lines: {
          show: true,
        },
      },
      xaxis: {
        lines: {
          show: true,
        },
      },
    },
    legend: {
      labels: {
        colors: '#f5f7ff',
      },
      show: true,
      position: 'bottom',
    },
    markers: {
      size: 4,
      strokeColors: '#1b2635',
      strokeWidth: 2,
    },
    stroke: {
      curve: 'smooth',
      width: 2,
    },
    xaxis: {
      categories: dates,
      axisBorder: {
        color: '#55596e',
        show: true,
      },
      axisTicks: {
        color: '#55596e',
        show: true,
      },
      labels: {
        offsetY: 5,
        style: {
          colors: '#f5f7ff',
          fontSize: '12px',
        },
        rotate: -45,
      },
    },
    yaxis: {
      min: Math.max(0, minPrice - padding),
      max: maxPrice + padding,
      title: {
        text: 'Price ($)',
        style: {
          color: '#f5f7ff',
        },
      },
      labels: {
        style: {
          colors: ['#f5f7ff'],
        },
        formatter: function (val) {
          return '$' + val.toFixed(2);
        },
      },
    },
    tooltip: {
      shared: true,
      intersect: false,
      theme: 'dark',
      x: {
        formatter: function (val, { dataPointIndex }) {
          const timestamp = timestamps[dataPointIndex];
          const date = new Date(timestamp * 1000);
          return date.toLocaleDateString('en-US', { 
            weekday: 'short',
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
          });
        },
      },
      y: {
        formatter: function (val) {
          return '$' + val.toFixed(2);
        },
      },
    },
  };

  // Destroy existing chart and create new one
  if (window.areaChart) {
    window.areaChart.destroy();
  }
  
  window.areaChart = new ApexCharts(
    document.querySelector('#area-chart'),
    areaChartOptions
  );
  window.areaChart.render();
}

// Update area chart with mock data (fallback)
function updateAreaChart(mockData) {
  const prices = mockData.prices || mockData; // Handle both old and new format
  const dates = mockData.dates || Array.from({length: prices.length}, (_, i) => `Day ${i + 1}`);
  
  // Calculate price range for better Y-axis scaling
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const padding = priceRange * 0.1; // 10% padding
  
  const areaChartOptions = {
    series: [
      {
        name: 'Stock Price',
        data: prices,
      },
    ],
    chart: {
      type: 'area',
      background: 'transparent',
      height: 350,
      stacked: false,
      toolbar: {
        show: false,
      },
    },
    colors: ['#334be9'],
    labels: dates,
    dataLabels: {
      enabled: false,
    },
    fill: {
      gradient: {
        opacityFrom: 0.4,
        opacityTo: 0.1,
        shadeIntensity: 1,
        stops: [0, 100],
        type: 'vertical',
      },
      type: 'gradient',
    },
    grid: {
      borderColor: '#55596e',
      yaxis: {
        lines: {
          show: true,
        },
      },
      xaxis: {
        lines: {
          show: true,
        },
      },
    },
    legend: {
      labels: {
        colors: '#f5f7ff',
      },
      show: true,
      position: 'bottom',
    },
    markers: {
      size: 6,
      strokeColors: '#1b2635',
      strokeWidth: 3,
    },
    stroke: {
      curve: 'smooth',
    },
    xaxis: {
      categories: dates,
      axisBorder: {
        color: '#55596e',
        show: true,
      },
      axisTicks: {
        color: '#55596e',
        show: true,
      },
      labels: {
        offsetY: 5,
        style: {
          colors: '#f5f7ff',
          fontSize: '12px',
        },
        rotate: -45,
      },
    },
    yaxis: {
      min: Math.max(0, minPrice - padding),
      max: maxPrice + padding,
      title: {
        text: 'Price ($)',
        style: {
          color: '#f5f7ff',
        },
      },
      labels: {
        style: {
          colors: ['#f5f7ff'],
        },
        formatter: function (val) {
          return '$' + val.toFixed(2);
        },
      },
    },
    tooltip: {
      shared: true,
      intersect: false,
      theme: 'dark',
      y: {
        formatter: function (val) {
          return '$' + val.toFixed(2);
        },
      },
    },
  };

  // Destroy existing chart and create new one
  if (window.areaChart) {
    window.areaChart.destroy();
  }
  
  window.areaChart = new ApexCharts(
    document.querySelector('#area-chart'),
    areaChartOptions
  );
  window.areaChart.render();
}

// Load market status
async function loadMarketStatus() {
  try {
    const response = await fetch('/api/market-status/');
    const data = await response.json();
    
    if (data.error) {
      document.getElementById('market-status').textContent = 'Error';
      return;
    }
    
    const status = data.isOpen ? 'Open' : 'Closed';
    document.getElementById('market-status').textContent = status;
  } catch (error) {
    console.error('Error loading market status:', error);
    document.getElementById('market-status').textContent = 'Error';
  }
}

// Load top stock cards data
async function loadTopStockCards() {
  const symbols = ['AAPL', 'PYPL', 'TSLA', 'AMZN'];
  
  try {
    const stockData = await Promise.all(
      symbols.map(async (symbol) => {
        try {
          const response = await fetch(`/api/quote/?symbol=${encodeURIComponent(symbol)}`);
          const data = await response.json();
          
          if (data && data.c) {
            return {
              symbol: symbol,
              price: data.c,
              change: data.d || 0,
              changePercent: data.dp || 0
            };
          }
          return null;
        } catch (error) {
          console.error(`Error loading data for ${symbol}:`, error);
          return null;
        }
      })
    );

    // Update each stock card with real data
    stockData.forEach((stock, index) => {
      if (stock) {
        const symbol = stock.symbol.toLowerCase();
        const priceElement = document.getElementById(`${symbol}-price`);
        const changeElement = document.getElementById(`${symbol}-change`);
        
        if (priceElement) {
          priceElement.textContent = `$${stock.price.toFixed(2)}`;
        }
        
        if (changeElement) {
          const isPositive = stock.change >= 0;
          const sign = isPositive ? '+' : '';
          changeElement.textContent = `${sign}${stock.changePercent.toFixed(2)}%`;
          changeElement.className = `stock-change ${isPositive ? 'positive' : 'negative'}`;
        }
      }
    });
  } catch (error) {
    console.error('Error loading top stock cards:', error);
  }
}

// Setup chart tabs functionality
function setupChartTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  
  tabButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Remove active class from all tabs
      tabButtons.forEach(btn => btn.classList.remove('active'));
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Get the period from data attribute
      const period = this.getAttribute('data-period');
      
      // For now, just log the period - can be extended later to update chart data
      console.log(`Switched to ${period} view`);
      
      // Here you could update the chart data based on the selected period
      // updateChartData(period);
    });
  });
}

// Load trending stocks data
async function loadTrendingStocks() {
  const symbols = ['TSLA', 'AAPL', 'SPOT', 'PYPL', 'AMZN'];
  
  try {
    const stockData = await Promise.all(
      symbols.map(async (symbol) => {
        try {
          const response = await fetch(`/api/quote/?symbol=${encodeURIComponent(symbol)}`);
          const data = await response.json();
          
          if (data && data.c) {
            return {
              symbol: symbol,
              price: data.c,
              change: data.d || 0,
              changePercent: data.dp || 0
            };
          }
          return null;
        } catch (error) {
          console.error(`Error loading data for ${symbol}:`, error);
          return null;
        }
      })
    );

    // Update each trending stock card with real data
    stockData.forEach((stock) => {
      if (stock) {
        const symbol = stock.symbol.toLowerCase();
        const priceElement = document.getElementById(`trending-${symbol}-price`);
        const changeElement = document.getElementById(`trending-${symbol}-change`);
        
        if (priceElement) {
          priceElement.textContent = `$${stock.price.toFixed(2)}`;
        }
        
        if (changeElement) {
          const isPositive = stock.change >= 0;
          const sign = isPositive ? '+' : '';
          changeElement.textContent = `${sign}${stock.changePercent.toFixed(2)}%`;
          changeElement.className = `trending-stock-change ${isPositive ? 'positive' : 'negative'}`;
        }
      }
    });
  } catch (error) {
    console.error('Error loading trending stocks:', error);
  }
}

// Update watchlist count
function updateWatchlistCount() {
  document.getElementById('watchlist-count').textContent = watchlist.length;
}

// Update selected stock
function updateSelectedStock() {
  const element = document.getElementById('selected-stock');
  if (selectedStock) {
    element.textContent = selectedStock.symbol;
  } else {
    element.textContent = 'None';
  }
}

// Update price change
function updatePriceChange(quoteData) {
  const element = document.getElementById('price-change');
  if (quoteData && quoteData.d !== undefined) {
    const change = quoteData.d;
    const changePercent = quoteData.dp || 0;
    const color = change >= 0 ? '#2e7d32' : '#d50000';
    const sign = change >= 0 ? '+' : '';
    
    element.innerHTML = `
      <span style="color: ${color}">
        ${sign}$${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)
      </span>
    `;
  } else {
    element.textContent = '$0.00';
  }
}

// Add to watchlist
function addToWatchlist(symbol, description) {
  if (!watchlist.find(stock => stock.symbol === symbol)) {
    watchlist.push({ symbol, description });
    updateWatchlistCount();
  }
}

// Remove from watchlist
function removeFromWatchlist(symbol) {
  watchlist = watchlist.filter(stock => stock.symbol !== symbol);
  updateWatchlistCount();
  saveWatchlist();
  renderWatchlist();
}

// Setup watchlist functionality
function setupWatchlistFunctionality() {
  const clearBtn = document.getElementById('clear-watchlist-btn');
  if (clearBtn) {
    clearBtn.addEventListener('click', clearWatchlist);
  }
}

// Toggle stock in watchlist
function toggleWatchlist(symbol, description) {
  const existingIndex = watchlist.findIndex(stock => stock.symbol === symbol);
  
  if (existingIndex > -1) {
    // Remove from watchlist
    watchlist.splice(existingIndex, 1);
  } else {
    // Add to watchlist
    watchlist.push({ symbol, description });
  }
  
  updateWatchlistCount();
  saveWatchlist();
  renderWatchlist();
  
  // Update search results if visible
  const searchResults = document.getElementById('search-results');
  if (searchResults.style.display !== 'none') {
    // Re-render search results to update button states
    const searchInput = document.getElementById('stock-search');
    if (searchInput.value.trim()) {
      performSearch();
    }
  }
}

// Clear all watchlist
function clearWatchlist() {
  if (confirm('Are you sure you want to clear all stocks from your watchlist?')) {
    watchlist = [];
    updateWatchlistCount();
    saveWatchlist();
    renderWatchlist();
  }
}

// Save watchlist to localStorage
function saveWatchlist() {
  try {
    localStorage.setItem('portfolai_watchlist', JSON.stringify(watchlist));
  } catch (error) {
    console.error('Error saving watchlist:', error);
  }
}

// Load watchlist from localStorage
function loadWatchlist() {
  try {
    const saved = localStorage.getItem('portfolai_watchlist');
    if (saved) {
      watchlist = JSON.parse(saved);
      updateWatchlistCount();
      renderWatchlist();
    }
  } catch (error) {
    console.error('Error loading watchlist:', error);
    watchlist = [];
  }
}

// Render watchlist
async function renderWatchlist() {
  const watchlistGrid = document.getElementById('watchlist-grid');
  const watchlistEmpty = document.getElementById('watchlist-empty');
  
  if (watchlist.length === 0) {
    watchlistGrid.style.display = 'none';
    watchlistEmpty.style.display = 'flex';
    return;
  }
  
  watchlistEmpty.style.display = 'none';
  watchlistGrid.style.display = 'grid';
  
  // Show loading state
  watchlistGrid.innerHTML = `
    <div class="watchlist-loading">
      <span class="material-icons-outlined">refresh</span>
      Loading watchlist data...
    </div>
  `;
  
  // Load data for all watchlist items
  const watchlistItems = await Promise.all(
    watchlist.map(async (stock) => {
      try {
        const [quoteResponse, profileResponse] = await Promise.all([
          fetch(`/api/quote/?symbol=${encodeURIComponent(stock.symbol)}`),
          fetch(`/api/profile/?symbol=${encodeURIComponent(stock.symbol)}`)
        ]);
        
        const quoteData = await quoteResponse.json();
        const profileData = await profileResponse.json();
        
        return {
          ...stock,
          quote: quoteData.error ? null : quoteData,
          profile: profileData.error ? null : profileData
        };
      } catch (error) {
        console.error(`Error loading data for ${stock.symbol}:`, error);
        return { ...stock, quote: null, profile: null };
      }
    })
  );
  
  // Render watchlist items
  const watchlistHTML = watchlistItems.map(stock => {
    const quote = stock.quote;
    const profile = stock.profile;
    
    if (!quote) {
      return `
        <div class="watchlist-item">
          <div class="watchlist-item-header">
            <div class="watchlist-symbol">${stock.symbol}</div>
            <button class="watchlist-remove" onclick="removeFromWatchlist('${stock.symbol}')">
              <span class="material-icons-outlined">close</span>
              Remove
            </button>
          </div>
          <div class="watchlist-company">${stock.description}</div>
          <div class="watchlist-loading">
            <span class="material-icons-outlined">error</span>
            Unable to load data
          </div>
        </div>
      `;
    }
    
    const currentPrice = quote.c || 0;
    const change = quote.d || 0;
    const changePercent = quote.dp || 0;
    const high = quote.h || 0;
    const low = quote.l || 0;
    const open = quote.o || 0;
    const prevClose = quote.pc || 0;
    
    const companyName = profile?.name || stock.description;
    
    return `
      <div class="watchlist-item" onclick="selectStock('${stock.symbol}', '${stock.description}')">
        <div class="watchlist-item-header">
          <div class="watchlist-symbol">${stock.symbol}</div>
          <button class="watchlist-remove" onclick="event.stopPropagation(); removeFromWatchlist('${stock.symbol}')">
            <span class="material-icons-outlined">close</span>
            Remove
          </button>
        </div>
        <div class="watchlist-company">${companyName}</div>
        <div class="watchlist-price-info">
          <div class="watchlist-current-price">$${currentPrice.toFixed(2)}</div>
          <div class="watchlist-price-change ${change >= 0 ? 'positive' : 'negative'}">
            ${change >= 0 ? '+' : ''}$${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)
          </div>
        </div>
        <div class="watchlist-details">
          <div class="watchlist-detail">
            <span class="watchlist-detail-label">High</span>
            <span class="watchlist-detail-value">$${high.toFixed(2)}</span>
          </div>
          <div class="watchlist-detail">
            <span class="watchlist-detail-label">Low</span>
            <span class="watchlist-detail-value">$${low.toFixed(2)}</span>
          </div>
          <div class="watchlist-detail">
            <span class="watchlist-detail-label">Open</span>
            <span class="watchlist-detail-value">$${open.toFixed(2)}</span>
          </div>
          <div class="watchlist-detail">
            <span class="watchlist-detail-label">Prev Close</span>
            <span class="watchlist-detail-value">$${prevClose.toFixed(2)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  watchlistGrid.innerHTML = watchlistHTML;
}

// Initialize Custom Ticker Tape Widget
function initializeTradingViewWidget() {
  const container = document.querySelector('.tradingview-widget-container__widget');
  
  if (!container) {
    console.warn('Ticker tape container not found');
    return;
  }

  // Create custom ticker tape using our Finnhub API
  createCustomTickerTape(container);
}

function createCustomTickerTape(container) {
  // Define popular stocks to display
  const tickerSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX'];
  
  // Create ticker tape HTML structure
  container.innerHTML = `
    <div class="custom-ticker-tape">
      <div class="ticker-content" id="ticker-content">
        <div class="ticker-loading">
          <span class="material-icons-outlined">refresh</span>
          Loading market data...
        </div>
      </div>
    </div>
  `;

  // Load ticker data
  loadTickerData(tickerSymbols);
}

async function loadTickerData(symbols) {
  const tickerContent = document.getElementById('ticker-content');
  
  try {
    // Load data for all symbols
    const tickerData = await Promise.all(
      symbols.map(async (symbol) => {
        try {
          const response = await fetch(`/api/quote/?symbol=${encodeURIComponent(symbol)}`);
          const data = await response.json();
          
          if (data && data.c) {
            return {
              symbol: symbol,
              price: data.c,
              change: data.d || 0,
              changePercent: data.dp || 0
            };
          }
          return null;
        } catch (error) {
          console.error(`Error loading data for ${symbol}:`, error);
          return null;
        }
      })
    );

    // Filter out null results
    const validData = tickerData.filter(item => item !== null);
    
    if (validData.length === 0) {
      tickerContent.innerHTML = `
        <div class="ticker-error">
          <span class="material-icons-outlined">error</span>
          Market data temporarily unavailable
        </div>
      `;
      return;
    }

    // Create ticker items
    const tickerItems = validData.map(item => {
      const isPositive = item.change >= 0;
      const changeClass = isPositive ? 'positive' : 'negative';
      const changeSymbol = isPositive ? '+' : '';
      
      return `
        <div class="ticker-item">
          <div class="ticker-symbol">${item.symbol}</div>
          <div class="ticker-price">$${item.price.toFixed(2)}</div>
          <div class="ticker-change ${changeClass}">
            ${changeSymbol}$${item.change.toFixed(2)} (${changeSymbol}${item.changePercent.toFixed(2)}%)
          </div>
        </div>
      `;
    }).join('');

    // Update ticker content
    tickerContent.innerHTML = `
      <div class="ticker-scroll">
        ${tickerItems}
        ${tickerItems} <!-- Duplicate for seamless scrolling -->
      </div>
    `;

    // Start scrolling animation
    startTickerAnimation();

  } catch (error) {
    console.error('Error loading ticker data:', error);
    tickerContent.innerHTML = `
      <div class="ticker-error">
        <span class="material-icons-outlined">error</span>
        Failed to load market data
      </div>
    `;
  }
}

function startTickerAnimation() {
  const tickerScroll = document.querySelector('.ticker-scroll');
  if (!tickerScroll) return;

  // Add CSS animation - slower speed (60 seconds)
  tickerScroll.style.animation = 'ticker-scroll 60s linear infinite';
}
