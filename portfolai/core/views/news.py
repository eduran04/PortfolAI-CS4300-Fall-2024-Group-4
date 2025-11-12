"""
News Views - Financial News Feed
=================================

News aggregation endpoints with symbol filtering.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import logging
from ._clients import newsapi, FALLBACK_NEWS

logger = logging.getLogger(__name__)


def _check_api_error(articles, context=""):
    """Check if API response contains an error and raise if so."""
    if not articles or articles.get('status') != 'error':
        return

    error_msg = articles.get('message', 'Unknown error')
    error_code = articles.get('code', 'unknown')
    logger.warning(f"News API error {context}: {error_code} - {error_msg}")

    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower() or error_code == 'rateLimited':
        logger.error(
            f"News API rate limit reached {context}. "
            "Consider upgrading plan or reducing requests."
        )

    raise Exception(f"News API error: {error_msg}")


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
    except Exception as e:
        logger.warning(f"News API failed for {symbol}: {e}")
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
    except Exception as fallback_error:
        logger.error(f"News API fallback also failed {context}: {fallback_error}")
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
    except Exception as e:
        logger.warning(f"News API top headlines failed: {e}")
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
    except Exception as fallback_error:
        logger.error(f"News API fallback also failed: {fallback_error}")
        raise fallback_error


def _format_time_ago(published_time):
    """Format published time as relative time string."""
    if not published_time:
        return "Recently"

    try:
        dt = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
        time_ago = datetime.now(dt.tzinfo) - dt

        if time_ago.days > 0:
            return f"{time_ago.days}d ago"
        if time_ago.seconds > 3600:
            return f"{time_ago.seconds // 3600}h ago"
        return f"{time_ago.seconds // 60}m ago"
    except Exception:
        return "Recently"


def _process_articles(articles):
    """Process raw articles into formatted news items."""
    news_items = []

    for article in articles.get('articles', []):
        if not article.get('title') or not article.get('url'):
            continue

        published_time = article.get('publishedAt', '')
        news_items.append({
            "title": article.get('title', ''),
            "source": article.get('source', {}).get('name', 'Unknown Source'),
            "time": _format_time_ago(published_time),
            "url": article.get('url', '#'),
            "description": article.get('description', ''),
            "publishedAt": published_time
        })

    return news_items


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
            logger.info(f'Returning cached news data for {symbol or "general"}')
            return Response(cached_data)
    else:
        logger.info(f'Force refresh requested for news {symbol or "general"}, bypassing cache')

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

        news_items = _process_articles(articles)

        if not news_items:
            return Response(_create_fallback_response())

        response_data = {
            "articles": news_items,
            "totalResults": articles.get('totalResults', 0)
        }

        cache.set(cache_key, response_data, 600)
        return Response(response_data)

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        fallback_data = _create_fallback_response()
        cache.set(cache_key, fallback_data, 60)
        return Response(fallback_data)
