"""
PortfolAI Analysis Test Suite — demo mode
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class AnalysisTests(TestCase):
    """Test suite for demo PortfolAI analysis endpoint."""

    def test_portfolai_analysis_no_symbol(self):
        """Missing symbol returns 400."""
        url = reverse('portfolai_analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_portfolai_analysis_with_symbol(self):
        """Valid symbol returns demo analysis."""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertIn('analysis', data)
        self.assertTrue(data.get('fallback', False))
        self.assertIn('timestamp', data)

    def test_portfolai_analysis_empty_symbol(self):
        """Empty symbol returns 400."""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': ''})
        self.assertEqual(response.status_code, 400)

    def test_portfolai_analysis_whitespace_symbol(self):
        """Whitespace-only symbol returns 400."""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': '   '})
        self.assertEqual(response.status_code, 400)

    def test_portfolai_analysis_lowercase_symbol(self):
        """Lowercase symbol is normalized to uppercase."""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'aapl'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['symbol'], 'AAPL')

    @patch('core.views.analysis.requests.get')
    @patch(
        'core.views.analysis.newsapi',
        {'api_token': 'test', 'base_url': 'https://api.thenewsapi.com'},
    )
    @patch('core.views.analysis.finnhub_client')
    @patch.object(settings, 'FINNHUB_API_KEY', 'test-key')
    def test_portfolai_analysis_enriches_with_mocked_finnhub(
        self, mock_finnhub, mock_requests_get
    ):
        """Demo analysis includes live data when Finnhub/news mocks are available."""
        mock_finnhub.quote.return_value = {
            'c': 150.0, 'pc': 148.0, 'v': 1000000,
            'h': 151.0, 'l': 149.0, 'o': 149.0,
        }
        mock_finnhub.company_profile2.return_value = {
            'name': 'Apple Inc.',
            'country': 'US',
            'industry': 'Technology',
            'marketCapitalization': 3000000000000,
        }
        mock_finnhub.stock_insider_sentiment.return_value = {
            'data': [
                {'month': 1, 'year': 2025, 'mspr': 10.5, 'change': 5000},
            ]
        }
        mock_finnhub.recommendation_trends.return_value = [{
            'period': '2025-01',
            'strongBuy': 5, 'buy': 10, 'hold': 8, 'sell': 2, 'strongSell': 1,
        }]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {
                    'title': 'Apple reports strong earnings',
                    'published_at': '2025-01-15T10:00:00Z',
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('fallback', False))
        self.assertIn('150.00', data['analysis'])
        self.assertIn('Apple Inc.', data['analysis'])
        self.assertIn('Recent News about AAPL', data['analysis'])
