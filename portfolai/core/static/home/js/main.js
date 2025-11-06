/**
 * Application Initialization
 * Coordinates all modules and handles application startup
 */

/**
 * Initialize the application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
  // Initialize all modules in dependency order
  initializeModals();
  initializeStockSearch();
  initializePortfolAIAnalysis();
  initializeWatchlist();
  initializeUI();
  
  // Set initial application state
  displayStockDetails(null);
  renderWatchlist();
  
  // Set default search if no value
  const searchInput = document.getElementById('stock-search');
  if (!searchInput.value) {
    searchInput.value = 'AAPL';
    performSearch();
  }
});
