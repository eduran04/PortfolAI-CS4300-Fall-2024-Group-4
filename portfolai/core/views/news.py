"""
News Views - Financial News Feed
=================================

News aggregation endpoints with symbol filtering.
"""

from datetime import datetime, timedelta
import logging
import urllib.parse

import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from ._clients import newsapi, finnhub_client, FALLBACK_NEWS
from ..api_helpers import format_time_ago

logger = logging.getLogger(__name__)


# Reputable financial news sources for filtering
REPUTABLE_SOURCES = [
    'bloomberg', 'reuters', 'financial times', 'wall street journal', 'wsj',
    'cnbc', 'yahoo finance', 'marketwatch', 'forbes', 'business insider',
    'the motley fool', 'seeking alpha', 'benzinga', 'zacks', 'thestreet',
    'barrons', 'financial post', 'investors business daily', 'morningstar',
    'fool.com', 'fool', 'cnbc.com', 'bloomberg.com', 'reuters.com',
    'marketwatch.com', 'forbes.com', 'wsj.com', 'ft.com'
]


def _transform_news_api_article(article):
    """
    Transform The News API article format to match frontend expectations.

    Args:
        article: Article dict from The News API

    Returns:
        dict: Transformed article with standard format
    """
    published_at = article.get('published_at', '')
    image_url = article.get('image_url', '') or article.get('image', '')

    return {
        'title': article.get('title', 'No title'),
        'source': article.get('source', 'Unknown'),
        'publishedAt': published_at,
        'url': article.get('url', '#'),
        'description': article.get('description') or article.get('snippet', ''),
        'image': image_url,
        'image_url': image_url,  # Also include image_url for compatibility
        'time': format_time_ago(published_at),
        'category': ','.join(article.get('categories', [])) if article.get('categories') else ''
    }


def _transform_finnhub_company_news(article):
    """
    Transform Finnhub company news article format to match frontend expectations.

    Args:
        article: Article dict from Finnhub company_news API

    Returns:
        dict: Transformed article with standard format
    """
    # Convert Unix timestamp to ISO format
    published_at = None
    if article.get('datetime'):
        try:
            dt = datetime.fromtimestamp(article['datetime'])
            published_at = dt.isoformat()
        except (ValueError, TypeError, OSError):
            published_at = None

    return {
        'title': article.get('headline', 'No title'),
        'source': article.get('source', 'Unknown'),
        'publishedAt': published_at,
        'url': article.get('url', '#'),
        'description': article.get('summary', ''),
        'image': article.get('image', ''),
        'image_url': article.get('image', ''),  # Also include image_url for compatibility
        'time': format_time_ago(published_at) if published_at else 'Recently',
        'category': article.get('category', 'company news'),
        'related': article.get('related', ''),
        'id': article.get('id', 0)
    }


def _is_reputable_source(source_name):
    """
    Check if a news source is reputable.

    Args:
        source_name: Name of the news source

    Returns:
        bool: True if source is reputable, False otherwise
    """
    if not source_name:
        return False

    source_lower = source_name.lower()
    return any(reputable in source_lower for reputable in REPUTABLE_SOURCES)


def _fetch_thenewsapi_headlines(
    category='business', locale='us', language='en', search=None, limit=10
):
    """
    Fetch news from The News API using the /all endpoint (available on free plan).

    Args:
        category: News category (business, general, tech, etc.)
        locale: Country code (us, gb, etc.)
        language: Language code (en, etc.)
        search: Optional search query
        limit: Number of articles to return

    Returns:
        dict: Response data or None on error
    """
    if not newsapi or not newsapi.get('api_token'):
        return None

    try:
        url = 'https://api.thenewsapi.com/v1/news/all'
        params = {
            'api_token': newsapi['api_token'],
            'locale': locale,
            'language': language,
            'categories': category,
            'limit': min(limit, 50),  # Max 50 on free plan
            'sort': 'published_at'  # Sort by most recent
        }

        if search:
            params['search'] = search

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Check for API errors
        if 'error' in data:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            logger.warning("The News API error: %s", error_msg)
            return None

        return data
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error fetching from The News API: %s", str(e))
        return None


