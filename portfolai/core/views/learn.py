"""
Learning Resources API Views
Provides topic lists, topic details, and AI explanations.
"""

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json


LEARN_DATA = {
    "stock-market-basics": {
        "title": "Stock Market Basics",
        "content": [
            "A stock represents fractional ownership in a company.",
            "When you buy a share, you own a small percentage of the business.",
            "Stock prices move based on supply/demand and company performance.",
            "Investors buy stocks to grow wealth over time."
        ],
    },

    "reading-stock-charts": {
        "title": "Reading Stock Charts",
        "content": [
            "Candlesticks represent price movement for a time interval.",
            "Green candles mean price closed higher; red means price fell.",
            "Volume bars show how many shares were traded.",
            "Trendlines help identify long-term movement."
        ],
    },

    "risk-vs-reward": {
        "title": "Risk vs Reward",
        "content": [
            "Higher potential returns usually come with higher risk.",
            "Diversification helps reduce portfolio risk.",
            "Understanding risk tolerance is key for investment strategy."
        ],
    },
}


def learn_topics(request):
    """
    Return a list of all learning topics (slugs).
    """
    return JsonResponse({"topics": list(LEARN_DATA.keys())})


def learn_topic_detail(request, slug):
    """
    Return detailed content for a specific topic slug.
    """
    if slug not in LEARN_DATA:
        return JsonResponse({"error": "Topic not found"}, status=404)

    return JsonResponse(LEARN_DATA[slug])


# ----------------------------
# Mock Client (for tests)
# ----------------------------

class MockClient:
    """Mock OpenAI client for unit tests."""

    class chat:
        """Mock chat namespace."""

        class completions:
            """Mock completions namespace."""

            @staticmethod
            def create(*args, **kwargs):
                return {
                    "choices": [
                        {"message": {"content": "Mock AI explanation text."}}
                    ]
                }


openai_client = MockClient()


@csrf_exempt
def learn_ai_explanation(request):
    """
    Generate an AI explanation for a topic.
    Tests patch the openai_client so this does not call a real API.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # Load JSON body safely
    try:
        body = json.loads(request.body) if request.body else {}
        topic = body.get("topic")
    except json.JSONDecodeError:
        topic = None

    if not topic:
        return JsonResponse({"error": "Missing topic"}, status=400)

    # Call mocked OpenAI client
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user",
                       "content": f"Explain this simply: {topic}"}],
        )
        explanation = response["choices"][0]["message"]["content"]
        return JsonResponse({"explanation": explanation})

    except Exception as exc:  
        return JsonResponse({"error": str(exc)}, status=500)
