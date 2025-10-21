from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json


class APITests(TestCase):
    def setUp(self):
        # Mock API responses
        self.mock_finnhub_quote = {
            'c': 150.25,  # current price
            'd': 2.15,    # change
            'dp': 1.45,   # change percent
            'h': 152.00,  # high
            'l': 148.50,  # low
            'o': 149.10,  # open
            'pc': 148.10, # previous close
            'v': 1000000  # volume
        }
        
        self.mock_finnhub_company = {
            'name': 'Apple Inc.',
            'marketCapitalization': 2500000000000,
            'pe': 25.5
        }
        
        self.mock_newsapi_response = {
            'articles': [
                {
                    'title': 'Test News Article',
                    'source': {'name': 'Test Source'},
                    'publishedAt': '2024-01-01T10:00:00Z',
                    'url': 'https://example.com',
                    'description': 'Test description'
                }
            ],
            'totalResults': 1
        }

    @patch('core.views.finnhub_client')
    def test_get_stock_data_success(self, mock_finnhub):
        """Test successful stock data retrieval"""
        mock_finnhub.quote.return_value = self.mock_finnhub_quote
        mock_finnhub.company_profile2.return_value = self.mock_finnhub_company
        
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['name'], 'Apple Inc.')
        self.assertEqual(data['price'], 150.25)
        self.assertEqual(data['change'], 2.15)
        self.assertEqual(data['changePercent'], 1.45)

    def test_get_stock_data_no_symbol(self):
        """Test stock data endpoint without symbol parameter"""
        url = reverse('get_stock_data')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    @patch('core.views.finnhub_client')
    def test_get_stock_data_api_error(self, mock_finnhub):
        """Test stock data endpoint with API error"""
        mock_finnhub.quote.side_effect = Exception("API Error")
        
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'INVALID'})
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)

    @patch('core.views.finnhub_client')
    def test_get_market_movers_success(self, mock_finnhub):
        """Test successful market movers retrieval"""
        mock_finnhub.quote.return_value = self.mock_finnhub_quote
        mock_finnhub.company_profile2.return_value = self.mock_finnhub_company
        
        url = reverse('get_market_movers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('gainers', data)
        self.assertIn('losers', data)
        self.assertIsInstance(data['gainers'], list)
        self.assertIsInstance(data['losers'], list)

    @patch('core.views.newsapi')
    def test_get_news_success(self, mock_newsapi):
        """Test successful news retrieval"""
        mock_newsapi.get_top_headlines.return_value = self.mock_newsapi_response
        
        url = reverse('get_news')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('articles', data)
        self.assertIn('totalResults', data)
        self.assertIsInstance(data['articles'], list)
        self.assertEqual(len(data['articles']), 1)

    @patch('core.views.newsapi')
    def test_get_news_with_symbol(self, mock_newsapi):
        """Test news retrieval with specific symbol"""
        mock_newsapi.get_everything.return_value = self.mock_newsapi_response
        
        url = reverse('get_news')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('articles', data)
        # Verify that newsapi was called with the symbol
        mock_newsapi.get_everything.assert_called_once()
        call_args = mock_newsapi.get_everything.call_args
        self.assertIn('AAPL stock', call_args[1]['q'])
        self.assertEqual(call_args[1]['sort_by'], 'popularity')

    @patch('core.views.newsapi')
    def test_get_news_api_error(self, mock_newsapi):
        """Test news endpoint with API error"""
        mock_newsapi.get_top_headlines.side_effect = Exception("News API Error")
        mock_newsapi.get_everything.side_effect = Exception("News API Error")
        
        url = reverse('get_news')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)  # Should return fallback data
        data = response.json()
        self.assertIn('articles', data)
        self.assertTrue(data.get('fallback', False))

    def test_hello_api(self):
        """Test hello API endpoint"""
        url = reverse('hello_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'Hello from Django + Basecoat + DRF!')

    def test_home_view(self):
        """Test home view renders correctly"""
        url = reverse('landing')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')

    @patch('core.views.openai_client')
    def test_portfolai_analysis_success(self, mock_openai_client):
        """Test successful PortfolAI analysis"""
        # Mock OpenAI response
        mock_response = type('MockResponse', (), {
            'choices': [type('MockChoice', (), {
                'message': type('MockMessage', (), {
                    'content': 'This is a test analysis for AAPL stock.'
                })()
            })()]
        })()
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('symbol', data)
        self.assertIn('analysis', data)
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertIn('test analysis', data['analysis'])

    def test_portfolai_analysis_no_symbol(self):
        """Test PortfolAI analysis without symbol"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_portfolai_analysis_fallback(self):
        """Test PortfolAI analysis with fallback when OpenAI is not available"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)
        self.assertIn('analysis', data)
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_fallback(self):
        """Test stock data with fallback when API is not available"""
        with patch('core.views.settings.FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            self.assertIn('fallback', data)
            self.assertTrue(data['fallback'])

    def test_get_market_movers_fallback(self):
        """Test market movers with fallback when API is not available"""
        with patch('core.views.settings.FINNHUB_API_KEY', None):
            url = reverse('get_market_movers')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('gainers', data)
            self.assertIn('losers', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_news_fallback(self):
        """Test news with fallback when API is not available"""
        with patch('core.views.settings.NEWS_API_KEY', None):
            url = reverse('get_news')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)
            self.assertTrue(data.get('fallback', False))

    def test_dashboard_view(self):
        """Test dashboard view renders correctly"""
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')

    def test_get_stock_data_invalid_symbol(self):
        """Test stock data with invalid symbol"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'INVALID123'})
        
        # Should return 404 or 500 depending on API response
        self.assertIn(response.status_code, [404, 500])

    def test_get_stock_data_empty_response(self):
        """Test stock data with empty API response"""
        with patch('core.views.finnhub_client') as mock_finnhub:
            mock_finnhub.quote.return_value = None
            
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'TEST'})
            
            self.assertEqual(response.status_code, 500)

    def test_get_market_movers_api_error(self):
        """Test market movers with API error"""
        with patch('core.views.finnhub_client') as mock_finnhub:
            mock_finnhub.quote.side_effect = Exception("API Error")
            
            url = reverse('get_market_movers')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('fallback', False))

    def test_get_news_empty_response(self):
        """Test news with empty API response"""
        with patch('core.views.newsapi') as mock_newsapi:
            mock_newsapi.get_top_headlines.return_value = None
            
            url = reverse('get_news')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('fallback', False))

    def test_portfolai_analysis_api_error(self):
        """Test PortfolAI analysis with API error"""
        with patch('core.views.openai_client') as mock_openai:
            mock_openai.chat.completions.create.side_effect = Exception("OpenAI Error")
            
            url = reverse('portfolai_analysis')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)

    def test_stock_summary_endpoint(self):
        """Test stock summary endpoint"""
        with patch('core.views.finnhub_client') as mock_finnhub, \
             patch('core.views.openai_client') as mock_openai:
            
            mock_finnhub.quote.return_value = self.mock_finnhub_quote
            mock_finnhub.company_profile2.return_value = self.mock_finnhub_company
            
            mock_response = type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': 'Test analysis'
                    })()
                })()]
            })()
            mock_openai.chat.completions.create.return_value = mock_response
            
            url = reverse('stock_summary')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            self.assertIn('analysis', data)

    def test_stock_summary_api_error(self):
        """Test stock summary with API error"""
        with patch('core.views.finnhub_client') as mock_finnhub:
            mock_finnhub.quote.side_effect = Exception("API Error")
            
            url = reverse('stock_summary')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)