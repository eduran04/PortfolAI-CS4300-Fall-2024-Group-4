from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings


class APITests(TestCase):
    
    def test_hello_api(self):
        """Test hello API endpoint"""
        url = reverse('hello_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'Hello from Django + Basecoat + DRF!')

    def test_landing_view(self):
        """Test landing page renders correctly"""
        url = reverse('landing')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')

    def test_dashboard_view(self):
        """Test dashboard view renders correctly"""
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')

    def test_get_stock_data_no_symbol(self):
        """Test stock data endpoint without symbol parameter"""
        url = reverse('get_stock_data')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_portfolai_analysis_no_symbol(self):
        """Test PortfolAI analysis without symbol"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_get_news_endpoint(self):
        """Test news endpoint returns response"""
        url = reverse('get_news')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('articles', data)

    def test_get_market_movers_endpoint(self):
        """Test market movers endpoint returns response"""
        url = reverse('get_market_movers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('gainers', data)
        self.assertIn('losers', data)

    def test_get_stock_data_with_symbol_fallback(self):
        """Test stock data with symbol using fallback data"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)
        self.assertIn('name', data)
        self.assertIn('price', data)

    def test_get_news_with_symbol(self):
        """Test news endpoint with symbol parameter"""
        url = reverse('get_news')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('articles', data)

    def test_portfolai_analysis_with_symbol_fallback(self):
        """Test PortfolAI analysis with symbol using fallback"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)
        self.assertIn('analysis', data)

    def test_stock_summary_endpoint(self):
        """Test stock summary endpoint - actually works"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        # Stock summary actually works and returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_stock_summary_no_symbol(self):
        """Test stock summary without symbol - uses default AAPL and works"""
        url = reverse('stock_summary')
        response = self.client.get(url)
        
        # Stock summary uses default symbol AAPL and actually works
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_get_stock_data_empty_symbol(self):
        """Test stock data with empty symbol"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': ''})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_portfolai_analysis_empty_symbol(self):
        """Test PortfolAI analysis with empty symbol"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': ''})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_empty_symbol(self):
        """Test stock summary with empty symbol - uses default AAPL and works"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': ''})
        
        # Stock summary uses default symbol AAPL and actually works
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_get_stock_data_whitespace_symbol(self):
        """Test stock data with whitespace symbol - actually works with fallback"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': '   '})
        
        # Whitespace gets stripped and treated as empty, which returns 400
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_portfolai_analysis_whitespace_symbol(self):
        """Test PortfolAI analysis with whitespace symbol - actually works with fallback"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': '   '})
        
        # Whitespace gets stripped and treated as empty, which returns 400
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_stock_summary_whitespace_symbol(self):
        """Test stock summary with whitespace symbol - uses default AAPL and works"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': '   '})
        
        # Stock summary uses default symbol AAPL and actually works
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_get_stock_data_lowercase_symbol(self):
        """Test stock data with lowercase symbol (should be converted to uppercase)"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'aapl'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')

    def test_portfolai_analysis_lowercase_symbol(self):
        """Test PortfolAI analysis with lowercase symbol"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'aapl'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')

    def test_stock_summary_lowercase_symbol(self):
        """Test stock summary with lowercase symbol - actually works"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'aapl'})
        
        # Stock summary actually works and returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_get_news_response_structure(self):
        """Test news response has correct structure"""
        url = reverse('get_news')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('articles', data)
        self.assertIn('totalResults', data)
        self.assertIsInstance(data['articles'], list)

    def test_get_market_movers_response_structure(self):
        """Test market movers response has correct structure"""
        url = reverse('get_market_movers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('gainers', data)
        self.assertIn('losers', data)
        self.assertIsInstance(data['gainers'], list)
        self.assertIsInstance(data['losers'], list)

    def test_get_stock_data_response_structure(self):
        """Test stock data response has correct structure"""
        url = reverse('get_stock_data')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)
        self.assertIn('name', data)
        self.assertIn('price', data)
        self.assertIn('change', data)
        self.assertIn('changePercent', data)

    def test_portfolai_analysis_response_structure(self):
        """Test PortfolAI analysis response has correct structure"""
        url = reverse('portfolai_analysis')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)
        self.assertIn('analysis', data)

    def test_stock_summary_response_structure(self):
        """Test stock summary response structure - actually works"""
        url = reverse('stock_summary')
        response = self.client.get(url, {'symbol': 'AAPL'})
        
        # Stock summary actually works and returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbol', data)

    def test_get_stock_data_fallback_data(self):
        """Test stock data with fallback data when API key is not available"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
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

    def test_get_news_fallback(self):
        """Test news with fallback data when API key is not available"""
        with patch.object(settings, 'NEWS_API_KEY', None):
            url = reverse('get_news')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)
            self.assertTrue(data.get('fallback', False))

    def test_portfolai_analysis_fallback(self):
        """Test PortfolAI analysis with fallback when API keys are not available"""
        with patch.object(settings, 'OPENAI_API_KEY', None):
            url = reverse('portfolai_analysis')
            response = self.client.get(url, {'symbol': 'AAPL'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('symbol', data)
            self.assertIn('analysis', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_valid_symbol_fallback(self):
        """Test stock data with valid symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'MSFT'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'MSFT')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_googl_symbol_fallback(self):
        """Test stock data with GOOGL symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'GOOGL'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'GOOGL')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_amzn_symbol_fallback(self):
        """Test stock data with AMZN symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'AMZN'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'AMZN')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_tsla_symbol_fallback(self):
        """Test stock data with TSLA symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'TSLA'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'TSLA')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_nvda_symbol_fallback(self):
        """Test stock data with NVDA symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'NVDA'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'NVDA')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_meta_symbol_fallback(self):
        """Test stock data with META symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'META'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'META')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_stock_data_with_oklo_symbol_fallback(self):
        """Test stock data with OKLO symbol using fallback data"""
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_stock_data')
            response = self.client.get(url, {'symbol': 'OKLO'})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['symbol'], 'OKLO')
            self.assertIn('name', data)
            self.assertIn('price', data)
            self.assertTrue(data.get('fallback', False))