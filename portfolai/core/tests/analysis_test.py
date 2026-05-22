"""
PortfolAI Analysis Test Suite — demo mode
"""

from django.test import TestCase
from django.urls import reverse


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
