"""
Stock Data Views - Real-Time Stock Data Retrieval
==================================================

Core stock data endpoints with comprehensive fallback systems.
"""

import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from ._clients import finnhub_client, openai_client, FALLBACK_STOCKS
from ..api_helpers import is_rate_limit_error


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
            return Response(cached_data)
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
    except Exception:  # pylint: disable=broad-exception-caught
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
    except Exception:  # pylint: disable=broad-exception-caught
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
        "logo": company.get('logo', '') if company else '',
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

        # Filter to US exchanges only, exclude symbols with "." extension,
        # and limit to top 10 results
        us_results = []
        for item in search_results.get("result", []):
            symbol = item.get("symbol", "")

            # Skip if not US exchange
            if not _is_us_exchange(symbol):
                continue

            # Skip symbols with "." extension (e.g., "2212.T", "8051.T")
            if "." in symbol:
                continue

            result_item = {
                "symbol": symbol,
                "displaySymbol": item.get("displaySymbol", ""),
                "description": item.get("description", ""),
                "type": item.get("type", ""),
                "logo": ""  # Will be fetched if available
            }

            # Try to fetch logo from company profile (non-blocking, may fail)
            try:
                company_profile = finnhub_client.company_profile2(symbol=symbol)
                if company_profile and company_profile.get('logo'):
                    result_item["logo"] = company_profile.get('logo', '')
            except Exception:  # pylint: disable=broad-exception-caught
                # Logo fetch failed, continue without logo
                pass

            us_results.append(result_item)

            if len(us_results) >= 10:
                break

        return Response({"results": us_results})

    except Exception:  # pylint: disable=broad-exception-caught
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
def get_stock_data(request):  # pylint: disable=too-many-return-statements
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
        # Try fallback data if available
        if symbol in FALLBACK_STOCKS:
            return _build_fallback_response(symbol, FALLBACK_STOCKS[symbol])
        return Response(
            {"error": f"Failed to fetch data for {symbol}: {str(e)}"},
            status=500
        )


def _format_large_number(value):
    """Format large numbers to billions/trillions."""
    if not value or value == "None" or value == "":
        return None
    try:
        num = float(value)
        if num >= 1_000_000_000_000:
            return round(num / 1_000_000_000_000, 2)
        if num >= 1_000_000_000:
            return round(num / 1_000_000_000, 2)
        if num >= 1_000_000:
            return round(num / 1_000_000, 2)
        return num
    except (ValueError, TypeError):
        return None


def _parse_numeric(value):
    """Parse numeric value from string, return None if invalid."""
    if not value or value == "None" or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@api_view(["GET"])
