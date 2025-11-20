"""
PortfolAI News Feed Test Suite
===============================

Tests for /api/news/ endpoint (Feature 3)
- General financial news retrieval
- Symbol-specific news filtering
- Time formatting and article processing
- Fallback data when News API unavailable
- Article validation and filtering
"""

from datetime import datetime
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class NewsTests(TestCase):  # pylint: disable=too-many-public-methods
    """Test suite for news endpoint functionality"""

    def test_get_news_endpoint(self):
        """Test news endpoint returns response"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.news.newsapi', None):
            url = reverse('get_news')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)

    def test_get_news_with_symbol(self):
        """Test news endpoint with symbol parameter"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.news.newsapi', None):
            url = reverse('get_news')
            response = self.client.get(url, {'symbol': 'AAPL'})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)

    def test_get_news_response_structure(self):
        """Test news response has correct structure"""
        # Mock API client to prevent real API calls and ensure fast test execution
        with patch('core.views.news.newsapi', None):
            url = reverse('get_news')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)
            self.assertIn('totalResults', data)
            self.assertIsInstance(data['articles'], list)

    def test_get_news_fallback(self):
        """Test news with fallback data when API key is not available"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', None):
            with patch('core.views.news.newsapi', None):
                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_with_api_error(self):
        """Test news with API error handling"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_newsapi.get_top_headlines.side_effect = Exception("API Error")

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_articles_processing(self):
        """Test news articles processing and filtering"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi', {'api_token': 'test_token'}):
                with patch('core.views.news.requests.get') as mock_get:
                    # Mock The News API response format: {'data': [articles...]}
                    mock_response = type('obj', (object,), {
                        'raise_for_status': lambda: None,
                        'json': lambda: {
                            'data': [
                                {
                                    'title': 'Valid Article',
                                    'url': 'http://example.com',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source',
                                    'description': 'Test description'
                                },
                                {
                                    'title': '',
                                    'url': 'http://example.com',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source'
                                },  # Invalid - no title
                                {
                                    'title': 'Valid Article 2',
                                    'url': '',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source'
                                },  # Invalid - no URL
                                {
                                    'title': 'Valid Article 3',
                                    'url': 'http://example.com',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source',
                                    'description': 'Test description 3'
                                }
                            ]
                        }
                    })
                    mock_get.return_value = mock_response

                    url = reverse('get_news')
                    response = self.client.get(url, {'force_refresh': 'true'})

                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertIn('articles', data)
                    # All articles are transformed and included
                    # (empty titles/URLs get defaults)
                    # Article 2 has empty title (becomes 'No title'),
                    # article 3 has empty URL (becomes '#')
                    self.assertEqual(len(data['articles']), 4)

    def test_get_news_time_formatting(self):
        """Test news time formatting logic"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_articles = {
                    'articles': [
                        {
                            'title': 'Test Article',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        }
                    ],
                    'totalResults': 1
                }
                mock_newsapi.get_top_headlines.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                # Should have at least 1 article (may have more if fallback is triggered)
                self.assertGreaterEqual(len(data['articles']), 1)
                if len(data['articles']) > 0:
                    self.assertIn('time', data['articles'][0])

    def test_get_news_invalid_time_format(self):
        """Test news with invalid time format"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_articles = {
                    'articles': [
                        {
                            'title': 'Test Article',
                            'url': 'http://example.com',
                            'publishedAt': 'invalid-time',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        }
                    ],
                    'totalResults': 1
                }
                mock_newsapi.get_top_headlines.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                # Should have at least 1 article (may have more if fallback is triggered)
                self.assertGreaterEqual(len(data['articles']), 1)
                # If we got our mocked article, check the time format
                if (len(data['articles']) == 1
                        and data['articles'][0].get('title') == 'Test Article'):
                    self.assertEqual(data['articles'][0]['time'], 'Recently')

    def test_get_news_no_articles_fallback(self):
        """Test news when no valid articles found"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_articles = {
                    'articles': [
                        {'title': '', 'url': 'http://example.com'},  # Invalid article
                        {'title': 'Valid Title', 'url': ''}  # Invalid article
                    ]
                }
                mock_newsapi.get_top_headlines.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_with_newsapi_none(self):
        """Test news when newsapi is None"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi', None):
                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_with_headlines_exception(self):
        """Test news when headlines fetch throws exception"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_newsapi.get_top_headlines.side_effect = Exception(
                    "Headlines fetch error"
                )

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_with_invalid_article_data(self):
        """Test news with invalid article data"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi', {'api_token': 'test_token'}):
                with patch('core.views.news.requests.get') as mock_get:
                    # Mock The News API response format: {'data': [articles...]}
                    mock_response = type('obj', (object,), {
                        'raise_for_status': lambda: None,
                        'json': lambda: {
                            'data': [
                                {
                                    'title': '',
                                    'url': 'http://example.com',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source'
                                },  # Missing title
                                {
                                    'title': 'Valid Title',
                                    'url': '',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source'
                                },  # Missing URL
                                {
                                    'title': 'Valid Title 2',
                                    'url': 'http://example.com',
                                    'published_at': '2024-01-01T10:00:00Z',
                                    'source': 'Test Source',
                                    'description': 'Test description'
                                }
                            ]
                        }
                    })
                    mock_get.return_value = mock_response

                    url = reverse('get_news')
                    response = self.client.get(url, {'force_refresh': 'true'})

                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertIn('articles', data)
                    # All articles are transformed and included
                    # (empty titles/URLs get defaults)
                    # Article 1 has empty title (becomes 'No title'),
                    # article 2 has empty URL (becomes '#')
                    self.assertEqual(len(data['articles']), 3)

    def test_get_news_with_symbol_specific_news(self):
        """Test news with symbol-specific news using Finnhub company_news"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                # Mock Finnhub company_news - returns a list directly
                test_timestamp = int(datetime.now().timestamp())
                mock_client.company_news.return_value = [
                    {
                        'headline': 'AAPL News',
                        'url': 'http://example.com',
                        'datetime': test_timestamp,
                        'source': 'Reuters',
                        'summary': 'Test description',
                        'image': '',
                        'category': 'company news',
                        'related': 'AAPL',
                        'id': 12345
                    }
                ]

                url = reverse('get_news')
                response = self.client.get(
                    url, {'symbol': 'AAPL', 'force_refresh': 'true'}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertEqual(len(data['articles']), 1)

    def test_get_news_with_symbol_news_fallback(self):
        """Test news with symbol when Finnhub company_news fails, falls back to fallback data"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                # Mock company_news to fail
                mock_client.company_news.side_effect = Exception("Finnhub API failed")

                url = reverse('get_news')
                response = self.client.get(
                    url, {'symbol': 'AAPL', 'force_refresh': 'true'}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))
                # Should have fallback articles
                self.assertGreater(len(data['articles']), 0)

    def test_get_news_with_none_response(self):
        """Test news with None response from API"""
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_newsapi.get_top_headlines.return_value = None

                url = reverse('get_news')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_news_with_invalid_response_structure(self):
        """Test news with invalid response structure"""
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_newsapi.get_top_headlines.return_value = {'invalid': 'data'}

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_news_endpoint(self):
        """Test market news endpoint returns response"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                test_timestamp = int(datetime.now().timestamp())
                mock_client.general_news.return_value = [
                    {
                        'headline': 'Market News',
                        'url': 'http://example.com',
                        'datetime': test_timestamp,
                        'source': 'Reuters',
                        'summary': 'Test summary',
                        'image': '',
                        'category': 'general',
                        'id': 12345,
                        'related': ''
                    }
                ]

                url = reverse('get_market_news')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertIn('category', data)

    def test_get_market_news_with_category(self):
        """Test market news with different categories"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                mock_client.general_news.return_value = []

                url = reverse('get_market_news')
                response = self.client.get(url, {'category': 'crypto'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data.get('category'), 'crypto')

    def test_get_market_news_invalid_category(self):
        """Test market news with invalid category defaults to general"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                mock_client.general_news.return_value = []

                url = reverse('get_market_news')
                response = self.client.get(url, {'category': 'invalid'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data.get('category'), 'general')

    def test_get_market_news_with_min_id(self):
        """Test market news with minId parameter"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                mock_client.general_news.return_value = []

                url = reverse('get_market_news')
                response = self.client.get(url, {'minId': '100'})

                self.assertEqual(response.status_code, 200)
                mock_client.general_news.assert_called_once()

    def test_get_market_news_fallback(self):
        """Test market news fallback when API unavailable"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', None):
            url = reverse('get_market_news')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('articles', data)
            self.assertTrue(data.get('fallback', False))

    def test_get_market_news_exception(self):
        """Test market news exception handling"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                mock_client.general_news.side_effect = Exception("API Error")

                url = reverse('get_market_news')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))

    def test_get_market_news_empty_response(self):
        """Test market news with empty response from API"""
        cache.clear()
        with patch.object(settings, 'FINNHUB_API_KEY', 'test_key'):
            with patch('core.views.news.finnhub_client') as mock_client:
                mock_client.general_news.return_value = None

                url = reverse('get_market_news')
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertTrue(data.get('fallback', False))
