"""
PortfolAI Chatbot Test Suite — demo mode
"""

import json

from django.test import TestCase
from django.urls import reverse

from core.views.chat import _get_demo_response


class ChatTests(TestCase):
    """Test suite for demo help chat endpoint."""

    def test_chatbot_valid_message(self):
        """Valid message returns demo help response."""
        url = reverse('chatbot')
        response = self.client.post(
            url,
            data=json.dumps({'message': 'How do I search for a stock?'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('response', data)
        self.assertTrue(data.get('demo', False))
        self.assertIn('search', data['response'].lower())

    def test_chatbot_empty_message(self):
        """Empty message returns 400."""
        url = reverse('chatbot')
        response = self.client.post(
            url,
            data=json.dumps({'message': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_chatbot_missing_message_field(self):
        """Missing message field returns 400."""
        url = reverse('chatbot')
        response = self.client.post(url, data={}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_chatbot_stores_session_history(self):
        """Chat stores conversation in session."""
        url = reverse('chatbot')
        self.client.post(
            url,
            data=json.dumps({'message': 'dashboard'}),
            content_type='application/json',
        )
        session = self.client.session
        self.assertIn('chat_history', session)
        self.assertEqual(len(session['chat_history']), 2)

    def test_clear_chat(self):
        """Clear chat removes session history."""
        url = reverse('chatbot')
        self.client.post(
            url,
            data=json.dumps({'message': 'hello'}),
            content_type='application/json',
        )
        clear_url = reverse('clear_chat')
        response = self.client.post(clear_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('chat_history', self.client.session)

    def test_get_demo_response_watchlist_keywords(self):
        """Keyword matching returns watchlist help."""
        response = _get_demo_response('What is the watchlist?')
        self.assertIn('localStorage', response)

    def test_get_demo_response_default(self):
        """Unknown query returns default help."""
        response = _get_demo_response('xyzzy unknown query')
        self.assertIn('Demo Help', response)
