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

import finnhub
from newsapi import NewsApiClient
from django.conf import settings
from datetime import datetime
import logging

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
        'title': 'AI Stocks Continue to Lead Market Gains',
        'source': 'TechCrunch',
        'time': '1h ago',
        'url': '#',
        'description': 'Artificial intelligence companies show continued strong performance.'
    }
]


class MarketDataService:
    """
    Service class for handling market data operations.

    Provides methods for retrieving market movers data with comprehensive
    error handling and fallback mechanisms.
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
                try:
                    try:
                        quote = self.finnhub_client.quote(symbol)
                    except Exception as api_error:
                        error_str = str(api_error).lower()
                        # Check for rate limit errors - stop fetching if rate limited
                        is_rate_limited = (
                            'rate limit' in error_str
                            or '429' in error_str
                            or 'too many requests' in error_str
                        )
                        if is_rate_limited:
                            logger.warning(
                                'Rate limit hit while fetching market movers, '
                                'using partial data'
                            )
                            # Break out of loop if rate limited
                            break
                        raise api_error

                    # Check if quote data is valid
                    if not quote or quote.get('c') is None:
                        continue

                    # Skip company profile to reduce API calls - use symbol as name
                    # This reduces API calls by 50% for market movers
                    current_price = quote.get('c', 0)
                    previous_close = quote.get('pc', 0)
                    change = current_price - previous_close
                    if previous_close != 0:
                        change_percent = (change / previous_close * 100)
                    else:
                        change_percent = 0

                    market_data.append({
                        "symbol": symbol,
                        "name": symbol,  # Use symbol as name to avoid extra API call
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_percent, 2)
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch data for {symbol}: {e}")
                    continue  # Skip symbols that fail

            # If no data was collected, use fallback
            if not market_data:
                return self._get_fallback_market_movers()

            # Sort by change percentage
            market_data.sort(key=lambda x: x['changePercent'], reverse=True)

            # Get top 5 gainers and losers
            gainers = market_data[:5]
            losers = market_data[-5:][::-1]  # Reverse to get worst performers first

            return {
                "gainers": gainers,
                "losers": losers
            }

        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            # Return fallback data on error
            return self._get_fallback_market_movers()

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


class NewsService:
    """
    Service class for handling financial news operations.

    Provides methods for retrieving financial news with symbol filtering
    and comprehensive error handling.
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
            return {
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            }

        try:
            if symbol:
                # Get company-specific news using everything endpoint
                try:
                    # Use today's date for better results
                    from_date = datetime.now().strftime('%Y-%m-%d')
                    articles = self.newsapi.get_everything(
                        q=f"{symbol} stock",
                        from_param=from_date,
                        language='en',
                        sort_by='popularity',  # Use popularity as recommended in docs
                        page_size=10
                    )
                except Exception as e:
                    logger.warning(f"News API failed for {symbol}: {e}")
                    # Fallback to top headlines for business category
                    articles = self.newsapi.get_top_headlines(
                        category='business',
                        language='en',
                        page_size=10
                    )
            else:
                # Get general financial market news using top headlines
                try:
                    articles = self.newsapi.get_top_headlines(
                        category='business',
                        language='en',
                        page_size=10
                    )
                except Exception as e:
                    logger.warning(f"News API top headlines failed: {e}")
                    # Fallback to everything endpoint
                    articles = self.newsapi.get_everything(
                        q='stock market OR finance OR economy',
                        language='en',
                        sort_by='popularity',
                        page_size=10
                    )

            # Check if we got valid articles
            if not articles or 'articles' not in articles:
                logger.warning("No articles found in NewsAPI response")
                return {
                    "articles": FALLBACK_NEWS,
                    "totalResults": len(FALLBACK_NEWS),
                    "fallback": True
                }

            news_items = []
            for article in articles.get('articles', []):
                # Skip articles without required fields
                if not article.get('title') or not article.get('url'):
                    continue

                # Format time
                published_time = article.get('publishedAt', '')
                if published_time:
                    try:
                        dt = datetime.fromisoformat(
                            published_time.replace('Z', '+00:00')
                        )
                        time_ago = datetime.now(dt.tzinfo) - dt
                        if time_ago.days > 0:
                            time_str = f"{time_ago.days}d ago"
                        elif time_ago.seconds > 3600:
                            time_str = f"{time_ago.seconds // 3600}h ago"
                        else:
                            time_str = f"{time_ago.seconds // 60}m ago"
                    except Exception:
                        time_str = "Recently"
                else:
                    time_str = "Recently"

                news_items.append({
                    "title": article.get('title', ''),
                    "source": article.get('source', {}).get('name', 'Unknown Source'),
                    "time": time_str,
                    "url": article.get('url', '#'),
                    "description": article.get('description', ''),
                    "publishedAt": published_time
                })

            # If no valid articles found, use fallback
            if not news_items:
                return {
                    "articles": FALLBACK_NEWS,
                    "totalResults": len(FALLBACK_NEWS),
                    "fallback": True
                }

            return {
                "articles": news_items,
                "totalResults": articles.get('totalResults', 0)
            }

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            # Return fallback news on error
            return {
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            }
