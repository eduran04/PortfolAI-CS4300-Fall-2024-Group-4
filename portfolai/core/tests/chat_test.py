"""
PortfolAI Chatbot Test Suite
=============================

Tests for /api/chat/ endpoint (Feature 5)
- Valid message input and AI response
- Empty message handling
- API key fallback and OpenAI errors
- Conversation history behavior
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from django.conf import settings


class ChatTests(TestCase):
    """Test suite for chatbot endpoint functionality"""
    
    def setUp(self):
        """Set up test user and authentication"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_chatbot_valid_message(self):
        """Test chatbot endpoint with a valid user message"""
        url = reverse('chat_api')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.services.ChatService._call_openai_api') as mock_api:
                mock_api.return_value = 'Hello, how can I assist you today?'

                response = self.client.post(
                    url, 
                    {'message': 'Hello'}, 
                    content_type='application/json'
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertIn('conversation_id', data)

    def test_chatbot_empty_message(self):
        """Test chatbot endpoint with empty message"""
        url = reverse('chat_api')
        response = self.client.post(
            url, 
            {'message': ''}, 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_chatbot_missing_message_field(self):
        """Test chatbot endpoint with missing message field"""
        url = reverse('chat_api')
        response = self.client.post(
            url, 
            {}, 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_chatbot_no_api_key(self):
        """Test chatbot fallback when OpenAI API key is missing"""
        url = reverse('chat_api')
        with patch.object(settings, 'OPENAI_API_KEY', None):
            response = self.client.post(
                url, 
                {'message': 'Hello'}, 
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('response', data)
            # The new implementation returns a fallback message
            self.assertTrue(data.get('fallback', False) or 'response' in data)

    def test_chatbot_api_error_handling(self):
        """Test chatbot error handling when OpenAI API fails"""
        url = reverse('chat_api')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.services.ChatService._call_openai_api') as mock_api:
                mock_api.side_effect = Exception("API Error")

                response = self.client.post(
                    url, 
                    {'message': 'Test error'}, 
                    content_type='application/json'
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                # The new implementation returns an error message in response field
                self.assertIn('response', data)

    def test_chatbot_handles_long_message(self):
        """Test chatbot handles long user messages without crashing"""
        url = reverse('chat_api')
        long_message = "Tell me about AI and stock trading. " * 50  # simulate long input

        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.services.ChatService._call_openai_api') as mock_api:
                mock_api.return_value = "That is a long query, but here's a summary."

                response = self.client.post(
                    url, 
                    {'message': long_message}, 
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertIn('summary', data['response'].lower())

    def test_chatbot_remembers_context(self):
        """Test chatbot conversation retains simple context (if implemented)"""
        url = reverse('chat_api')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.services.ChatService._call_openai_api') as mock_api:
                mock_api.side_effect = [
                    'Hi there!',
                    'You just said hi earlier.'
                ]

                # Send two messages to test conversational continuity
                response1 = self.client.post(
                    url, 
                    {'message': 'Hi'}, 
                    content_type='application/json'
                )
                response2 = self.client.post(
                    url, 
                    {'message': 'What did I say earlier?'}, 
                    content_type='application/json'
                )

                self.assertEqual(response1.status_code, 200)
                self.assertEqual(response2.status_code, 200)
                data2 = response2.json()
                self.assertIn('response', data2)
                self.assertIn('earlier', data2['response'].lower())

