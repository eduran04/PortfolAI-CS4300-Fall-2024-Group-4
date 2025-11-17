"""Tests for the Learn feature API endpoints."""

import json

from django.test import Client, TestCase
from django.urls import reverse


class LearnFeatureTests(TestCase):
    """Basic tests for Learn API endpoints."""

    def setUp(self) -> None:
        self.client = Client()

    def test_learn_topics_list(self) -> None:
        """Learn topics endpoint returns a non-empty list."""
        response = self.client.get(reverse("learn_topics"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("topics", data)
        self.assertIsInstance(data["topics"], list)
        self.assertGreater(len(data["topics"]), 0)

    def test_learn_topic_details_valid(self) -> None:
        """Valid slug returns topic details with title and content."""
        response = self.client.get(
            reverse("learn_topic_detail", args=["stock-market-basics"])
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_learn_topic_details_invalid_slug(self) -> None:
        """Invalid slug returns 404 and an error message."""
        response = self.client.get(
            reverse("learn_topic_detail", args=["does-not-exist"])
        )
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn("error", data)

    def test_learn_ai_missing_topic(self) -> None:
        """AI explanation endpoint returns 400 when topic is missing."""
        response = self.client.post(
            reverse("learn_ai_explanation"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("error", data)
