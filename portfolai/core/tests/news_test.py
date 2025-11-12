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

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings


class NewsTests(TestCase):
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
        from django.core.cache import cache
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
        from django.core.cache import cache
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
        from django.core.cache import cache
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                mock_articles = {
                    'articles': [
                        {
                            'title': 'Valid Article',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        },
                        {
                            'title': '',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'}
                        },  # Invalid - no title
                        {
                            'title': 'Valid Article 2',
                            'url': '',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'}
                        },  # Invalid - no URL
                        {
                            'title': 'Valid Article 3',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description 3'
                        }
                    ],
                    'totalResults': 4
                }
                mock_newsapi.get_top_headlines.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                # Should only have 2 valid articles
                # (filtered out invalid ones: article 2 has no title, article 3 has no URL)
                self.assertEqual(len(data['articles']), 2)

    def test_get_news_time_formatting(self):
        """Test news time formatting logic"""
        from django.core.cache import cache
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
        from django.core.cache import cache
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
        from django.core.cache import cache
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
        from django.core.cache import cache
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
        from django.core.cache import cache
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
        from django.core.cache import cache
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                # Mock articles with missing required fields
                mock_articles = {
                    'articles': [
                        {
                            'title': '',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'}
                        },  # Missing title
                        {
                            'title': 'Valid Title',
                            'url': '',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'}
                        },  # Missing URL
                        {
                            'title': 'Valid Title 2',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        }
                    ],
                    'totalResults': 3
                }
                mock_newsapi.get_top_headlines.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(url, {'force_refresh': 'true'})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                # Should only have 1 valid article (others filtered out)
                self.assertEqual(len(data['articles']), 1)

    def test_get_news_with_symbol_specific_news(self):
        """Test news with symbol-specific news using get_everything"""
        from django.core.cache import cache
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                # Mock successful get_everything call
                mock_articles = {
                    'articles': [
                        {
                            'title': 'AAPL News',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        }
                    ],
                    'totalResults': 1
                }
                mock_newsapi.get_everything.return_value = mock_articles

                url = reverse('get_news')
                response = self.client.get(
                    url, {'symbol': 'AAPL', 'force_refresh': 'true'}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertEqual(len(data['articles']), 1)

    def test_get_news_with_symbol_news_fallback(self):
        """Test news with symbol when get_everything fails, falls back to headlines"""
        from django.core.cache import cache
        cache.clear()  # Clear cache to ensure fresh request
        with patch.object(settings, 'NEWS_API_KEY', 'test_key'):
            with patch('core.views.news.newsapi') as mock_newsapi:
                # Mock get_everything to fail, headlines to succeed
                mock_newsapi.get_everything.side_effect = Exception("Everything API failed")
                mock_newsapi.get_top_headlines.return_value = {
                    'articles': [
                        {
                            'title': 'Business News',
                            'url': 'http://example.com',
                            'publishedAt': '2024-01-01T10:00:00Z',
                            'source': {'name': 'Test Source'},
                            'description': 'Test description'
                        }
                    ],
                    'totalResults': 1
                }

                url = reverse('get_news')
                response = self.client.get(
                    url, {'symbol': 'AAPL', 'force_refresh': 'true'}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('articles', data)
                self.assertEqual(len(data['articles']), 1)

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
        from django.core.cache import cache
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
