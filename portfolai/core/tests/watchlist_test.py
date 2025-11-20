"""
PortfolAI Watchlist Test Suite
===============================

Tests for watchlist endpoints (functional tests)
- GET /api/watchlist/ - Retrieve user's watchlist
- POST /api/watchlist/add/ - Add symbol to watchlist
- DELETE /api/watchlist/remove/ - Remove symbol from watchlist

Note: Authentication tests are in auth_test.py
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Watchlist
from .test_helpers import assert_watchlist_response_empty, assert_watchlist_response_with_items


class WatchlistTests(TestCase):
    """Test suite for watchlist endpoint functionality"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_get_watchlist_empty(self):
        """Test getting empty watchlist"""
        url = reverse('get_watchlist')
        response = self.client.get(url)
        assert_watchlist_response_empty(response, self)

    def test_add_to_watchlist(self):
        """Test adding symbol to watchlist"""
        url = reverse('add_to_watchlist')
        response = self.client.post(
            url,
            {'symbol': 'AAPL'},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['symbol'], 'AAPL')

        # Verify it was added to database
        self.assertTrue(
            Watchlist.objects.filter(user=self.user, symbol='AAPL').exists()
        )

    def test_get_watchlist_with_items(self):
        """Test getting watchlist with items"""
        # Add some items first
        Watchlist.objects.create(user=self.user, symbol='AAPL')
        Watchlist.objects.create(user=self.user, symbol='MSFT')

        url = reverse('get_watchlist')
        response = self.client.get(url)
        assert_watchlist_response_with_items(response, self, 2, ['AAPL', 'MSFT'])

    def test_remove_from_watchlist(self):
        """Test removing symbol from watchlist"""
        # Add item first
        Watchlist.objects.create(user=self.user, symbol='AAPL')

        url = reverse('remove_from_watchlist')
        response = self.client.delete(
            url,
            {'symbol': 'AAPL'},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

        # Verify it was removed from database
        self.assertFalse(
            Watchlist.objects.filter(user=self.user, symbol='AAPL').exists()
        )

    def test_add_duplicate_symbol(self):
        """Test adding duplicate symbol to watchlist"""
        # Add item first
        Watchlist.objects.create(user=self.user, symbol='AAPL')

        url = reverse('add_to_watchlist')
        response = self.client.post(
            url,
            {'symbol': 'AAPL'},
            content_type='application/json'
        )

        # Should return 200 for duplicate (idempotent behavior)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('already in your watchlist', data['message'])

    def test_remove_nonexistent_symbol(self):
        """Test removing symbol that doesn't exist in watchlist"""
        url = reverse('remove_from_watchlist')
        response = self.client.delete(
            url,
            {'symbol': 'AAPL'},
            content_type='application/json'
        )

        # Should return 404 for nonexistent symbol
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('not in your watchlist', data['message'])

    def test_get_watchlist_exception(self):
        """Test get_watchlist exception handling"""
        url = reverse('get_watchlist')
        with patch('core.views.watchlist.Watchlist.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            response = self.client.get(url)

            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)

    def test_add_to_watchlist_exception(self):
        """Test add_to_watchlist exception handling"""
        url = reverse('add_to_watchlist')
        with patch('core.views.watchlist.Watchlist.objects.create') as mock_create:
            mock_create.side_effect = Exception("Database error")

            response = self.client.post(
                url,
                {'symbol': 'AAPL'},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)

    def test_add_to_watchlist_empty_symbol(self):
        """Test add_to_watchlist with empty symbol"""
        url = reverse('add_to_watchlist')
        response = self.client.post(
            url,
            {'symbol': ''},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_remove_from_watchlist_exception(self):
        """Test remove_from_watchlist exception handling"""
        url = reverse('remove_from_watchlist')
        with patch('core.views.watchlist.Watchlist.objects.filter') as mock_filter:
            # Mock the queryset and its delete method
            mock_queryset = MagicMock()
            mock_queryset.delete.side_effect = Exception("Database error")
            mock_filter.return_value = mock_queryset

            response = self.client.delete(
                url,
                {'symbol': 'AAPL'},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)

    def test_remove_from_watchlist_empty_symbol(self):
        """Test remove_from_watchlist with empty symbol"""
        url = reverse('remove_from_watchlist')
        response = self.client.delete(
            url,
            {'symbol': ''},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_remove_from_watchlist_query_param(self):
        """Test remove_from_watchlist with symbol in query parameter"""
        # Add item first
        Watchlist.objects.create(user=self.user, symbol='AAPL')

        url = reverse('remove_from_watchlist')
        response = self.client.delete(url + '?symbol=AAPL')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
