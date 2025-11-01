/**
 * UI Components
 * Handles theme, navigation, ticker, market movers, and news functionality
 */

// DOM references
const themeToggleBtn = document.getElementById('theme-toggle');
const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

const tickerMove = document.querySelector('.ticker-move');
const topGainersList = document.getElementById('top-gainers-list');
const topLosersList = document.getElementById('top-losers-list');
const newsFeedDiv = document.getElementById('news-feed');

// Ticker data storage
let tickerData = [];

/**
 * Initialize theme system with localStorage persistence
 */
function initializeTheme() {
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

  themeToggleBtn.addEventListener('click', toggleTheme);
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
  themeToggleDarkIcon.classList.toggle('hidden');
  themeToggleLightIcon.classList.toggle('hidden');
  document.documentElement.classList.toggle('dark');
  const currentTheme = document.documentElement.classList.contains('dark')
    ? 'dark'
    : 'light';
  localStorage.setItem('color-theme', currentTheme);
  
  // Dispatch custom event for components that need to react to theme changes
  window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme: currentTheme } }));
}

/**
 * Initialize mobile menu functionality
 */
function initializeMobileMenu() {
  mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    const isExpanded =
      mobileMenuButton.getAttribute('aria-expanded') === 'true' || false;
    mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
    mobileMenuButton
      .querySelectorAll('svg')
      .forEach((icon) => icon.classList.toggle('hidden'));
  });
}

/**
 * Populate the scrolling ticker with market data
 */
async function populateTicker() {
  try {
    const data = await fetchMarketMovers();

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

/**
 * Populate market movers (gainers and losers) lists
 */
async function populateMarketMovers() {
  try {
    const data = await fetchMarketMovers();
    const { gainers, losers } = data;

    // Display gainers
    topGainersList.innerHTML = gainers.length
      ? gainers
          .map(
                    (stock) => `
                  <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="document.getElementById('stock-search').value='${
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
            <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="document.getElementById('stock-search').value='${
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

/**
 * Populate news feed with articles
 * @param {string} symbol - Optional stock symbol to filter news
 */
async function populateNewsFeed(symbol = null) {
  const searchInput = document.getElementById('stock-search');
  const currentSymbol = symbol || searchInput.value.toUpperCase().trim();
  
  try {
    const data = await fetchNews(currentSymbol);
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

/**
 * Initialize smooth scrolling for navigation links
 */
function initializeSmoothScrolling() {
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
}

/**
 * Initialize all UI components
 */
function initializeUI() {
  initializeTheme();
  initializeMobileMenu();
  initializeSmoothScrolling();
  
  // Set current year
  document.getElementById('currentYear').textContent = new Date().getFullYear();
  
  // Initialize data loading
  populateTicker();
  populateMarketMovers();
  populateNewsFeed();
  
  // Set up periodic updates
  setInterval(populateTicker, 30000); // Update ticker every 30 seconds
  setInterval(populateMarketMovers, 15000); // Update market movers every 15 seconds
  
  // Set up news feed updates on search
  const searchButton = document.getElementById('search-button');
  const searchInput = document.getElementById('stock-search');
  searchButton.addEventListener('click', () => populateNewsFeed());
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      populateNewsFeed();
    }
  });
}
