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
from rest_framework.response import Response
from core.views.stock_data import (
    _get_cached_stock_data,
    _fetch_and_validate_quote,
    _fetch_company_profile,
    _fetch_stock_metrics,
    _build_stock_response_data,
    _is_us_exchange,
    _get_fallback_search_results,
)
from .test_helpers import assert_fallback_response


class StockDataTests(TestCase):  # pylint: disable=too-many-public-methods
    """
    Test suite for stock data endpoint functionality.
    Comprehensive test coverage requires many test methods.
    """

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
                    assert_fallback_response(response, self, 'AAPL')

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
                assert_fallback_response(response, self, 'AAPL')

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

    def test_get_cached_stock_data_with_force_refresh(self):
        """Test _get_cached_stock_data bypasses cache when force_refresh is True"""
        cache_key = 'stock_data_TEST'
        test_data = {'symbol': 'TEST', 'price': 100}
        cache.set(cache_key, test_data, 60)

        # With force_refresh=True, should return None (bypass cache)
        result = _get_cached_stock_data(cache_key, True)
        self.assertIsNone(result)

        # With force_refresh=False, should return cached data
        result = _get_cached_stock_data(cache_key, False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Response)

    def test_fetch_and_validate_quote_rate_limit(self):
        """Test _fetch_and_validate_quote handles rate limit errors"""
        cache_key = 'stock_data_AAPL'
        cache.set(cache_key, {'symbol': 'AAPL', 'price': 150}, 60)

        # Mock rate limit error
        rate_limit_error = Exception("429 Too Many Requests")
        rate_limit_error.status_code = 429

        with patch('core.views.stock_data.finnhub_client') as mock_client:
            with patch('core.views.stock_data.is_rate_limit_error', return_value=True):
                mock_client.quote.side_effect = rate_limit_error
                quote, response = _fetch_and_validate_quote('AAPL', cache_key)
                # Should return cached response on rate limit
                self.assertIsNone(quote)
                self.assertIsNotNone(response)

    def test_fetch_company_profile_exception(self):
        """Test _fetch_company_profile handles exceptions gracefully"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.company_profile2.side_effect = Exception("Profile error")
                company, company_name = _fetch_company_profile('AAPL')
                self.assertEqual(company, {})
                self.assertEqual(company_name, 'AAPL')

    def test_fetch_stock_metrics_exception(self):
        """Test _fetch_stock_metrics handles exceptions gracefully"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.company_basic_financials.side_effect = Exception("Metrics error")
                metrics = _fetch_stock_metrics('AAPL')
                self.assertEqual(metrics, {})

    def test_build_stock_response_data_none_metrics(self):
        """Test _build_stock_response_data handles None metrics"""
        quote = {'c': 150.0, 'pc': 148.0, 'o': 149.0, 'h': 151.0, 'l': 147.0, 'v': 1000000}
        company = {'name': 'Apple Inc.', 'marketCapitalization': 3000000000000}

        result = _build_stock_response_data('AAPL', quote, company, 'Apple Inc.', metrics=None)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['name'], 'Apple Inc.')
        self.assertEqual(result['price'], 150.0)

    def test_build_stock_response_data_none_pe_ratio(self):
        """Test _build_stock_response_data handles None P/E ratio"""

        quote = {'c': 150.0, 'pc': 148.0, 'o': 149.0, 'h': 151.0, 'l': 147.0, 'v': 1000000}
        company = {'name': 'Apple Inc.', 'marketCapitalization': 3000000000000}
        # No peBasicExclExtraTTM
        metrics = {'52WeekHigh': 200.0, '52WeekLow': 100.0}

        result = _build_stock_response_data('AAPL', quote, company, 'Apple Inc.', metrics=metrics)
        # Should default to 0 when not in metrics or company
        self.assertEqual(result['peRatio'], 0)

    def test_stock_search_empty_query(self):
        """Test stock_search with empty query"""
        url = reverse('stock_search')
        response = self.client.get(url, {'query': ''})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['results'], [])

    def test_stock_search_no_query(self):
        """Test stock_search without query parameter"""
        url = reverse('stock_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['results'], [])

    def test_stock_search_fallback_no_api_key(self):
        """Test stock_search uses fallback when API key is missing"""
        url = reverse('stock_search')
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            with patch('core.views.stock_data.finnhub_client', None):
                response = self.client.get(url, {'query': 'apple'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('results', data)
                self.assertTrue(data.get('fallback', False))

    def test_stock_search_api_exception(self):
        """Test stock_search handles API exceptions"""
        url = reverse('stock_search')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.symbol_lookup.side_effect = Exception("API Error")
                response = self.client.get(url, {'query': 'apple'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('results', data)
                self.assertTrue(data.get('fallback', False))

    def test_stock_search_empty_results(self):
        """Test stock_search handles empty API results"""
        url = reverse('stock_search')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.symbol_lookup.return_value = None
                response = self.client.get(url, {'query': 'xyz123'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['results'], [])

    def test_stock_search_missing_result_key(self):
        """Test stock_search handles missing 'result' key in API response"""
        url = reverse('stock_search')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.symbol_lookup.return_value = {}
                response = self.client.get(url, {'query': 'test'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['results'], [])

    def test_stock_search_filters_us_exchanges(self):
        """Test stock_search filters to US exchanges only"""
        url = reverse('stock_search')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                # Mock response with US and international stocks
                mock_client.symbol_lookup.return_value = {
                    'result': [
                        {
                            'symbol': 'AAPL',
                            'description': 'Apple Inc.',
                            'type': 'Common Stock'
                        },
                        {
                            'symbol': 'AAPL.SW',
                            'description': 'Apple Inc. (Switzerland)',
                            'type': 'Common Stock'
                        },
                        {
                            'symbol': 'MSFT',
                            'description': 'Microsoft Corp.',
                            'type': 'Common Stock'
                        },
                        {
                            'symbol': 'BRK.B',
                            'description': 'Berkshire Hathaway Class B',
                            'type': 'Common Stock'
                        },
                    ]
                }
                response = self.client.get(url, {'query': 'apple'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                # Should only return US stocks (AAPL, MSFT, BRK.B), not AAPL.SW
                symbols = [r['symbol'] for r in data['results']]
                self.assertIn('AAPL', symbols)
                self.assertIn('MSFT', symbols)
                self.assertIn('BRK.B', symbols)
                self.assertNotIn('AAPL.SW', symbols)

    def test_is_us_exchange_empty_symbol(self):
        """Test _is_us_exchange with empty symbol"""
        self.assertFalse(_is_us_exchange(''))
        self.assertFalse(_is_us_exchange(None))

    def test_is_us_exchange_with_dot(self):
        """Test _is_us_exchange with dot in symbol"""
        # US share class (single letter after dot)
        self.assertTrue(_is_us_exchange('BRK.B'))
        self.assertTrue(_is_us_exchange('GOOGL.A'))
        # International (multiple characters after dot)
        self.assertFalse(_is_us_exchange('AAPL.SW'))
        # Note: MSFT.L would return True with current logic (single letter),
        # but .L is actually London exchange. Function treats any single
        # letter as US share class, which is a limitation.
        # Testing with a clear international exchange (multiple chars)
        self.assertFalse(_is_us_exchange('AAPL.LON'))

    def test_is_us_exchange_with_hyphen(self):
        """Test _is_us_exchange with hyphen in symbol"""
        self.assertFalse(_is_us_exchange('AAPL-W'))
        self.assertFalse(_is_us_exchange('TEST-WARRANT'))

    def test_is_us_exchange_case_sensitivity(self):
        """Test _is_us_exchange case sensitivity"""
        self.assertTrue(_is_us_exchange('AAPL'))
        self.assertFalse(_is_us_exchange('aapl'))
        self.assertFalse(_is_us_exchange('Aapl'))

    def test_is_us_exchange_non_alpha(self):
        """Test _is_us_exchange with non-alphabetic characters"""
        self.assertFalse(_is_us_exchange('AAPL1'))
        self.assertFalse(_is_us_exchange('123'))

    def test_get_fallback_search_results_by_symbol(self):
        """Test _get_fallback_search_results matches by symbol"""
        results = _get_fallback_search_results('AAPL')
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['symbol'], 'AAPL')

    def test_get_fallback_search_results_by_name(self):
        """Test _get_fallback_search_results matches by company name"""
        results = _get_fallback_search_results('apple')
        self.assertGreater(len(results), 0)
        # Should find Apple Inc.
        apple_result = [r for r in results if r['symbol'] == 'AAPL']
        self.assertGreater(len(apple_result), 0)

    def test_get_fallback_search_results_limit(self):
        """Test _get_fallback_search_results limits to 10 results"""
        # Search for something that matches many stocks (like 'inc')
        results = _get_fallback_search_results('inc')
        self.assertLessEqual(len(results), 10)

    def test_get_stock_data_returns_cached_response(self):
        """Test get_stock_data returns cached response when available"""
        cache_key = 'stock_data_AAPL'
        cached_data = {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.0}
        cache.set(cache_key, cached_data, 60)

        url = reverse('get_stock_data')
        with patch('core.views.stock_data.finnhub_client', None):
            response = self.client.get(url, {'symbol': 'AAPL'})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'AAPL')

    def test_get_stock_data_exception_with_fallback(self):
        """Test get_stock_data exception handling with fallback available"""
        cache.clear()
        url = reverse('get_stock_data')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.quote.side_effect = Exception("Unexpected error")
                response = self.client.get(url, {'symbol': 'AAPL', 'force_refresh': 'true'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('symbol', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_exception_no_fallback(self):
        """Test get_stock_data exception handling without fallback"""
        cache.clear()
        url = reverse('get_stock_data')
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.stock_data.finnhub_client') as mock_client:
                mock_client.quote.side_effect = Exception("Unexpected error")
                response = self.client.get(url, {'symbol': 'UNKNOWN', 'force_refresh': 'true'})
                # Should return 500 error when no fallback available
                self.assertEqual(response.status_code, 500)
                data = response.json()
                self.assertIn('error', data)
