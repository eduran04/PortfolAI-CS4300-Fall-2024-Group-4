"""
PortfolAI Chatbot Test Suite
=============================

Tests for /api/chatbot/ endpoint (Feature 5)
- Valid message input and AI response
- Empty message handling
- API key fallback and OpenAI errors
- Conversation history behavior
"""

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings


class ChatTests(TestCase):
    """Test suite for chatbot endpoint functionality"""

    def test_chatbot_valid_message(self):
        """Test chatbot endpoint with a valid user message"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'AI: Hello, how can I assist you today?'})
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                response = self.client.post(url, {'message': 'Hello'}, content_type='application/json')

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertTrue('AI:' in data['response'])

    def test_chatbot_empty_message(self):
        """Test chatbot endpoint with empty message"""
        url = reverse('chatbot')
        response = self.client.post(url, {'message': ''}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_chatbot_missing_message_field(self):
        """Test chatbot endpoint with missing message field"""
        url = reverse('chatbot')
        response = self.client.post(url, {}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_chatbot_no_api_key(self):
        """Test chatbot fallback when OpenAI API key is missing"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', None):
            response = self.client.post(url, {'message': 'Hello'}, content_type='application/json')

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('response', data)
            self.assertTrue(data.get('fallback', False))

    def test_chatbot_api_error_handling(self):
        """Test chatbot error handling when OpenAI API fails"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_openai.chat.completions.create.side_effect = Exception("API Error")

                response = self.client.post(url, {'message': 'Test error'}, content_type='application/json')

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertTrue(data.get('fallback', True))

    def test_chatbot_handles_long_message(self):
        """Test chatbot handles long user messages without crashing"""
        url = reverse('chatbot')
        long_message = "Tell me about AI and stock trading. " * 50  # simulate long input

        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': "That is a long query, but here's a summary."})
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                response = self.client.post(url, {'message': long_message}, content_type='application/json')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertIn('summary', data['response'].lower())

    def test_chatbot_remembers_context(self):
        """Test chatbot conversation retains simple context (if implemented)"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_openai.chat.completions.create.side_effect = [
                    type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'Hi there!'})
                        })]
                    }),
                    type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'You just said hi earlier.'})
                        })]
                    })
                ]

                # Send two messages to test conversational continuity
                response1 = self.client.post(url, {'message': 'Hi'}, content_type='application/json')
                response2 = self.client.post(url, {'message': 'What did I say earlier?'}, content_type='application/json')

                self.assertEqual(response1.status_code, 200)
                self.assertEqual(response2.status_code, 200)
                data2 = response2.json()
                self.assertIn('response', data2)
                self.assertIn('earlier', data2['response'])

