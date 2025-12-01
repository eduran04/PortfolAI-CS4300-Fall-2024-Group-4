"""
Watchlist Views - User Watchlist Management
============================================

User-specific watchlist endpoints with authentication.
"""

import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Watchlist
from ..api_helpers import log_error_with_context

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
        watchlist_items = Watchlist.objects.filter(user=request.user)  # pylint: disable=no-member
        symbols = [item.symbol for item in watchlist_items]
        return Response({
            "symbols": symbols,
            "count": len(symbols)
        })
    except Exception as e:  # pylint: disable=broad-exception-caught
        log_error_with_context(
            e, request, logger,
            "Error fetching watchlist: Type=%s, Message=%s, User=%s"
        )
        return Response(
            {
                "error": (
                    "An internal error occurred while fetching your watchlist. "
                    "Please try again later."
                )
            },
            status=500
        )


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
        if Watchlist.objects.filter(  # pylint: disable=no-member
                user=request.user, symbol=symbol
        ).exists():
            return Response({
                "message": f"{symbol} is already in your watchlist",
                "symbol": symbol
            }, status=200)

        # Add to watchlist
        Watchlist.objects.create(user=request.user, symbol=symbol)  # pylint: disable=no-member

        return Response({
            "message": f"{symbol} added to watchlist",
            "symbol": symbol
        }, status=201)

    except Exception as e:  # pylint: disable=broad-exception-caught
        # Log detailed error information for debugging
        symbol_attempted = request.data.get('symbol', 'unknown')
        user_id = request.user.id if request.user.is_authenticated else 'N/A'
        log_error_with_context(
            e, request, logger,
            "Error adding %s to watchlist (UserID=%s): Type=%s, Message=%s, User=%s",
            symbol_attempted, user_id
        )
        return Response(
            {
                "error": (
                    "An internal error occurred while adding to watchlist. "
                    "Please try again later."
                )
            },
            status=500
        )


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
        deleted_count, _ = Watchlist.objects.filter(  # pylint: disable=no-member
            user=request.user, symbol=symbol
        ).delete()

        if deleted_count == 0:
            return Response({
                "message": f"{symbol} is not in your watchlist",
                "symbol": symbol
            }, status=404)

        return Response({
            "message": f"{symbol} removed from watchlist",
            "symbol": symbol
        }, status=200)

    except Exception as e:  # pylint: disable=broad-exception-caught
        symbol_attempted = (
            request.data.get('symbol')
            or request.GET.get('symbol', 'unknown')
        )
        log_error_with_context(
            e, request, logger,
            "Error removing %s from watchlist: Type=%s, Message=%s, User=%s",
            symbol_attempted
        )
        return Response(
            {
                "error": (
                    "An internal error occurred while removing from watchlist. "
                    "Please try again later."
                )
            },
            status=500
        )
