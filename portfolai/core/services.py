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
import requests

import finnhub
try:
    from newsapi import NewsApiClient
except ImportError:
    NewsApiClient = None  # pylint: disable=invalid-name

from django.conf import settings
from .api_helpers import process_news_articles

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

    def get_market_movers(self):  # pylint: disable=too-many-return-statements
        """
        Retrieve market movers data (top gainers and losers).

        Returns:
            dict: Market movers data with gainers and losers lists
        """
        # Check if API key is available, if not use fallback data
        if not settings.ALPHA_VANTAGE_API_KEY:
            return self._get_fallback_market_movers()

        try:
            # Use Alpha Vantage TOP_GAINERS_LOSERS endpoint
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TOP_GAINERS_LOSERS",
                "apikey": settings.ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check for Alpha Vantage API errors and validate response
            fallback_reason = self._validate_alpha_vantage_response(data)
            if fallback_reason:
                print(f"Alpha Vantage API issue: {fallback_reason}")
                return self._get_fallback_market_movers()

            # Transform Alpha Vantage response format
            gainers = self._parse_market_movers_items(data.get('top_gainers', [])[:5])
            losers = self._parse_market_movers_items(data.get('top_losers', [])[:5])

            if not gainers and not losers:
                print("No valid gainers or losers after parsing, using fallback")
                return self._get_fallback_market_movers()

            result = {
                "gainers": gainers,
                "losers": losers
            }
            print(
                f"Successfully fetched {len(gainers)} gainers "
                f"and {len(losers)} losers from Alpha Vantage"
            )
            return result

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
            print(f"Exception in get_market_movers: {str(e)}")
            # Return fallback data on error
            return self._get_fallback_market_movers()

    def _validate_alpha_vantage_response(self, data):
        """
        Validate Alpha Vantage API response.

        Args:
            data: Response data from API

        Returns:
            str: Error message if validation fails, None if valid
        """
        if "Error Message" in data:
            return data.get("Error Message", "Unknown error")
        if "Note" in data:
            return data.get("Note", "Rate limit or subscription issue")
        if "Information" in data:
            return data.get("Information", "Rate limit or subscription issue")
        if not data:
            return "Empty response"
        if 'top_gainers' not in data:
            return f"Missing 'top_gainers'. Keys: {list(data.keys())}"
        if 'top_losers' not in data:
            return f"Missing 'top_losers'. Keys: {list(data.keys())}"
        top_gainers = data.get('top_gainers', [])
        top_losers = data.get('top_losers', [])
        if not top_gainers and not top_losers:
            return "Empty top_gainers and top_losers arrays"
        return None

    def _parse_market_movers_items(self, items):
        """
        Parse market movers items from Alpha Vantage response.

        Args:
            items: List of items to parse

        Returns:
            list: Parsed items
        """
        parsed_items = []
        for item in items:
            try:
                ticker = item.get('ticker', '')
                if not ticker:
                    continue

                # Parse change_percentage string (e.g., "448.3959%") to float
                change_percentage_str = item.get('change_percentage', '0%')
                change_percent = float(change_percentage_str.rstrip('%'))

                parsed_items.append({
                    "symbol": ticker,
                    "name": ticker,  # Use ticker as name
                    "price": float(item.get('price', 0)),
                    "change": float(item.get('change_amount', 0)),
                    "changePercent": round(change_percent, 2)
                })
            except (ValueError, TypeError):
                continue
        return parsed_items

    def _get_fallback_market_movers(self):
        """Get fallback market movers data when API is unavailable."""
        print("Using fallback market movers data")
        # Convert dict to list with symbol included
        fallback_stocks = [
            {**stock_data, "symbol": symbol}
            for symbol, stock_data in FALLBACK_STOCKS.items()
        ]
        fallback_stocks.sort(key=lambda x: x['changePercent'], reverse=True)

        gainers = fallback_stocks[:5]
        losers = fallback_stocks[-5:][::-1]

        result = {
            "gainers": gainers,
            "losers": losers,
            "fallback": True
        }
        print(f"Fallback data: {len(gainers)} gainers, {len(losers)} losers")
        return result


class NewsService:  # pylint: disable=too-few-public-methods
    """
    Service class for handling financial news operations.

    Provides methods for retrieving financial news with symbol filtering
    and comprehensive error handling.
    Service class with single public method is acceptable design.
    """

    def __init__(self):
        """Initialize the service with API clients if keys are available."""
        if settings.NEWS_API_KEY and NewsApiClient:
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

        except Exception:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
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

    def _fetch_news_with_fallback(self, primary_call, fallback_call, _error_message):
        """
        Execute primary API call with fallback on failure.

        Args:
            primary_call (callable): Primary API call to execute
            fallback_call (callable): Fallback API call if primary fails
            _error_message (str): Error message for logging (unused, kept for API consistency)

        Returns:
            dict: Articles response from API
        """
        try:
            return primary_call()
        except Exception:  # pylint: disable=broad-exception-caught
            # Catch all exceptions to handle various API errors (network, rate limits, etc.)
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
