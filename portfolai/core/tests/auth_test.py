"""
PortfolAI Authentication Test Suite
===================================

Tests for demo-mode authentication: login, logout, protected views,
and ensure_demo_user management command.
"""

from io import StringIO

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.core.management import call_command


class AuthenticationTests(TestCase):
    """Test suite for demo authentication functionality."""

    def setUp(self) -> None:
        """Set up test user for login tests."""
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )

    def test_user_login_success(self) -> None:
        """Test successful login with valid credentials."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')

    def test_user_login_invalid_username(self) -> None:
        """Test login with invalid username should fail."""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Your username and password didn't match"
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_login_invalid_password(self) -> None:
        """Test login with invalid password should fail."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Your username and password didn't match"
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_login_empty_credentials(self) -> None:
        """Test login with empty credentials should fail."""
        url = reverse('login')
        data = {
            'username': '',
            'password': ''
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_login_get_request(self) -> None:
        """Test login page renders correctly on GET request."""
        url = reverse('login')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login', status_code=200)
        self.assertContains(response, 'Demo account')

    def test_user_login_redirects_to_dashboard(self) -> None:
        """Test login redirects to dashboard after success."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI', status_code=200)

    def test_signup_route_removed(self) -> None:
        """Test signup URL is no longer available."""
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 404)

    def test_user_logout_success(self) -> None:
        """Test successful logout."""
        self.client.login(username='testuser', password='TestPassword123!')
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        url = reverse('logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_logout_redirects_to_landing(self) -> None:
        """Test logout redirects to landing page."""
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('logout')
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI', status_code=200)

    def test_dashboard_access_when_authenticated(self) -> None:
        """Test dashboard is accessible when user is authenticated."""
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')

    def test_dashboard_access_when_unauthenticated(self) -> None:
        """Test dashboard redirects to login when user is not authenticated."""
        url = reverse('dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    @override_settings(DEMO_USERNAME='demo', DEMO_PASSWORD='demo123')
    def test_ensure_demo_user_creates_user(self) -> None:
        """Test ensure_demo_user management command creates the demo account."""
        out = StringIO()
        call_command('ensure_demo_user', stdout=out)

        self.assertTrue(User.objects.filter(username='demo').exists())
        user = User.objects.get(username='demo')
        self.assertTrue(user.check_password('demo123'))
        self.assertIn('demo', out.getvalue())

    @override_settings(DEMO_USERNAME='demo', DEMO_PASSWORD='newpass456')
    def test_ensure_demo_user_updates_password(self) -> None:
        """Test ensure_demo_user updates password on existing user."""
        User.objects.create_user(username='demo', password='oldpass')

        call_command('ensure_demo_user', stdout=StringIO())

        user = User.objects.get(username='demo')
        self.assertTrue(user.check_password('newpass456'))
        self.assertFalse(user.check_password('oldpass'))
