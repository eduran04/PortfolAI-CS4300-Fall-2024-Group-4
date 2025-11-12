"""
PortfolAI Basic Views Test Suite
=================================

Tests for core application views and basic API functionality:
- Landing page rendering
- Dashboard view
- Hello API endpoint
"""

from django.test import TestCase
from django.urls import reverse


class BasicViewsTests(TestCase):
    """Test suite for basic application views"""

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
        # Dashboard requires authentication, so create and login a user
        from django.contrib.auth.models import User
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        url = reverse('dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')
