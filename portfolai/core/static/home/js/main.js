/**
 * Application Initialization
 * Coordinates all modules and handles application startup
 */

/**
 * Initialize the application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOMContentLoaded - Initializing application...');
  
  // Initialize all modules in dependency order
  try {
    initializeModals();
    console.log('Modals initialized');
  } catch (e) {
    console.error('Error initializing modals:', e);
  }
  
  try {
    initializeStockSearch();
    console.log('Stock search initialized');
  } catch (e) {
    console.error('Error initializing stock search:', e);
  }
  
  try {
    initializePortfolAIAnalysis();
    console.log('PortfolAI analysis initialized');
  } catch (e) {
    console.error('Error initializing PortfolAI analysis:', e);
  }
  
  try {
    initializeCompanyOverview();
    console.log('Company overview initialized');
  } catch (e) {
    console.error('Error initializing company overview:', e);
  }
  
  try {
    initializeWatchlist();
    console.log('Watchlist initialized');
  } catch (e) {
    console.error('Error initializing watchlist:', e);
  }
  
  try {
    initializeUI();
    console.log('UI initialized');
  } catch (e) {
    console.error('Error initializing UI:', e);
  }
  
  // Set initial application state
  try {
    displayStockDetails(null);
    renderWatchlist();
    console.log('Initial state set');
  } catch (e) {
    console.error('Error setting initial state:', e);
  }
  
  // Set default search if no value
  try {
    const searchInput = getSearchInput();
    if (searchInput && !searchInput.value) {
      console.log('Setting default search to AAPL');
      searchInput.value = 'AAPL';
      performSearch();
    } else if (!searchInput) {
      console.error('Search input element not found!');
    } else {
      console.log('Search input already has value:', searchInput.value);
    }
  } catch (e) {
    console.error('Error performing initial search:', e);
  }
  
  console.log('Application initialization complete');
});
