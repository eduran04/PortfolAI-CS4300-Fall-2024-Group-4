"""
PortfolAI Authentication Test Suite
===================================

This test suite validates all authentication features of the PortfolAI application:

SECTION 1: USER REGISTRATION TESTS
- User registration with valid data
- Duplicate email validation
- Duplicate username validation
- Form validation errors
- Password mismatch handling

SECTION 2: USER LOGIN TESTS
- Successful login with valid credentials
- Login with invalid username
- Login with invalid password
- Login redirects and session management

SECTION 3: USER LOGOUT TESTS
- Successful logout
- Logout redirects
- Session destruction

SECTION 4: PROTECTED VIEW TESTS
- Dashboard access when authenticated
- Dashboard access when unauthenticated
- Login_required decorator functionality

SECTION 5: WATCHLIST API AUTHENTICATION TESTS
- GET /api/watchlist/ authentication
- POST /api/watchlist/add/ authentication
- DELETE /api/watchlist/remove/ authentication
- User isolation between different users

Test Coverage: Comprehensive authentication flow testing
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from core.models import Watchlist


class AuthenticationTests(TestCase):
    """
    Test suite for authentication functionality including registration,
    login, logout, protected views, and authenticated API endpoints.
    """
    
    # ============================================================================
    # SECTION 1: USER REGISTRATION TESTS
    # ============================================================================
    # Tests for user registration functionality
    # - Valid registration
    # - Duplicate email/username validation
    # - Form validation errors
    # - Password requirements
    # ============================================================================
    
    def test_user_registration_success(self):
        """Test successful user registration with valid data"""
        url = reverse('signup')
        data = {
            'username': 'newuser1',
            'email': 'newuser1@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should redirect to login page after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser1').exists())
        user = User.objects.get(username='newuser1')
        self.assertEqual(user.email, 'newuser1@example.com')
        self.assertTrue(user.check_password('TestPassword123!'))
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email should fail"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='password123'
        )
        
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Duplicate email
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error (200 status, not redirect)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with this email already exists')
        
        # Verify new user was NOT created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username should fail"""
        # Create existing user for this test (use unique username to avoid conflicts)
        existing_username = 'duplicate_test_user'
        if not User.objects.filter(username=existing_username).exists():
            User.objects.create_user(
                username=existing_username,
                email='duplicate@example.com',
                password='password123'
            )
        
        url = reverse('signup')
        data = {
            'username': existing_username,  # Duplicate username
            'email': 'newduplicate@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error (200 status, not redirect)
        self.assertEqual(response.status_code, 200)
        # Django's UserCreationForm shows username error
        self.assertContains(response, 'A user with that username already exists', status_code=200)
        
        # Verify no additional user was created (should still be just the one we created)
        self.assertEqual(User.objects.filter(username=existing_username).count(), 1)
    
    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords should fail"""
        url = reverse('signup')
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'TestPassword123!',
            'password2': 'DifferentPassword123!'  # Mismatch
        }
        response = self.client.post(url, data)
        
        # Should return form with error
        self.assertEqual(response.status_code, 200)
        # Check for password mismatch error (can be in different formats)
        self.assertContains(response, "didn't match", status_code=200)
        
        # Verify user was NOT created
        self.assertFalse(User.objects.filter(username='newuser2').exists())
    
    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields should fail"""
        url = reverse('signup')
        data = {
            'username': 'newuser3',
            # Missing email
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error (200 status, not redirect)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was NOT created
        self.assertFalse(User.objects.filter(username='newuser3').exists())
    
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format should fail"""
        url = reverse('signup')
        data = {
            'username': 'newuser4',
            'email': 'invalid-email',  # Invalid format
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error (200 status, not redirect)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was NOT created
        self.assertFalse(User.objects.filter(username='newuser4').exists())
    
    def test_user_registration_get_request(self):
        """Test registration page renders correctly on GET request"""
        url = reverse('signup')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'signup', status_code=200)
    
    # ============================================================================
    # SECTION 2: USER LOGIN TESTS
    # ============================================================================
    # Tests for user login functionality
    # - Successful login
    # - Invalid credentials
    # - Redirects after login
    # - Session management
    # ============================================================================
    
    def setUp(self):
        """Set up test user for login tests"""
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
    
    def test_user_login_success(self):
        """Test successful login with valid credentials"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Verify user is authenticated
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')
    
    def test_user_login_invalid_username(self):
        """Test login with invalid username should fail"""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error (200 status, not redirect)
        self.assertEqual(response.status_code, 200)
        # Check for the actual error message from the template
        self.assertContains(response, "Your username and password didn't match")
        
        # Verify user is NOT authenticated
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_user_login_invalid_password(self):
        """Test login with invalid password should fail"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(url, data)
        
        # Should return form with error
        self.assertEqual(response.status_code, 200)
        # Check for the actual error message from the template
        self.assertContains(response, "Your username and password didn't match")
        
        # Verify user is NOT authenticated
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_user_login_empty_credentials(self):
        """Test login with empty credentials should fail"""
        url = reverse('login')
        data = {
            'username': '',
            'password': ''
        }
        response = self.client.post(url, data)
        
        # Should return form with error
        self.assertEqual(response.status_code, 200)
        
        # Verify user is NOT authenticated
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_user_login_get_request(self):
        """Test login page renders correctly on GET request"""
        url = reverse('login')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login', status_code=200)
    
    def test_user_login_redirects_to_dashboard(self):
        """Test login redirects to dashboard after success"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, data, follow=True)
        
        # Should eventually reach dashboard
        self.assertEqual(response.status_code, 200)
        # Check if redirected to dashboard (based on LOGIN_REDIRECT_URL setting)
        self.assertContains(response, 'PortfolAI', status_code=200)
    
    # ============================================================================
    # SECTION 3: USER LOGOUT TESTS
    # ============================================================================
    # Tests for user logout functionality
    # - Successful logout
    # - Logout redirects
    # - Session destruction
    # ============================================================================
    
    def test_user_logout_success(self):
        """Test successful logout"""
        # First login
        self.client.login(username='testuser', password='TestPassword123!')
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        
        # Then logout (Django's LogoutView requires POST)
        url = reverse('logout')
        response = self.client.post(url)
        
        # Should redirect to landing page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Verify user is NOT authenticated after logout
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_user_logout_redirects_to_landing(self):
        """Test logout redirects to landing page"""
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('logout')
        response = self.client.post(url, follow=True)
        
        # Should eventually reach landing page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI', status_code=200)
    
    def test_user_logout_destroys_session(self):
        """Test user session is destroyed after logout"""
        # Login and verify user is authenticated
        self.client.login(username='testuser', password='TestPassword123!')
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        
        # Logout (Django's LogoutView requires POST)
        url = reverse('logout')
        self.client.post(url)
        
        # User should be unauthenticated after logout
        # Note: Django test client may maintain session object, but authentication should be cleared
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    # ============================================================================
    # SECTION 4: PROTECTED VIEW TESTS
    # ============================================================================
    # Tests for protected views that require authentication
    # - Dashboard access when authenticated
    # - Dashboard access when unauthenticated
    # - Login_required decorator functionality
    # ============================================================================
    
    def test_dashboard_access_when_authenticated(self):
        """Test dashboard is accessible when user is authenticated"""
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('dashboard')
        response = self.client.get(url)
        
        # Should succeed (200 status)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PortfolAI')
    
    def test_dashboard_access_when_unauthenticated(self):
        """Test dashboard redirects to login when user is not authenticated"""
        url = reverse('dashboard')
        response = self.client.get(url)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        # Check if redirect URL contains login
        self.assertIn('login', response.url.lower())
    
    def test_login_required_decorator_functionality(self):
        """Test login_required decorator properly protects views"""
        # Try to access dashboard without authentication
        url = reverse('dashboard')
        response = self.client.get(url, follow=False)
        
        # Should redirect (not 200)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        
        # After login, should be able to access
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    # ============================================================================
    # SECTION 5: WATCHLIST API AUTHENTICATION TESTS
    # ============================================================================
    # Tests for watchlist API endpoints that require authentication
    # - GET /api/watchlist/ authentication
    # - POST /api/watchlist/add/ authentication
    # - DELETE /api/watchlist/remove/ authentication
    # - User isolation between different users
    # ============================================================================
    
    def test_get_watchlist_when_authenticated(self):
        """Test GET /api/watchlist/ succeeds when authenticated"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Add some items to watchlist
        Watchlist.objects.create(user=self.test_user, symbol='AAPL')
        Watchlist.objects.create(user=self.test_user, symbol='MSFT')
        
        url = reverse('get_watchlist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbols', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 2)
        self.assertIn('AAPL', data['symbols'])
        self.assertIn('MSFT', data['symbols'])
    
    def test_get_watchlist_when_unauthenticated(self):
        """Test GET /api/watchlist/ returns 401 when unauthenticated"""
        url = reverse('get_watchlist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Authentication required')
    
    def test_get_watchlist_empty_when_authenticated(self):
        """Test GET /api/watchlist/ returns empty list for new user"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        url = reverse('get_watchlist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['symbols'], [])
    
    def test_add_to_watchlist_when_authenticated(self):
        """Test POST /api/watchlist/add/ succeeds when authenticated"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        url = reverse('add_to_watchlist')
        data = {'symbol': 'AAPL'}
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('symbol', response_data)
        self.assertEqual(response_data['symbol'], 'AAPL')
        
        # Verify item was added to database
        self.assertTrue(Watchlist.objects.filter(user=self.test_user, symbol='AAPL').exists())
    
    def test_add_to_watchlist_when_unauthenticated(self):
        """Test POST /api/watchlist/add/ returns 401 when unauthenticated"""
        url = reverse('add_to_watchlist')
        data = {'symbol': 'AAPL'}
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Authentication required')
        
        # Verify item was NOT added to database
        self.assertFalse(Watchlist.objects.filter(symbol='AAPL').exists())
    
    def test_add_to_watchlist_duplicate_symbol(self):
        """Test adding duplicate symbol to watchlist returns success message"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Add symbol first time
        Watchlist.objects.create(user=self.test_user, symbol='AAPL')
        
        url = reverse('add_to_watchlist')
        data = {'symbol': 'AAPL'}
        response = self.client.post(url, data, content_type='application/json')
        
        # Should return 200 (not 201) with message that it's already in watchlist
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('already in your watchlist', response_data['message'])
    
    def test_add_to_watchlist_missing_symbol(self):
        """Test POST /api/watchlist/add/ with missing symbol returns 400"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        url = reverse('add_to_watchlist')
        data = {}  # Missing symbol
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Symbol is required')
    
    def test_remove_from_watchlist_when_authenticated(self):
        """Test DELETE /api/watchlist/remove/ succeeds when authenticated"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Add item first
        Watchlist.objects.create(user=self.test_user, symbol='AAPL')
        
        url = reverse('remove_from_watchlist')
        response = self.client.delete(url + '?symbol=AAPL')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('removed from watchlist', response_data['message'])
        
        # Verify item was removed from database
        self.assertFalse(Watchlist.objects.filter(user=self.test_user, symbol='AAPL').exists())
    
    def test_remove_from_watchlist_when_unauthenticated(self):
        """Test DELETE /api/watchlist/remove/ returns 401 when unauthenticated"""
        # Add item first (as another user or directly)
        Watchlist.objects.create(user=self.test_user, symbol='AAPL')
        
        url = reverse('remove_from_watchlist')
        response = self.client.delete(url + '?symbol=AAPL')
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Authentication required')
        
        # Verify item was NOT removed (still exists)
        self.assertTrue(Watchlist.objects.filter(user=self.test_user, symbol='AAPL').exists())
    
    def test_remove_from_watchlist_nonexistent_symbol(self):
        """Test DELETE /api/watchlist/remove/ with nonexistent symbol returns 404"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        url = reverse('remove_from_watchlist')
        response = self.client.delete(url + '?symbol=XYZ')
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('not in your watchlist', response_data['message'])
    
    def test_remove_from_watchlist_missing_symbol(self):
        """Test DELETE /api/watchlist/remove/ with missing symbol returns 400"""
        self.client.login(username='testuser', password='TestPassword123!')
        
        url = reverse('remove_from_watchlist')
        response = self.client.delete(url)  # No symbol parameter
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Symbol is required')
    
    def test_watchlist_user_isolation(self):
        """Test watchlist isolation between different users"""
        # Create second user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPassword123!'
        )
        
        # Add items for both users
        Watchlist.objects.create(user=self.test_user, symbol='AAPL')
        Watchlist.objects.create(user=self.test_user, symbol='MSFT')
        Watchlist.objects.create(user=user2, symbol='GOOGL')
        Watchlist.objects.create(user=user2, symbol='TSLA')
        
        # Login as first user
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('get_watchlist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should only see first user's items
        self.assertEqual(data['count'], 2)
        self.assertIn('AAPL', data['symbols'])
        self.assertIn('MSFT', data['symbols'])
        self.assertNotIn('GOOGL', data['symbols'])
        self.assertNotIn('TSLA', data['symbols'])
        
        # Login as second user
        self.client.logout()
        self.client.login(username='testuser2', password='TestPassword123!')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should only see second user's items
        self.assertEqual(data['count'], 2)
        self.assertIn('GOOGL', data['symbols'])
        self.assertIn('TSLA', data['symbols'])
        self.assertNotIn('AAPL', data['symbols'])
        self.assertNotIn('MSFT', data['symbols'])
    
    def test_watchlist_add_user_isolation(self):
        """Test adding to watchlist only affects current user"""
        # Create second user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPassword123!'
        )
        
        # Login as first user and add symbol
        self.client.login(username='testuser', password='TestPassword123!')
        url = reverse('add_to_watchlist')
        data = {'symbol': 'AAPL'}
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        # Verify only first user has the symbol
        self.assertTrue(Watchlist.objects.filter(user=self.test_user, symbol='AAPL').exists())
        self.assertFalse(Watchlist.objects.filter(user=user2, symbol='AAPL').exists())
        
        # Login as second user and add same symbol
        self.client.logout()
        self.client.login(username='testuser2', password='TestPassword123!')
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        # Now both users should have it, but as separate entries
        self.assertTrue(Watchlist.objects.filter(user=self.test_user, symbol='AAPL').exists())
        self.assertTrue(Watchlist.objects.filter(user=user2, symbol='AAPL').exists())
        self.assertEqual(Watchlist.objects.filter(symbol='AAPL').count(), 2)

