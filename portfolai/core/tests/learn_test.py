"""
Tests for the learning resources API (core.views.learn).
"""

import json
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from core.views.learn import MockCompletion


class LearnFeatureTests(TestCase):
    """Test suite for the Learn API endpoints."""

    def setUp(self):
        """Initialize test client."""
        self.client = Client()

    def test_learn_topics_list(self):
        """GET /api/learn/topics/ should return list of slugs."""
        url = reverse("learn_topics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("topics", data)
        self.assertGreater(len(data["topics"]), 0)

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

    def test_learn_ai_requires_post_method(self):
        """GET on learn_ai_explanation should return 405."""
        url = reverse("learn_ai_explanation")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_learn_ai_missing_topic(self):
        """POST without topic should return 400."""
        url = reverse("learn_ai_explanation")
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 400)

    def test_learn_ai_invalid_json_body(self):
        """Invalid JSON with application/json should return 400."""
        url = reverse("learn_ai_explanation")
        response = self.client.post(
            url,
            data="not-valid-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("core.views.learn.openai_client")
    def test_learn_ai_valid_request(self, mock_openai):
        """POST valid topic returns mock explanation."""
        mock_openai.chat.completions.create.return_value = {
            "choices": [{"message": {"content": "Mock explanation"}}]
        }

        url = reverse("learn_ai_explanation")
        payload = {"topic": "risk-vs-reward"}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("explanation", data)
        self.assertEqual(data["explanation"], "Mock explanation")

    @patch("core.views.learn.openai_client")
    def test_learn_ai_api_error(self, mock_openai):
        """Mock client error returns 500."""
        mock_openai.chat.completions.create.side_effect = Exception("fail")

        url = reverse("learn_ai_explanation")
        payload = {"topic": "stock-market-basics"}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())


class MockCompletionTests(TestCase):
    """Tests for the MockCompletion helper."""

    def test_mock_completion_direct_call(self):
        """Direct call to MockCompletion.create returns expected structure."""
        result = MockCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
        )
        self.assertEqual(
            result["choices"][0]["message"]["content"],
            "Mock AI explanation text.",
        )
