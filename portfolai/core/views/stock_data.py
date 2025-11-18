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
from ..api_helpers import is_rate_limit_error

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


def _update_recent_searches(request, symbol):
    """Update recent searches in session for chatbot context."""
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


def _get_cached_stock_data(cache_key, force_refresh):
    """Get cached stock data if available and not forcing refresh."""
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info('Returning cached stock data for %s', cache_key.split('_')[-1])
            return Response(cached_data)
    else:
        logger.info('Force refresh requested for %s, bypassing cache', cache_key.split('_')[-1])
    return None


def _fetch_and_validate_quote(symbol, cache_key):
    """
    Fetch and validate stock quote from API.
    Returns tuple (quote, None) on success, (None, Response) on error/fallback.
    """
    try:
        quote = finnhub_client.quote(symbol)
    except Exception as api_error:  # pylint: disable=broad-exception-caught
        # Check for rate limit errors
        if is_rate_limit_error(api_error):
            fallback_response = _handle_rate_limit(symbol, cache_key)
            if fallback_response:
                return None, fallback_response
        raise api_error

    # Check if quote data is valid
    if not quote or quote.get('c') is None:
        if symbol in FALLBACK_STOCKS:
            return None, _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
        return None, Response(
            {"error": f"No data found for symbol {symbol}"},
            status=404
        )

    return quote, None


def _fetch_company_profile(symbol):
    """
    Fetch company profile from API.
    Returns tuple (company_dict, company_name).
    """
    company = {}
    company_name = symbol  # Default to symbol
    try:
        company = finnhub_client.company_profile2(symbol=symbol)
        company_name = company.get('name', symbol)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not fetch company profile for %s: %s", symbol, e)
        company = {}

    return company, company_name


def _fetch_stock_metrics(symbol):
    """
    Fetch stock metrics including 52-week high/low, P/E ratio, etc.
    Returns metrics dict or empty dict on error.
    """
    try:
        metrics_response = finnhub_client.company_basic_financials(symbol, 'all')
        return metrics_response.get('metric', {})
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not fetch metrics for %s: %s", symbol, e)
        return {}


def _build_stock_response_data(symbol, quote, company, company_name, metrics=None):
    """Build stock response data dictionary from quote, company info, and metrics."""
    # Calculate price change and percentage
    current_price = quote.get('c', 0)
    previous_close = quote.get('pc', 0)
    change = current_price - previous_close
    change_percent = (change / previous_close * 100) if previous_close != 0 else 0

    # Get metrics data if available
    if metrics is None:
        metrics = {}

    # Use accurate 52-week high/low from metrics if available
    year_high = metrics.get('52WeekHigh', quote.get('h', 0))
    year_low = metrics.get('52WeekLow', quote.get('l', 0))

    # Use P/E ratio from metrics if available, fallback to company profile
    pe_ratio = metrics.get('peBasicExclExtraTTM')
    if pe_ratio is None:
        pe_ratio = company.get('pe', 0) if company else 0

    return {
        "symbol": symbol,
        "name": company_name,
        "price": round(current_price, 2),
        "change": round(change, 2),
        "changePercent": round(change_percent, 2),
        "open": quote.get('o', 0),
        "high": quote.get('h', 0),
        "low": quote.get('l', 0),
        "volume": int(quote.get('v', 0)),
        "marketCap": company.get('marketCapitalization', 0) if company else 0,
        "peRatio": round(pe_ratio, 2) if pe_ratio else 0,
        "yearHigh": round(year_high, 2) if year_high else 0,
        "yearLow": round(year_low, 2) if year_low else 0,
    }


