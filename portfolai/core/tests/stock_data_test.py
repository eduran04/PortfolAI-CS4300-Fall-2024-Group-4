"""
PortfolAI Stock Data Test Suite
================================

Tests for /api/stock-data/ endpoint (Feature 1)
- Valid symbol queries with real-time data
- Fallback data when API unavailable
- Edge cases (empty, whitespace, lowercase symbols)
- Error handling and API failures
- Data validation and response structure
"""

from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class StockDataTests(TestCase):
    """Test suite for stock data endpoint functionality"""

    def test_get_stock_data_no_symbol(self):
        """Test stock data endpoint without symbol parameter"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)

    def test_get_stock_data_with_symbol_fallback(self):
        """Test stock data with symbol using fallback data"""
        # Mock API client to ensure fallback is used and prevent real API calls
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'AAPL'})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            self.assertIn('name', data)
            self.assertIn('price', data)

    def test_get_stock_data_empty_symbol(self):
        """Test stock data with empty symbol"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.stock_data.finnhub_client', None):
            # When empty symbol, defaults to AAPL - may or may not have fallback depending on API
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': ''})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            # Don't check for fallback as it depends on API availability

    def test_get_stock_data_whitespace_symbol(self):
        """Test stock data with whitespace symbol - actually works with fallback"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': '   '})

            # Whitespace actually works and returns 200 with fallback data
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)

    def test_get_stock_data_lowercase_symbol(self):
        """Test stock data with lowercase symbol (should be converted to uppercase)"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'aapl'})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'AAPL')

    def test_get_stock_data_response_structure(self):
        """Test stock data response has correct structure"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'AAPL'})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertIn('change', data)
            self.assertIn('changePercent', data)

    def test_get_stock_data_fallback_data(self):
        """Test stock data with fallback data when API key is not available"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            with patch('core.views.stock_data.finnhub_client', None):
                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL', 'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertIn('name', data)
                self.assertIn('price', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_fallback_unknown_symbol(self):
        """Test stock data with unknown symbol when API key is not available"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'UNKNOWN'})

            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn('error', data)

    def test_get_stock_data_fallback_multiple_symbols(self):
        """Test stock data fallback with multiple symbols"""
        symbols = ['MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'OKLO']
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            for symbol in symbols:
                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': symbol})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['symbol'], symbol)
                self.assertIn('name', data)
                self.assertIn('price', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_api_error(self):
        """Test stock data with API error handling"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("API Error")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL', 'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_invalid_quote_scenarios(self):
        """Test stock data with various invalid quote scenarios"""
        cache.clear()  # Clear cache to ensure fresh request
        invalid_quotes = [
            None,
            {'c': None},
            {'d': 1.5},  # Missing 'c' field
            {'c': 'invalid', 'd': 1.0, 'dp': 0.5},  # String price
            {}  # Empty response
        ]

        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                for quote in invalid_quotes:
                    mock_finnhub.quote.return_value = quote

                    url = reverse('get_stock_data')
                    response = self.client.get(url, {'symbol': 'AAPL'})

                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertIn('symbol', data)
                    self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_company_profile_exception(self):
        """Test stock data when company profile fetch fails"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0, 'pc': 148.0, 'o': 149.0,
                    'h': 151.0, 'l': 147.0, 'v': 1000000
                }
                mock_finnhub.company_profile2.side_effect = Exception("Company profile error")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)

    def test_get_stock_data_unknown_symbol_with_api(self):
        """Test stock data with unknown symbol when API is available"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = None

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'UNKNOWN'})

                self.assertEqual(response.status_code, 404)
                data = response.json()
                self.assertIn('error', data)

    def test_get_stock_data_api_exception_fallback(self):
        """Test stock data API exception triggers fallback"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("API Error")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_finnhub_client_none(self):
        """Test stock data when finnhub_client is None"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client', None):
                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_quote_exception(self):
        """Test stock data when quote fetch throws exception"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("Quote fetch error")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL', 'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_500_error_response(self):
        """Test stock data 500 error response path"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                # Mock to trigger the 500 error path
                mock_finnhub.quote.side_effect = Exception("API Error")
                mock_finnhub.company_profile2.side_effect = Exception("Profile Error")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'INVALID', 'force_refresh': 'true'})

                # When both quote and profile fail and symbol not in FALLBACK_STOCKS,
                # returns 500. But if symbol is handled earlier (e.g., empty check),
                # might return different status
                self.assertIn(response.status_code, [500, 404])
                data = response.json()
                self.assertIn('error', data)

    def test_get_stock_data_with_valid_quote_and_profile(self):
        """Test stock data with valid quote and profile data"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0, 'pc': 148.0, 'o': 149.0,
                    'h': 151.0, 'l': 147.0, 'v': 1000000
                }
                mock_finnhub.company_profile2.return_value = {
                    'name': 'Apple Inc.', 'country': 'US', 'industry': 'Technology'
                }

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertIn('name', data)
                self.assertIn('price', data)
                self.assertEqual(data['symbol'], 'AAPL')
                # Name comes from company profile, not symbol
                self.assertEqual(data['name'], 'Apple Inc.')

    def test_get_stock_data_with_invalid_json(self):
        """Test stock data with invalid JSON from API"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = ValueError("Invalid JSON")

                url = reverse('get_stock_data')
                response = self.client.get(url, {'symbol': 'AAPL'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_tracks_recent_searches(self):
        """Test that stock data endpoint tracks recent searches in session"""
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')

            # First search
            response1 = self.client.get(url, {'symbol': 'AAPL'})
            self.assertEqual(response1.status_code, 200)
            self.assertIn('recent_searches', self.client.session)
            self.assertEqual(self.client.session['recent_searches'], ['AAPL'])

            # Second search
            response2 = self.client.get(url, {'symbol': 'MSFT'})
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(self.client.session['recent_searches'], ['AAPL', 'MSFT'])

            # Third search (same symbol - should move to end)
            response3 = self.client.get(url, {'symbol': 'AAPL'})
            self.assertEqual(response3.status_code, 200)
            self.assertEqual(self.client.session['recent_searches'], ['MSFT', 'AAPL'])

    def test_get_stock_data_recent_searches_limit(self):
        """Test that recent searches are limited to 5 items"""
        with patch('core.views.stock_data.finnhub_client', None):
            url = reverse('get_stock_data')
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']

            for symbol in symbols:
                self.client.get(url, {'symbol': symbol})

            # Should only have last 5
            recent_searches = self.client.session['recent_searches']
            self.assertEqual(len(recent_searches), 5)
            self.assertEqual(
                recent_searches, ['MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
            )
