"""
Stock Data Views - Real-Time Stock Data Retrieval
==================================================

Core stock data endpoints with comprehensive fallback systems.
"""

import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from ._clients import finnhub_client, openai_client, FALLBACK_STOCKS

logger = logging.getLogger(__name__)


def _build_fallback_response(symbol, stock_data, rate_limited=False):
    """Build a fallback response from fallback stock data."""
    return Response({
        "symbol": symbol,
        "name": stock_data['name'],
        "price": stock_data['price'],
        "change": stock_data['change'],
        "changePercent": stock_data['changePercent'],
        "open": stock_data['price'] - stock_data['change'],
        "high": stock_data['price'] + abs(stock_data['change']),
        "low": stock_data['price'] - abs(stock_data['change']),
        "volume": 1000000,
        "marketCap": 0,
        "peRatio": 0,
        "yearHigh": stock_data['price'] + abs(stock_data['change']),
        "yearLow": stock_data['price'] - abs(stock_data['change']),
        "fallback": True,
        **({"rateLimited": True} if rate_limited else {})
    })


def _handle_rate_limit(symbol, cache_key):
    """Handle rate limit errors by trying cache or fallback."""
    logger.warning('Rate limit hit for %s, using cached or fallback data', symbol)
    # Try to return cached data even if expired
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)
    # Use fallback
    if symbol in FALLBACK_STOCKS:
        return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol], True)
    return None


def _get_fallback_or_error(symbol):
    """Get fallback data if available, otherwise return error."""
    if symbol in FALLBACK_STOCKS:
        return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
    return Response(
        {
            "error": (
                f"No data available for symbol {symbol} "
                "(API not configured)"
            )
        },
        status=404
    )


@api_view(["GET"])
def stock_summary(request):
    """
    Advanced Stock Summary - Feature 1: Real-Time Stock Data + AI Analysis
    Endpoint: /api/stock/?symbol=AAPL
    Requires: Both Finnhub API key AND OpenAI API key
    Returns: Stock data + AI-generated summary
    Example: /api/stock/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "AAPL").strip().upper()

    # Handle empty or whitespace symbols
    if not symbol:
        symbol = "AAPL"

    # Check if API keys are available - return error if not
    has_finnhub = settings.FINNHUB_API_KEY and finnhub_client
    has_openai = settings.OPENAI_API_KEY and openai_client

    if not has_finnhub or not has_openai:
        return Response({"error": "API keys not configured"}, status=500)

    try:
        # Fetch stock quote from Finnhub
        quote = finnhub_client.quote(symbol)
        company = finnhub_client.company_profile2(symbol=symbol)

        # Ask OpenAI to summarize
        summary_prompt = f"Summarize this stock data for {symbol}: {quote}"
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        ai_summary = response.choices[0].message.content

        return Response({
            "symbol": symbol,
            "company": company,
            "quote": quote,
            "ai_summary": ai_summary
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_stock_data(request):
    """
    Core Stock Data Retrieval - Feature 1: Real-Time Stock Data
    Endpoint: /api/stock-data/?symbol=AAPL
    Purpose: Get basic stock data for search functionality
    Features: Real-time data, fallback system, input validation, caching
    Example: /api/stock-data/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "").strip().upper()
    force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

    # Handle whitespace-only symbols by using default AAPL
    if not symbol:
        symbol = "AAPL"

    # Track recent searches in session (for chatbot context)
    if 'recent_searches' not in request.session:
        request.session['recent_searches'] = []

    recent_searches = request.session['recent_searches']
    # Remove symbol if it exists (to move it to the end as most recent)
    if symbol in recent_searches:
        recent_searches.remove(symbol)
    # Add symbol to the end (most recent)
    recent_searches.append(symbol)
    # Keep only last 5 searches
    if len(recent_searches) > 5:
        recent_searches.pop(0)
    request.session['recent_searches'] = recent_searches
    request.session.modified = True

    # Define cache_key early so it's available throughout the function
    cache_key = f'stock_data_{symbol}'

    # Check cache first (1 minute cache) - skip if force_refresh is True
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info('Returning cached stock data for %s', symbol)
            return Response(cached_data)
    else:
        logger.info('Force refresh requested for %s, bypassing cache', symbol)

    # Check if API key is available, if not use fallback data
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        return _get_fallback_or_error(symbol)

    try:
        # Fetch stock quote from Finnhub
        try:
            quote = finnhub_client.quote(symbol)
        except Exception as api_error:
            error_str = str(api_error).lower()
            # Check for rate limit errors
            is_rate_limited = (
                'rate limit' in error_str
                or '429' in error_str
                or 'too many requests' in error_str
            )
            if is_rate_limited:
                fallback_response = _handle_rate_limit(symbol, cache_key)
                if fallback_response:
                    return fallback_response
            raise api_error

        # Check if quote data is valid
        if not quote or quote.get('c') is None:
            if symbol in FALLBACK_STOCKS:
                return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
            return Response(
                {"error": f"No data found for symbol {symbol}"},
                status=404
            )

        # Try to get company profile, but don't fail if it's not available
        # Only fetch if we don't have name from quote (reduces API calls)
        company = {}
        company_name = symbol  # Default to symbol
        try:
            # Only fetch company profile if we really need it (reduces API calls)
            # For basic display, we can use symbol as name
            company = finnhub_client.company_profile2(symbol=symbol)
            company_name = company.get('name', symbol)
        except Exception as e:
            logger.warning("Could not fetch company profile for %s: %s", symbol, e)
            company = {}

        # Calculate price change and percentage
        current_price = quote.get('c', 0)
        previous_close = quote.get('pc', 0)
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0

        response_data = {
            "symbol": symbol,
            "name": company_name,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "open": quote.get('o', 0),
            "high": quote.get('h', 0),
            "low": quote.get('l', 0),
            "volume": quote.get('v', 0),
            "marketCap": company.get('marketCapitalization', 0) if company else 0,
            "peRatio": company.get('pe', 0) if company else 0,
            "yearHigh": quote.get('h', 0),  # Using current high as year high for now
            "yearLow": quote.get('l', 0),   # Using current low as year low for now
        }

        # Cache the response for 1 minute
        cache.set(cache_key, response_data, 60)

        return Response(response_data)

    except Exception as e:
        logger.error("Error fetching data for %s: %s", symbol, str(e))
        # Try fallback data if available
        if symbol in FALLBACK_STOCKS:
            return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
        return Response(
            {"error": f"Failed to fetch data for {symbol}: {str(e)}"},
            status=500
        )
