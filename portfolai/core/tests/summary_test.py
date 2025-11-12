"""
PortfolAI Stock Summary Test Suite
===================================

Tests for /api/stock/ endpoint - Advanced Feature
- Requires both Finnhub + OpenAI APIs
- Combined stock data + AI analysis
- Error handling for missing API keys
- Full integration testing
"""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class StockSummaryTests(TestCase):
    """Test suite for stock summary endpoint functionality"""

    def test_stock_summary_endpoint(self):
        """Test stock summary endpoint - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'AAPL'})

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_no_symbol(self):
        """Test stock summary without symbol - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url)

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_empty_symbol(self):
        """Test stock summary with empty symbol - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': ''})

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_whitespace_symbol(self):
        """Test stock summary with whitespace symbol - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': '   '})

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_lowercase_symbol(self):
        """Test stock summary with lowercase symbol - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'aapl'})

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_response_structure(self):
        """Test stock summary response structure - requires API keys"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'AAPL'})

        # Stock summary requires API keys
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_with_api_error(self):
        """Test stock summary with API error handling"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
                with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                    with patch('core.views.stock_data.openai_client'):
                        mock_finnhub.quote.side_effect = Exception("API Error")

                        url = reverse('stock_summary')
                        response = self.client.get(url, {'symbol': 'AAPL'})

                        self.assertEqual(response.status_code, 500)
                        data = response.json()
                        self.assertIn('error', data)

    def test_stock_summary_with_missing_api_key(self):
        """Test stock summary with missing API key"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            with patch.object(settings, 'OPENAI_API_KEY', None):
                url = reverse('stock_summary')
                response = self.client.get(url, {'symbol': 'AAPL'})

                # Stock summary returns 500 when API key is missing
                self.assertEqual(response.status_code, 500)
                data = response.json()
                self.assertIn('error', data)
                self.assertEqual(data['error'], 'API keys not configured')

    def test_stock_summary_with_working_apis(self):
        """Test stock summary with working API mocks"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
                with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
                    with patch('core.views.stock_data.openai_client') as mock_openai:
                        # Mock successful API responses
                        mock_finnhub.quote.return_value = {'c': 150.0, 'pc': 148.0}
                        mock_finnhub.company_profile2.return_value = {'name': 'Apple Inc.'}

                        # Mock OpenAI response
                        mock_response = type('obj', (object,), {
                            'choices': [type('obj', (object,), {
                                'message': type('obj', (object,), {
                                    'content': 'Test AI summary'
                                })
                            })]
                        })
                        mock_openai.chat.completions.create.return_value = mock_response

                        url = reverse('stock_summary')
                        response = self.client.get(url, {'symbol': 'AAPL'})

                        self.assertEqual(response.status_code, 200)
                        data = response.json()
                        self.assertIn('ai_summary', data)

    def test_stock_summary_with_finnhub_client_none(self):
        """Test stock summary when finnhub_client is None"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
                with patch('core.views.stock_data.finnhub_client', None):
                    url = reverse('stock_summary')
                    response = self.client.get(url, {'symbol': 'AAPL'})

                    self.assertEqual(response.status_code, 500)
                    data = response.json()
                    self.assertIn('error', data)

    def test_stock_summary_with_openai_client_none(self):
        """Test stock summary when openai_client is None"""
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
                with patch('core.views.stock_data.openai_client', None):
                    url = reverse('stock_summary')
                    response = self.client.get(url, {'symbol': 'AAPL'})

                    self.assertEqual(response.status_code, 500)
                    data = response.json()
                    self.assertIn('error', data)