def company_overview(request):  # pylint: disable=too-many-return-statements
    """
    Company Overview - Get detailed company information using Alpha Vantage OVERVIEW endpoint
    Endpoint: /api/company-overview/?symbol=AAPL
    Purpose: Get comprehensive company overview data
    Features: Company description, financials, valuation, profitability, growth, analyst ratings
    Example: /api/company-overview/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "").strip().upper()
    force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

    if not symbol:
        return Response({"error": "Symbol parameter is required"}, status=400)

    # Check if API key is available
    if not settings.ALPHA_VANTAGE_API_KEY:
        return Response({"error": "Alpha Vantage API key not configured"}, status=500)

    # Check cache first (5 minute cache)
    cache_key = f'company_overview_{symbol}'
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

    try:
        # Fetch from Alpha Vantage OVERVIEW endpoint
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for Alpha Vantage API errors
        if "Error Message" in data:
            return Response({"error": data.get("Error Message", "API error")}, status=500)

        if "Note" in data:
            # Rate limit - try to return cached data even if expired
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
            return Response({"error": "API rate limit reached"}, status=429)

        # Check if we got valid data
        if not data or "Symbol" not in data:
            return Response({"error": "No data available for this symbol"}, status=404)

        # Transform Alpha Vantage flat response into structured format
        overview = {
            "symbol": data.get("Symbol", symbol),
            "name": data.get("Name", ""),
            "description": data.get("Description", ""),
            "sector": data.get("Sector", ""),
            "industry": data.get("Industry", ""),
            "exchange": data.get("Exchange", ""),
            "country": data.get("Country", ""),
            "currency": data.get("Currency", ""),
            "fiscalYearEnd": data.get("FiscalYearEnd", ""),
            "financials": {
                "marketCap": _parse_numeric(data.get("MarketCapitalization")),
                "ebitda": _parse_numeric(data.get("EBITDA")),
                "revenueTTM": _parse_numeric(data.get("RevenueTTM")),
                "grossProfitTTM": _parse_numeric(data.get("GrossProfitTTM")),
                "bookValue": _parse_numeric(data.get("BookValue")),
                "eps": _parse_numeric(data.get("EPS")),
            },
            "valuation": {
                "peRatio": _parse_numeric(data.get("PERatio")),
                "pegRatio": _parse_numeric(data.get("PEGRatio")),
                "priceToBook": _parse_numeric(data.get("PriceToBookRatio")),
                "priceToSales": _parse_numeric(data.get("PriceToSalesRatio")),
                "evToRevenue": _parse_numeric(data.get("EVToRevenue")),
                "evToEbitda": _parse_numeric(data.get("EVToEBITDA")),
            },
            "profitability": {
                "profitMargin": _parse_numeric(data.get("ProfitMargin")),
                "operatingMargin": _parse_numeric(data.get("OperatingMarginTTM")),
                "returnOnAssets": _parse_numeric(data.get("ReturnOnAssetsTTM")),
                "returnOnEquity": _parse_numeric(data.get("ReturnOnEquityTTM")),
            },
            "growth": {
                "earningsGrowthYOY": _parse_numeric(data.get("QuarterlyEarningsGrowthYOY")),
                "revenueGrowthYOY": _parse_numeric(data.get("QuarterlyRevenueGrowthYOY")),
            },
            "analyst": {
                "targetPrice": _parse_numeric(data.get("AnalystTargetPrice")),
                "ratings": {
                    "strongBuy": int(data.get("RatingStrongBuy", 0) or 0),
                    "buy": int(data.get("RatingBuy", 0) or 0),
                    "hold": int(data.get("RatingHold", 0) or 0),
                    "sell": int(data.get("RatingSell", 0) or 0),
                    "strongSell": int(data.get("RatingStrongSell", 0) or 0),
                }
            },
            "technical": {
                "52WeekHigh": _parse_numeric(data.get("52WeekHigh")),
                "52WeekLow": _parse_numeric(data.get("52WeekLow")),
                "50DayMA": _parse_numeric(data.get("50DayMovingAverage")),
                "200DayMA": _parse_numeric(data.get("200DayMovingAverage")),
                "beta": _parse_numeric(data.get("Beta")),
            },
            "shares": {
                "outstanding": _parse_numeric(data.get("SharesOutstanding")),
                "float": _parse_numeric(data.get("SharesFloat")),
                "percentInsiders": _parse_numeric(data.get("PercentInsiders")),
                "percentInstitutions": _parse_numeric(data.get("PercentInstitutions")),
            },
            "dividend": {
                "perShare": _parse_numeric(data.get("DividendPerShare")),
                "yield": _parse_numeric(data.get("DividendYield")),
                "date": data.get("DividendDate", ""),
                "exDate": data.get("ExDividendDate", ""),
            }
        }

        # Cache the response for 5 minutes (300 seconds)
        cache.set(cache_key, overview, 300)

        return Response(overview)

    except Exception as e:  # pylint: disable=broad-exception-caught
        # Try to return cached data even if expired as fallback
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        return Response(
            {"error": f"Failed to fetch company overview: {str(e)}"},
            status=500
        )
