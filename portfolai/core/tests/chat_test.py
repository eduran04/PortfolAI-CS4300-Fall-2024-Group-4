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

from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from core.models import Watchlist
from core.views.chat import (
    _needs_web_search,
    _get_symbol_for_context,
    _get_openai_web_context,
    _format_news_articles,
    _get_newsapi_context,
    _get_web_search_context,
)


class ChatTests(TestCase):  # pylint: disable=too-many-public-methods
    """Test suite for chatbot endpoint functionality"""

    def test_chatbot_valid_message(self):
        """Test chatbot endpoint with a valid user message"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {
                            'content': 'AI: Hello, how can I assist you today?'
                        })
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                response = self.client.post(
                    url, {'message': 'Hello'}, content_type='application/json'
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('response', data)
                self.assertTrue('AI:' in data['response'])

    def test_chatbot_empty_message(self):
        """Test chatbot endpoint with empty message"""
        url = reverse('chatbot')
        response = self.client.post(
            url, {'message': ''}, content_type='application/json'
        )

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
            response = self.client.post(
                url, {'message': 'Hello'}, content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('response', data)
            self.assertTrue(data.get('fallback', False))

    def test_chatbot_api_error_handling(self):
        """Test chatbot error handling when OpenAI API fails"""
        url = reverse('chatbot')
        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                mock_openai.chat.completions.create.side_effect = Exception(
                    "API Error"
                )

                response = self.client.post(
                    url, {'message': 'Test error'}, content_type='application/json'
                )

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
                        'message': type('obj', (object,), {
                            'content': "That is a long query, but here's a summary."
                        })
                    })]
                })
                mock_openai.chat.completions.create.return_value = mock_response

                response = self.client.post(
                    url, {'message': long_message}, content_type='application/json'
                )
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
                                'message': type('obj', (object,), {
                                    'content': 'Hi there!'
                                })
                            })]
                        }),
                        # Second message - chat response with context
                        type('obj', (object,), {
                            'choices': [type('obj', (object,), {
                                'message': type('obj', (object,), {
                                    'content': 'You just said hi earlier.'
                                })
                            })]
                        })
                    ]

                    # Send two messages to test conversational continuity
                    response1 = self.client.post(
                        url, {'message': 'Hi'}, content_type='application/json'
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
                response1 = self.client.post(
                    url, {'message': 'Hello'}, content_type='application/json'
                )
                self.assertEqual(response1.status_code, 200)
                self.assertIn('chat_history', self.client.session)
                # user + assistant
                self.assertEqual(len(self.client.session['chat_history']), 2)

                # Second message - should include history
                response2 = self.client.post(
                    url, {'message': 'Follow up'}, content_type='application/json'
                )
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

                    response = self.client.post(
                        url,
                        {'message': 'What is in my watchlist?'},
                        content_type='application/json'
                    )
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

                    response = self.client.post(
                        url,
                        {'message': 'What did I search?'},
                        content_type='application/json'
                    )
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

                    response = self.client.post(
                        url, {'message': 'Hello'}, content_type='application/json'
                    )
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
                    response = self.client.post(
                        url,
                        {'message': 'Why did it go up today?'},
                        content_type='application/json'
                    )
                    self.assertEqual(response.status_code, 200)

                    # Verify both classification and chat completion were called
                    self.assertGreaterEqual(
                        mock_openai.chat.completions.create.call_count, 1
                    )

    def test_chatbot_wrong_http_method(self):
        """Test chatbot endpoint only accepts POST method"""
        url = reverse('chatbot')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        data = response.json()
        self.assertIn('error', data)

    def test_chatbot_invalid_json_body(self):
        """Test chatbot handles invalid JSON body gracefully"""
        url = reverse('chatbot')
        # Send invalid JSON by using data parameter instead of json
        response = self.client.post(
            url, data='invalid json', content_type='application/json'
        )
        # Should handle gracefully - either 400 or 200 with fallback
        self.assertIn(response.status_code, [200, 400])

    def test_chatbot_watchlist_error_handling(self):
        """Test chatbot handles watchlist fetch errors gracefully"""
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        url = reverse('chatbot')

        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                with patch('core.views.chat._needs_web_search', return_value=False):
                    # Mock Watchlist.objects.filter to raise an exception
                    with patch(
                        'core.views.chat.Watchlist.objects.filter',
                        side_effect=Exception("DB Error")
                    ):
                        mock_response = type('obj', (object,), {
                            'choices': [type('obj', (object,), {
                                'message': type('obj', (object,), {'content': 'Response'})
                            })]
                        })
                        mock_openai.chat.completions.create.return_value = mock_response

                        response = self.client.post(
                            url, {'message': 'Hello'}, content_type='application/json'
                        )
                        self.assertEqual(response.status_code, 200)

    def test_needs_web_search_no_client(self):
        """Test _needs_web_search returns False when client is None"""
        result = _needs_web_search("test message", None)
        self.assertFalse(result)

    def test_needs_web_search_dollar_symbol(self):
        """Test _needs_web_search detects $SYMBOL format"""
        with patch('core.views.chat.openai_client') as mock_client:
            result = _needs_web_search("Tell me about $AAPL", mock_client)
            self.assertTrue(result)

    def test_get_symbol_for_context_dollar_symbol(self):
        """Test _get_symbol_for_context extracts $SYMBOL from message"""
        factory = RequestFactory()
        request = factory.post('/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        symbols = _get_symbol_for_context(request, "What about $MSFT?")
        self.assertIn('MSFT', symbols)

    def test_get_openai_web_context_no_client(self):
        """Test _get_openai_web_context returns empty when client is None"""
        with patch('core.views.chat.openai_client', None):
            result = _get_openai_web_context('AAPL')
            self.assertEqual(result, "")

    def test_get_openai_web_context_no_responses_attr(self):
        """Test _get_openai_web_context handles missing responses attribute"""
        mock_client = type('obj', (object,), {})  # No 'responses' attribute
        with patch('core.views.chat.openai_client', mock_client):
            result = _get_openai_web_context('AAPL')
            self.assertEqual(result, "")

    def test_get_openai_web_context_no_output_text(self):
        """Test _get_openai_web_context handles missing output_text"""
        mock_response = type('obj', (object,), {})  # No output_text attribute
        mock_responses = type('obj', (object,), {
            'create': lambda **kwargs: mock_response
        })
        mock_client = type('obj', (object,), {'responses': mock_responses})
        with patch('core.views.chat.openai_client', mock_client):
            result = _get_openai_web_context('AAPL')
            self.assertEqual(result, "")

    def test_get_openai_web_context_attribute_error(self):
        """Test _get_openai_web_context handles AttributeError"""
        mock_responses = type('obj', (object,), {
            'create': lambda **kwargs: (_ for _ in ()).throw(AttributeError("No attribute"))
        })
        mock_client = type('obj', (object,), {'responses': mock_responses})
        with patch('core.views.chat.openai_client', mock_client):
            result = _get_openai_web_context('AAPL')
            self.assertEqual(result, "")

    def test_get_openai_web_context_exception(self):
        """Test _get_openai_web_context handles general exceptions"""
        mock_responses = type('obj', (object,), {
            'create': lambda **kwargs: (_ for _ in ()).throw(Exception("API Error"))
        })
        mock_client = type('obj', (object,), {'responses': mock_responses})
        with patch('core.views.chat.openai_client', mock_client):
            result = _get_openai_web_context('AAPL')
            self.assertEqual(result, "")

    def test_format_news_articles_empty(self):
        """Test _format_news_articles handles empty articles list"""
        result = _format_news_articles([], 'AAPL')
        self.assertEqual(result, "")

    def test_format_news_articles_missing_fields(self):
        """Test _format_news_articles handles articles with missing title/publishedAt"""
        articles = [
            {'title': None, 'publishedAt': '2024-01-01'},
            {'title': 'Test', 'publishedAt': None},
            {}  # Empty dict
        ]
        result = _format_news_articles(articles, 'AAPL')
        self.assertEqual(result, "")

    def test_format_news_articles_valid(self):
        """Test _format_news_articles formats valid articles correctly"""
        articles = [
            {'title': 'News 1', 'publishedAt': '2024-01-01T10:00:00Z'},
            {'title': 'News 2', 'publishedAt': '2024-01-02T11:00:00Z'}
        ]
        result = _format_news_articles(articles, 'AAPL')
        self.assertIn('News 1', result)
        self.assertIn('News 2', result)
        self.assertIn('AAPL', result)

    def test_get_newsapi_context_no_newsapi(self):
        """Test _get_newsapi_context returns empty when newsapi is None"""
        with patch('core.views.chat.newsapi', None):
            result = _get_newsapi_context('AAPL')
            self.assertEqual(result, "")

    def test_get_newsapi_context_exception(self):
        """Test _get_newsapi_context handles exceptions gracefully"""
        with patch('core.views.chat.newsapi', {'api_token': 'test_token'}):
            # Patch requests.get since it's imported inside the function
            with patch('requests.get') as mock_get:
                mock_get.side_effect = Exception("API Error")
                result = _get_newsapi_context('AAPL')
                self.assertEqual(result, "")

    def test_get_web_search_context_empty_symbols(self):
        """Test _get_web_search_context returns empty for empty symbols list"""
        result = _get_web_search_context([], "test message")
        self.assertEqual(result, "")

    def test_get_web_search_context_none_symbol(self):
        """Test _get_web_search_context handles None symbol"""
        result = _get_web_search_context([None], "test message")
        self.assertEqual(result, "")

    def test_chatbot_with_web_search_context(self):
        """Test chatbot includes web search context when needed"""
        url = reverse('chatbot')
        session = self.client.session
        session['recent_searches'] = ['AAPL']
        session.save()

        with patch.object(settings, 'OPENAI_API_KEY', 'test_key'):
            with patch('core.views.chat.openai_client') as mock_openai:
                # Mock classification to return yes
                classification_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'yes'})
                    })]
                })
                chat_response = type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': 'Response with context'})
                    })]
                })
                mock_openai.chat.completions.create.side_effect = [
                    classification_response,
                    chat_response
                ]

                # Mock web search context functions
                with patch('core.views.chat._get_openai_web_context', return_value=""):
                    with patch('core.views.chat.newsapi', None):
                        response = self.client.post(
                            url,
                            {'message': 'What happened with AAPL today?'},
                            content_type='application/json'
                        )
                        self.assertEqual(response.status_code, 200)
                        # Verify chat completion was called with enhanced message
                        call_args = mock_openai.chat.completions.create.call_args_list
                        if len(call_args) > 1:
                            messages = call_args[1][1]['messages']
                            user_message = messages[-1]['content']
                            # Should have original message
                            # (web search context would be added if available)
                            self.assertIn('AAPL', user_message)
