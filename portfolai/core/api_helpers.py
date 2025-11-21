"""
API Helper Functions - Shared Utilities for API Operations
============================================================

This module contains shared utility functions for API operations to eliminate
code duplication across the codebase.
"""

from datetime import datetime
from django.core.cache import cache
from rest_framework.response import Response


def is_rate_limit_error(exception):
    """
    Check if an exception is a rate limit error.

    Args:
        exception: The exception to check

    Returns:
        bool: True if the exception indicates a rate limit error, False otherwise
    """
    error_str = str(exception).lower()
    return (
        'rate limit' in error_str
        or '429' in error_str
        or 'too many requests' in error_str
    )


def format_time_ago(published_time):
    """
    Format published time as relative time string.

    Args:
        published_time: ISO format datetime string or None

    Returns:
        str: Formatted time string (e.g., "2d ago", "3h ago", "15m ago", or "Recently")
    """
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
    except Exception:  # pylint: disable=broad-exception-caught
        return "Recently"


def process_news_articles(articles, format_time_func=None):
    """
    Process raw news articles into formatted news items.

    Args:
        articles: Dictionary containing 'articles' key with list of article dicts
        format_time_func: Optional function to format published time.
                         If None, uses default format_time_ago function.

    Returns:
        list: List of formatted news item dictionaries with keys:
              - title: Article title
              - source: Source name
              - time: Formatted time string
              - url: Article URL
              - description: Article description
              - publishedAt: Original published time string
    """
    if format_time_func is None:
        format_time_func = format_time_ago

    news_items = []

    for article in articles.get('articles', []):
        # Skip articles without required fields
        if not article.get('title') or not article.get('url'):
            continue

        published_time = article.get('publishedAt', '')
        news_items.append({
            "title": article.get('title', ''),
            "source": article.get('source', {}).get('name', 'Unknown Source'),
            "time": format_time_func(published_time),
            "url": article.get('url', '#'),
            "description": article.get('description', ''),
            "publishedAt": published_time
        })

    return news_items


def get_cached_response(cache_key, force_refresh):
    """
    Get cached response if available and not forcing refresh.

    Args:
        cache_key: The cache key to check
        force_refresh: If True, skip cache check

    Returns:
        Response object if cached data found, None otherwise
    """
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    return None
