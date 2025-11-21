"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    landing,
    trading_dashboard,
    markets_view,
    learn_view,
    hello_api,
    stock_summary,
    get_stock_data,
    stock_search,
    company_overview,
    get_market_movers,
    get_ticker_data,
    get_news,
    get_market_news,
    portfolai_analysis,
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    chat_api,
    clear_chat,
)
from core.views import learn

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("dashboard/", trading_dashboard, name="dashboard"),
    path("markets/", markets_view, name="markets"),
    path("learn/", learn_view, name="learn"),
    # Authentication URLs (login, logout, signup)
    path("accounts/", include('core.urls')),
    # API endpoints
    path("api/hello/", hello_api, name="hello_api"),
    path("api/stock/", stock_summary, name="stock_summary"),
    path("api/stock-data/", get_stock_data, name="get_stock_data"),
    path("api/stock-search/", stock_search, name="stock_search"),
    path("api/company-overview/", company_overview, name="company_overview"),
    path("api/market-movers/", get_market_movers, name="get_market_movers"),
    path("api/ticker/", get_ticker_data, name="get_ticker_data"),
    path("api/news/", get_news, name="get_news"),
    path("api/market-news/", get_market_news, name="get_market_news"),
    path("api/portfolai-analysis/", portfolai_analysis, name="portfolai_analysis"),
    # Chatbot API endpoints
    path("api/chat/", chat_api, name="chat_api"),
    path("api/chat/clear/", clear_chat, name="clear_chat"),
    path("api/chatbot/", chat_api, name="chatbot"),
    # Watchlist endpoints
    path("api/watchlist/", get_watchlist, name="get_watchlist"),
    path("api/watchlist/add/", add_to_watchlist, name="add_to_watchlist"),
    path("api/watchlist/remove/", remove_from_watchlist, name="remove_from_watchlist"),
    # learning resources endpoints
    path("api/learn/topics/", learn.learn_topics, name="learn_topics"),
    path("api/learn/topic/<slug:slug>/", learn.learn_topic_detail, name="learn_topic_detail"),
    path("api/learn/explain/", learn.learn_ai_explanation, name="learn_ai_explanation"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve files from STATICFILES_DIRS
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
