from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json


class LearnFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_learn_topics_list(self):
        """Check that the learn topics endpoint returns a list of topics"""
        response = self.client.get(reverse("learn_topics"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("topics", data)
        self.assertIsInstance(data["topics"], list)
        self.assertGreater(len(data["topics"]), 0)

    def test_learn_topic_details_valid(self):
        """Check that a valid topic slug returns topic details"""
        response = self.client.get(reverse("learn_topic_detail", args=["stock-market-basics"]))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_learn_topic_details_invalid_slug(self):
        """Check that invalid topic slugs return 404"""
        response = self.client.get(reverse("learn_topic_detail", args=["does-not-exist"]))
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn("error", data)

    def test_learn_ai_missing_topic(self):
        """Missing topic should return 400"""
        response = self.client.post(
            reverse("learn_ai_explanation"),
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        
    def test_learn_ai_empty_api_key(self):
        """If OPENAI_API_KEY is an empty string, return 500."""
        with self.settings(OPENAI_API_KEY=""):
            response = self.client.post(
                reverse("learn_ai_explanation"),
                data=json.dumps({"topic": "stocks"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())

    def test_learn_ai_invalid_json(self):
        """Invalid JSON should safely return missing topic."""
        response = self.client.post(
            reverse("learn_ai_explanation"),
            data="{not valid json",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_learn_ai_missing_topic_form(self):
        """POSTing form data without topic triggers missing topic error."""
        response = self.client.post(
            reverse("learn_ai_explanation"),
            data={},            # Form POST, not JSON
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("core.views.learn.openai_client.chat.completions.create")
    def test_learn_ai_openai_exception(self, mock_ai):
        """If the AI client raises an exception, return 500."""
        mock_ai.side_effect = Exception("AI failure")
        response = self.client.post(
            reverse("learn_ai_explanation"),
            data=json.dumps({"topic": "risk"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())

    @patch("core.views.learn.openai_client.chat.completions.create")
    def test_learn_ai_valid_json_request(self, mock_ai):
        """Valid JSON POST should succeed."""
        mock_ai.return_value = {
            "choices": [{"message": {"content": "Explanation text"}}]
        }

        response = self.client.post(
            reverse("learn_ai_explanation"),
            data=json.dumps({"topic": "chart analysis"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("explanation", response.json())