@api_view(["GET"])
def stock_search(request):
    """
    Stock Symbol Search - Search for stocks by symbol or company name
    Endpoint: /api/stock-search/?query=apple
    Purpose: Provide autocomplete suggestions for stock search
    Features: Symbol and company name search, US exchange filter, top 10 results
    Example: /api/stock-search/?query=tesla
    """
    query = request.GET.get("query", "").strip()

    # Validate query
    if not query or len(query) < 1:
        return Response({"results": []})

    # Check if API key is available
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        # Return fallback suggestions for common stocks
        fallback_results = _get_fallback_search_results(query)
        return Response({"results": fallback_results, "fallback": True})

    try:
        # Use Finnhub's symbol search endpoint with US exchange filter
        search_results = finnhub_client.symbol_lookup(query)

        if not search_results or 'result' not in search_results:
            return Response({"results": []})

        # Filter to US exchanges only and limit to top 10 results
        us_results = [
            {
                "symbol": item.get("symbol", ""),
                "displaySymbol": item.get("displaySymbol", ""),
                "description": item.get("description", ""),
                "type": item.get("type", "")
            }
            for item in search_results.get("result", [])
            if _is_us_exchange(item.get("symbol", ""))
        ][:10]

        return Response({"results": us_results})

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error searching for stocks with query %s: %s", query, str(e))
        # Return fallback results on error
        fallback_results = _get_fallback_search_results(query)
        return Response({"results": fallback_results, "fallback": True})


def _is_us_exchange(symbol):
    """Check if a symbol belongs to a US exchange (NASDAQ, NYSE, AMEX).

    US stocks have simple symbols like 'AAPL' or share classes like 'BRK.B'.
    International stocks have country suffixes like 'AAPL.SW' (Switzerland).
    """
    if not symbol:
        return False

    # Check if symbol has a dot
    if '.' in symbol:
        # Allow single-letter share classes (.A, .B, .C, etc.)
        parts = symbol.split('.')
        if len(parts) == 2:
            # US share class: base symbol + single letter (e.g., BRK.B)
            if len(parts[1]) == 1 and parts[1].isalpha():
                return True
        # All other dots indicate international exchanges
        return False

    # Exclude symbols with hyphens (often warrants or special securities)
    if '-' in symbol:
        return False

    # Must be all uppercase letters (US convention)
    if not symbol.isalpha() or not symbol.isupper():
        return False

    return True


def _get_fallback_search_results(query):
    """Get fallback search results from predefined stock list."""
    query_lower = query.lower()
    results = []

    # Search through fallback stocks
    for symbol, data in FALLBACK_STOCKS.items():
        name = data.get('name', '')
        # Match by symbol or name
        if (query_lower in symbol.lower()
                or query_lower in name.lower()):
            results.append({
                "symbol": symbol,
                "displaySymbol": symbol,
                "description": name,
                "type": "Common Stock"
            })

    return results[:10]


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

    except Exception as e:  # pylint: disable=broad-exception-caught
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
    _update_recent_searches(request, symbol)

    # Define cache_key early so it's available throughout the function
    cache_key = f'stock_data_{symbol}'

    # Check cache first (1 minute cache) - skip if force_refresh is True
    cached_response = _get_cached_stock_data(cache_key, force_refresh)
    if cached_response:
        return cached_response

    # Check if API key is available, if not use fallback data
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        return _get_fallback_or_error(symbol)

    try:
        # Fetch and validate quote
        quote, error_response = _fetch_and_validate_quote(symbol, cache_key)
        if error_response:
            return error_response

        # Fetch company profile
        company, company_name = _fetch_company_profile(symbol)

        # Fetch stock metrics (52-week high/low, P/E ratio, etc.)
        metrics = _fetch_stock_metrics(symbol)

        # Build response data
        response_data = _build_stock_response_data(symbol, quote, company, company_name, metrics)

        # Cache the response for 1 minute
        cache.set(cache_key, response_data, 60)

        return Response(response_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error fetching data for %s: %s", symbol, str(e))
        # Try fallback data if available
        if symbol in FALLBACK_STOCKS:
            return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
        return Response(
            {"error": f"Failed to fetch data for {symbol}: {str(e)}"},
            status=500
        )
