"""
Unit tests for Learn API feature.
"""

import json
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse


class LearnFeatureTests(TestCase):
    """Tests for learning topics, details, and AI explanations."""

    def test_learn_topics_list(self):
        """Ensure /api/learn/topics returns the topic slugs."""
        url = reverse("learn_topics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("topics", data)
        self.assertGreater(len(data["topics"]), 0)

    def test_learn_topic_details_valid(self):
        """Ensure /api/learn/topic/<slug> works for a real topic."""
        url = reverse("learn_topic_detail",
                      args=["stock-market-basics"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_learn_topic_details_invalid_slug(self):
        """Ensure invalid slugs return 404."""
        url = reverse("learn_topic_detail", args=["bad-slug"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch("core.views.learn.openai_client")
    def test_learn_ai_valid_request(self, mock_client):
        """AI explanation works when patched with mock client."""
        mock_client.chat.completions.create.return_value = {
            "choices": [
                {"message": {"content": "Test explanation"}}
            ]
        }

        url = reverse("learn_ai_explanation")
        payload = {"topic": "stocks"}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("explanation", data)
        self.assertEqual(data["explanation"], "Test explanation")
