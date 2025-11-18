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


def _build_stock_response_data(symbol, quote, company, company_name):
    """Build stock response data dictionary from quote and company info."""
    # Calculate price change and percentage
    current_price = quote.get('c', 0)
    previous_close = quote.get('pc', 0)
    change = current_price - previous_close
    change_percent = (change / previous_close * 100) if previous_close != 0 else 0

    return {
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

        # Build response data
        response_data = _build_stock_response_data(symbol, quote, company, company_name)

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


@api_view(["GET"])
def search_stock_symbols(request):
    """
    Stock Symbol Search - Autocomplete functionality
    Endpoint: /api/stock-symbols/?query=apple
    Purpose: Search for stock symbols using Finnhub API for autocomplete
    Features: Real-time search, US exchange filtering, caching, fallback
    Example: /api/stock-symbols/?query=apple
    """
    query = request.GET.get("query", "").strip()

    # Handle empty query
    if not query:
        return Response({
            "count": 0,
            "results": []
        })

    # Check cache first (5 minute cache for searches)
    cache_key = f'stock_symbols_search_{query.lower()}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)

    # Check if API key is available
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        # Fallback to static list filtering
        return _get_fallback_symbol_search(query)

    try:
        # Use Finnhub search API
        # Note: If search method doesn't exist, fall back to static list
        try:
            search_result = finnhub_client.search(q=query)
        except AttributeError:
            # If search method doesn't exist, use fallback
            msg = "Finnhub search method not available, using fallback"
            logger.warning(msg)
            return _get_fallback_symbol_search(query)

        if not search_result or 'result' not in search_result:
            return Response({
                "count": 0,
                "results": []
            })

        # Format results: limit to top 10, extract symbol and description
        results = []
        for item in search_result.get('result', [])[:10]:
            results.append({
                "symbol": item.get('displaySymbol', item.get('symbol', '')),
                "description": item.get('description', ''),
                "type": item.get('type', '')
            })

        response_data = {
            "count": len(results),
            "results": results
        }

        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)

        return Response(response_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "Error searching symbols for query '%s': %s", query, str(e)
        )
        # Fallback to static list
        return _get_fallback_symbol_search(query)


