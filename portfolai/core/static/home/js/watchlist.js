/**
 * Watchlist Management
 * Handles watchlist CRUD operations with database persistence via API
 */

// Watchlist state (loaded from API)
let watchlist = [];

// DOM references
const watchlistItemsDiv = document.getElementById('watchlist-items');
const emptyWatchlistMessage = document.getElementById('empty-watchlist-message');

/**
 * Load watchlist from API
 * @returns {Promise<Array>} Array of stock symbols
 */
async function loadWatchlist() {
  try {
    const response = await fetch('/api/watchlist/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.warn('User not authenticated, watchlist unavailable');
        return [];
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    watchlist = data.symbols || [];
    return watchlist;
  } catch (error) {
    console.error('Error loading watchlist:', error);
    // Return empty array on error
    return [];
  }
}

/**
 * Migrate localStorage watchlist to database
 * Called once on page load if user has localStorage data
 */
async function migrateLocalStorageWatchlist() {
  try {
    const localWatchlist = JSON.parse(localStorage.getItem('stockWatchlist')) || [];
    
    if (localWatchlist.length === 0) {
      return; // Nothing to migrate
    }

    console.log(`Migrating ${localWatchlist.length} items from localStorage to database...`);
    
    // Add each symbol from localStorage to database
    for (const symbol of localWatchlist) {
      try {
        await fetch('/api/watchlist/add/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'same-origin',
          body: JSON.stringify({ symbol: symbol }),
        });
      } catch (error) {
        console.warn(`Failed to migrate ${symbol}:`, error);
      }
    }
    
    // Clear localStorage after successful migration
    localStorage.removeItem('stockWatchlist');
    console.log('LocalStorage watchlist migrated successfully');
    
    // Reload watchlist from API
    await loadWatchlist();
  } catch (error) {
    console.error('Error migrating localStorage watchlist:', error);
  }
}

/**
 * Check if a stock is in the watchlist
 * @param {string} symbol - Stock symbol to check
 * @returns {boolean} True if stock is in watchlist
 */
function isStockInWatchlist(symbol) {
  return watchlist.includes(symbol);
}

/**
 * Toggle a stock in the watchlist (add if not present, remove if present)
 * @param {string} symbol - Stock symbol to toggle
 */
