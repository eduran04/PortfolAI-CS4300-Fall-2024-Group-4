"""
Pytest configuration and fixtures for PortfolAI
"""
import os
import sys
import django
import pytest
from django.test import Client

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolai.settings')
django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for tests"""
    pass


@pytest.fixture
def client():
    """Django test client fixture"""
    return Client()


@pytest.fixture
def test_stocks():
    """Test stocks fixture"""
    return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']


@pytest.fixture
def sample_quote_data():
    """Sample quote data for testing"""
    return {
        'c': 150.25,  # current price
        'd': 2.15,    # change
        'dp': 1.45,   # change percent
        'h': 152.00,  # high
        'l': 148.50,  # low
        'o': 149.00,  # open
        'pc': 148.10  # previous close
    }


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return {
        'name': 'Apple Inc.',
        'country': 'US',
        'finnhubIndustry': 'Technology',
        'ticker': 'AAPL',
        'weburl': 'https://www.apple.com',
        'logo': 'https://logo.clearbit.com/apple.com'
    }


@pytest.fixture
def sample_search_data():
    """Sample search data for testing"""
    return {
        'result': [
            {
                'symbol': 'AAPL',
                'description': 'Apple Inc.',
                'type': 'Common Stock'
            },
            {
                'symbol': 'AAPL.L',
                'description': 'Apple Inc. London',
                'type': 'Common Stock'
            }
        ]
    }


@pytest.fixture
def sample_candles_data():
    """Sample candles data for testing"""
    return {
        'c': [150.25, 151.00, 149.50, 152.00, 150.75],  # close prices
        'h': [151.50, 152.25, 150.00, 152.50, 151.25],  # high prices
        'l': [149.75, 150.50, 148.25, 150.75, 149.50],  # low prices
        'o': [150.00, 150.75, 149.25, 151.25, 150.50],  # open prices
        's': 'ok',  # status
        't': [1700000000, 1700086400, 1700172800, 1700259200, 1700345600],  # timestamps
        'v': [1000000, 1200000, 800000, 1500000, 1100000]  # volumes
    }


@pytest.fixture
def sample_market_status_data():
    """Sample market status data for testing"""
    return {
        'isOpen': True,
        'session': 'regular',
        'timezone': 'America/New_York'
    }
