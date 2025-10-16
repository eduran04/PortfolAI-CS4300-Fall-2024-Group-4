# urls.py (- SK)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('finance-dashboard/', views.finance_dashboard, name='finance_dashboard'),
    
    # API endpoints
    path('api/search/', views.api_search_stocks, name='api_search_stocks'),
    path('api/quote/', views.api_stock_quote, name='api_stock_quote'),
    path('api/profile/', views.api_company_profile, name='api_company_profile'),
    path('api/market-status/', views.api_market_status, name='api_market_status'),
    path('api/candles/', views.api_stock_candles, name='api_stock_candles'),
]
