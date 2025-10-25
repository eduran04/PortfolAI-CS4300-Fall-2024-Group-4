/**
 * Modal Management
 * Handles all modal interactions and animations
 */

// Modal DOM references
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const priceAlertModal = document.getElementById('priceAlertModal');

const loginBtnNav = document.getElementById('loginBtnNav');
const loginBtnMobile = document.getElementById('loginBtnMobile');
const closeLoginModalBtn = document.getElementById('closeLoginModal');
const switchToRegisterBtn = document.getElementById('switchToRegister');

const closeRegisterModalBtn = document.getElementById('closeRegisterModal');
const switchToLoginBtn = document.getElementById('switchToLogin');

const closePriceAlertModalBtn = document.getElementById('closePriceAlertModal');

/**
 * Open a modal with animation
 * @param {HTMLElement} modal - The modal element to open
 */
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

/**
 * Close a modal with animation
 * @param {HTMLElement} modal - The modal element to close
 */
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

/**
 * Show the analysis modal with content
 * @param {string} symbol - The stock symbol being analyzed
 * @param {string} analysis - The analysis content to display
 * @param {boolean} isFallback - Whether this is fallback demo data
 */
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

/**
 * Close the analysis modal
 */
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

/**
 * Initialize all modal event listeners
 */
function initializeModals() {
  // Login modal
  [loginBtnNav, loginBtnMobile].forEach((btn) =>
    btn.addEventListener('click', () => openModal(loginModal))
  );
  closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
  switchToRegisterBtn.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal(loginModal);
    openModal(registerModal);
  });

  // Register modal
  closeRegisterModalBtn.addEventListener('click', () =>
    closeModal(registerModal)
  );
  switchToLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal(registerModal);
    openModal(loginModal);
  });

  // Price alert modal
  closePriceAlertModalBtn.addEventListener('click', () =>
    closeModal(priceAlertModal)
  );
}
