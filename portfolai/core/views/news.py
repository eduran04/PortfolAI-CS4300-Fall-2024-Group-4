"""
News Views - Financial News Feed
=================================

News aggregation endpoints with symbol filtering.
"""

from datetime import datetime, timedelta
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from ._clients import newsapi, FALLBACK_NEWS
from ..api_helpers import process_news_articles

logger = logging.getLogger(__name__)


def _check_api_error(articles, context=""):
    """Check if API response contains an error and raise if so."""
    if not articles or articles.get('status') != 'error':
        return

    error_msg = articles.get('message', 'Unknown error')
    error_code = articles.get('code', 'unknown')
    logger.warning("News API error %s: %s - %s", context, error_code, error_msg)

    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower() or error_code == 'rateLimited':
        logger.error(
            "News API rate limit reached %s. Consider upgrading plan or reducing requests.",
            context
        )

    # Raise a specific exception for API errors
    # This is intentionally broad to handle various API error scenarios
    raise ValueError(f"News API error: {error_msg}")  # pylint: disable=broad-exception-raised


def _get_date_range():
    """Get date range for news API queries (yesterday to 30 days ago)."""
    to_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    return from_date, to_date


def _get_symbol_news(symbol):
    """Get company-specific news for a symbol."""
    from_date, to_date = _get_date_range()

    try:
        articles = newsapi.get_everything(
            q=f"{symbol} stock",
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='popularity',
            page_size=3
        )
        _check_api_error(articles, f"for {symbol}")
        return articles
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("News API failed for %s: %s", symbol, e)
        return _get_fallback_headlines(page_size=3, context=f"for {symbol}")


def _get_fallback_headlines(page_size=10, context=""):
    """Fallback to top headlines when everything endpoint fails."""
    try:
        articles = newsapi.get_top_headlines(
            category='business',
            language='en',
            page_size=page_size
        )
        _check_api_error(articles, context)
        return articles
    except Exception as fallback_error:  # pylint: disable=broad-exception-caught
        logger.error("News API fallback also failed %s: %s", context, fallback_error)
        raise fallback_error


def _get_general_news():
    """Get general financial market news."""
    try:
        articles = newsapi.get_top_headlines(
            category='business',
            language='en',
            page_size=10
        )
        _check_api_error(articles, "for general news")
        return articles
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("News API top headlines failed: %s", e)
        return _get_fallback_everything()


def _get_fallback_everything():
    """Fallback to everything endpoint when top headlines fails."""
    from_date, to_date = _get_date_range()

    try:
        articles = newsapi.get_everything(
            q='stock market OR finance OR economy',
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='popularity',
            page_size=10
        )
        _check_api_error(articles, "for general news fallback")
        return articles
    except Exception as fallback_error:  # pylint: disable=broad-exception-caught
        logger.error("News API fallback also failed: %s", fallback_error)
        raise fallback_error




def _create_fallback_response():
    """Create a fallback response with default news."""
    return {
        "articles": FALLBACK_NEWS,
        "totalResults": len(FALLBACK_NEWS),
        "fallback": True
    }


@api_view(["GET"])
def get_news(request):
    """
    Financial News Feed - Feature 3: Market News & Analysis
    Endpoint: /api/news/?symbol=AAPL (optional)
    Purpose: Get financial news from NewsAPI.org
    Features: General news, symbol-specific filtering, time formatting, caching
    Example: /api/news/?symbol=AAPL (optional)
    """
    symbol = request.GET.get("symbol", "").upper()
    force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

    cache_key = f'news_{symbol or "general"}'

    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info('Returning cached news data for %s', symbol or "general")
            return Response(cached_data)
    else:
        logger.info('Force refresh requested for news %s, bypassing cache', symbol or "general")

    if not settings.NEWS_API_KEY or not newsapi:
        return Response(_create_fallback_response())

    try:
        if symbol:
            articles = _get_symbol_news(symbol)
        else:
            articles = _get_general_news()

        if not articles or 'articles' not in articles:
            logger.warning("No articles found in NewsAPI response")
            return Response(_create_fallback_response())

        news_items = process_news_articles(articles)

        if not news_items:
            return Response(_create_fallback_response())

        response_data = {
            "articles": news_items,
            "totalResults": articles.get('totalResults', 0)
        }

        cache.set(cache_key, response_data, 600)
        return Response(response_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error fetching news: %s", str(e))
        fallback_data = _create_fallback_response()
        cache.set(cache_key, fallback_data, 60)
        return Response(fallback_data)
