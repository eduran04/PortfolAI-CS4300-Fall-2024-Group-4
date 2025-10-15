"""
Comprehensive test suite for PortfolAI API functionality
Run with: pytest -v
"""
import os
import sys
import django
import json
import pytest
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolai.settings')
django.setup()

from home.utils import get_stock_quote, get_company_profile, search_stocks, get_market_status, get_stock_candles


# Pytest fixtures
@pytest.fixture
def client():
    """Django test client fixture"""
    return Client()


@pytest.fixture
def test_stocks():
    """Test stocks fixture"""
    return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']


# Test utility functions
def test_stock_quote():
    """Test stock quote functionality"""
    quote = get_stock_quote('AAPL')
    assert quote is not None, "Stock quote should not be None"
    assert 'c' in quote, "Quote should contain current price (c)"
    assert isinstance(quote['c'], (int, float)), "Current price should be numeric"


def test_company_profile():
    """Test company profile functionality"""
    profile = get_company_profile('AAPL')
    assert profile is not None, "Company profile should not be None"
    assert 'name' in profile, "Profile should contain company name"
    assert isinstance(profile['name'], str), "Company name should be string"


def test_stock_search():
    """Test stock search functionality"""
    search_results = search_stocks('Apple')
    assert search_results is not None, "Search results should not be None"
    assert 'result' in search_results, "Search results should contain 'result' key"
    assert isinstance(search_results['result'], list), "Search results should be a list"
    assert len(search_results['result']) > 0, "Search should return at least one result"


def test_market_status():
    """Test market status functionality"""
    status = get_market_status()
    assert status is not None, "Market status should not be None"
    assert 'isOpen' in status, "Market status should contain 'isOpen' key"
    assert isinstance(status['isOpen'], bool), "Market open status should be boolean"


@pytest.mark.skipif(True, reason="Candles API requires paid Finnhub plan")
def test_stock_candles():
    """Test historical data functionality"""
    candles = get_stock_candles('AAPL', 'D', 5)
    
    # Handle API access issues gracefully
    if candles is None:
        pytest.skip("Candles API not accessible (403 Forbidden - likely API plan limitation)")
    
    assert 'c' in candles, "Candles should contain close prices (c)"
    assert isinstance(candles['c'], list), "Close prices should be a list"
    assert len(candles['c']) > 0, "Should return at least one data point"


# Test API endpoints
def test_search_api_endpoint(client):
    """Test search API endpoint"""
    response = client.get('/api/search/', {'q': 'Apple'})
    assert response.status_code == 200, "Search API should return 200"
    
    data = response.json()
    assert 'result' in data, "Response should contain 'result' key"
    assert isinstance(data['result'], list), "Result should be a list"


def test_quote_api_endpoint(client):
    """Test quote API endpoint"""
    response = client.get('/api/quote/', {'symbol': 'AAPL'})
    assert response.status_code == 200, "Quote API should return 200"
    
    data = response.json()
    assert 'c' in data, "Response should contain current price (c)"
    assert isinstance(data['c'], (int, float)), "Current price should be numeric"


def test_profile_api_endpoint(client):
    """Test profile API endpoint"""
    response = client.get('/api/profile/', {'symbol': 'AAPL'})
    assert response.status_code == 200, "Profile API should return 200"
    
    data = response.json()
    assert 'name' in data, "Response should contain company name"
    assert isinstance(data['name'], str), "Company name should be string"


def test_market_status_api_endpoint(client):
    """Test market status API endpoint"""
    response = client.get('/api/market-status/')
    assert response.status_code == 200, "Market status API should return 200"
    
    data = response.json()
    assert 'isOpen' in data, "Response should contain 'isOpen' key"
    assert isinstance(data['isOpen'], bool), "Market open status should be boolean"


@pytest.mark.skipif(True, reason="Candles API requires paid Finnhub plan")
def test_candles_api_endpoint(client):
    """Test candles API endpoint"""
    response = client.get('/api/candles/', {
        'symbol': 'AAPL', 
        'resolution': 'D', 
        'count': '5'
    })
    
    # Handle API access issues gracefully
    if response.status_code == 500:
        data = response.json()
        if 'error' in data and '403' in str(data.get('error', '')):
            pytest.skip("Candles API not accessible (403 Forbidden - likely API plan limitation)")
    
    assert response.status_code == 200, f"Candles API should return 200, got {response.status_code}"
    
    data = response.json()
    assert 'c' in data, "Response should contain close prices (c)"
    assert isinstance(data['c'], list), "Close prices should be a list"


# Test error handling
def test_invalid_symbol_quote(client):
    """Test quote API with invalid symbol"""
    response = client.get('/api/quote/', {'symbol': 'INVALID_SYMBOL_12345'})
    # Should either return error data or server error
    assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"


def test_missing_parameters_quote(client):
    """Test quote API with missing parameters"""
    response = client.get('/api/quote/')
    assert response.status_code == 400, f"Expected 400 for missing parameters, got {response.status_code}"


def test_empty_search_query(client):
    """Test search API with empty query"""
    response = client.get('/api/search/', {'q': ''})
    assert response.status_code == 400, f"Expected 400 for empty query, got {response.status_code}"


# Test multiple stocks
@pytest.mark.parametrize("symbol", ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'])
def test_stock_quotes(symbol):
    """Test stock quotes for multiple stocks"""
    quote = get_stock_quote(symbol)
    assert quote is not None, f"Quote for {symbol} should not be None"
    assert 'c' in quote, f"Quote for {symbol} should contain current price"
    assert quote['c'] > 0, f"Price for {symbol} should be positive"


# Test data validation
@pytest.mark.parametrize("field", ['c', 'd', 'dp', 'h', 'l', 'o', 'pc'])
def test_quote_data_structure(field):
    """Test quote data structure"""
    quote = get_stock_quote('AAPL')
    assert quote is not None, "Quote should not be None"
    assert field in quote, f"Quote should contain {field}"
    assert isinstance(quote[field], (int, float)), f"{field} should be numeric"


@pytest.mark.parametrize("field", ['name', 'country', 'finnhubIndustry'])
def test_profile_data_structure(field):
    """Test profile data structure"""
    profile = get_company_profile('AAPL')
    assert profile is not None, "Profile should not be None"
    assert field in profile, f"Profile should contain {field}"
    assert isinstance(profile[field], str), f"{field} should be string"


def test_search_results_structure():
    """Test search results structure"""
    search_results = search_stocks('Apple')
    assert search_results is not None, "Search results should not be None"
    assert 'result' in search_results, "Search results should contain 'result' key"
    
    results_list = search_results['result']
    assert isinstance(results_list, list), "Results should be a list"
    assert len(results_list) > 0, "Should have at least one result"
    
    if results_list:
        first_result = results_list[0]
        required_fields = ['symbol', 'description']
        for field in required_fields:
            assert field in first_result, f"Result should contain {field}"
            assert isinstance(first_result[field], str), f"{field} should be string"


# Test markers for pytest
pytestmark = pytest.mark.django_db
