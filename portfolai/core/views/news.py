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
    
    # Check cache first (5 minute cache) - skip if force_refresh is True
    cache_key = f'news_{symbol or "general"}'
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f'Returning cached news data for {symbol or "general"}')
            return Response(cached_data)
    else:
        logger.info(f'Force refresh requested for news {symbol or "general"}, bypassing cache')
    
    # Check if API key is available, if not use fallback data
    if not settings.NEWS_API_KEY or not newsapi:
        return Response({
            "articles": FALLBACK_NEWS,
            "totalResults": len(FALLBACK_NEWS),
            "fallback": True
        })
    
    try:
        if symbol:
            # Get company-specific news using everything endpoint
            # Limit to 3 articles for stock-specific news
            try:
                # Free plan has 24-hour delay, so search from yesterday back to a month ago
                # Use date range to get recent articles (yesterday to 30 days ago)
                to_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday (24h delay)
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
                articles = newsapi.get_everything(
                    q=f"{symbol} stock",
                    from_param=from_date,
                    to=to_date,
                    language='en',
                    sort_by='popularity',  # Use popularity as recommended in docs
                    page_size=3  # Limit to 3 articles for stock-specific news
                )
                # Check if API returned an error response
                if articles and articles.get('status') == 'error':
                    error_msg = articles.get('message', 'Unknown error')
                    error_code = articles.get('code', 'unknown')
                    logger.warning(f"News API error for {symbol}: {error_code} - {error_msg}")
                    # Check for rate limit errors
                    if 'rate' in error_msg.lower() or 'limit' in error_msg.lower() or error_code == 'rateLimited':
                        logger.error(f"News API rate limit reached for {symbol}. Consider upgrading plan or reducing requests.")
                    raise Exception(f"News API error: {error_msg}")
            except Exception as e:
                logger.warning(f"News API failed for {symbol}: {e}")
                # Try fallback to top headlines for business category
                try:
                    articles = newsapi.get_top_headlines(
                        category='business',
                        language='en',
                        page_size=3
                    )
                    # Check if fallback also returned an error
                    if articles and articles.get('status') == 'error':
                        raise Exception(f"News API fallback also failed: {articles.get('message', 'Unknown error')}")
                except Exception as fallback_error:
                    logger.error(f"News API fallback also failed for {symbol}: {fallback_error}")
                    raise fallback_error
        else:
            # Get general financial market news using top headlines
            try:
                articles = newsapi.get_top_headlines(
                    category='business',
                    language='en',
                    page_size=10
                )
                # Check if API returned an error response
                if articles and articles.get('status') == 'error':
                    error_msg = articles.get('message', 'Unknown error')
                    logger.warning(f"News API error for general news: {error_msg}")
                    raise Exception(f"News API error: {error_msg}")
            except Exception as e:
                logger.warning(f"News API top headlines failed: {e}")
                # Fallback to everything endpoint
                try:
                    # Free plan has 24-hour delay, so search from yesterday back to a month ago
                    to_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday (24h delay)
                    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
                    articles = newsapi.get_everything(
                        q='stock market OR finance OR economy',
                        from_param=from_date,
                        to=to_date,
                        language='en',
                        sort_by='popularity',
                        page_size=10
                    )
                    # Check if fallback also returned an error
                    if articles and articles.get('status') == 'error':
                        raise Exception(f"News API fallback also failed: {articles.get('message', 'Unknown error')}")
                except Exception as fallback_error:
                    logger.error(f"News API fallback also failed: {fallback_error}")
                    raise fallback_error
        
        # Check if we got valid articles
        if not articles or 'articles' not in articles:
            print("No articles found in NewsAPI response")
            return Response({
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            })
        
        news_items = []
        for article in articles.get('articles', []):
            # Skip articles without required fields
            if not article.get('title') or not article.get('url'):
                continue
                
            # Format time
            published_time = article.get('publishedAt', '')
            if published_time:
                try:
                    dt = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
                    time_ago = datetime.now(dt.tzinfo) - dt
                    if time_ago.days > 0:
                        time_str = f"{time_ago.days}d ago"
                    elif time_ago.seconds > 3600:
                        time_str = f"{time_ago.seconds // 3600}h ago"
                    else:
                        time_str = f"{time_ago.seconds // 60}m ago"
                except:
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
            return Response({
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            })
        
        response_data = {
            "articles": news_items,
            "totalResults": articles.get('totalResults', 0)
        }
        
        # Cache the response for 10 minutes to reduce API calls (free plan: 100 requests/day)
        # Longer cache helps stay within rate limits
        cache.set(cache_key, response_data, 600)
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        # Return fallback news on error
        fallback_data = {
            "articles": FALLBACK_NEWS,
            "totalResults": len(FALLBACK_NEWS),
            "fallback": True
        }
        # Cache fallback data too (shorter duration)
        cache.set(cache_key, fallback_data, 60)
        return Response(fallback_data)