def _get_fallback_symbol_search(query):
    """Fallback symbol search using static stock list."""
    query_lower = query.lower().strip()
    results = []

    # Expanded stock metadata with company names and common aliases
    stock_metadata = {
        'AAPL': {
            'name': 'Apple Inc.',
            'aliases': ['apple', 'iphone', 'ipad', 'mac']
        },
        'MSFT': {
            'name': 'Microsoft Corporation',
            'aliases': ['microsoft', 'windows', 'xbox', 'azure']
        },
        'GOOGL': {
            'name': 'Alphabet Inc. (Class A)',
            'aliases': ['google', 'alphabet', 'youtube', 'android']
        },
        'AMZN': {
            'name': 'Amazon.com, Inc.',
            'aliases': ['amazon', 'aws', 'prime']
        },
        'NVDA': {
            'name': 'NVIDIA Corporation',
            'aliases': ['nvidia', 'nvidia corp']
        },
        'TSLA': {
            'name': 'Tesla, Inc.',
            'aliases': ['tesla', 'electric vehicle', 'ev']
        },
        'META': {
            'name': 'Meta Platforms, Inc.',
            'aliases': ['meta', 'facebook', 'instagram', 'whatsapp']
        },
        'NFLX': {'name': 'Netflix, Inc.', 'aliases': ['netflix']},
        'DIS': {
            'name': 'The Walt Disney Company',
            'aliases': ['disney', 'walt disney']
        },
        'JPM': {
            'name': 'JPMorgan Chase & Co.',
            'aliases': ['jpmorgan', 'jp morgan', 'chase']
        },
        'COST': {
            'name': 'Costco Wholesale Corporation',
            'aliases': ['costco', 'costco wholesale']
        },
        'WMT': {
            'name': 'Walmart Inc.',
            'aliases': ['walmart', 'wal mart']
        },
        'HD': {
            'name': 'The Home Depot, Inc.',
            'aliases': ['home depot', 'homedepot']
        },
        'TGT': {'name': 'Target Corporation', 'aliases': ['target']},
        'NKE': {
            'name': 'Nike, Inc.',
            'aliases': ['nike', 'just do it']
        },
        'SBUX': {
            'name': 'Starbucks Corporation',
            'aliases': ['starbucks', 'starbucks coffee']
        },
        'MCD': {
            'name': "McDonald's Corporation",
            'aliases': ['mcdonalds', "mcdonald's"]
        },
        'BAC': {
            'name': 'Bank of America Corp.',
            'aliases': ['bank of america', 'bofa', 'boa']
        },
        'WFC': {
            'name': 'Wells Fargo & Company',
            'aliases': ['wells fargo']
        },
        'V': {'name': 'Visa Inc.', 'aliases': ['visa']},
        'MA': {
            'name': 'Mastercard Incorporated',
            'aliases': ['mastercard', 'master card']
        },
        'PYPL': {
            'name': 'PayPal Holdings, Inc.',
            'aliases': ['paypal', 'pay pal']
        },
        'INTC': {'name': 'Intel Corporation', 'aliases': ['intel']},
        'AMD': {
            'name': 'Advanced Micro Devices, Inc.',
            'aliases': ['amd', 'advanced micro devices']
        },
        'VOO': {
            'name': 'Vanguard S&P 500 ETF',
            'aliases': ['voo', 'sp500', 's&p 500']
        },
        'SPY': {
            'name': 'SPDR S&P 500 ETF Trust',
            'aliases': ['spy', 'spdr']
        },
        'QQQ': {
            'name': 'Invesco QQQ Trust',
            'aliases': ['qqq', 'nasdaq 100']
        },
        'VTI': {
            'name': 'Vanguard Total Stock Market ETF',
            'aliases': ['vti']
        },
        'ARKK': {
            'name': 'ARK Innovation ETF',
            'aliases': ['arkk', 'ark innovation']
        }
    }

    # Search in fallback stocks first
    for symbol, stock_data in FALLBACK_STOCKS.items():
        symbol_lower = symbol.lower()
        name_lower = stock_data.get('name', '').lower()

        # Match by symbol or company name
        if query_lower in symbol_lower or query_lower in name_lower:
            results.append({
                "symbol": symbol,
                "description": stock_data.get('name', ''),
                "type": "Common Stock"
            })

    # Search in expanded stock metadata
    for symbol, data in stock_metadata.items():
        # Skip if already in results
        if any(r['symbol'] == symbol for r in results):
            continue

        symbol_lower = symbol.lower()
        name_lower = data['name'].lower()
        aliases = [alias.lower() for alias in data.get('aliases', [])]

        # Check if query matches symbol, name, or any alias
        # Also check if query is contained in any of these
        has_alias_match = any(
            query_lower in alias or alias in query_lower
            for alias in aliases
        )
        matches = (
            query_lower == symbol_lower
            or query_lower in symbol_lower
            or query_lower in name_lower
            or has_alias_match
            or any(query_lower == alias for alias in aliases)
        )

        if matches:
            # Calculate match score for sorting (exact matches first)
            score = 0
            if query_lower == symbol_lower:
                score = 100  # Exact symbol match
            elif query_lower in symbol_lower:
                score = 90   # Partial symbol match
            elif any(query_lower == alias for alias in aliases):
                score = 80   # Exact alias match
            elif query_lower in name_lower:
                score = 70   # Name contains query
            else:
                score = 60   # Alias contains query

            results.append({
                "symbol": symbol,
                "description": data['name'],
                "type": "Common Stock",
                "_score": score  # For sorting
            })

    # Sort by match score (highest first), then alphabetically
    results.sort(key=lambda x: (-x.get('_score', 0), x['symbol']))

    # Remove score before returning
    for result in results:
        result.pop('_score', None)

    # Limit to top 10
    results = results[:10]

    return Response({
        "count": len(results),
        "results": results
    })
