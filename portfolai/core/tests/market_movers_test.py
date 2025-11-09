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

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings


class MarketMoversTests(TestCase):
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
        with patch.object(settings, 'FINNHUB_API_KEY', None):
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
        with patch.object(settings, 'FINNHUB_API_KEY', None):
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
                mock_finnhub.quote.return_value = {'c': 150.0, 'pc': 148.0, 'o': 149.0, 'h': 151.0, 'l': 147.0, 'v': 1000000}
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
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                # Mock the client to exist but throw exceptions
                mock_finnhub.quote.side_effect = Exception("API Error")
                
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
                mock_finnhub.quote.return_value = {'c': 150.0, 'pc': 148.0, 'o': 149.0, 'h': 151.0, 'l': 147.0, 'v': 1000000}
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
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views._clients.finnhub_client') as mock_finnhub:
                # Mock to trigger the exception handler
                mock_finnhub.quote.side_effect = Exception("Market data error")
                
                url = reverse('get_market_movers')
                response = self.client.get(url)
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('gainers', data)
                self.assertIn('losers', data)
                self.assertTrue(data.get('fallback', False))

