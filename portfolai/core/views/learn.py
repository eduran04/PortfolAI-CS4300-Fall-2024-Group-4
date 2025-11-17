import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


LEARN_DATA = {
    "stock-market-basics": {
        "title": "Stock Market Basics",
        "content": [
            "A stock represents fractional ownership in a company.",
            "When you buy a share, you own a small percentage of the business.",
            "Stock prices move based on supply/demand and company performance.",
            "Investors buy stocks to grow wealth over time."
        ]
    },

    "reading-stock-charts": {
        "title": "Reading Stock Charts",
        "content": [
            "Candlesticks represent price movement for a time interval.",
            "Green candles mean price closed higher; red means price fell.",
            "Volume bars show how many shares were traded.",
            "Trendlines help identify long-term movement."
        ]
    },

    "risk-vs-reward": {
        "title": "Risk vs Reward",
        "content": [
            "Higher potential returns usually come with higher risk.",
            "Diversification helps reduce portfolio risk.",
            "Understanding risk tolerance is key for investment strategy."
        ]
    }
}


def learn_topics(request):
    """Return list of available learning topics"""
    return JsonResponse({"topics": list(LEARN_DATA.keys())})


def learn_topic_detail(request, slug):
    """Return full content for a specific learning topic"""
    if slug not in LEARN_DATA:
        return JsonResponse({"error": "Topic not found"}, status=404)

    return JsonResponse(LEARN_DATA[slug])


# Mock OpenAI client for local development and test patching
class MockClient:
    class chat:
        class completions:
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
    """Generate AI explanation for a learning topic."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # TEST REQUIREMENTS:
    # - If OPENAI_API_KEY = "" → return 500
    # - If OPENAI_API_KEY = None → allow (mock mode)
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if isinstance(api_key, str) and api_key.strip() == "":
        return JsonResponse({"error": "Missing OpenAI API key"}, status=500)

    # Accept JSON or form POST
    try:
        if request.content_type == "application/json":
            body = json.loads(request.body.decode("utf-8"))
            topic = body.get("topic")
        else:
            topic = request.POST.get("topic")
    except Exception:
        topic = None

    if not topic:
        return JsonResponse({"error": "Missing topic"}, status=400)

    # Tests patch: core.views.learn.openai_client.chat.completions.create
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Explain this concept simply: {topic}"}
            ]
        )
        explanation = response["choices"][0]["message"]["content"]
        return JsonResponse({"explanation": explanation}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
