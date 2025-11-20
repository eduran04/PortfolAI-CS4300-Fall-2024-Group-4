"""
Market Movers Views - Market Analysis Dashboard
================================================

Market analysis endpoints for trending stocks.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from ._clients import MarketDataService


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
