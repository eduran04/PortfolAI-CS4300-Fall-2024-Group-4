"""
PortfolAI Views Package
========================

This package contains all view functions and classes organized by feature.
All views are imported here for backward compatibility with existing imports.
"""

from ._clients import (
    finnhub_client,
    newsapi,
    MarketDataService,
    FALLBACK_STOCKS,
    FALLBACK_NEWS,
)

from .basic import landing, trading_dashboard, markets_view, learn_view, hello_api
from .auth import DemoLoginView
from .stock_data import get_stock_data, stock_summary, stock_search, company_overview
from .market_movers import get_market_movers, get_ticker_data
from .news import get_news, get_market_news
from .analysis import portfolai_analysis
from .chat import chat_api, clear_chat

__all__ = [
    'finnhub_client',
    'newsapi',
    'MarketDataService',
    'FALLBACK_STOCKS',
    'FALLBACK_NEWS',
    'landing',
    'trading_dashboard',
    'markets_view',
    'learn_view',
    'hello_api',
    'DemoLoginView',
    'get_stock_data',
    'stock_summary',
    'stock_search',
    'company_overview',
    'get_market_movers',
    'get_ticker_data',
    'get_news',
    'get_market_news',
    'portfolai_analysis',
    'chat_api',
    'clear_chat',
]
