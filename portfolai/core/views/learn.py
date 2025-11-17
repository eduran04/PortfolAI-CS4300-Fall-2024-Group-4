"""Learning resources API views for the PortfolAI application."""

import json
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# -------------------------------------------------------------------
# Learning Topic Data
# -------------------------------------------------------------------

LEARN_DATA = {
    "stock-market-basics": {
        "title": "Stock Market Basics",
        "content": [
            "A stock represents fractional ownership in a company.",
            "When you buy a share, you own a small percentage of the business.",
            "Stock prices move based on supply/demand and company performance.",
            "Investors buy stocks to grow wealth over time.",
        ],
    },
    "reading-stock-charts": {
        "title": "Reading Stock Charts",
        "content": [
            "Candlesticks represent price movement for a time interval.",
            "Green candles mean price closed higher; red means price fell.",
            "Volume bars show how many shares were traded.",
            "Trendlines help identify long-term movement.",
        ],
    },
    "risk-vs-reward": {
        "title": "Risk vs Reward",
        "content": [
            "Higher potential returns usually come with higher risk.",
            "Diversification helps reduce portfolio risk.",
            "Understanding risk tolerance is key for investment strategy.",
        ],
    },
}


# -------------------------------------------------------------------
# OpenAI Mock Client (Pylint-clean)
# -------------------------------------------------------------------

class MockCompletion:
    """Mock of OpenAI completion behavior."""

    @staticmethod
    def create(model, messages):
        """
        Return static mock content.

        Arguments are required for signature correctness,
        even though not used inside the mock.
        """
        _ = model  # avoid pylint unused-variable
        _ = messages
        return {"choices": [{"message": {"content": "Mock AI explanation text."}}]}


class MockChat:
    """Mock chat parent for OpenAI mock client."""
    completions = MockCompletion()


class MockClient:
    """Mock for the AI client."""
    chat = MockChat()


openai_client = MockClient()


# -------------------------------------------------------------------
# Views
# -------------------------------------------------------------------

def learn_topics(request: HttpRequest) -> JsonResponse:
    """Return a list of available learning topic slugs."""
    _ = request  # avoid unused argument warning
    return JsonResponse({"topics": list(LEARN_DATA.keys())})


def learn_topic_detail(request: HttpRequest, slug: str) -> JsonResponse:
    """Return details for a specific learning topic."""
    _ = request
    if slug not in LEARN_DATA:
        return JsonResponse({"error": "Topic not found"}, status=404)
    return JsonResponse(LEARN_DATA[slug])


@csrf_exempt
def learn_ai_explanation(request: HttpRequest) -> JsonResponse:
    """
    Generate an AI explanation for a supplied topic.

    Expected POST body:
        { "topic": "risk-vs-reward" }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # Validate API key
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if isinstance(api_key, str) and api_key.strip() == "":
        return JsonResponse({"error": "Missing OpenAI API key"}, status=500)

    # Parse request body
    try:
        if request.content_type == "application/json":
            body = json.loads(request.body.decode("utf-8"))
            topic = body.get("topic")
        else:
            topic = request.POST.get("topic")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not topic:
        return JsonResponse({"error": "Missing topic"}, status=400)

    # Call AI mock client
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Explain this concept simply: {topic}"}],
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return JsonResponse({"error": str(exc)}, status=500)

    explanation = response["choices"][0]["message"]["content"]
    return JsonResponse({"explanation": explanation})
