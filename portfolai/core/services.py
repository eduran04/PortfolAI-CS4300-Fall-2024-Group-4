"""
PortfolAI Service Layer - Business Logic Abstraction
===================================================

This module contains service classes that handle business logic for the PortfolAI application.
Services abstract complex operations and API interactions, making views cleaner and more testable.

Services:
- MarketDataService: Handles market movers data retrieval
- NewsService: Handles financial news data retrieval

All services include comprehensive error handling and fallback data
for when external APIs are unavailable.
"""

from datetime import datetime
import logging

import finnhub
from newsapi import NewsApiClient
from django.conf import settings
from .api_helpers import is_rate_limit_error, process_news_articles

logger = logging.getLogger(__name__)

# ============================================================================
# FALLBACK DATA FOR API UNAVAILABILITY
# ============================================================================
# Ensures application remains functional even without external API access

FALLBACK_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'price': 150.25, 'change': 2.15, 'changePercent': 1.45},
    'MSFT': {'name': 'Microsoft Corp.', 'price': 420.72, 'change': -0.50, 'changePercent': -0.12},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 175.60, 'change': 2.10, 'changePercent': 1.21},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 180.97, 'change': -1.80, 'changePercent': -0.98},
    'TSLA': {'name': 'Tesla Inc.', 'price': 177.46, 'change': 3.50, 'changePercent': 2.01},
    'NVDA': {
        'name': 'NVIDIA Corporation',
        'price': 900.55,
        'change': 15.20,
        'changePercent': 1.72
    },
    'META': {
        'name': 'Meta Platforms Inc.',
        'price': 480.10,
        'change': -2.30,
        'changePercent': -0.48
    },
    'OKLO': {'name': 'Oklo Inc.', 'price': 12.45, 'change': 0.85, 'changePercent': 7.33},
}

FALLBACK_NEWS = [
    {
        'title': 'Tech Stocks Rally on Positive Economic Outlook',
        'source': 'Market News Today',
        'time': '2h ago',
        'url': '#',
        'description': (
            'Technology stocks show strong performance amid '
            'positive economic indicators.'
        )
    },
    {
        'title': 'Federal Reserve Hints at Interest Rate Stability',
        'source': 'Global Finance Times',
        'time': '3h ago',
        'url': '#',
        'description': 'Central bank signals potential stability in interest rate policy.'
    },
    {
        'title': 'AGI Lead to End of the World as we know it',
        'source': 'Onion',
        'time': '1h ago',
        'url': '#',
        'description': 'Artificial intelligence companies show continued strong performance.'
    }
]


