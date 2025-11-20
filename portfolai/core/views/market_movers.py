"""
Market Movers Views - Market Analysis Dashboard
================================================

Market analysis endpoints for trending stocks.
"""

import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from ._clients import MarketDataService, finnhub_client

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_market_movers(_request):
    """
    Market Movers Dashboard - Feature 2: Top Gainers & Losers
    Endpoint: /api/market-movers/
    Purpose: Get top gainers and losers from the market
    Features: Real-time market data, sorted by percentage change, caching
    Example: /api/market-movers/
    """
    # Check cache first (5 minute cache)
    cache_key = 'market_movers'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    try:
        # Use service layer to handle business logic
        market_data_service = MarketDataService()
        market_movers_data = market_data_service.get_market_movers()

        # Ensure we always return valid data structure
        if not market_movers_data:
            # Access protected method for fallback behavior
            # pylint: disable=protected-access
            market_movers_data = market_data_service._get_fallback_market_movers()

        # Ensure gainers and losers are always lists
        if 'gainers' not in market_movers_data:
            market_movers_data['gainers'] = []
        if 'losers' not in market_movers_data:
            market_movers_data['losers'] = []

        # Cache the response for 5 minutes (300 seconds)
        cache.set(cache_key, market_movers_data, 300)

        return Response(market_movers_data)

    except Exception:  # pylint: disable=broad-exception-caught
        # Return fallback data on error instead of error response
        try:
            market_data_service = MarketDataService()
            # Access protected method for fallback behavior
            # pylint: disable=protected-access
            fallback_data = market_data_service._get_fallback_market_movers()
            return Response(fallback_data)
        except Exception:  # pylint: disable=broad-exception-caught
            # Last resort - return empty structure
            return Response({
                "gainers": [],
                "losers": [],
                "fallback": True,
                "error": "Unable to retrieve market movers"
            })


@api_view(["GET"])
def get_ticker_data(request):
    """
    Ticker Data Endpoint - Uses Finnhub for real-time quotes
    Endpoint: /api/ticker/
    Purpose: Get ticker data for fixed list of popular stocks using Finnhub API
    Features: Real-time Finnhub quotes for fixed symbol list, caching
    Example: /api/ticker/
    """
    force_refresh = request.GET.get("force_refresh", "false").lower() == "true"
    
    # Fixed list of ticker symbols
    TICKER_SYMBOLS = [
        "AAPL",   # Apple (fixed from APPL)
        "NVDA",   # NVIDIA
        "AMZN",   # Amazon
        "TSLA",   # Tesla
        "META",   # Meta
        "NFLX",   # Netflix
        "AMD",    # AMD
        "VOO",    # Vanguard S&P 500 ETF
        "GOOGL",  # Google
        "MSFT",   # Microsoft (fixed from MFST)
        "AVGO",   # Broadcom
        "INTC"    # Intel (fixed from INTEL)
    ]
    
    # Check cache first (1 minute cache) - skip if force_refresh is True
    cache_key = 'ticker_data'
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

    try:
        ticker_stocks = []
        
        if settings.FINNHUB_API_KEY and finnhub_client:
            # Fetch quotes from Finnhub for all symbols
            for symbol in TICKER_SYMBOLS:
                try:
                    quote = finnhub_client.quote(symbol)
                    
                    if quote and quote.get('c') is not None:
                        current_price = quote.get('c', 0)
                        previous_close = quote.get('pc', 0)
                        change = current_price - previous_close
                        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                        
                        stock_data = {
                            "symbol": symbol,
                            "name": symbol,
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "changePercent": round(change_percent, 2)
                        }
                        ticker_stocks.append(stock_data)
                            
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.warning("Failed to fetch Finnhub quote for %s: %s", symbol, str(e))
                    # Skip symbols that fail to fetch
                    continue
        else:
            # No Finnhub API key, return empty structure
            return Response({
                "gainers": [],
                "losers": [],
                "fallback": True,
                "error": "Finnhub API key not configured"
            })
        
        if not ticker_stocks:
            return Response({
                "gainers": [],
                "losers": [],
                "fallback": True,
                "error": "No ticker data available"
            })
        
        # Split into gainers and losers based on change
        ticker_gainers = [stock for stock in ticker_stocks if stock.get('change', 0) >= 0]
        ticker_losers = [stock for stock in ticker_stocks if stock.get('change', 0) < 0]
        
        # Sort gainers by changePercent descending, losers by changePercent ascending
        ticker_gainers.sort(key=lambda x: x.get('changePercent', 0), reverse=True)
        ticker_losers.sort(key=lambda x: x.get('changePercent', 0))
        
        result = {
            "gainers": ticker_gainers,
            "losers": ticker_losers
        }
        
        # Cache the response for 1 minute (60 seconds)
        cache.set(cache_key, result, 60)
        
        return Response(result)
        
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error in get_ticker_data: %s", str(e))
        # Return empty structure on error
        return Response({
            "gainers": [],
            "losers": [],
            "fallback": True,
            "error": "Unable to retrieve ticker data"
        })
