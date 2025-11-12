"""
Analysis Views - AI-Powered Stock Analysis
===========================================

Advanced AI analysis endpoints with OpenAI integration.
"""

from datetime import datetime, timedelta
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from ._clients import finnhub_client, openai_client, newsapi
from ..serializers import SymbolInputSerializer

logger = logging.getLogger(__name__)

# PROMPT CONSTANTS

FALLBACK_ANALYSIS = """
**PortfolAI Analysis for {symbol}**

**Technical Analysis:**
- Current price data is being analyzed
- Market trends and patterns are being evaluated
- Support and resistance levels are being calculated

**Fundamental Analysis:**
- Company financials are being reviewed
- Industry position and competitive analysis
- Growth prospects and valuation metrics

**Market Sentiment:**
- Overall market conditions are being assessed
- Investor sentiment and trading volume analysis
- News and events impact evaluation

**Risk Assessment:**
- Volatility analysis and risk factors
- Market and sector-specific risks
- Economic environment considerations

**Investment Recommendation:**
- This is a demo analysis for educational purposes
- Always conduct your own research before making investment decisions
- Consider consulting with a financial advisor

**Key Factors to Watch:**
- Earnings reports and financial updates
- Industry developments and regulatory changes
- Market volatility and economic indicators

*Note: This is a basic analysis. For detailed AI-powered insights
with real-time web search data, latest news, and current market
information, please configure the OpenAI API key.*
"""

ANALYSIS_PROMPT = """
        As a financial analyst AI, provide a comprehensive analysis of {symbol}
        stock using real-time web data.

        {context}

        Please search for and analyze:
        1. Latest news and developments about {symbol}
        2. Recent earnings reports and financial performance
        3. Market sentiment and analyst opinions
        4. Industry trends and competitive landscape
        5. Recent price movements and technical indicators
        6. Regulatory or legal developments affecting the company

        Provide a structured analysis with:
        - Technical Analysis (current price trends, support/resistance levels)
        - Fundamental Analysis (recent financials, earnings, growth prospects)
        - Market Sentiment (news sentiment, analyst ratings, market buzz)
        - Risk Assessment (key risks and opportunities)
        - Investment Recommendation (Buy/Hold/Sell with detailed reasoning)
        - Key Factors to Watch (upcoming events, catalysts)

        Include specific recent data points, news headlines, and market
        developments. Keep the analysis professional, balanced, and educational.
        Remember this is for learning purposes only, not financial advice.
        """

SYSTEM_PROMPT = (
    "You are a hyper-intelligent quant who's worked at Citadel, "
    "Jane Street, Fidelity Investments, Schwabs, Vanguard and SIG. "
    "You speak like a confident tech bro - sharp, casual, and full "
    "of finance + beginner friendly analogies. You're extremely good "
    "at breaking down complex quant, ML, and finance topics into "
    "simple, intuitive explanations — like you're explaining it to an "
    "intern over coffee. Your tone should be analytical but chill: "
    "drop bits of quant/tech slang naturally (\"alpha,\" \"variance,\" "
    "\"latency,\" \"throughput,\" \"regime shift,\" \"P&L,\" "
    "\"backtest,\" etc.). Always keep responses structured, with "
    "concise reasoning and occasional one-liners that make you sound "
    "like you've been in the trenches. When explaining something "
    "technical: Use examples from trading, ML, or data pipelines. "
    "Avoid academic verbosity - aim for clarity and alpha bro aura. "
    "Sprinkle in dry humor or mild flexes (\"Yeah, that's basically "
    "half my PhD thesis compressed into two lines of Python.\"). "
    "When you don't know something, reason it out like you're "
    "debugging a bad backtest, not guessing. Provide detailed, "
    "educational stock analysis using the provided real-time data and "
    "your knowledge. Always remind users that this is for educational "
    "purposes only and not financial advice."
)


# HELPER FUNCTIONS TO PREVENT NESTING

def _fetch_stock_data(symbol):
    """
    Fetch stock data for the given symbol.

    Args:
        symbol: Stock symbol to fetch data for

    Returns:
        dict: Stock data with price, change, volume, etc. or None if unavailable
    """
    if not finnhub_client:
        return None

    try:
        quote = finnhub_client.quote(symbol)
        if quote and quote.get('c') is not None:
            return {
                "symbol": symbol,
                "price": quote.get('c', 0),
                "change": quote.get('c', 0) - quote.get('pc', 0),
                "changePercent": (
                    ((quote.get('c', 0) - quote.get('pc', 0))
                     / quote.get('pc', 1) * 100)
                    if quote.get('pc', 0) != 0 else 0
                ),
                "volume": quote.get('v', 0),
                "high": quote.get('h', 0),
                "low": quote.get('l', 0),
                "open": quote.get('o', 0)
            }
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Warning: Could not fetch stock data for analysis: {e}")

    return None