class MarketDataService:  # pylint: disable=too-few-public-methods
    """
    Service class for handling market data operations.

    Provides methods for retrieving market movers data with comprehensive
    error handling and fallback mechanisms.
    Service class with single public method is acceptable design.
    """

    def __init__(self):
        """Initialize the service with API clients if keys are available."""
        if settings.FINNHUB_API_KEY:
            self.finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)
        else:
            self.finnhub_client = None

    def get_market_movers(self):
        """
        Retrieve market movers data (top gainers and losers).

        Returns:
            dict: Market movers data with gainers and losers lists
        """
        # Check if API key is available, if not use fallback data
        if not settings.FINNHUB_API_KEY or not self.finnhub_client:
            return self._get_fallback_market_movers()

        try:
            # Get stock symbols for major companies
            major_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
                'NVDA', 'META', 'NFLX', 'AMD', 'INTC'
            ]

            market_data = []

            for symbol in major_symbols:
                quote = self._fetch_quote_for_symbol(symbol)
                if quote is None:
                    # Rate limit hit, stop fetching
                    break

                processed_data = self._process_quote_data(symbol, quote)
                if processed_data:
                    market_data.append(processed_data)

            # If no data was collected, use fallback
            if not market_data:
                return self._get_fallback_market_movers()

            return self._build_market_movers_response(market_data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
            logger.error("Error fetching market data: %s", str(e))
            # Return fallback data on error
            return self._get_fallback_market_movers()

    def _fetch_quote_for_symbol(self, symbol):
        """
        Fetch quote data for a single symbol with rate limit detection.

        Args:
            symbol (str): Stock symbol to fetch quote for

        Returns:
            dict or None: Quote data if successful, None if rate limited
        """
        try:
            quote = self.finnhub_client.quote(symbol)
            return quote
        except Exception as api_error:  # pylint: disable=broad-exception-caught
            # Check for rate limit errors - stop fetching if rate limited
            if is_rate_limit_error(api_error):
                logger.warning(
                    'Rate limit hit while fetching market movers, '
                    'using partial data'
                )
                return None
            # Re-raise other exceptions to be caught by outer handler
            raise api_error

    def _process_quote_data(self, symbol, quote):
        """
        Process quote data into market data dictionary format.

        Args:
            symbol (str): Stock symbol
            quote (dict): Quote data from API

        Returns:
            dict or None: Processed market data if valid, None otherwise
        """
        # Check if quote data is valid
        if not quote or quote.get('c') is None:
            return None

        try:
            # Skip company profile to reduce API calls - use symbol as name
            # This reduces API calls by 50% for market movers
            current_price = quote.get('c', 0)
            previous_close = quote.get('pc', 0)
            change = current_price - previous_close

            if previous_close != 0:
                change_percent = change / previous_close * 100
            else:
                change_percent = 0

            return {
                "symbol": symbol,
                "name": symbol,  # Use symbol as name to avoid extra API call
                "price": round(current_price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2)
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various processing errors
            logger.warning("Could not process data for %s: %s", symbol, e)
            return None

    def _build_market_movers_response(self, market_data):
        """
        Sort and format market data into gainers and losers response.

        Args:
            market_data (list): List of market data dictionaries

        Returns:
            dict: Market movers data with gainers and losers lists
        """
        # Sort by change percentage
        market_data.sort(key=lambda x: x['changePercent'], reverse=True)

        # Get top 5 gainers and losers
        gainers = market_data[:5]
        losers = market_data[-5:][::-1]  # Reverse to get worst performers first

        return {
            "gainers": gainers,
            "losers": losers
        }

    def _get_fallback_market_movers(self):
        """Get fallback market movers data when API is unavailable."""
        fallback_stocks = list(FALLBACK_STOCKS.values())
        fallback_stocks.sort(key=lambda x: x['changePercent'], reverse=True)

        gainers = fallback_stocks[:5]
        losers = fallback_stocks[-5:][::-1]

        return {
            "gainers": gainers,
            "losers": losers,
            "fallback": True
        }


class NewsService:  # pylint: disable=too-few-public-methods
    """
    Service class for handling financial news operations.

    Provides methods for retrieving financial news with symbol filtering
    and comprehensive error handling.
    Service class with single public method is acceptable design.
    """

    def __init__(self):
        """Initialize the service with API clients if keys are available."""
        if settings.NEWS_API_KEY:
            self.newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
        else:
            self.newsapi = None

    def get_financial_news(self, symbol=None):
        """
        Retrieve financial news data with optional symbol filtering.

        Args:
            symbol (str, optional): Stock symbol to filter news by

        Returns:
            dict: News data with articles list and metadata
        """
        # Check if API key is available, if not use fallback data
        if not settings.NEWS_API_KEY or not self.newsapi:
            return self._get_fallback_news_response()

        try:
            if symbol:
                articles = self._fetch_symbol_news(symbol)
            else:
                articles = self._fetch_general_news()

            return self._build_news_response(articles)

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
            logger.error("Error fetching news: %s", str(e))
            # Return fallback news on error
            return self._get_fallback_news_response()

    def _fetch_symbol_news(self, symbol):
        """
        Fetch symbol-specific news with fallback to general news.

        Args:
            symbol (str): Stock symbol to fetch news for

        Returns:
            dict: Articles response from API
        """
        def primary_call():
            return self._call_get_everything(
                q=f"{symbol} stock",
                from_param=datetime.now().strftime('%Y-%m-%d')
            )

        def fallback_call():
            return self._call_get_top_headlines(category='business')

        error_message = f"News API failed for {symbol}"

        return self._fetch_news_with_fallback(primary_call, fallback_call, error_message)

    def _fetch_general_news(self):
        """
        Fetch general financial market news with fallback.

        Returns:
            dict: Articles response from API
        """
        def primary_call():
            return self._call_get_top_headlines(category='business')

        def fallback_call():
            return self._call_get_everything(
                q='stock market OR finance OR economy'
            )

        error_message = "News API top headlines failed"

        return self._fetch_news_with_fallback(primary_call, fallback_call, error_message)

    def _fetch_news_with_fallback(self, primary_call, fallback_call, error_message):
        """
        Execute primary API call with fallback on failure.

        Args:
            primary_call (callable): Primary API call to execute
            fallback_call (callable): Fallback API call if primary fails
            error_message (str): Error message for logging

        Returns:
            dict: Articles response from API
        """
        try:
            return primary_call()
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
            logger.warning("%s: %s", error_message, e)
            return fallback_call()

    def _call_get_everything(self, q, **kwargs):
        """
        Call NewsAPI get_everything endpoint with standard parameters.

        Args:
            q (str): Query string
            **kwargs: Additional parameters:
                from_param (str, optional): Date filter
                language (str, optional): Language code (default: 'en')
                sort_by (str, optional): Sort order (default: 'popularity')
                page_size (int, optional): Number of results (default: 10)

        Returns:
            dict: Articles response from API
        """
        params = {
            'q': q,
            'language': kwargs.get('language', 'en'),
            'sort_by': kwargs.get('sort_by', 'popularity'),
            'page_size': kwargs.get('page_size', 10)
        }
        if 'from_param' in kwargs:
            params['from_param'] = kwargs['from_param']
        return self.newsapi.get_everything(**params)

    def _call_get_top_headlines(self, category='business', language='en', page_size=10):
        """
        Call NewsAPI get_top_headlines endpoint with standard parameters.

        Args:
            category (str): News category
            language (str): Language code
            page_size (int): Number of results

        Returns:
            dict: Articles response from API
        """
        return self.newsapi.get_top_headlines(
            category=category,
            language=language,
            page_size=page_size
        )

    def _build_news_response(self, articles):
        """
        Build and validate news response from API articles.

        Args:
            articles (dict): Raw articles response from API

        Returns:
            dict: Formatted news response with articles and metadata
        """
        # Check if we got valid articles
        if not articles or 'articles' not in articles:
            logger.warning("No articles found in NewsAPI response")
            return self._get_fallback_news_response()

        news_items = process_news_articles(articles)

        # If no valid articles found, use fallback
        if not news_items:
            return self._get_fallback_news_response()

        return {
            "articles": news_items,
            "totalResults": articles.get('totalResults', 0)
        }

    def _get_fallback_news_response(self):
        """
        Get fallback news response when API is unavailable.

        Returns:
            dict: Fallback news data with articles and metadata
        """
        return {
            "articles": FALLBACK_NEWS,
            "totalResults": len(FALLBACK_NEWS),
            "fallback": True
        }
