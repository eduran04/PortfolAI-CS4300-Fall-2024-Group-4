"""
PortfolAI Service Layer - Business Logic Abstraction
===================================================

This module contains service classes that handle business logic for the PortfolAI application.
Services abstract complex operations and API interactions, making views cleaner and more testable.

Services:
- MarketDataService: Handles market movers data retrieval
- NewsService: Handles financial news data retrieval

All services include comprehensive error handling and fallback data for when external APIs are unavailable.
"""

import openai
import finnhub
from newsapi import NewsApiClient
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# FALLBACK DATA FOR API UNAVAILABILITY
# ============================================================================
# Ensures application remains functional even without external API access

FALLBACK_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'price': 150.25, 'change': 2.15, 'changePercent': 1.45},
    'MSFT': {'name': 'Microsoft Corp.', 'price': 420.72, 'change': -0.50, 'changePercent': -0.12},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 175.60, 'change': 2.10, 'changePercent': 1.21},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 180.97, 'change': -1.80, 'changePercent': -0.98},
    'TSLA': {'name': 'Tesla Inc.', 'price': 177.46, 'change': 3.50, 'changePercent': 2.01},
    'NVDA': {'name': 'NVIDIA Corporation', 'price': 900.55, 'change': 15.20, 'changePercent': 1.72},
    'META': {'name': 'Meta Platforms Inc.', 'price': 480.10, 'change': -2.30, 'changePercent': -0.48},
    'OKLO': {'name': 'Oklo Inc.', 'price': 12.45, 'change': 0.85, 'changePercent': 7.33},
}

FALLBACK_NEWS = [
    {
        'title': 'Tech Stocks Rally on Positive Economic Outlook',
        'source': 'Market News Today',
        'time': '2h ago',
        'url': '#',
        'description': 'Technology stocks show strong performance amid positive economic indicators.'
    },
    {
        'title': 'Federal Reserve Hints at Interest Rate Stability',
        'source': 'Global Finance Times',
        'time': '3h ago',
        'url': '#',
        'description': 'Central bank signals potential stability in interest rate policy.'
    },
    {
        'title': 'AI Stocks Continue to Lead Market Gains',
        'source': 'TechCrunch',
        'time': '1h ago',
        'url': '#',
        'description': 'Artificial intelligence companies show continued strong performance.'
    }
]


