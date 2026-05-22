"""
Chat Views - Demo Help API
===========================

Canned demo responses for navigation and feature help. Session history
is stored in the user's session (no database).
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

DEFAULT_RESPONSE = (
    "I'm the PortfolAI **Demo Help** assistant. I can help you navigate the app:\n\n"
    "1. **Dashboard** — search stocks, view charts, and manage your browser watchlist\n"
    "2. **Markets** — top movers and market news\n"
    "3. **Learn** — investing fundamentals\n\n"
    "Try asking: \"How do I search for a stock?\" or \"What is the watchlist?\"\n\n"
    "*This is a demo — not financial advice.*"
)

DEMO_RESPONSES = [
    (
        ("dashboard", "home", "navigate", "where"),
        (
            "The **Dashboard** (`/dashboard/`) is your main workspace:\n"
            "- Search any ticker in the search bar\n"
            "- View price charts and company details\n"
            "- Add stocks to your watchlist (saved in your browser)\n"
            "- Open **PortfolAI Analysis** for template insights with live data"
        ),
    ),
    (
        ("market", "mover", "news"),
        (
            "The **Markets** page (`/markets/`) shows:\n"
            "- Top gainers and losers\n"
            "- Latest market news\n\n"
            "Live data comes from Finnhub, Alpha Vantage, and NewsAPI."
        ),
    ),
    (
        ("learn", "education", "tutorial", "basics"),
        (
            "The **Learn** page (`/learn/`) covers investing fundamentals:\n"
            "- Stock market basics\n"
            "- Reading charts\n"
            "- Risk vs reward\n\n"
            "Select a topic and request an explanation."
        ),
    ),
    (
        ("watchlist", "watch list", "save stock", "track"),
        (
            "Your **watchlist** is stored in your browser (localStorage):\n"
            "- Click **Add to Watchlist** on the dashboard\n"
            "- Remove items from the watchlist table\n"
            "- Data persists across page refreshes on this device\n\n"
            "It is not saved to a server in demo mode."
        ),
    ),
    (
        ("search", "find stock", "ticker", "symbol", "quote"),
        (
            "To **search for a stock**:\n"
            "1. Go to the Dashboard\n"
            "2. Type a ticker (e.g. `AAPL`) in the search bar\n"
            "3. Press Enter or click Search\n\n"
            "You'll see live quotes, charts, and company overview when API keys are configured."
        ),
    ),
    (
        ("analysis", "portfolai analysis", "insights", "analyze"),
        (
            "**PortfolAI Analysis** provides template insights enriched with live market data:\n"
            "- Click the analysis button on the dashboard after searching a stock\n"
            "- Includes price, news, and company context when APIs are available\n\n"
            "*Demo mode — for educational purposes only, not financial advice.*"
        ),
    ),
    (
        ("login", "log in", "sign in", "account", "password"),
        (
            "Use the shared **demo account** to log in:\n"
            "- Username is shown on the login page\n"
            "- Password is set via the `DEMO_PASSWORD` environment variable\n\n"
            "Registration is disabled in demo mode."
        ),
    ),
    (
        ("api", "data", "live", "real-time", "real time"),
        (
            "Live market data requires these API keys in `.env`:\n"
            "- `FINNHUB_API_KEY` — quotes, search, company profiles\n"
            "- `ALPHA_VANTAGE_API_KEY` — market movers, company overview\n"
            "- `NEWS_API_KEY` — financial news\n\n"
            "Without keys, the app falls back to static demo data."
        ),
    ),
]


def _get_demo_response(user_message):
    """Return a canned response based on keyword matching."""
    lowered = user_message.lower().strip()
    if not lowered:
        return DEFAULT_RESPONSE

    for keywords, response in DEMO_RESPONSES:
        if any(keyword in lowered for keyword in keywords):
            return response

    return DEFAULT_RESPONSE


@csrf_exempt
def chat_api(request):
    """
    Demo help chat endpoint.
    Responds with canned navigation and feature guidance.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        user_message = ""

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
        request.session['chat_history'] = chat_history

    reply = _get_demo_response(user_message)

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": reply})
    request.session['chat_history'] = chat_history
    request.session.modified = True

    return JsonResponse({"response": reply, "demo": True}, status=200)


@csrf_exempt
def clear_chat(request):
    """Clear chat session history."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    if 'chat_history' in request.session:
        del request.session['chat_history']
        request.session.modified = True

    return JsonResponse({"success": True, "message": "Chat history cleared"}, status=200)
