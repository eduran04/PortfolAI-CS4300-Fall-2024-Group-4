/**
 * Application Initialization
 * Coordinates all modules and handles application startup
 */

/**
 * Initialize the application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
  try {
    // Initialize all modules in dependency order
    initializeModals();
    initializeStockSearch();
    initializePortfolAIAnalysis();
    initializeWatchlist();
    initializeUI();
    
    // Set initial application state
    displayStockDetails(null);
    renderWatchlist();
    
    // Set default search if no value - with proper error handling
    const searchInput = document.getElementById('stock-search');
    if (searchInput && !searchInput.value) {
      searchInput.value = 'AAPL';
      // Perform search with error handling
      performSearch().catch((error) => {
        console.error('Error performing initial search:', error);
        // Ensure loader is hidden even if search fails
        const chartLoader = document.getElementById('chart-loader');
        if (chartLoader) {
          chartLoader.classList.add('hidden');
        }
      });
    }
  } catch (error) {
    console.error('Error initializing application:', error);
    // Ensure loader is hidden on initialization error
    const chartLoader = document.getElementById('chart-loader');
    if (chartLoader) {
      chartLoader.classList.add('hidden');
    }
  }
});
