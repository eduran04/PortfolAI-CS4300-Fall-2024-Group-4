"""
Tests for the learning resources API (core.views.learn).
"""

import json
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class LearnFeatureTests(TestCase):
    """Test suite for the Learn API endpoints."""

    def setUp(self):
        """Initialize test client."""
        self.client = Client()

    # ------------------------------------------------------------------
    # Topic list
    # ------------------------------------------------------------------
    def test_learn_topics_list(self):
        """GET /api/learn/topics/ should return list of slugs."""
        url = reverse("learn_topics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("topics", data)
        self.assertGreater(len(data["topics"]), 0)

    # ------------------------------------------------------------------
    # Topic details
    # ------------------------------------------------------------------
    def test_learn_topic_details_valid(self):
        """GET valid slug should return topic content."""
        url = reverse("learn_topic_detail", args=["stock-market-basics"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_learn_topic_details_invalid_slug(self):
        """GET invalid slug should return 404."""
        url = reverse("learn_topic_detail", args=["invalid-topic-xyz"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # AI Explanation
    # ------------------------------------------------------------------
    def test_learn_ai_missing_topic(self):
        """POST without topic should return 400."""
        url = reverse("learn_ai_explanation")
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Missing topic")

    @patch("core.views.learn.openai_client")
    def test_learn_ai_valid_request(self, mock_openai):
        """POST valid topic should return generated explanation."""
        # Mock AI response
        mock_openai.chat.completions.create.return_value = {
            "choices": [{"message": {"content": "Mock explanation"}}]
        }

        url = reverse("learn_ai_explanation")
        payload = {"topic": "risk-vs-reward"}

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("explanation", data)
        self.assertEqual(data["explanation"], "Mock explanation")

    def test_learn_ai_requires_api_key(self):
        """Empty API key ('') should trigger a 500 error."""
        old_key = getattr(settings, "OPENAI_API_KEY", None)
        setattr(settings, "OPENAI_API_KEY", "")

        url = reverse("learn_ai_explanation")
        response = self.client.post(url, {"topic": "test"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"], "Missing OpenAI API key")

        # Restore key
        setattr(settings, "OPENAI_API_KEY", old_key)

    @patch("core.views.learn.openai_client")
    def test_learn_ai_api_error(self, mock_openai):
        """If OpenAI call throws an error, return 500."""
        mock_openai.chat.completions.create.side_effect = Exception("fail")

        url = reverse("learn_ai_explanation")
        payload = {"topic": "stock-market-basics"}

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())