def _fetch_news_context(symbol):
    """
    Fetch recent news context for the given symbol.

    Args:
        symbol: Stock symbol to fetch news for

    Returns:
        str: Formatted news context string or empty string if unavailable
    """
    if not newsapi:
        return ""

    try:
        news_articles = newsapi.get_everything(
            q=f"{symbol} stock",
            from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=5
        )
        if not news_articles or not news_articles.get('articles'):
            return ""

        recent_news = []
        for article in news_articles['articles'][:3]:
            if article.get('title') and article.get('publishedAt'):
                title = article['title']
                date = article['publishedAt'][:10]
                recent_news.append(f"- {title} ({date})")

        if recent_news:
            return (
                f"\n\n**Recent News about {symbol}:**\n"
                + "\n".join(recent_news)
            )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Warning: Could not fetch news for analysis: {e}")

    return ""


def _fetch_company_context(symbol):
    """
    Fetch company profile context for the given symbol.

    Args:
        symbol: Stock symbol to fetch company profile for

    Returns:
        str: Formatted company context string or empty string if unavailable
    """
    if not finnhub_client:
        return ""

    try:
        company_profile = finnhub_client.company_profile2(symbol=symbol)
        if not company_profile:
            return ""

        context = "\n\n**Company Information:**\n"
        if company_profile.get('name'):
            context += f"- Company: {company_profile['name']}\n"
        if company_profile.get('country'):
            context += f"- Country: {company_profile['country']}\n"
        if company_profile.get('industry'):
            context += f"- Industry: {company_profile['industry']}\n"
        if company_profile.get('marketCapitalization'):
            market_cap = company_profile['marketCapitalization']
            context += f"- Market Cap: ${market_cap:,.0f}\n"

        return context
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Warning: Could not fetch company profile for analysis: {e}")

    return ""


def _build_analysis_context(symbol, stock_data):
    """
    Build analysis context string from symbol and stock data.

    Args:
        symbol: Stock symbol
        stock_data: Stock data dictionary or None

    Returns:
        str: Formatted context string
    """
    context = f"Analyze the stock {symbol}"
    if stock_data:
        context += (
            f" with current price ${stock_data['price']:.2f}, "
            f"change {stock_data['change']:.2f} "
            f"({stock_data['changePercent']:.2f}%), "
            f"volume {stock_data['volume']:,}, "
            f"high ${stock_data['high']:.2f}, "
            f"low ${stock_data['low']:.2f}, "
            f"open ${stock_data['open']:.2f}"
        )
    return context


def _generate_ai_analysis(_symbol, enhanced_prompt):
    """
    Generate AI analysis using OpenAI API.

    Args:
        _symbol: Stock symbol (unused, kept for API consistency)
        enhanced_prompt: Complete prompt with all context

    Returns:
        str: AI-generated analysis text

    Raises:
        Exception: If OpenAI API call fails
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": enhanced_prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return response.choices[0].message.content


@api_view(["GET"])
def portfolai_analysis(request):
    """
    AI-Powered Stock Analysis - Feature 4: OpenAI Integration
    Endpoint: /api/portfolai-analysis/?symbol=AAPL
    Purpose: Get AI-powered stock analysis using OpenAI
    Features: Web search integration, real-time data analysis, educational insights
    Example: /api/portfolai-analysis/?symbol=AAPL
    """
    # Validate and sanitize input using serializer
    serializer = SymbolInputSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid input", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    symbol = serializer.validated_data['symbol']

    # Check if API key is available
    if not settings.OPENAI_API_KEY or not openai_client:
        fallback_analysis = FALLBACK_ANALYSIS.format(symbol=symbol)
        return Response({
            "symbol": symbol,
            "analysis": fallback_analysis,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        })

    try:
        # Get stock data for context
        stock_data = _fetch_stock_data(symbol)

        # Build context for OpenAI
        context = _build_analysis_context(symbol, stock_data)

        # Create the prompt for OpenAI with web search
        prompt = ANALYSIS_PROMPT.format(symbol=symbol, context=context)

        # Get additional real-time data to enhance the analysis
        additional_context = _fetch_news_context(symbol)
        additional_context += _fetch_company_context(symbol)

        # Enhanced prompt with real-time data
        enhanced_prompt = prompt + additional_context

        # Generate AI analysis
        try:
            analysis = _generate_ai_analysis(symbol, enhanced_prompt)

            return Response({
                "symbol": symbol,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "data_used": stock_data is not None
            })
        except Exception as api_error:  # pylint: disable=broad-exception-caught
            # Log detailed error information for debugging
            error_type = type(api_error).__name__
            error_message = str(api_error)
            user_name = (
                request.user.username if request.user.is_authenticated
                else 'anonymous'
            )
            logger.error(
                "OpenAI API error generating analysis for %s: Type=%s, Message=%s, User=%s",
                symbol, error_type, error_message, user_name
            )
            # Re-raise to be caught by outer exception handler
            raise

    except Exception as e:  # pylint: disable=broad-exception-caught
        # Log detailed error information for debugging
        error_type = type(e).__name__
        error_message = str(e)
        user_name = (
            request.user.username if request.user.is_authenticated
            else 'anonymous'
        )
        logger.error(
            "Error generating AI analysis for %s: Type=%s, Message=%s, User=%s",
            symbol, error_type, error_message, user_name
        )
        return Response({
            "error": (
                f"Failed to generate analysis for {symbol}: "
                f"{error_message}"
            ),
            "fallback": True
        }, status=500)
