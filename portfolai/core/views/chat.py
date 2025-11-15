"""
Chat Views - PortfolAI Chatbot API
===================================

Chatbot endpoint for AI-powered user interactions with session-based memory,
user context awareness, and real-time web search capabilities.
"""

from datetime import datetime, timedelta
import json
import logging
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from ._clients import openai_client, newsapi
from ..models import Watchlist

logger = logging.getLogger(__name__)


# PROMPT CONSTANTS

CLASSIFICATION_PROMPT = """You are a classifier for a stock market chatbot.
Determine if the user's query requires real-time stock market data, current news,
or up-to-date information to answer properly.

Answer with ONLY 'yes' or 'no' - no other text.

User query: {user_message}

Does this query require real-time data? Answer:"""

CLASSIFICATION_SYSTEM_MESSAGE = "You are a classifier. Respond with only 'yes' or 'no'."

SYSTEM_PROMPT_BASE = """You are PortfolAI Assistant; a friendly, knowledgeable AI chatbot
that helps users with stock market insights, portfolio strategy, and
investment education."""

SCOPE_PROMPT = """
IMPORTANT: You MUST only answer questions related to:
- Stock market analysis and investment education
- Portfolio management and strategy
- Questions about stocks, markets, and financial instruments
- PortfolAI application features and data

If users ask about topics outside this scope (e.g., general knowledge,
other subjects, personal advice unrelated to investing), politely decline
and redirect them to ask about stocks, markets, or portfolio management.
Keep your tone concise, analytical, and beginner-friendly."""

USER_CONTEXT_HEADER = """
CRITICAL USER CONTEXT (use this information, do NOT make assumptions or hallucinate!!!):
{user_context}"""

USER_CONTEXT_RULES = """
IMPORTANT RULES FOR USING CONTEXT:
- When asked about the user's watchlist, ONLY list the symbols shown in
  'User's watchlist' above
- If 'User's watchlist: empty' is shown, tell the user their watchlist is empty
- When asked about search history or 'what did I search', refer to
  'Recent searches' from the context above
- If recent searches are provided, you DO have access to search history -
  use it directly
- The most recent search is the LAST item in the 'Recent searches' list
- NEVER claim you don't have access to search history if 'Recent searches'
  is provided in the context
- NEVER add stocks to the watchlist that aren't explicitly listed in the context
- If the context says 'empty' or 'none', that is the accurate answer -
  do not guess or assume"""


# PROMPT BUILDERS

def _build_classification_prompt(user_message):
    """Build classification prompt with user message."""
    return CLASSIFICATION_PROMPT.format(user_message=user_message)


def _build_system_prompt(user_context=None):
    """Build complete system prompt with optional user context."""
    prompt = SYSTEM_PROMPT_BASE + SCOPE_PROMPT

    if user_context:
        prompt += USER_CONTEXT_HEADER.format(user_context=user_context)
        prompt += USER_CONTEXT_RULES

    return prompt


# HELPER FUNCTIONS TO PREVENT NESTING

def _get_user_context(request):
    """Build user context string from watchlist and recent searches."""
    context_parts = []

    # Get watchlist if user is authenticated
    if request.user.is_authenticated:
        try:
            # Explicitly filter by authenticated user to prevent cross-user data leakage
            user_id = request.user.id
            watchlist_items = Watchlist.objects.filter(user_id=user_id)  # pylint: disable=no-member
            symbols = [item.symbol for item in watchlist_items]

            # Log for debugging
            logger.info(
                "Fetching watchlist for user %s (ID: %s): %s items",
                request.user.username, user_id, len(symbols)
            )

            if symbols:
                context_parts.append(f"User's watchlist: {', '.join(symbols)}")
            else:
                # Explicitly state empty to prevent AI from hallucinating
                context_parts.append("User's watchlist: empty")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error fetching watchlist for user %s: %s", request.user.username, e)
            context_parts.append("User's watchlist: error fetching data")

    # Get recent searches from session
    recent_searches = request.session.get('recent_searches', [])
    if recent_searches:
        context_parts.append(f"Recent searches (most recent first): {', '.join(recent_searches)}")
    else:
        context_parts.append("Recent searches: none")

    return ". ".join(context_parts) if context_parts else None


def _needs_web_search(user_message, client):
    """
    Use AI to determine if the query requires real-time web search data.
    Returns True if the query needs current stock market data, news, or real-time information.
    """
    if not client:
        return False

    # Quick check for explicit $SYMBOL format - always needs web search
    if re.search(r'\$[A-Z]{1,5}\b', user_message.upper()):
        return True

    # Use AI to classify if the query needs real-time data
    try:
        classification_prompt = _build_classification_prompt(user_message)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CLASSIFICATION_SYSTEM_MESSAGE},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=5
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith('yes')

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Error classifying query for web search: %s", e)
        # Fallback: return False to avoid unnecessary API calls
        return False


