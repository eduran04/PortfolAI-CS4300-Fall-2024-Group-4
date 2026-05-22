"""
PortfolAI Stock Summary Test Suite — demo mode
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class StockSummaryTests(TestCase):
    """Test suite for stock summary endpoint (Finnhub only)."""

    def test_stock_summary_no_finnhub_key(self):
        """Missing Finnhub key returns 500."""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            with patch('core.views.stock_data.finnhub_client', None):
                url = reverse('stock_summary')
                response = self.client.get(url, {'symbol': 'AAPL'})
                self.assertEqual(response.status_code, 500)
                self.assertIn('error', response.json())

    def test_stock_summary_success(self):
        """Valid request returns demo summary with quote data."""
        mock_client = MagicMock()
        mock_client.quote.return_value = {'c': 150.0, 'pc': 148.0}
        mock_client.company_profile2.return_value = {'name': 'Apple Inc.'}

        with patch.object(settings, 'FINNHUB_API_KEY', 'test-key'):
            with patch('core.views.stock_data.finnhub_client', mock_client):
                url = reverse('stock_summary')
                response = self.client.get(url, {'symbol': 'AAPL'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertIn('summary', data)
        self.assertTrue(data.get('demo', False))
        self.assertIn('quote', data)

    def test_stock_summary_empty_symbol_defaults_to_aapl(self):
        """Empty symbol defaults to AAPL."""
        mock_client = MagicMock()
        mock_client.quote.return_value = {'c': 150.0, 'pc': 148.0}
        mock_client.company_profile2.return_value = {'name': 'Apple Inc.'}

        with patch.object(settings, 'FINNHUB_API_KEY', 'test-key'):
            with patch('core.views.stock_data.finnhub_client', mock_client):
                url = reverse('stock_summary')
                response = self.client.get(url, {'symbol': ''})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['symbol'], 'AAPL')

    def test_stock_summary_api_error(self):
        """Finnhub exception returns 500."""
        mock_client = MagicMock()
        mock_client.quote.side_effect = Exception('API error')

        with patch.object(settings, 'FINNHUB_API_KEY', 'test-key'):
            with patch('core.views.stock_data.finnhub_client', mock_client):
                url = reverse('stock_summary')
                response = self.client.get(url, {'symbol': 'AAPL'})

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())
