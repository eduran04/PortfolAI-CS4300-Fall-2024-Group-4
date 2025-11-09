"""
PortfolAI Views Package
========================

This package contains all view functions and classes organized by feature.
All views are imported here for backward compatibility with existing imports.
"""

# Import shared API clients for backward compatibility with tests
from ._clients import (
    openai_client,
    finnhub_client,
    newsapi,
    MarketDataService,
    FALLBACK_STOCKS,
    FALLBACK_NEWS,
)

# Basic views
from .basic import landing, trading_dashboard, hello_api

# Authentication views
from .auth import SignUpView

# Stock data views
from .stock_data import get_stock_data, stock_summary

# Market movers views
from .market_movers import get_market_movers

# News views
from .news import get_news

# Analysis views
from .analysis import portfolai_analysis

# Chat views
from .chat import chat_api

# Watchlist views
from .watchlist import get_watchlist, add_to_watchlist, remove_from_watchlist

# Export all views and clients for backward compatibility
__all__ = [
    # API clients (for testing)
    'openai_client',
    'finnhub_client',
    'newsapi',
    'MarketDataService',
    'FALLBACK_STOCKS',
    'FALLBACK_NEWS',
    # Basic views
    'landing',
    'trading_dashboard',
    'hello_api',
    # Authentication
    'SignUpView',
    # Stock data
    'get_stock_data',
    'stock_summary',
    # Market movers
    'get_market_movers',
    # News
    'get_news',
    # Analysis
    'portfolai_analysis',
    # Chat
    'chat_api',
    # Watchlist
    'get_watchlist',
    'add_to_watchlist',
    'remove_from_watchlist',
]

