"""
Market Movers Views - Market Analysis Dashboard
================================================

Market analysis endpoints for trending stocks.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
import logging
from ._clients import MarketDataService

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_market_movers(request):
    """
    Market Movers Dashboard - Feature 2: Top Gainers & Losers
    Endpoint: /api/market-movers/
    Purpose: Get top gainers and losers from the market
    Features: Real-time market data, sorted by percentage change, caching
    Example: /api/market-movers/
    """
    # Check cache first (2 minute cache)
    cache_key = 'market_movers'
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info('Returning cached market movers data')
        return Response(cached_data)
    
    try:
        # Use service layer to handle business logic
        market_data_service = MarketDataService()
        market_movers_data = market_data_service.get_market_movers()
        
        # Cache the response for 2 minutes
        cache.set(cache_key, market_movers_data, 120)
        
        return Response(market_movers_data)
        
    except Exception as e:
        logger.error(f"Error in market movers view: {e}")
        return Response({"error": "Unable to retrieve market movers"}, status=500)