async function toggleWatchlist(symbol) {
  if (!symbol) return;

  const isInWatchlist = isStockInWatchlist(symbol);
  
  try {
    if (isInWatchlist) {
      // Remove from watchlist
      const response = await fetch(`/api/watchlist/remove/?symbol=${encodeURIComponent(symbol)}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Remove from local state
      const index = watchlist.indexOf(symbol);
      if (index > -1) {
        watchlist.splice(index, 1);
      }
    } else {
      // Add to watchlist
      const response = await fetch('/api/watchlist/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({ symbol: symbol }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Add to local state
      if (!watchlist.includes(symbol)) {
        watchlist.push(symbol);
      }
    }

    // Update UI
    renderWatchlist();

    const searchInput = document.getElementById('stock-search');
    const currentSearchSymbol = searchInput.value.toUpperCase().trim();
    if (currentSearchSymbol === symbol) {
      updateWatchlistButton(symbol);
    }
  } catch (error) {
    console.error(`Error toggling watchlist for ${symbol}:`, error);
    alert(`Failed to update watchlist: ${error.message}`);
  }
}

/**
 * Update the watchlist button state and styling
 * @param {string} symbol - Stock symbol to update button for
 */
function updateWatchlistButton(symbol) {
  const addToWatchlistBtn = document.getElementById('addToWatchlistBtn');
  if (!addToWatchlistBtn) return;
  
  const isInWatchlist = isStockInWatchlist(symbol);
  
  addToWatchlistBtn.textContent = isInWatchlist
    ? 'Remove from Watchlist'
    : 'Add to Watchlist';
  
  addToWatchlistBtn.classList.toggle('bg-red-500', isInWatchlist);
  addToWatchlistBtn.classList.toggle('hover:bg-red-600', isInWatchlist);
  addToWatchlistBtn.classList.toggle('bg-green-500', !isInWatchlist);
  addToWatchlistBtn.classList.toggle('hover:bg-green-600', !isInWatchlist);
}

/**
 * Render the watchlist table with current data
 */
async function renderWatchlist() {
  // Ensure watchlist is loaded
  if (watchlist.length === 0) {
    await loadWatchlist();
  }

  if (watchlist.length === 0) {
    watchlistItemsDiv.innerHTML = '<tr id="empty-watchlist-message" class="bg-white dark:bg-gray-800"><td colspan="8" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">Your watchlist is empty. Search for a stock and add it!</td></tr>';
    if (emptyWatchlistMessage) emptyWatchlistMessage.classList.remove('hidden');
    return;
  }
  if (emptyWatchlistMessage) emptyWatchlistMessage.classList.add('hidden');
  
  // Fetch data for each symbol in watchlist
  const fetchedData = await Promise.all(
    watchlist.map(async (symbol, index) => {
      try {
        const stockData = await fetchStockData(symbol);

        return {
          symbol,
          index,
          data: stockData,
          error: null
        };
      } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        return {
          symbol,
          index,
          data: null,
          error: error.message
        };
      }
    })
  );

  // Render data
  const watchlistItems = fetchedData.map((item, index) => {
    if (item.error) {
      const rowClass = index % 2 === 0 
        ? 'bg-white dark:bg-gray-800' 
        : 'bg-gray-50 dark:bg-gray-700';
      return `
      <tr class="${rowClass} border-b dark:border-gray-700">
          <td class="px-6 py-4">
              <div class="font-medium text-gray-900 dark:text-white">${item.symbol}</div>
              <div class="text-xs text-red-500">Error loading data</div>
          </td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4 text-gray-500 dark:text-gray-400">-</td>
          <td class="px-6 py-4">
              <button class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm p-1" onclick="event.stopPropagation(); toggleWatchlist('${item.symbol}');" title="Remove from watchlist">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
              </button>
          </td>
      </tr>
      `;
    }

    const stockData = item.data;
    const changeClass = stockData.change >= 0
      ? 'text-green-500 dark:text-green-400'
      : 'text-red-500 dark:text-red-400';
    const changeSign = stockData.change >= 0 ? '+' : '';

    // Alternating row colors
    const rowClass = index % 2 === 0 
      ? 'bg-white dark:bg-gray-800' 
      : 'bg-gray-50 dark:bg-gray-700';

    return `
    <tr class="${rowClass} border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 cursor-pointer" onclick="document.getElementById('stock-search').value='${item.symbol}'; performSearch(); document.getElementById('stock-search').scrollIntoView({ behavior: 'smooth' });">
        <td class="px-6 py-4">
            <div class="font-medium text-gray-900 dark:text-white">${item.symbol}</div>
            <div class="text-xs text-gray-500 dark:text-gray-400">${stockData.name}</div>
        </td>
        <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white">$${stockData.price.toFixed(2)}</td>
        <td class="px-6 py-4 ${changeClass}">${changeSign}$${Math.abs(stockData.change).toFixed(2)}</td>
        <td class="px-6 py-4 ${changeClass}">${changeSign}${Math.abs(stockData.changePercent).toFixed(2)}%</td>
        <td class="px-6 py-4 text-gray-500 dark:text-gray-400">$${stockData.open.toFixed(2)}</td>
        <td class="px-6 py-4 text-gray-500 dark:text-gray-400">$${stockData.high.toFixed(2)}</td>
        <td class="px-6 py-4 text-gray-500 dark:text-gray-400">$${stockData.low.toFixed(2)}</td>
        <td class="px-6 py-4">
            <button class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm p-1" onclick="event.stopPropagation(); toggleWatchlist('${item.symbol}');" title="Remove from watchlist">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>
        </td>
    </tr>
    `;
  });

  watchlistItemsDiv.innerHTML = watchlistItems.join('');
}

/**
 * Initialize watchlist functionality
 * Loads watchlist from API and migrates localStorage if needed
 */
async function initializeWatchlist() {
  // Check for localStorage data and migrate if user is authenticated
  const localWatchlist = JSON.parse(localStorage.getItem('stockWatchlist')) || [];
  if (localWatchlist.length > 0) {
    // Try to migrate localStorage data to database
    await migrateLocalStorageWatchlist();
  } else {
    // Just load from API
    await loadWatchlist();
  }
  
  // Render the watchlist
  await renderWatchlist();
  
  // Set up button event listener
  const addToWatchlistBtn = document.getElementById('addToWatchlistBtn');
  const searchInput = document.getElementById('stock-search');
  if (addToWatchlistBtn && searchInput) {
    addToWatchlistBtn.addEventListener('click', async () => {
      const symbol = searchInput.value.toUpperCase().trim();
      if (symbol) {
        await toggleWatchlist(symbol);
      }
    });
  }
}
