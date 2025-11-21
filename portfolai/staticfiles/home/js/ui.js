/**
 * UI Components
 * Handles theme, navigation, ticker, market movers, and news functionality
 */

// DOM references - accessed via getter functions to ensure DOM is ready
function getThemeToggleBtn() {
  return document.getElementById('theme-toggle');
}

function getThemeToggleDarkIcon() {
  return document.getElementById('theme-toggle-dark-icon');
}

function getThemeToggleLightIcon() {
  return document.getElementById('theme-toggle-light-icon');
}

function getMobileMenuButton() {
  return document.getElementById('mobile-menu-button');
}

function getMobileMenu() {
  return document.getElementById('mobile-menu');
}

function getTickerMove() {
  return document.querySelector('.ticker-move');
}

function getTopGainersList() {
  return document.getElementById('top-gainers-list');
}

function getTopLosersList() {
  return document.getElementById('top-losers-list');
}

function getNewsFeedDiv() {
  return document.getElementById('news-feed');
}

// Ticker data storage
let tickerData = [];

/**
 * Initialize theme system with localStorage persistence
 */
function initializeTheme() {
  const themeToggleBtn = getThemeToggleBtn();
  const themeToggleDarkIcon = getThemeToggleDarkIcon();
  const themeToggleLightIcon = getThemeToggleLightIcon();
  
  if (!themeToggleBtn || !themeToggleDarkIcon || !themeToggleLightIcon) {
    console.warn('Theme toggle elements not found');
    return;
  }
  
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
  const themeToggleDarkIcon = getThemeToggleDarkIcon();
  const themeToggleLightIcon = getThemeToggleLightIcon();
  
  if (!themeToggleDarkIcon || !themeToggleLightIcon) return;
  
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
  const mobileMenuButton = getMobileMenuButton();
  const mobileMenu = getMobileMenu();
  
  if (!mobileMenuButton || !mobileMenu) {
    console.warn('Mobile menu elements not found');
    return;
  }
  
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
 * @param {boolean} forceRefresh - Force refresh, bypass cache
 */
async function populateTicker(forceRefresh = false) {
  console.log('populateTicker called', forceRefresh ? '(force refresh)' : '(using cache if available)');
  const tickerMove = getTickerMove();
  if (!tickerMove) {
    console.warn('Ticker element not found');
    return;
  }
  
  try {
    console.log('Fetching ticker data (Finnhub quotes)...');
    const data = await fetchTickerData(forceRefresh);
    console.log('Ticker data received:', data);

    // Combine gainers and losers for ticker
    const gainers = data.gainers || [];
    const losers = data.losers || [];
    tickerData = [...gainers, ...losers].filter(stock => stock && stock.symbol); // Filter out invalid entries
    
    if (tickerData.length === 0) {
      tickerMove.innerHTML = '<div class="ticker-item text-gray-400">No market data available</div>';
      return;
    }
    
    let tickerHTML = '';
    // Display each stock twice for continuous scrolling
    for (let i = 0; i < 2; i++) {
      tickerData.forEach((stock) => {
        // Defensive checks for all required fields
        if (!stock || !stock.symbol || stock.price === undefined || stock.change === undefined || stock.changePercent === undefined) {
          console.warn('Invalid stock data in ticker:', stock);
          return;
        }
        
        const changeClass = stock.change >= 0
          ? 'text-green-400'
          : 'text-red-400';
        const changeSign = stock.change >= 0 ? '+' : '';
        
        tickerHTML += `
        <div class="ticker-item inline-flex items-center">
            <span class="font-semibold">${stock.symbol}</span>
            <span class="ml-2 text-sm">$${Number(stock.price).toFixed(2)}</span>
            <span class="ml-1 text-xs ${changeClass}">${changeSign}${Number(stock.change).toFixed(2)} (${changeSign}${Number(stock.changePercent).toFixed(2)}%)</span>
        </div>
    `;
      });
    }
    tickerMove.innerHTML = tickerHTML;

  } catch (error) {
    console.error('Error fetching ticker data:', error);
    tickerMove.innerHTML = '<div class="ticker-item text-gray-400">Error loading market data</div>';
  }
}

/**
 * Populate market movers (gainers and losers) lists
 */
async function populateMarketMovers() {
  console.log('populateMarketMovers called');
  const topGainersList = getTopGainersList();
  const topLosersList = getTopLosersList();
  
  if (!topGainersList || !topLosersList) {
    console.warn('Market movers elements not found');
    return;
  }
  
  try {
    console.log('Fetching market movers...');
    const data = await fetchMarketMovers();
    console.log('Market movers data received:', data);
    const { gainers, losers } = data;

    // Display gainers
    const validGainers = gainers.filter(stock => stock && stock.symbol && stock.price !== undefined && stock.changePercent !== undefined);
    topGainersList.innerHTML = validGainers.length
      ? validGainers
          .map(
                    (stock) => `
                  <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="document.getElementById('stock-search').value='${
                    stock.symbol || ''
                  }'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
                  <div>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">${
                            stock.symbol || 'N/A'
                          }</span>
                          <span class="text-xs text-gray-500 dark:text-gray-400 block">${(stock.name || stock.symbol || '').substring(
                            0,
                            20
                          )}${(stock.name || stock.symbol || '').length > 20 ? '...' : ''}</span>
                          </div>
                          <div class="text-right">
                          <span class="font-medium text-gray-800 dark:text-gray-200">$${Number(stock.price || 0).toFixed(
                            2
                          )}</span>
                          <span class="block text-sm text-green-500 dark:text-green-400">+${Number(stock.changePercent || 0).toFixed(2)}%</span>
                          </div>
                  </li>
              `
          )
          .join('')
      : '<li class="text-sm text-gray-500 dark:text-gray-400">No significant gainers today.</li>';

    // Display losers
    const validLosers = losers.filter(stock => stock && stock.symbol && stock.price !== undefined && stock.changePercent !== undefined);
    topLosersList.innerHTML = validLosers.length
      ? validLosers
          .map(
            (stock) => `
            <li class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-150 cursor-pointer" onclick="document.getElementById('stock-search').value='${
              stock.symbol || ''
            }'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
                <div>
                    <span class="font-semibold text-gray-800 dark:text-gray-200">${
                      stock.symbol || 'N/A'
                    }</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400 block">${(stock.name || stock.symbol || '').substring(
                            0,
                            20
                          )}${(stock.name || stock.symbol || '').length > 20 ? '...' : ''}</span>
                          </div>
                          <div class="text-right">
                              <span class="font-medium text-gray-800 dark:text-gray-200">$${Number(stock.price || 0).toFixed(
                                2
                              )}</span>
                              <span class="block text-sm text-red-500 dark:text-red-400">${Number(stock.changePercent || 0).toFixed(2)}%</span>
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
 * Populate news feed with article(s)
 * @param {string} symbol - Optional stock symbol to filter news (if provided, forces refresh)
 */
async function populateNewsFeed(symbol = null) {
  console.log('populateNewsFeed called with symbol:', symbol);
  const newsFeedDiv = getNewsFeedDiv();
  if (!newsFeedDiv) {
    console.warn('News feed element not found');
    return;
  }

  const searchInput = document.getElementById('stock-search');
  // If symbol is explicitly passed, use it; otherwise check search input
  const currentSymbol = (symbol && symbol.trim()) ? symbol.toUpperCase().trim() : (searchInput ? searchInput.value.toUpperCase().trim() : '');

  // Force refresh if symbol is explicitly provided (from search) or if we have a current symbol from search input
  const shouldForceRefresh = (symbol !== null && symbol !== undefined && symbol !== '');

  // Clear all news caches when switching symbols to prevent stale data
  if (shouldForceRefresh && currentSymbol) {
    // Clear cache for the new symbol and any old symbols
    if (typeof clearCachedData === 'function') {
      clearCachedData(`news_${currentSymbol}`);
      clearCachedData('news_general');
      // Also try to clear any other symbol caches that might exist
      try {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.startsWith('news_') && key !== `news_${currentSymbol}`) {
            clearCachedData(key);
          }
        });
      } catch (e) {
        console.warn('Could not clear all news caches:', e);
      }
    }
  }

  // Show loading state when fetching news
  if (currentSymbol) {
    newsFeedDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">Loading news for ' + currentSymbol + '...</p>';
  } else {
    newsFeedDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">Loading news...</p>';
  }

  try {
    console.log('Fetching news for symbol:', currentSymbol || 'general', 'forceRefresh:', shouldForceRefresh);

    const data = await fetchNews(currentSymbol || null, shouldForceRefresh);
    console.log('News data received:', data);
    console.log('Number of articles:', data.articles ? data.articles.length : 0);
    console.log('Current symbol:', currentSymbol);

    const articles = data.articles || [];
    
    // Verify we have articles for the correct symbol
    if (currentSymbol && articles.length > 0) {
      console.log('First article source:', articles[0].source);
      console.log('First article title:', articles[0].title);
    }

    const displayArticles = currentSymbol ? articles.slice(0, 3) : articles;
    
    // Clear the news feed div completely before rendering new content
    newsFeedDiv.innerHTML = '';

    let fallbackNotice = '';
    if (data.fallback) {
      fallbackNotice = `
        <div class="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-700 dark:text-yellow-300 px-4 py-3 rounded mb-4">
          ⚠️ Using demo news - API not configured or unavailable
        </div>
      `;
    }

    const newsFeed = getNewsFeedDiv();
    if (newsFeed) {
      const newsSection = newsFeed.closest('section');
      if (newsSection) {
        const titleElement = newsSection.querySelector('h2');
        if (titleElement) {
          titleElement.textContent = currentSymbol
            ? `Latest News for ${currentSymbol}`
            : 'Latest News';
        }
      }
    }

    // Build the news feed HTML
    const newsHTML = fallbackNotice +
      (displayArticles.length
        ? displayArticles
            .map(
              (news) => {
                // Handle both old and new format
                const source = news.source || 'Unknown';
                // Backend already provides formatted time, but fallback to formatting if needed
                let time = news.time;
                if (!time && (news.publishedAt || news.published_at)) {
                  const publishedAt = news.publishedAt || news.published_at;
                  try {
                    const date = new Date(publishedAt);
                    const now = new Date();
                    const diffMs = now - date;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffHours = Math.floor(diffMs / 3600000);
                    const diffDays = Math.floor(diffMs / 86400000);
                    
                    if (diffMins < 1) {
                      time = 'Just now';
                    } else if (diffMins < 60) {
                      time = `${diffMins}m ago`;
                    } else if (diffHours < 24) {
                      time = `${diffHours}h ago`;
                    } else if (diffDays < 7) {
                      time = `${diffDays}d ago`;
                    } else {
                      time = date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
                    }
                  } catch (e) {
                    time = 'Recently';
                  }
                }
                const description = news.description || news.snippet || '';
                const truncatedDescription = description.length > 150 
                  ? description.substring(0, 150) + '...' 
                  : description;
                
                // Handle image URL - check multiple possible field names and ensure it's a valid URL
                let imageUrl = news.image || news.image_url || '';
                // If image URL is empty or invalid, use placeholder
                if (!imageUrl || imageUrl.trim() === '' || imageUrl === '#' || !imageUrl.startsWith('http')) {
                  imageUrl = 'https://via.placeholder.com/400x200?text=News';
                }
                
                return `
            <article class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
              <div class="flex flex-col md:flex-row gap-4">
                <div class="md:w-1/3">
                  <img 
                    src="${imageUrl}" 
                    alt="${news.title || 'News image'}"
                    class="w-full h-48 object-cover rounded-md"
                    onerror="this.onerror=null; this.src='https://via.placeholder.com/400x200?text=News'"
                    loading="lazy"
                  />
                </div>
                <div class="md:w-2/3 flex flex-col justify-between">
                  <div>
                    <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                      <a 
                        href="${news.url || '#'}" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                      >
                        ${news.title || 'No title'}
                      </a>
                    </h3>
                    ${
                      truncatedDescription
                        ? `<p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                             ${truncatedDescription}
                           </p>`
                        : ''
                    }
                  </div>
                  <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <div class="flex items-center gap-2">
                      <span class="font-medium">${source}</span>
                      <span>•</span>
                      <span>${time}</span>
                    </div>
                    <a 
                      href="${news.url || '#'}" 
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
              }
            )
            .join('')
        : '<p class="text-sm text-gray-500 dark:text-gray-400">No news available at the moment.</p>');
    
    // Update the DOM with new content
    newsFeedDiv.innerHTML = newsHTML;
    console.log('News feed updated with', displayArticles.length, 'articles for', currentSymbol || 'general news');
  } catch (error) {
    console.error('Error fetching news:', error);
    newsFeedDiv.innerHTML =
      '<p class="text-sm text-red-500 dark:text-red-400">Error loading news. Please try again later.</p>';
  }
}