def _fetch_thenewsapi_all(
    category='business', locale='us', language='en',
    search=None, published_after=None, limit=10
):  # pylint: disable=too-many-positional-arguments
    """
    Fetch news from The News API using the /all endpoint with date filtering.

    Args:
        category: News category (business, general, tech, etc.)
        locale: Country code (us, gb, etc.)
        language: Language code (en, etc.)
        search: Optional search query
        published_after: Optional date filter (format: Y-m-d)
        limit: Number of articles to return

    Returns:
        dict: Response data or None on error
    """
    if not newsapi or not newsapi.get('api_token'):
        return None

    try:
        url = 'https://api.thenewsapi.com/v1/news/all'
        params = {
            'api_token': newsapi['api_token'],
            'locale': locale,
            'language': language,
            'categories': category,
            'limit': min(limit, 50),  # Max 50 on free plan
            'sort': 'published_at'  # Sort by most recent
        }

        if search:
            # URL encode the search query to handle special characters like quotes, OR, etc.
            params['search'] = urllib.parse.quote(search)

        if published_after:
            params['published_after'] = published_after

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Check for API errors
        if 'error' in data:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            logger.warning("The News API error: %s", error_msg)
            return None

        return data
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error fetching from The News API: %s", str(e))
        return None


def _extract_articles_from_response(response_data, category=None):
    """
    Extract articles from The News API /all endpoint response.
    Response structure: {"data": [articles...], "meta": {...}}

    Args:
        response_data: The News API response
        category: Optional category filter (not used for /all endpoint, but kept for compatibility)

    Returns:
        list: List of articles
    """
    if not response_data or 'data' not in response_data:
        return []

    articles = response_data.get('data', [])

    # Filter by category if specified (articles have categories array)
    if category and articles:
        filtered = []
        for article in articles:
            article_categories = article.get('categories', [])
            if category in article_categories or not article_categories:
                filtered.append(article)
        return filtered

    return articles if isinstance(articles, list) else []


def _create_fallback_response():
    """Create a fallback response with default news."""
    return {
        "articles": FALLBACK_NEWS,
        "totalResults": len(FALLBACK_NEWS),
        "fallback": True
    }


@api_view(["GET"])
def get_news(request):  # pylint: disable=too-many-return-statements
    """
    Financial News Feed - Feature 3: Market News & Analysis
    Endpoint: /api/news/?symbol=AAPL (optional)
    Purpose: Get financial news - Finnhub company_news for symbols, The News API for general
    Features: General news, symbol-specific filtering (Finnhub), time formatting, caching
    Example: /api/news/?symbol=AAPL (optional)
    """
    symbol = request.GET.get("symbol", "").upper()
    force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

    cache_key = f'news_{symbol or "general"}'

    # If force refresh, clear the cache first
    if force_refresh:
        cache.delete(cache_key)
        logger.info("Force refresh requested for %s news - cache cleared", symbol or 'general')
    else:
        # Check cache only if not forcing refresh
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

    try:
        if symbol:
            # Use Finnhub company_news API for symbol-specific news
            if not settings.FINNHUB_API_KEY or not finnhub_client:
                return Response(_create_fallback_response())

            # Calculate date range for last 30 days
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)

            # Format dates as YYYY-MM-DD
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')

            try:
                # Fetch company news from Finnhub
                company_news_data = finnhub_client.company_news(
                    symbol, _from=from_date_str, to=to_date_str
                )

                if not company_news_data:
                    return Response(_create_fallback_response())

                # Filter for reputable sources and transform articles
                news_items = []
                all_news_items = []

                for article in company_news_data:
                    source_name = article.get('source', '')
                    transformed = _transform_finnhub_company_news(article)
                    all_news_items.append(transformed)

                    # Only include articles from reputable sources in preferred list
                    if _is_reputable_source(source_name):
                        news_items.append(transformed)

                # If no reputable sources found, use all news from last 1-30 days
                if not news_items:
                    logger.info(
                        "No reputable news sources found for %s, "
                        "using all available news from last 30 days",
                        symbol
                    )
                    news_items = all_news_items

                # If still no news items, return fallback
                if not news_items:
                    logger.warning("No news found for %s in the last 30 days", symbol)
                    return Response(_create_fallback_response())

                # Sort by datetime (most recent first)
                news_items.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)

                # Limit to top 10 most recent (frontend will show 3)
                news_items = news_items[:10]

                response_data = {
                    "articles": news_items,
                    "totalResults": len(news_items)
                }

                # Cache for 15 minutes (900 seconds) per stock symbol
                cache.set(cache_key, response_data, 900)
                return Response(response_data)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error fetching Finnhub company news for %s: %s", symbol, str(e))
                return Response(_create_fallback_response())
        else:
            # For general news, use The News API
            if not settings.NEWS_API_KEY or not newsapi:
                return Response(_create_fallback_response())

            # For general news, use business category
            response_data = _fetch_thenewsapi_headlines(
                category='business',
                locale='us',
                language='en',
                limit=20
            )

            if not response_data:
                return Response(_create_fallback_response())

            # Extract articles from response
            raw_articles = _extract_articles_from_response(response_data, category='business')

            if not raw_articles:
                return Response(_create_fallback_response())

            # Transform articles to standard format
            news_items = [_transform_news_api_article(article) for article in raw_articles]

            # Sort articles by recency (most recent first)
            def sort_key(item):
                published_at = item.get('publishedAt', '')
                source_name = item.get('source', '').lower()

                # Popular financial news sources get slight boost
                source_boost = 1 if _is_reputable_source(source_name) else 0

                # Use publishedAt for primary sorting (most recent first)
                try:
                    if published_at:
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                        # Add small boost for popular sources (within same day)
                        return (timestamp + source_boost * 3600, source_boost)
                    return (0, source_boost)
                except Exception:  # pylint: disable=broad-exception-caught
                    return (0, source_boost)

            news_items.sort(key=sort_key, reverse=True)

            response_data = {
                "articles": news_items,
                "totalResults": len(news_items)
            }

            # Cache for 5 minutes (300 seconds) for fresher news
            cache.set(cache_key, response_data, 300)
            return Response(response_data)

    except Exception:  # pylint: disable=broad-exception-caught
        fallback_data = _create_fallback_response()
        cache.set(cache_key, fallback_data, 60)
        return Response(fallback_data)


