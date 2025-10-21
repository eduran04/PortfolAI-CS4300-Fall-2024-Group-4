from django.test import TestCase
from django.urls import reverse


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