/**
 * Initialize smooth scrolling for navigation links
 * Only handles anchor links (href starting with #), not forms or other links
 */
function initializeSmoothScrolling() {
  const mobileMenu = getMobileMenu();
  const mobileMenuButton = getMobileMenuButton();
  
  // Only target anchor links within nav that start with # (exclude forms and other links)
  document.querySelectorAll('nav a[href^="#"]').forEach((anchor) => {
    // Double-check it's an anchor link and not inside a form
    if (anchor.tagName === 'A' && anchor.closest('form') === null) {
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

          if (mobileMenu && mobileMenuButton && !mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenuButton
              .querySelectorAll('svg')
              .forEach((icon) => icon.classList.toggle('hidden'));
          }
        }
      });
    }
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
  // Force refresh on initial load to ensure fresh data
  populateTicker(true); // Force refresh on initial load
  populateMarketMovers();
  populateNewsFeed();
  
  // Set up periodic updates
  // Ticker: Refresh every 1 minute, will use cache if available but can make API calls
  setInterval(() => populateTicker(false), 60000); // Update ticker every 1 minute, using cache if available
  // Market movers: Refresh every 2 minutes to reduce API calls
  setInterval(populateMarketMovers, 120000); // Update market movers every 2 minutes (was 15 seconds)
  
  // Set up news feed updates on search
  const searchButton = document.getElementById('search-button');
  const searchInput = document.getElementById('stock-search');
  if (searchButton) {
    searchButton.addEventListener('click', () => populateNewsFeed());
  }
  if (searchInput) {
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        populateNewsFeed();
      }
    });
  }
}