@api_view(["GET"])
def get_market_news(request):
    """
    Market News Feed - Using Finnhub general_news API
    Endpoint: /api/market-news/?category=general&minId=0
    Purpose: Get market news from Finnhub API
    Features: Category filtering (general, forex, crypto, merger), minId pagination, caching
    Example: /api/market-news/?category=general&minId=0
    """
    category = request.GET.get("category", "general").lower()
    min_id = request.GET.get("minId", "0")

    # Validate category
    valid_categories = ["general", "forex", "crypto", "merger"]
    if category not in valid_categories:
        category = "general"

    # Validate minId
    try:
        min_id = max(int(min_id), 0)
    except (ValueError, TypeError):
        min_id = 0

    cache_key = f'market_news_{category}_{min_id}'

    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # Check if Finnhub client is available
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        return Response({
            "articles": FALLBACK_NEWS[:3],
            "totalResults": min(len(FALLBACK_NEWS), 3),
            "fallback": True,
            "category": category
        })

    try:
        # Fetch news from Finnhub
        news_data = finnhub_client.general_news(category, min_id=min_id)

        if not news_data:
            return Response({
                "articles": FALLBACK_NEWS[:3],
                "totalResults": min(len(FALLBACK_NEWS), 3),
                "fallback": True,
                "category": category
            })

        # Transform Finnhub response format to match frontend expectations
        articles = []
        for item in news_data:
            # Convert Unix timestamp to ISO format
            published_at = None
            if item.get('datetime'):
                try:
                    dt = datetime.fromtimestamp(item['datetime'])
                    published_at = dt.isoformat()
                except (ValueError, TypeError, OSError):
                    published_at = None

            # Format article to match expected structure
            article = {
                'title': item.get('headline', 'No title'),
                'source': item.get('source', 'Unknown'),
                'publishedAt': published_at,
                'url': item.get('url', '#'),
                'description': item.get('summary', ''),
                'image': item.get('image', ''),
                'image_url': item.get('image', ''),  # Also include image_url for compatibility
                'category': item.get('category', category),
                'id': item.get('id', 0),
                'related': item.get('related', ''),
                'time': format_time_ago(published_at) if published_at else 'Recently'
            }
            articles.append(article)

        # Sort by published_at (most recent first) and limit to 3
        articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        articles = articles[:3]

        response_data = {
            "articles": articles,
            "totalResults": len(articles),
            "category": category,
            "minId": min_id
        }

        # Cache for 5 minutes (300 seconds)
        cache.set(cache_key, response_data, 300)
        return Response(response_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        # Log detailed error information for debugging
        error_type = type(e).__name__
        error_message = str(e)
        user_name = (
            request.user.username if request.user.is_authenticated
            else 'anonymous'
        )
        logger.error(
            "Error fetching market news for category '%s': Type=%s, Message=%s, User=%s",
            category, error_type, error_message, user_name
        )
        # Return fallback data on error
        fallback_data = {
            "articles": FALLBACK_NEWS[:3],
            "totalResults": min(len(FALLBACK_NEWS), 3),
            "fallback": True,
            "category": category
        }
        cache.set(cache_key, fallback_data, 60)
        return Response(fallback_data)
