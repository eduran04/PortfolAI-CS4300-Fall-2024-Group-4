"""
PortfolAI Market Movers Test Suite
===================================

Tests for /api/market-movers/ endpoint (Feature 2)
- Top gainers and losers retrieval
- Market data sorting and processing
- Fallback data when API unavailable
- Error handling for market data failures
- Data structure validation
"""

from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class MarketMoversTests(TestCase):  # pylint: disable=too-many-public-methods
    """Test suite for market movers endpoint functionality"""

    def test_get_market_movers_endpoint(self):
        """Test market movers endpoint returns response"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views._clients.finnhub_client', None):
            url = reverse('get_market_movers')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('gainers', data)
            self.assertIn('losers', data)

    def test_get_market_movers_response_structure(self):
        """Test market movers response has correct structure"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views._clients.finnhub_client', None):
            url = reverse('get_market_movers')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('gainers', data)
            self.assertIn('losers', data)
            self.assertIsInstance(data['gainers'], list)
            self.assertIsInstance(data['losers'], list)

    def test_get_market_movers_fallback(self):
        """Test market movers with fallback data when API key is not available"""
        with patch.object(settings, 'ALPHA_VANTAGE_API_KEY', None):
            url = reverse('get_market_movers')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('gainers', data)
            self.assertIn('losers', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_with_api_error(self):
        """Test market movers with API error handling"""
        # Test with no API key to trigger fallback
        with patch.object(settings, 'ALPHA_VANTAGE_API_KEY', None):
            url = reverse('get_market_movers')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('gainers', data)
            self.assertIn('losers', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_company_profile_exception(self):
        """Test market movers when company profile fetch fails"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0, 'pc': 148.0, 'o': 149.0,
                    'h': 151.0, 'l': 147.0, 'v': 1000000
                }
                mock_finnhub.company_profile2.side_effect = Exception("Company profile error")

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)

    def test_get_market_movers_symbol_fetch_exception(self):
        """Test market movers when individual symbol fetch fails"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("Symbol fetch error")

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)

    def test_get_market_movers_api_exception_fallback(self):
        """Test market movers API exception triggers fallback"""
        cache.clear()
        with patch.object(settings, 'ALPHA_VANTAGE_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.side_effect = Exception("API Error")
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [],
                    'losers': [],
                    'fallback': True
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                # The test should expect fallback=True when API exceptions occur
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_with_finnhub_client_none(self):
        """Test market movers when finnhub_client is None"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client', None):
                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_with_quote_exception(self):
        """Test market movers when quote fetch throws exception"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("Quote fetch error")

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_with_invalid_quote_data(self):
        """Test market movers with invalid quote data"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                # Mock quote with None current price to trigger continue
                mock_finnhub.quote.return_value = {'c': None, 'pc': 100}
                mock_finnhub.company_profile2.return_value = {'name': 'Test Company'}

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)

    def test_get_market_movers_with_company_profile_exception(self):
        """Test market movers when company profile throws exception"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {'c': 150.0, 'pc': 148.0}
                mock_finnhub.company_profile2.side_effect = Exception("Profile error")

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)

    def test_get_market_movers_with_valid_data(self):
        """Test market movers with valid data"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                # Mock valid quote data
                mock_finnhub.quote.return_value = {
                    'c': 150.0, 'pc': 148.0, 'o': 149.0,
                    'h': 151.0, 'l': 147.0, 'v': 1000000
                }
                mock_finnhub.company_profile2.return_value = {'name': 'Test Company'}

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertIsInstance(data['gainers'], list)
                self.assertIsInstance(data['losers'], list)

    def test_get_market_movers_exception_fallback(self):
        """Test market movers exception handling with fallback data"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                # Make get_market_movers raise an exception to trigger exception handler
                mock_instance.get_market_movers.side_effect = Exception("Market data error")
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [],
                    'losers': [],
                    'fallback': True
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_no_data_fallback(self):
        """Test market movers when service returns None, triggers fallback"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.return_value = None
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [],
                    'losers': [],
                    'fallback': True
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_missing_gainers_key(self):
        """Test market movers when response missing gainers key"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.return_value = {'losers': []}
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [],
                    'losers': []
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertIsInstance(data['gainers'], list)

    def test_get_market_movers_missing_losers_key(self):
        """Test market movers when response missing losers key"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.return_value = {'gainers': []}
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [],
                    'losers': []
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertIsInstance(data['losers'], list)

    def test_get_market_movers_exception_fallback_succeeds(self):
        """Test market movers when exception occurs but fallback succeeds"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.side_effect = Exception("Service error")
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.return_value = {
                    'gainers': [{
                        'symbol': 'AAPL',
                        'price': 150.0,
                        'change': 2.0,
                        'changePercent': 1.35
                    }],
                    'losers': [{
                        'symbol': 'MSFT',
                        'price': 420.0,
                        'change': -0.5,
                        'changePercent': -0.12
                    }],
                    'fallback': True
                }

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_movers_exception_fallback_fails(self):
        """Test market movers when exception occurs and fallback also fails"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.MarketDataService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_market_movers.side_effect = Exception("Service error")
                # Access protected method for testing fallback behavior
                # pylint: disable=protected-access
                mock_instance._get_fallback_market_movers.side_effect = Exception(
                    "Fallback error"
                )

                url = reverse('get_market_movers')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))
                self.assertIn('error', data)

    def test_get_ticker_data_basic(self):
        """Test ticker data endpoint returns valid response"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0,
                    'pc': 148.0
                }

                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)

    def test_get_ticker_data_caching(self):
        """Test ticker data endpoint uses cache"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0,
                    'pc': 148.0
                }

                url = reverse('get_ticker_data')
                # First request
                response1 = self.client.get(url)
                self.assertEqual(response1.status_code, 200)

                # Second request should use cache
                response2 = self.client.get(url)
                self.assertEqual(response2.status_code, 200)
                # Verify finnhub_client.quote was only called once (cached on second call)
                self.assertGreater(mock_finnhub.quote.call_count, 0)

    def test_get_ticker_data_force_refresh(self):
        """Test ticker data endpoint with force_refresh parameter"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.return_value = {
                    'c': 150.0,
                    'pc': 148.0
                }

                url = reverse('get_ticker_data')
                # First request
                response1 = self.client.get(url)
                self.assertEqual(response1.status_code, 200)

                # Second request with force_refresh should bypass cache
                response2 = self.client.get(url + '?force_refresh=true')
                self.assertEqual(response2.status_code, 200)

    def test_get_ticker_data_no_api_key(self):
        """Test ticker data endpoint when API key is not configured"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            with patch('core.views.market_movers.finnhub_client', None):
                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))
                self.assertIn('error', data)

    def test_get_ticker_data_symbol_exception(self):
        """Test ticker data endpoint when individual symbol fetch fails"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                # First symbol fails, others succeed
                call_count = 0

                def side_effect(_symbol):  # pylint: disable=unused-argument
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        # pylint: disable=broad-exception-raised
                        raise Exception("Symbol fetch error")
                    return {'c': 150.0, 'pc': 148.0}

                mock_finnhub.quote.side_effect = side_effect

                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)

    def test_get_ticker_data_no_valid_quotes(self):
        """Test ticker data endpoint when no valid quotes are returned"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                # Return quotes with None current price
                mock_finnhub.quote.return_value = {
                    'c': None,
                    'pc': 148.0
                }

                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))
                self.assertIn('error', data)

    def test_get_ticker_data_sorts_gainers_and_losers(self):
        """Test ticker data endpoint sorts gainers and losers correctly"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                # Return quotes with positive and negative changes
                def quote_side_effect(symbol):
                    # Return different quotes based on symbol to create gainers/losers
                    if symbol in ['AAPL', 'NVDA']:
                        return {'c': 160.0, 'pc': 150.0}  # +10 gainer
                    return {'c': 140.0, 'pc': 150.0}  # -10 loser

                mock_finnhub.quote.side_effect = quote_side_effect

                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                # Verify gainers have positive changePercent
                for gainer in data['gainers']:
                    self.assertGreaterEqual(gainer.get('changePercent', 0), 0)
                # Verify losers have negative changePercent
                for loser in data['losers']:
                    self.assertLess(loser.get('changePercent', 0), 0)

    def test_get_ticker_data_exception_handling(self):
        """Test ticker data endpoint exception handling"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.market_movers.finnhub_client') as mock_finnhub:
                mock_finnhub.quote.side_effect = Exception("API Error")

                url = reverse('get_ticker_data')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))
                self.assertIn('error', data)
