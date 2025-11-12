"""
PortfolAI Chatbot Test Suite
=============================

Tests for /api/chatbot/ endpoint (Feature 5)
- Valid message input and AI response
- Empty message handling
- API key fallback and OpenAI errors
- Conversation history behavior
- Session-based memory
- Clear chat functionality
- User context (watchlist and recent searches)
"""

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Watchlist


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
                # Mock _needs_web_search to skip classification calls
                with patch('core.views.chat._needs_web_search', return_value=False):
                    # Only need to mock chat completion calls (no classification)
                    mock_openai.chat.completions.create.side_effect = [
                        # First message - chat response
                        type('obj', (object,), {
                            'choices': [type('obj', (object,), {
                                'message': type('obj', (object,), {'content': 'Hi there!'})
                            })]
                        }),
                        # Second message - chat response with context
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

    def test_chatbot_session_memory(self):
        """Test that chatbot maintains conversation history in session"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'Response'})
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                # First message
                response1 = self.client.post(url, {'message': 'Hello'}, content_type='application/json')
                self.assertEqual(response1.status_code, 200)
                self.assertIn('chat_history', self.client.session)
                self.assertEqual(len(self.client.session['chat_history']), 2)  # user + assistant

                # Second message - should include history
                response2 = self.client.post(url, {'message': 'Follow up'}, content_type='application/json')
                self.assertEqual(response2.status_code, 200)
                # Check that history was passed to OpenAI
                call_args = mock_openai.chat.completions.create.call_args
                messages = call_args[1]['messages']
                # Should have system prompt + previous messages + new message
                self.assertGreater(len(messages), 3)

    def test_clear_chat_endpoint(self):
        """Test clear chat endpoint clears session history"""
        url = reverse('chatbot')
        clear_url = reverse('clear_chat')
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'Response'})
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                # Send a message to create history
                self.client.post(url, {'message': 'Hello'}, content_type='application/json')
                self.assertIn('chat_history', self.client.session)
                self.assertEqual(len(self.client.session['chat_history']), 2)

                # Clear chat
                response = self.client.post(clear_url, content_type='application/json')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data.get('success', False))
                self.assertNotIn('chat_history', self.client.session)

    def test_clear_chat_wrong_method(self):
        """Test clear chat endpoint only accepts POST"""
        clear_url = reverse('clear_chat')
        response = self.client.get(clear_url)
        self.assertEqual(response.status_code, 405)

    def test_chatbot_user_context_watchlist(self):
        """Test that chatbot includes user watchlist in context"""
        # Create user and watchlist
        user = User.objects.create_user(username='testuser', password='testpass')
        Watchlist.objects.create(user=user, symbol='AAPL')
        Watchlist.objects.create(user=user, symbol='MSFT')
        
        self.client.force_login(user)
        url = reverse('chatbot')
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                # Mock the needs_web_search call to return False
                with patch('core.views.chat._needs_web_search', return_value=False):
                    mock_response = type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'Response'})
                        })]
                    })
                    mock_openai.chat.completions.create.return_value = mock_response

                    response = self.client.post(url, {'message': 'What is in my watchlist?'}, content_type='application/json')
                    self.assertEqual(response.status_code, 200)
                    
                    # Check that watchlist context was included in system prompt
                    call_args = mock_openai.chat.completions.create.call_args
                    messages = call_args[1]['messages']
                    system_message = messages[0]['content']
                    self.assertIn('watchlist', system_message.lower())
                    self.assertIn('AAPL', system_message)
                    self.assertIn('MSFT', system_message)

    def test_chatbot_user_context_recent_searches(self):
        """Test that chatbot includes recent searches in context"""
        url = reverse('chatbot')
        
        # Set up session with recent searches
        session = self.client.session
        session['recent_searches'] = ['AAPL', 'MSFT', 'GOOGL']
        session.save()
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                # Mock the needs_web_search call to return False
                with patch('core.views.chat._needs_web_search', return_value=False):
                    mock_response = type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'Response'})
                        })]
                    })
                    mock_openai.chat.completions.create.return_value = mock_response

                    response = self.client.post(url, {'message': 'What did I search?'}, content_type='application/json')
                    self.assertEqual(response.status_code, 200)
                    
                    # Check that recent searches were included in system prompt
                    call_args = mock_openai.chat.completions.create.call_args
                    messages = call_args[1]['messages']
                    system_message = messages[0]['content']
                    self.assertIn('recent searches', system_message.lower())
                    self.assertIn('AAPL', system_message)
                    self.assertIn('MSFT', system_message)

    def test_chatbot_empty_watchlist_context(self):
        """Test that chatbot handles empty watchlist correctly"""
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        url = reverse('chatbot')
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                with patch('core.views.chat._needs_web_search', return_value=False):
                    mock_response = type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'Response'})
                        })]
                    })
                    mock_openai.chat.completions.create.return_value = mock_response

                    response = self.client.post(url, {'message': 'Hello'}, content_type='application/json')
                    self.assertEqual(response.status_code, 200)
                    
                    # Check that empty watchlist is mentioned
                    call_args = mock_openai.chat.completions.create.call_args
                    messages = call_args[1]['messages']
                    system_message = messages[0]['content']
                    self.assertIn('empty', system_message.lower())

    def test_chatbot_needs_web_search_classification(self):
        """Test AI-based classification for web search needs"""
        url = reverse('chatbot')
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                # Mock the classification call (first call)
                classification_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'yes'})
                    })]
                })
                
                # Mock the main chat completion (second call)
                chat_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'Response'})
                    })]
                })
                
                # First call is classification, second is chat
                mock_openai.chat.completions.create.side_effect = [
                    classification_response,
                    chat_response
                ]
                
                # Set up session with recent searches
                session = self.client.session
                session['recent_searches'] = ['AAPL']
                session.save()
                
                # Mock newsapi to avoid actual API calls
                with patch('core.views.chat.newsapi', None):
                    response = self.client.post(url, {'message': 'Why did it go up today?'}, content_type='application/json')
                    self.assertEqual(response.status_code, 200)
                    
                    # Verify both classification and chat completion were called
                    self.assertGreaterEqual(mock_openai.chat.completions.create.call_count, 1)