class MarketDataService:
    """
    Service class for handling market data operations.
    
    Provides methods for retrieving market movers data with comprehensive
    error handling and fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize the service with API clients if keys are available."""
        self.finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else None
    
    def get_market_movers(self):
        """
        Retrieve market movers data (top gainers and losers).
        
        Returns:
            dict: Market movers data with gainers and losers lists
        """
        # Check if API key is available, if not use fallback data
        if not settings.FINNHUB_API_KEY or not self.finnhub_client:
            return self._get_fallback_market_movers()
        
        try:
            # Get stock symbols for major companies
            major_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
            
            market_data = []
            
            for symbol in major_symbols:
                try:
                    try:
                        quote = self.finnhub_client.quote(symbol)
                    except Exception as api_error:
                        error_str = str(api_error).lower()
                        # Check for rate limit errors - stop fetching if rate limited
                        if 'rate limit' in error_str or '429' in error_str or 'too many requests' in error_str:
                            logger.warning(f'Rate limit hit while fetching market movers, using partial data')
                            # Break out of loop if rate limited
                            break
                        raise api_error
                    
                    # Check if quote data is valid
                    if not quote or quote.get('c') is None:
                        continue
                    
                    # Skip company profile to reduce API calls - use symbol as name
                    # This reduces API calls by 50% for market movers
                    current_price = quote.get('c', 0)
                    previous_close = quote.get('pc', 0)
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                    
                    market_data.append({
                        "symbol": symbol,
                        "name": symbol,  # Use symbol as name to avoid extra API call
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_percent, 2)
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch data for {symbol}: {e}")
                    continue  # Skip symbols that fail
            
            # If no data was collected, use fallback
            if not market_data:
                return self._get_fallback_market_movers()
            
            # Sort by change percentage
            market_data.sort(key=lambda x: x['changePercent'], reverse=True)
            
            # Get top 5 gainers and losers
            gainers = market_data[:5]
            losers = market_data[-5:][::-1]  # Reverse to get worst performers first
            
            return {
                "gainers": gainers,
                "losers": losers
            }
            
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            # Return fallback data on error
            return self._get_fallback_market_movers()
    
    def _get_fallback_market_movers(self):
        """Get fallback market movers data when API is unavailable."""
        fallback_stocks = list(FALLBACK_STOCKS.values())
        fallback_stocks.sort(key=lambda x: x['changePercent'], reverse=True)
        
        gainers = fallback_stocks[:5]
        losers = fallback_stocks[-5:][::-1]
        
        return {
            "gainers": gainers,
            "losers": losers,
            "fallback": True
        }


class NewsService:
    """
    Service class for handling financial news operations.
    
    Provides methods for retrieving financial news with symbol filtering
    and comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize the service with API clients if keys are available."""
        self.newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY) if settings.NEWS_API_KEY else None
    
    def get_financial_news(self, symbol=None):
        """
        Retrieve financial news data with optional symbol filtering.
        
        Args:
            symbol (str, optional): Stock symbol to filter news by
            
        Returns:
            dict: News data with articles list and metadata
        """
        # Check if API key is available, if not use fallback data
        if not settings.NEWS_API_KEY or not self.newsapi:
            return {
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            }
        
        try:
            if symbol:
                # Get company-specific news using everything endpoint
                try:
                    # Use today's date for better results
                    from_date = datetime.now().strftime('%Y-%m-%d')
                    articles = self.newsapi.get_everything(
                        q=f"{symbol} stock",
                        from_param=from_date,
                        language='en',
                        sort_by='popularity',  # Use popularity as recommended in docs
                        page_size=10
                    )
                except Exception as e:
                    logger.warning(f"News API failed for {symbol}: {e}")
                    # Fallback to top headlines for business category
                    articles = self.newsapi.get_top_headlines(
                        category='business',
                        language='en',
                        page_size=10
                    )
            else:
                # Get general financial market news using top headlines
                try:
                    articles = self.newsapi.get_top_headlines(
                        category='business',
                        language='en',
                        page_size=10
                    )
                except Exception as e:
                    logger.warning(f"News API top headlines failed: {e}")
                    # Fallback to everything endpoint
                    articles = self.newsapi.get_everything(
                        q='stock market OR finance OR economy',
                        language='en',
                        sort_by='popularity',
                        page_size=10
                    )
            
            # Check if we got valid articles
            if not articles or 'articles' not in articles:
                logger.warning("No articles found in NewsAPI response")
                return {
                    "articles": FALLBACK_NEWS,
                    "totalResults": len(FALLBACK_NEWS),
                    "fallback": True
                }
            
            news_items = []
            for article in articles.get('articles', []):
                # Skip articles without required fields
                if not article.get('title') or not article.get('url'):
                    continue
                    
                # Format time
                published_time = article.get('publishedAt', '')
                if published_time:
                    try:
                        dt = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
                        time_ago = datetime.now(dt.tzinfo) - dt
                        if time_ago.days > 0:
                            time_str = f"{time_ago.days}d ago"
                        elif time_ago.seconds > 3600:
                            time_str = f"{time_ago.seconds // 3600}h ago"
                        else:
                            time_str = f"{time_ago.seconds // 60}m ago"
                    except:
                        time_str = "Recently"
                else:
                    time_str = "Recently"
                
                news_items.append({
                    "title": article.get('title', ''),
                    "source": article.get('source', {}).get('name', 'Unknown Source'),
                    "time": time_str,
                    "url": article.get('url', '#'),
                    "description": article.get('description', ''),
                    "publishedAt": published_time
                })
            
            # If no valid articles found, use fallback
            if not news_items:
                return {
                    "articles": FALLBACK_NEWS,
                    "totalResults": len(FALLBACK_NEWS),
                    "fallback": True
                }
            
            return {
                "articles": news_items,
                "totalResults": articles.get('totalResults', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            # Return fallback news on error
            return {
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            }


# ============================================================================
# CHAT SERVICE
# ============================================================================

from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from .models import AIChatSession, AIRequest, Watchlist


class ChatService:
    """
    Service class for handling AI chat operations.
    
    Provides methods for conversation management, message handling,
    context management, and rate limiting. Supports both synchronous
    and asynchronous (Celery) processing.
    """
    
    def __init__(self):
        """Initialize the chat service with configuration."""
        self.config = getattr(settings, 'CHAT_CONFIG', {})
        self.context_window = self.config.get('CONTEXT_WINDOW_TOKENS', 8000)
        self.rate_limit_requests = self.config.get('RATE_LIMIT_REQUESTS', 30)
        self.rate_limit_window = self.config.get('RATE_LIMIT_WINDOW', 60)
        self.max_message_length = self.config.get('MAX_MESSAGE_LENGTH', 5000)
        self.default_model = self.config.get('DEFAULT_MODEL', 'gpt-4o-mini')
        self.temperature = self.config.get('TEMPERATURE', 0.7)
        self.enable_celery = self.config.get('ENABLE_CELERY', False)
    
    def _is_financial_question(self, content):
        """
        Check if the question is related to finance/investments.
        
        Allows greetings and general questions, but blocks clearly non-financial topics
        like programming, coding, etc.
        
        Args:
            content (str): User message content
            
        Returns:
            bool: True if question should be allowed, False if it's clearly non-financial
        """
        content_lower = content.lower().strip()
        
        # Allow greetings and general questions (let AI handle context)
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(content_lower.startswith(greeting) for greeting in greetings):
            return True
        
        # Non-financial keywords that should be rejected (strong signal)
        non_financial_keywords = [
            'python', 'program', 'code', 'coding', 'programming', 'script', 'function',
            'hello world', 'javascript', 'java', 'c++', 'html', 'css', 'sql', 'database',
            'algorithm', 'data structure', 'api', 'web development', 'software',
            'app development', 'mobile app', 'game', 'website', 'build a', 'create a',
            'write a program', 'make a program', 'how to code', 'tutorial', 'compile',
            'debug', 'variable', 'class', 'object', 'method', 'library', 'framework'
        ]
        
        # Check for non-financial keywords (strong rejection signal)
        for keyword in non_financial_keywords:
            if keyword in content_lower:
                return False
        
        # Check for patterns that indicate programming requests
        programming_patterns = [
            r'build.*python',
            r'create.*python',
            r'write.*python',
            r'make.*python',
            r'python.*program',
            r'python.*code',
            r'hello.*world',
            r'print.*hello'
        ]
        
        for pattern in programming_patterns:
            if re.search(pattern, content_lower):
                return False
        
        # Default to allowing (let AI decide based on context and system prompt)
        # The system prompt will enforce financial-only responses
        return True
    
    def _sanitize_input(self, content):
        """
        Sanitize user input to prevent injection attacks while preserving content.
        
        Note: HTML escaping is handled at the frontend for display.
        This function focuses on removing dangerous characters and validating input.
        
        Args:
            content (str): Raw user input
            
        Returns:
            str: Sanitized content
        """
        if not isinstance(content, str):
            raise ValidationError("Content must be a string")
        
        # Remove null bytes and other control characters (except newlines and tabs)
        content = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', content)
        
        # Remove excessive whitespace (but preserve intentional line breaks)
        content = re.sub(r'[ \t]+', ' ', content)  # Collapse spaces and tabs
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
        content = content.strip()
        
        # Check length
        if len(content) > self.max_message_length:
            raise ValidationError(
                f"Message exceeds maximum length of {self.max_message_length} characters"
            )
        
        # Check for empty content after sanitization
        if not content:
            raise ValidationError("Message cannot be empty after sanitization")
        
        return content
    
    def _check_rate_limit(self, user):
        """
        Check if user has exceeded rate limit.
        
        Args:
            user: Django User instance
            
        Returns:
            bool: True if within rate limit, False otherwise
            
        Raises:
            ValidationError: If rate limit exceeded
        """
        cache_key = f'chat_rate_limit_{user.id}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.rate_limit_requests:
            logger.warning(f"Rate limit exceeded for user {user.username}")
            raise ValidationError(
                f"Rate limit exceeded. Maximum {self.rate_limit_requests} "
                f"requests per {self.rate_limit_window} seconds."
            )
        
        # Increment counter
        cache.set(cache_key, current_count + 1, self.rate_limit_window)
        return True
    
    def _estimate_tokens(self, text):
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text (str): Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def create_conversation(self, user, title=None, current_stock=None):
        """
        Create a new conversation session for a user.
        
        Args:
            user: Django User instance
            title (str, optional): Optional title for the conversation
            current_stock (str, optional): Currently viewed stock symbol
            
        Returns:
            AIChatSession: Created session instance
        """
        if not user or not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        session = AIChatSession.objects.create(
            user=user,
            title=title or f"Conversation {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Create welcome message with current stock context
        self.create_first_message(session, current_stock=current_stock)
        
        logger.info(f"Created new conversation {session.id} for user {user.username}")
        return session
    
    def get_or_create_conversation(self, user, conversation_id=None, current_stock=None):
        """
        Get existing conversation or create a new one.
        
        If conversation_id is provided, retrieve that conversation.
        Otherwise, get the most recent active conversation or create a new one.
        
        Args:
            user: Django User instance
            conversation_id (int, optional): ID of conversation to retrieve
            current_stock (str, optional): Currently viewed stock symbol
            
        Returns:
            tuple: (AIChatSession, bool) - session and whether it was created
        """
        if not user or not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        if conversation_id:
            try:
                session = AIChatSession.objects.get(
                    id=conversation_id,
                    user=user,
                    is_active=True
                )
                return session, False
            except AIChatSession.DoesNotExist:
                logger.warning(
                    f"Conversation {conversation_id} not found for user {user.username}"
                )
                # Fall through to create new conversation
        
        # Get most recent active conversation
        session = AIChatSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-updated_at').first()
        
        if session:
            return session, False
        
        # Create new conversation with current stock context
        session = self.create_conversation(user, current_stock=current_stock)
        return session, True
    
    def create_first_message(self, session, current_stock=None):
        """
        Create the initial system/welcome message for a conversation.
        
        Args:
            session: AIChatSession instance
            current_stock (str, optional): Currently viewed stock symbol
            
        Returns:
            AIRequest: Created system message
        """
        # Get user's watchlist for context
        watchlist_items = Watchlist.objects.filter(user=session.user)
        watchlist_symbols = [item.symbol for item in watchlist_items]
        
        # Build context information
        context_info = ""
        if watchlist_symbols:
            context_info += f"\n\nUSER'S WATCHLIST: {', '.join(watchlist_symbols)}\n"
            context_info += "You have access to the user's watchlist. When they ask about their watchlist, "
            context_info += "you can reference these stocks. You can list them, analyze them, or provide "
            context_info += "insights about any of these stocks.\n"
        
        if current_stock:
            context_info += f"\n\nCURRENT STOCK BEING VIEWED: {current_stock}\n"
            context_info += "The user is currently viewing/searching for this stock on their dashboard. "
            context_info += "When they ask about 'this stock', 'the current stock', 'the stock I searched', "
            context_info += "or similar references, they are referring to " + current_stock + ". "
            context_info += "You can provide insights, analysis, and context about this specific stock. "
            context_info += "You ARE aware of what stock they searched for - it is " + current_stock + ".\n"
        
        system_prompt = (
            "You are PortfolAI Assistant — a specialized financial AI chatbot. "
            "You ONLY answer questions about finance, stocks, investments, portfolios, and financial markets.\n\n"
            
            "CRITICAL RULES - YOU MUST FOLLOW THESE:\n"
            "1. You MUST REFUSE to answer any questions about programming, coding, software development, "
            "or any non-financial topics. If asked about these, say: 'I'm specialized in financial and "
            "investment topics only. I can help you with stock analysis, portfolio strategy, or investment "
            "questions instead. What would you like to know about?'\n"
            "2. You MUST NOT write code, create programs, or provide programming tutorials.\n"
            "3. You MUST ONLY discuss: stocks, investments, portfolios, market analysis, financial concepts, "
            "company analysis, trading strategies, and related financial topics.\n\n"
            
            "WHAT YOU CAN HELP WITH:\n"
            "- Stock market insights and analysis\n"
            "- Portfolio strategy and management\n"
            "- Investment education and financial concepts\n"
            "- Company analysis and market trends\n"
            "- Risk assessment and investment advice (educational only)\n"
            "- Watchlist management and analysis\n"
            "- Current stock information and insights\n\n"
            
            f"{context_info}\n"
            
            "RESPONSE FORMATTING:\n"
            "- Use plain text only - NO markdown (no **bold**, *italic*, # headers, code blocks)\n"
            "- Use proper paragraph breaks for readability\n"
            "- Keep formatting clean and simple\n"
            "- Write conversationally without formatting artifacts\n\n"
            
            "DATA LIMITATIONS:\n"
            "You do NOT have live/real-time data, but you can reason about historical trends, "
            "company performance, and general market context. If users ask for live prices, "
            "politely explain you can't provide them, but offer useful historical or strategic insights instead.\n\n"
            
            "TONE: Keep responses concise, analytical, and beginner-friendly. Always remind users "
            "that investment advice is for educational purposes only and not financial advice."
        )
        
        return AIRequest.objects.create(
            user=session.user,
            session=session,
            role=AIRequest.ROLE_SYSTEM,
            content=system_prompt,
            status=AIRequest.COMPLETED
        )
    
    def create_message(self, session, role, content, status=AIRequest.PENDING):
        """
        Create and save a message in a conversation.
        
        Args:
            session: AIChatSession instance
            role (str): Message role (user, assistant, or system)
            content (str): Message content
            status (str): Request status (default: PENDING)
            
        Returns:
            AIRequest: Created message instance
        """
        if role == AIRequest.ROLE_USER:
            content = self._sanitize_input(content)
        
        message = AIRequest.objects.create(
            user=session.user,
            session=session,
            role=role,
            content=content,
            status=status
        )
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])
        
        return message
    
    def get_conversation_history(self, session, limit=None):
        """
        Fetch complete message history for a conversation.
        
        Args:
            session: AIChatSession instance
            limit (int, optional): Maximum number of messages to retrieve
            
        Returns:
            QuerySet: AIRequest queryset ordered by creation time
        """
        queryset = AIRequest.objects.filter(session=session).order_by('created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_last_request(self, session):
        """
        Retrieve the most recent user message in a conversation.
        
        Args:
            session: AIChatSession instance
            
        Returns:
            AIRequest or None: Most recent user message, or None if not found
        """
        return AIRequest.objects.filter(
            session=session,
            role=AIRequest.ROLE_USER
        ).order_by('-created_at').first()
    
    def format_messages_for_ai(self, session, include_system=True):
        """
        Format messages in the correct structure for AI API calls.
        
        Implements context window management by keeping only recent messages
        that fit within the token limit.
        
        Args:
            session: AIChatSession instance
            include_system (bool): Whether to include system messages
            
        Returns:
            list: List of message dicts formatted for OpenAI API
        """
        messages = []
        total_tokens = 0
        
        # Get all messages
        all_messages = self.get_conversation_history(session)
        
        # Process messages in reverse to keep most recent ones
        message_list = list(all_messages)
        message_list.reverse()
        
        for msg in message_list:
            # Skip system messages if not including them (except first one)
            if not include_system and msg.role == AIRequest.ROLE_SYSTEM:
                if not messages:  # Always include first system message
                    messages.insert(0, {
                        'role': msg.role,
                        'content': msg.content
                    })
                    total_tokens += self._estimate_tokens(msg.content)
                continue
            
            # Estimate tokens for this message
            msg_tokens = self._estimate_tokens(msg.content)
            
            # Check if adding this message would exceed context window
            if total_tokens + msg_tokens > self.context_window:
                logger.warning(
                    f"Context window limit reached for session {session.id}. "
                    f"Truncating older messages."
                )
                break
            
            # Add message to list (insert at beginning to maintain order)
            messages.insert(0, {
                'role': msg.role,
                'content': msg.content
            })
            total_tokens += msg_tokens
        
        # Ensure we have at least the system message and it's always the most recent one
        # Get the most recent system message (should be the updated one with current stock)
        system_msg = AIRequest.objects.filter(
            session=session,
            role=AIRequest.ROLE_SYSTEM
        ).order_by('-updated_at', '-created_at').first()
        
        if system_msg:
            # Remove any existing system messages from the list
            messages = [msg for msg in messages if msg['role'] != AIRequest.ROLE_SYSTEM]
            # Insert the most recent system message at the beginning
            messages.insert(0, {
                'role': system_msg.role,
                'content': system_msg.content
            })
        elif not messages:
            # If no messages at all, create a default system message
            logger.warning(f"No system message found for session {session.id}")
            messages.insert(0, {
                'role': AIRequest.ROLE_SYSTEM,
                'content': "You are PortfolAI Assistant — a friendly, knowledgeable AI chatbot that helps users with stock market insights."
            })
        
        return messages
    
    def _clean_response_formatting(self, response):
        """
        Clean and format AI response to remove markdown and ensure plain text.
        
        Args:
            response (str): Raw AI response
            
        Returns:
            str: Cleaned response with plain text formatting
        """
        import re
        
        # Remove markdown bold (**text** or __text__)
        response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        response = re.sub(r'__(.*?)__', r'\1', response)
        
        # Remove markdown italic (*text* or _text_)
        response = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'\1', response)
        response = re.sub(r'(?<!_)_(?!_)(.*?)(?<!_)_(?!_)', r'\1', response)
        
        # Remove markdown headers (# Header)
        response = re.sub(r'^#{1,6}\s+(.*)$', r'\1', response, flags=re.MULTILINE)
        
        # Remove markdown code blocks (```code```)
        response = re.sub(r'```[\s\S]*?```', '', response)
        
        # Remove inline code (`code`)
        response = re.sub(r'`([^`]+)`', r'\1', response)
        
        # Remove markdown links [text](url) -> text
        response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', response)
        
        # Normalize whitespace - replace multiple spaces with single space
        response = re.sub(r' +', ' ', response)
        
        # Normalize line breaks - ensure consistent paragraph breaks
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in response.split('\n')]
        response = '\n'.join(lines)
        
        # Final cleanup - remove excessive blank lines
        response = re.sub(r'\n\n\n+', '\n\n', response)
        
        return response.strip()
    
    def _call_openai_api(self, messages, model=None):
        """
        Call OpenAI API to get AI response.
        
        Args:
            messages (list): Formatted messages for OpenAI API
            model (str, optional): Model to use (defaults to configured model)
            
        Returns:
            str: AI response content (cleaned and formatted)
        """
        from .views._clients import openai_client
        
        if not openai_client:
            raise Exception("OpenAI client not available")
        
        model = model or self.default_model
        
        try:
            completion = openai_client.chat.completions.create(
                model=model,
                temperature=self.temperature,
                messages=messages,
            )
            
            raw_response = completion.choices[0].message.content.strip()
            
            # Clean response to remove markdown and ensure plain text formatting
            cleaned_response = self._clean_response_formatting(raw_response)
            
            return cleaned_response
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _update_system_message_with_current_stock(self, session, current_stock):
        """
        Update or create a system message with current stock context.
        
        If a system message exists, update it. Otherwise, create a new one.
        This ensures the AI is always aware of the current stock being viewed.
        
        Args:
            session: AIChatSession instance
            current_stock (str): Currently viewed stock symbol
        """
        # Get existing system message
        system_message = AIRequest.objects.filter(
            session=session,
            role=AIRequest.ROLE_SYSTEM
        ).order_by('created_at').first()
        
        # Get user's watchlist for context
        watchlist_items = Watchlist.objects.filter(user=session.user)
        watchlist_symbols = [item.symbol for item in watchlist_items]
        
        watchlist_context = ""
        if watchlist_symbols:
            watchlist_context = (
                f"\n\nUser's Watchlist: {', '.join(watchlist_symbols)}. "
                "You can reference these stocks when providing insights."
            )
        
        # Build context information
        context_info = ""
        if watchlist_symbols:
            context_info += f"\n\nUSER'S WATCHLIST: {', '.join(watchlist_symbols)}\n"
            context_info += "You have access to the user's watchlist. When they ask about their watchlist, "
            context_info += "you can reference these stocks. You can list them, analyze them, or provide "
            context_info += "insights about any of these stocks.\n"
        
        if current_stock:
            context_info += f"\n\nCURRENT STOCK BEING VIEWED: {current_stock}\n"
            context_info += "The user is currently viewing/searching for this stock on their dashboard. "
            context_info += "When they ask about 'this stock', 'the current stock', 'the stock I searched', "
            context_info += "or similar references, they are referring to " + current_stock + ". "
            context_info += "You can provide insights, analysis, and context about this specific stock. "
            context_info += "You ARE aware of what stock they searched for - it is " + current_stock + ".\n"
        
        system_prompt = (
            "You are PortfolAI Assistant — a specialized financial AI chatbot. "
            "You ONLY answer questions about finance, stocks, investments, portfolios, and financial markets.\n\n"
            
            "CRITICAL RULES - YOU MUST FOLLOW THESE:\n"
            "1. You MUST REFUSE to answer any questions about programming, coding, software development, "
            "or any non-financial topics. If asked about these, say: 'I'm specialized in financial and "
            "investment topics only. I can help you with stock analysis, portfolio strategy, or investment "
            "questions instead. What would you like to know about?'\n"
            "2. You MUST NOT write code, create programs, or provide programming tutorials.\n"
            "3. You MUST ONLY discuss: stocks, investments, portfolios, market analysis, financial concepts, "
            "company analysis, trading strategies, and related financial topics.\n\n"
            
            "WHAT YOU CAN HELP WITH:\n"
            "- Stock market insights and analysis\n"
            "- Portfolio strategy and management\n"
            "- Investment education and financial concepts\n"
            "- Company analysis and market trends\n"
            "- Risk assessment and investment advice (educational only)\n"
            "- Watchlist management and analysis\n"
            "- Current stock information and insights\n\n"
            
            f"{context_info}\n"
            
            "RESPONSE FORMATTING:\n"
            "- Use plain text only - NO markdown (no **bold**, *italic*, # headers, code blocks)\n"
            "- Use proper paragraph breaks for readability\n"
            "- Keep formatting clean and simple\n"
            "- Write conversationally without formatting artifacts\n\n"
            
            "DATA LIMITATIONS:\n"
            "You do NOT have live/real-time data, but you can reason about historical trends, "
            "company performance, and general market context. If users ask for live prices, "
            "politely explain you can't provide them, but offer useful historical or strategic insights instead.\n\n"
            
            "TONE: Keep responses concise, analytical, and beginner-friendly. Always remind users "
            "that investment advice is for educational purposes only and not financial advice."
        )
        
        if system_message:
            # Update existing system message
            system_message.content = system_prompt
            system_message.save()
        else:
            # Create new system message
            AIRequest.objects.create(
                user=session.user,
                session=session,
                role=AIRequest.ROLE_SYSTEM,
                content=system_prompt,
                status=AIRequest.COMPLETED
            )
    
    @transaction.atomic
    def send_message(self, user, content, conversation_id=None, current_stock=None, async_processing=False):
        """
        Handle the full message flow: validation → AI processing → response → storage.
        
        Supports both synchronous and asynchronous (Celery) processing.
        
        Args:
            user: Django User instance
            content (str): User message content
            conversation_id (int, optional): ID of conversation to use
            current_stock (str, optional): Currently viewed stock symbol
            async_processing (bool): Whether to process asynchronously via Celery
            
        Returns:
            dict: Response containing conversation_id, response, and status
        """
        # Validate user
        if not user or not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        # Check if question is financial-related (pre-filter non-financial questions)
        if not self._is_financial_question(content):
            raise ValidationError(
                "I'm specialized in financial and investment topics only. "
                "I can help you with stock analysis, portfolio strategy, or investment questions instead. "
                "What would you like to know about?"
            )
        
        # Check rate limit
        self._check_rate_limit(user)
        
        # Get or create conversation
        session, created = self.get_or_create_conversation(user, conversation_id, current_stock=current_stock)
        
        # Update system message with current stock if provided
        # This ensures the AI always has the latest context about what stock the user is viewing
        if current_stock:
            self._update_system_message_with_current_stock(session, current_stock)
        
        # Create user message
        user_message = self.create_message(
            session=session,
            role=AIRequest.ROLE_USER,
            content=content,
            status=AIRequest.COMPLETED
        )
        
        # Check if async processing is enabled and Celery is available
        if async_processing and self.enable_celery:
            try:
                from .tasks import process_chat_message_async, CELERY_AVAILABLE
                
                if CELERY_AVAILABLE:
                    # Create pending assistant message
                    assistant_message = self.create_message(
                        session=session,
                        role=AIRequest.ROLE_ASSISTANT,
                        content="",
                        status=AIRequest.PENDING
                    )
                    
                    # Queue async task
                    task = process_chat_message_async.delay(
                        user_id=user.id,
                        session_id=session.id,
                        assistant_message_id=assistant_message.id
                    )
                    
                    logger.info(
                        f"Queued async chat task {task.id} for user {user.username} "
                        f"in session {session.id}"
                    )
                    
                    return {
                        'conversation_id': session.id,
                        'response': 'Your message is being processed. Please wait...',
                        'status': 'pending',
                        'task_id': str(task.id)
                    }
            except ImportError:
                # Celery not available, fall through to sync processing
                logger.warning("Celery not available, using synchronous processing")
        
        # Synchronous processing
        # Format messages for AI
        ai_messages = self.format_messages_for_ai(session, include_system=True)
        
        # Create pending assistant message
        assistant_message = self.create_message(
            session=session,
            role=AIRequest.ROLE_ASSISTANT,
            content="",
            status=AIRequest.RUNNING
        )
        
        try:
            # Call OpenAI API
            ai_response = self._call_openai_api(ai_messages)
            
            # Update assistant message with response
            assistant_message.content = ai_response
            assistant_message.status = AIRequest.COMPLETED
            assistant_message.save()
            
            logger.info(
                f"Successfully processed message for user {user.username} "
                f"in session {session.id}"
            )
            
            return {
                'conversation_id': session.id,
                'response': ai_response,
                'status': 'success'
            }
            
        except Exception as e:
            # Update assistant message with error
            error_msg = "I apologize, but I'm having trouble processing your request right now. Please try again later."
            assistant_message.content = error_msg
            assistant_message.status = AIRequest.FAILED
            assistant_message.error_message = str(e)
            assistant_message.save()
            
            logger.error(
                f"Error processing message for user {user.username} "
                f"in session {session.id}: {str(e)}"
            )
            
            # Return fallback response
            return {
                'conversation_id': session.id,
                'response': error_msg,
                'status': 'error',
                'fallback': True
            }