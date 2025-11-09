"""
Watchlist Views - User Watchlist Management
============================================

User-specific watchlist endpoints with authentication.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
from ..models import Watchlist

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_watchlist(request):
    """
    Get current user's watchlist
    Endpoint: /api/watchlist/
    Requires: User authentication
    Returns: List of stock symbols in user's watchlist
    """
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        symbols = [item.symbol for item in watchlist_items]
        return Response({
            "symbols": symbols,
            "count": len(symbols)
        })
    except Exception as e:
        logger.error(f"Error fetching watchlist for user {request.user.username}: {str(e)}")
        return Response({"error": f"Failed to fetch watchlist: {str(e)}"}, status=500)


@api_view(["POST"])
def add_to_watchlist(request):
    """
    Add a stock symbol to user's watchlist
    Endpoint: /api/watchlist/
    Method: POST
    Body: {"symbol": "AAPL"}
    Requires: User authentication
    """
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        symbol = request.data.get("symbol", "").strip().upper()
        
        if not symbol:
            return Response({"error": "Symbol is required"}, status=400)
        
        # Check if already in watchlist
        if Watchlist.objects.filter(user=request.user, symbol=symbol).exists():
            return Response({
                "message": f"{symbol} is already in your watchlist",
                "symbol": symbol
            }, status=200)
        
        # Add to watchlist
        Watchlist.objects.create(user=request.user, symbol=symbol)
        
        return Response({
            "message": f"{symbol} added to watchlist",
            "symbol": symbol
        }, status=201)
        
    except Exception as e:
        # Log detailed error information for debugging
        error_type = type(e).__name__
        error_message = str(e)
        symbol_attempted = request.data.get('symbol', 'unknown')
        logger.error(
            f"Error adding {symbol_attempted} to watchlist for user {request.user.username}: "
            f"Type={error_type}, Message={error_message}, "
            f"UserID={request.user.id if request.user.is_authenticated else 'N/A'}"
        )
        return Response({"error": f"Failed to add to watchlist: {error_message}"}, status=500)


@api_view(["DELETE"])
def remove_from_watchlist(request):
    """
    Remove a stock symbol from user's watchlist
    Endpoint: /api/watchlist/remove/?symbol=AAPL
    Method: DELETE
    Body (optional): {"symbol": "AAPL"}
    Requires: User authentication
    """
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        # Support both query params and JSON body (like POST does)
        symbol = request.data.get("symbol") or request.GET.get("symbol", "")
        symbol = symbol.strip().upper() if symbol else ""
        
        if not symbol:
            return Response({"error": "Symbol is required"}, status=400)
        
        # Remove from watchlist
        deleted_count, _ = Watchlist.objects.filter(user=request.user, symbol=symbol).delete()
        
        if deleted_count == 0:
            return Response({
                "message": f"{symbol} is not in your watchlist",
                "symbol": symbol
            }, status=404)
        
        return Response({
            "message": f"{symbol} removed from watchlist",
            "symbol": symbol
        }, status=200)
        
    except Exception as e:
        symbol_attempted = request.data.get('symbol') or request.GET.get('symbol', 'unknown')
        logger.error(f"Error removing {symbol_attempted} from watchlist for user {request.user.username}: {str(e)}")
        return Response({"error": f"Failed to remove from watchlist: {str(e)}"}, status=500)

