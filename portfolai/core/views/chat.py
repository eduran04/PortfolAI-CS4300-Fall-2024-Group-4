"""
Chat Views - PortfolAI Chatbot API
===================================

Chatbot endpoint for AI-powered user interactions with session-based memory,
user context awareness, and real-time web search capabilities.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, timedelta
import json
import logging
import re
from ._clients import openai_client, newsapi
from ..models import Watchlist

logger = logging.getLogger(__name__)


def _get_user_context(request):
    """Build user context string from watchlist and recent searches."""
    context_parts = []
    
    # Get watchlist if user is authenticated
    if request.user.is_authenticated:
        try:
            # Explicitly filter by authenticated user to prevent cross-user data leakage
            user_id = request.user.id
            watchlist_items = Watchlist.objects.filter(user_id=user_id)
            symbols = [item.symbol for item in watchlist_items]
            
            # Log for debugging
            logger.info(f"Fetching watchlist for user {request.user.username} (ID: {user_id}): {len(symbols)} items")
            
            if symbols:
                context_parts.append(f"User's watchlist: {', '.join(symbols)}")
            else:
                # Explicitly state empty to prevent AI from hallucinating
                context_parts.append("User's watchlist: empty")
        except Exception as e:
            logger.error(f"Error fetching watchlist for user {request.user.username}: {e}")
            context_parts.append("User's watchlist: error fetching data")
    
    # Get recent searches from session
    recent_searches = request.session.get('recent_searches', [])
    if recent_searches:
        context_parts.append(f"Recent searches (most recent first): {', '.join(recent_searches)}")
    else:
        context_parts.append("Recent searches: none")
    
    return ". ".join(context_parts) if context_parts else None


def _needs_web_search(user_message, openai_client):
    """
    Use AI to determine if the query requires real-time web search data.
    Returns True if the query needs current stock market data, news, or real-time information.
    """
    if not openai_client:
        return False
    
    # Quick check for explicit $SYMBOL format - always needs web search
    if re.search(r'\$[A-Z]{1,5}\b', user_message.upper()):
        return True
    
    # Use AI to classify if the query needs real-time data
    try:
        classification_prompt = (
            "You are a classifier for a stock market chatbot. "
            "Determine if the user's query requires real-time stock market data, current news, "
            "or up-to-date information to answer properly.\n\n"
            "Answer with ONLY 'yes' or 'no' - no other text.\n\n"
            f"User query: {user_message}\n\n"
            "Does this query require real-time data? Answer:"
        )
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a classifier. Respond with only 'yes' or 'no'."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=5
        )
        
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith('yes')
        
    except Exception as e:
        logger.warning(f"Error classifying query for web search: {e}")
        # Fallback: return False to avoid unnecessary API calls
        return False


def _get_symbol_for_context(request, user_message):
    """
    Get stock symbol for context - prioritizes recent searches, falls back to explicit $SYMBOL format.
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


def _get_web_search_context(symbols, user_message):
    """
    Get web search context using both OpenAI's web search tool (if available) and NewsAPI.
    Returns combined context from both sources.
    """
    if not symbols:
        return ""
    
    symbol = symbols[0] if symbols else None
    
    if not symbol:
        return ""
    
    # Try OpenAI's web search tool first (if available)
    openai_web_context = ""
    if openai_client:
        try:
            # Check if responses.create() API is available (newer feature)
            if hasattr(openai_client, 'responses'):
                search_query = f"{symbol} stock news today"
                response = openai_client.responses.create(
                    model="gpt-4o",  # Use gpt-4o for web search capability
                    tools=[{"type": "web_search"}],
                    input=search_query,
                )
                if hasattr(response, 'output_text') and response.output_text:
                    openai_web_context = f"\n\n**Web Search Results for {symbol}:**\n{response.output_text}"
        except AttributeError:
            # responses.create() not available in this SDK version
            pass
        except Exception as e:
            logger.warning(f"OpenAI web search failed for {symbol}: {e}")
    
    # Get NewsAPI context (always use as fallback or supplement)
    newsapi_context = ""
    if newsapi:
        try:
            news_articles = newsapi.get_everything(
                q=f"{symbol} stock",
                from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                language='en',
                sort_by='publishedAt',
                page_size=3
            )
            if news_articles and news_articles.get('articles'):
                recent_news = []
                for article in news_articles['articles'][:3]:
                    if article.get('title') and article.get('publishedAt'):
                        recent_news.append(f"- {article['title']} ({article['publishedAt'][:10]})")
                if recent_news:
                    newsapi_context = f"\n\n**Recent News about {symbol}:**\n" + "\n".join(recent_news)
        except Exception as e:
            logger.warning(f"Could not fetch news for {symbol}: {e}")
    
    # Combine both contexts
    combined_context = openai_web_context + newsapi_context
    return combined_context


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

    # Initialize or get conversation history from session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    
    chat_history = request.session['chat_history']
    
    # Limit history to last 20 messages (10 exchanges) to prevent token overflow
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
        request.session['chat_history'] = chat_history

    # Build system prompt with scope restrictions and user context
    system_prompt = (
        "You are PortfolAI Assistant — a friendly, knowledgeable AI chatbot "
        "that helps users with stock market insights, portfolio strategy, and "
        "investment education. "
        "\n\n"
        "IMPORTANT: You MUST only answer questions related to:\n"
        "- Stock market analysis and investment education\n"
        "- Portfolio management and strategy\n"
        "- Questions about stocks, markets, and financial instruments\n"
        "- PortfolAI application features and data\n"
        "\n"
        "If users ask about topics outside this scope (e.g., general knowledge, "
        "other subjects, personal advice unrelated to investing), politely decline "
        "and redirect them to ask about stocks, markets, or portfolio management. "
        "Keep your tone concise, analytical, and beginner-friendly."
    )
    
    # Add user context if available (fetched fresh on each request)
    user_context = _get_user_context(request)
    if user_context:
        system_prompt += (
            f"\n\nCRITICAL USER CONTEXT (use this information, do NOT make assumptions or hallucinate):\n"
            f"{user_context}\n\n"
            "IMPORTANT RULES FOR USING CONTEXT:\n"
            "- When asked about the user's watchlist, ONLY list the symbols shown in 'User's watchlist' above\n"
            "- If 'User's watchlist: empty' is shown, tell the user their watchlist is empty\n"
            "- When asked about search history or 'what did I search', refer to 'Recent searches' from the context above\n"
            "- If recent searches are provided, you DO have access to search history - use it directly\n"
            "- The most recent search is the LAST item in the 'Recent searches' list\n"
            "- NEVER claim you don't have access to search history if 'Recent searches' is provided in the context\n"
            "- NEVER add stocks to the watchlist that aren't explicitly listed in the context\n"
            "- If the context says 'empty' or 'none', that is the accurate answer - do not guess or assume"
        )

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

    except Exception as e:
        logger.error(f"Chatbot error: {e}")
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

