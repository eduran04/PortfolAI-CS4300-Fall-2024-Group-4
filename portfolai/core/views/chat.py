"""
Chat Views - PortfolAI Chatbot API
===================================

Chatbot endpoint for AI-powered user interactions.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import logging
from ._clients import openai_client

logger = logging.getLogger(__name__)


@csrf_exempt
def chat_api(request):
    """
    PortfolAI Chatbot API Endpoint
    Responds to user chat messages with AI-powered answers.
    Maintains test expectations (400 on invalid, fallback on API error)
    while keeping PortfolAI's custom system prompt.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
    except Exception:
        user_message = ""

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Check if API key or client unavailable
    if not getattr(settings, "OPENAI_API_KEY", None) or openai_client is None:
        return JsonResponse(
            {"response": f"(Fallback) You said: {user_message}", "fallback": True},
            status=200,
        )

    # Define the chatbot's behavior and tone
    system_prompt = (
        "You are PortfolAI Assistant — a friendly, knowledgeable AI chatbot "
        "that helps users with stock market insights, portfolio strategy, and "
        "investment education. You do NOT have live data, but you can reason "
        "about historical trends, company performance, and general market context. "
        "If users ask for live prices, politely explain that you can't provide them, "
        "but offer useful historical or strategic insights instead. "
        "Keep your tone concise, analytical, and beginner-friendly."
    )

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        reply = completion.choices[0].message.content.strip()
        return JsonResponse({"response": reply}, status=200)

    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return JsonResponse(
            {
                "response": f"(Fallback after error) Could not reach AI: {str(e)}",
                "fallback": True,
            },
            status=200,
        )

