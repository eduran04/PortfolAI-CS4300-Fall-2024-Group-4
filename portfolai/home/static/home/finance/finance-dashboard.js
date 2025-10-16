// Finance Dashboard JavaScript - Stock Analysis Integration

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('stock-search-input');
    const searchBtn = document.getElementById('search-stock-btn');
    const stockResultsSection = document.getElementById('stock-results-section');
    const stockAnalysisContainer = document.getElementById('stock-analysis-container');

    // Search functionality
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            searchStocks(query);
        }
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchStocks(query);
            }
        }
    });

    // Search stocks function
    async function searchStocks(query) {
        try {
            showLoading();
            
            const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.result && data.result.length > 0) {
                // Get the first result and fetch detailed information
                const stock = data.result[0];
                await fetchStockDetails(stock.symbol);
            } else {
                showError('No stocks found for your search. Please try a different search term.');
            }
        } catch (error) {
            console.error('Search error:', error);
            showError('Failed to search stocks. Please try again.');
        }
    }

    // Fetch detailed stock information
    async function fetchStockDetails(symbol) {
        try {
            const [quoteResponse, profileResponse] = await Promise.all([
                fetch(`/api/quote/?symbol=${symbol}`),
                fetch(`/api/profile/?symbol=${symbol}`)
            ]);

            const quote = await quoteResponse.json();
            const profile = await profileResponse.json();

            if (quote.c && profile.name) {
                displayStockAnalysis({
                    symbol: symbol,
                    quote: quote,
                    profile: profile
                });
            } else {
                showError('Failed to fetch stock details. Please try again.');
            }
        } catch (error) {
            console.error('Details fetch error:', error);
            showError('Failed to fetch stock details. Please try again.');
        }
    }

    // Display stock analysis results
    function displayStockAnalysis(data) {
        const { symbol, quote, profile } = data;
        
        const priceChange = quote.d || 0;
        const percentChange = quote.dp || 0;
        const isPositive = priceChange >= 0;
        
        const stockCard = document.createElement('div');
        stockCard.className = 'stock-card';
        stockCard.innerHTML = `
            <div class="stock-header">
                <div>
                    <div class="stock-symbol">${symbol}</div>
                    <div class="stock-company">${profile.name || 'N/A'}</div>
                </div>
                <div class="text-right">
                    <div class="stock-price">$${quote.c?.toFixed(2) || 'N/A'}</div>
                    <div class="stock-change ${isPositive ? '' : 'negative'}">
                        ${isPositive ? '+' : ''}${priceChange.toFixed(2)} (${isPositive ? '+' : ''}${percentChange.toFixed(2)}%)
                    </div>
                </div>
            </div>
            
            <div class="stock-details">
                <div class="detail-item">
                    <span class="detail-label">High:</span>
                    <span class="detail-value">$${quote.h?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Low:</span>
                    <span class="detail-value">$${quote.l?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Open:</span>
                    <span class="detail-value">$${quote.o?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Previous Close:</span>
                    <span class="detail-value">$${quote.pc?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Market Cap:</span>
                    <span class="detail-value">${profile.marketCapitalization ? formatMarketCap(profile.marketCapitalization) : 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Country:</span>
                    <span class="detail-value">${profile.country || 'N/A'}</span>
                </div>
            </div>
            
            <div class="tw-mt-4 tw-p-4 tw-bg-blue-50 tw-rounded-lg">
                <h4 class="tw-text-lg tw-font-semibold tw-mb-2">AI Analysis Summary</h4>
                <p class="tw-text-gray-700">
                    Based on current market data, ${symbol} is showing ${isPositive ? 'positive' : 'negative'} momentum. 
                    ${isPositive ? 'The stock has gained' : 'The stock has lost'} ${Math.abs(percentChange).toFixed(2)}% today, 
                    indicating ${isPositive ? 'strong' : 'weak'} market sentiment. 
                    ${getAIAnalysis(percentChange, quote.c, quote.h, quote.l)}
                </p>
            </div>
        `;

        stockAnalysisContainer.innerHTML = '';
        stockAnalysisContainer.appendChild(stockCard);
        stockResultsSection.style.display = 'block';
        
        // Scroll to results
        stockResultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Helper function to format market cap
    function formatMarketCap(marketCap) {
        if (marketCap >= 1e12) {
            return `$${(marketCap / 1e12).toFixed(2)}T`;
        } else if (marketCap >= 1e9) {
            return `$${(marketCap / 1e9).toFixed(2)}B`;
        } else if (marketCap >= 1e6) {
            return `$${(marketCap / 1e6).toFixed(2)}M`;
        } else {
            return `$${marketCap.toLocaleString()}`;
        }
    }

    // AI Analysis helper function
    function getAIAnalysis(percentChange, current, high, low) {
        const volatility = ((high - low) / current * 100).toFixed(1);
        
        if (Math.abs(percentChange) > 5) {
            return `High volatility detected (${volatility}% range). Consider this when making investment decisions.`;
        } else if (Math.abs(percentChange) > 2) {
            return `Moderate price movement observed. Monitor for trend continuation.`;
        } else {
            return `Stable price action. Good for conservative analysis.`;
        }
    }

    // Show loading state
    function showLoading() {
        stockAnalysisContainer.innerHTML = '<div class="loading">Analyzing stock data...</div>';
        stockResultsSection.style.display = 'block';
    }

    // Show error state
    function showError(message) {
        stockAnalysisContainer.innerHTML = `<div class="error">${message}</div>`;
        stockResultsSection.style.display = 'block';
    }

    // Initialize with some sample data or instructions
    function initializeDashboard() {
        // You can add any initialization logic here
        console.log('Finance Dashboard initialized');
    }

    // Initialize the dashboard
    initializeDashboard();
});
