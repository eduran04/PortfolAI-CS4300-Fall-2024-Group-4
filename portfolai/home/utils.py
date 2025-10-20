"""
Utility functions for PortfolAI application
"""

import requests
import os
from django.conf import settings
from decouple import config

# Get Finnhub API key from environment
FINNHUB_API_KEY = config('FINNHUB_API_KEY', default='')
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'

# Debug logging for API key
print(f"DEBUG: FINNHUB_API_KEY loaded: {'YES' if FINNHUB_API_KEY else 'NO'}")
if not FINNHUB_API_KEY:
    print("WARNING: FINNHUB_API_KEY is empty or not set!")

def get_stock_quote(symbol):
    """
    Get real-time stock quote from Finnhub API
    """
    try:
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {
            'symbol': symbol.upper(),
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching stock quote for {symbol}: {str(e)}")
        return None

def get_company_profile(symbol):
    """
    Get company profile information from Finnhub API
    """
    try:
        url = f"{FINNHUB_BASE_URL}/stock/profile2"
        params = {
            'symbol': symbol.upper(),
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching company profile for {symbol}: {str(e)}")
        return None

def search_stocks(query):
    """
    Search for stocks using Finnhub API
    """
    try:
        url = f"{FINNHUB_BASE_URL}/search"
        params = {
            'q': query,
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching stocks for {query}: {str(e)}")
        return None

def get_market_status():
    """
    Get market status (open/closed)
    """
    try:
        url = f"{FINNHUB_BASE_URL}/stock/market-status"
        params = {
            'exchange': 'US',
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching market status: {str(e)}")
        return None

def get_top_gainers():
    """
    Get top gaining stocks
    """
    try:
        url = f"{FINNHUB_BASE_URL}/stock/market-status"
        params = {
            'exchange': 'US',
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching top gainers: {str(e)}")
        return None

def get_stock_candles(symbol, resolution='D', count=30):
    """
    Get stock candlestick data for charts
    """
    try:
        url = f"{FINNHUB_BASE_URL}/stock/candle"
        params = {
            'symbol': symbol.upper(),
            'resolution': resolution,
            'count': count,
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        
        # Handle 403 Forbidden (API plan limitation)
        if response.status_code == 403:
            print(f"Warning: Candles API not accessible for {symbol} (403 Forbidden - likely API plan limitation)")
            return None
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching stock candles for {symbol}: {str(e)}")
        return None