def _get_symbol_for_context(request, user_message):
    """
    Get stock symbol for context - prioritizes recent searches,
    falls back to explicit $SYMBOL format.
    Returns list of symbols (usually just one, the most recent search).
    """
    symbols = []

    # Primary approach: Use most recently searched symbol from session
    recent_searches = request.session.get('recent_searches', [])
    if recent_searches:
        # Get the last (most recent) search
        most_recent = recent_searches[-1]
        symbols.append(most_recent)

    # Fallback: Only extract explicit $SYMBOL format from message
    # Avoid extracting from natural language to prevent false positives
    dollar_symbols = re.findall(r'\$([A-Z]{1,5})\b', user_message.upper())
    for symbol in dollar_symbols:
        if symbol not in symbols:
            symbols.append(symbol)

    return symbols[:2]  # Limit to 2 symbols


def _get_openai_web_context(symbol):
    """Get OpenAI web search context for a symbol."""
    if not openai_client:
        return ""

    if not hasattr(openai_client, 'responses'):
        return ""

    try:
        search_query = f"{symbol} stock news today"
        response = openai_client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search"}],
            input=search_query,
        )

        if not hasattr(response, 'output_text') or not response.output_text:
            return ""

        return f"\n\n**Web Search Results for {symbol}:**\n{response.output_text}"

    except AttributeError:
        # responses.create() not available in this SDK version
        return ""
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("OpenAI web search failed for %s: %s", symbol, e)
        return ""


def _format_news_articles(articles, symbol):
    """Format news articles into a readable context string."""
    if not articles:
        return ""

    recent_news = []
    for article in articles[:3]:
        title = article.get('title')
        published_at = article.get('publishedAt')
        if title and published_at:
            recent_news.append(f"- {title} ({published_at[:10]})")

    if not recent_news:
        return ""

    return f"\n\n**Recent News about {symbol}:**\n" + "\n".join(recent_news)


def _get_newsapi_context(symbol):
    """Get NewsAPI context for a symbol."""
    if not newsapi:
        return ""

    try:
        news_articles = newsapi.get_everything(
            q=f"{symbol} stock",
            from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=3
        )

        articles = news_articles.get('articles') if news_articles else None
        return _format_news_articles(articles, symbol)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not fetch news for %s: %s", symbol, e)
        return ""


def _get_web_search_context(symbols, _user_message):
    """
    Get web search context using both OpenAI's web search tool (if available) and NewsAPI.
    Returns combined context from both sources.
    """
    if not symbols:
        return ""

    symbol = symbols[0] if symbols else None
    if not symbol:
        return ""

    openai_web_context = _get_openai_web_context(symbol)
    newsapi_context = _get_newsapi_context(symbol)

    return openai_web_context + newsapi_context


@csrf_exempt
def chat_api(request):
    """
    PortfolAI Chatbot API Endpoint
    Responds to user chat messages with AI-powered answers.
    Maintains session-based conversation memory and user context awareness.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
    except Exception:  # pylint: disable=broad-exception-caught
        user_message = ""

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Check if API key or client unavailable
    if not getattr(settings, "OPENAI_API_KEY", None) or openai_client is None:
        return JsonResponse(
            {"response": f"(Fallback) You said: {user_message}", "fallback": True},
            status=200,
        )

    # Initialize or get conversation history from session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']

    # Limit history to last 20 messages (10 exchanges) to prevent token overflow
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
        request.session['chat_history'] = chat_history

    # Build system prompt with scope restrictions and user context
    user_context = _get_user_context(request)
    system_prompt = _build_system_prompt(user_context)

    # Only fetch web search context if AI determines the query needs real-time data
    web_search_context = ""
    if _needs_web_search(user_message, openai_client):
        # Get stock symbol for context (prioritizes recent searches)
        symbols = _get_symbol_for_context(request, user_message)
        if symbols:
            web_search_context = _get_web_search_context(symbols, user_message)

    # Build enhanced user message with web search context if available
    enhanced_message = user_message
    if web_search_context:
        enhanced_message += "\n\n" + web_search_context

    # Build messages list: system prompt + conversation history + current message
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for msg in chat_history:
        messages.append(msg)

    # Add current user message
    messages.append({"role": "user", "content": enhanced_message})

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=messages,
        )

        reply = completion.choices[0].message.content.strip()

        # Update session history with user message and bot response
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": reply})
        request.session['chat_history'] = chat_history
        request.session.modified = True

        return JsonResponse({"response": reply}, status=200)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Chatbot error: %s", e)
        return JsonResponse(
            {
                "response": f"(Fallback after error) Could not reach AI: {str(e)}",
                "fallback": True,
            },
            status=200,
        )


@csrf_exempt
def clear_chat(request):
    """
    Clear chat session history.
    Endpoint: /api/chat/clear/
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    if 'chat_history' in request.session:
        del request.session['chat_history']
        request.session.modified = True

    return JsonResponse({"success": True, "message": "Chat history cleared"}, status=200)