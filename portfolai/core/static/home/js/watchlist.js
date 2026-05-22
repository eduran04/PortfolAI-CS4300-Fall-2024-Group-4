/**
 * Watchlist Management
 * Browser localStorage persistence (demo mode — no server-side storage)
 */

const WATCHLIST_STORAGE_KEY = 'stockWatchlist';

let watchlist = [];

const watchlistItemsDiv = document.getElementById('watchlist-items');
const emptyWatchlistMessage = document.getElementById('empty-watchlist-message');

function saveWatchlist() {
  localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(watchlist));
}

function loadWatchlist() {
  try {
    watchlist = JSON.parse(localStorage.getItem(WATCHLIST_STORAGE_KEY)) || [];
  } catch (error) {
    console.error('Error loading watchlist from localStorage:', error);
    watchlist = [];
  }
  return watchlist;
}

function isStockInWatchlist(symbol) {
  return watchlist.includes(symbol);
}

async function toggleWatchlist(symbol) {
  if (!symbol) return;

  const isInWatchlist = isStockInWatchlist(symbol);

  if (isInWatchlist) {
    const index = watchlist.indexOf(symbol);
    if (index > -1) {
      watchlist.splice(index, 1);
    }
  } else if (!watchlist.includes(symbol)) {
    watchlist.push(symbol);
  }

  saveWatchlist();
  renderWatchlist();

  const searchInput = document.getElementById('stock-search');
  const currentSearchSymbol = searchInput.value.toUpperCase().trim();
  if (currentSearchSymbol === symbol) {
    updateWatchlistButton(symbol);
  }
}

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

async function renderWatchlist() {
  loadWatchlist();

  if (watchlist.length === 0) {
    watchlistItemsDiv.innerHTML = '<tr id="empty-watchlist-message" class="bg-white dark:bg-gray-800"><td colspan="8" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">Your watchlist is empty. Search for a stock and add it!</td></tr>';
    if (emptyWatchlistMessage) emptyWatchlistMessage.classList.remove('hidden');
    return;
  }
  if (emptyWatchlistMessage) emptyWatchlistMessage.classList.add('hidden');

  const fetchedData = await Promise.all(
    watchlist.map(async (symbol, index) => {
      try {
        const stockData = await fetchStockData(symbol);
        return { symbol, index, data: stockData, error: null };
      } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        return { symbol, index, data: null, error: error.message };
      }
    })
  );

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

async function initializeWatchlist() {
  loadWatchlist();
  await renderWatchlist();

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
