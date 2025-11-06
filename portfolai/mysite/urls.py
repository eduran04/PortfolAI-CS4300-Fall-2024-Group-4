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
from core.views import landing, trading_dashboard, hello_api, stock_summary, get_stock_data, get_market_movers, get_news, portfolai_analysis

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("dashboard/", trading_dashboard, name="dashboard"),
    path("accounts/", include('core.urls')),
    path("api/hello/", hello_api, name="hello_api"),
    path("api/stock/", stock_summary, name="stock_summary"),
    path("api/stock-data/", get_stock_data, name="get_stock_data"),
    path("api/market-movers/", get_market_movers, name="get_market_movers"),
    path("api/news/", get_news, name="get_news"),
    path("api/portfolai-analysis/", portfolai_analysis, name="portfolai_analysis"),
]
