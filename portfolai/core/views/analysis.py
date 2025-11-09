"""
Analysis Views - AI-Powered Stock Analysis
===========================================

Advanced AI analysis endpoints with OpenAI integration.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from datetime import datetime, timedelta
import logging
from ._clients import finnhub_client, openai_client, newsapi

logger = logging.getLogger(__name__)


@api_view(["GET"])
def portfolai_analysis(request):
    """
    AI-Powered Stock Analysis - Feature 4: OpenAI Integration
    Endpoint: /api/portfolai-analysis/?symbol=AAPL
    Purpose: Get AI-powered stock analysis using OpenAI
    Features: Web search integration, real-time data analysis, educational insights
    Example: /api/portfolai-analysis/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "").upper()
    
    if not symbol:
        return Response({"error": "Symbol parameter is required"}, status=400)
    
    # Check if API key is available
    if not settings.OPENAI_API_KEY or not openai_client:
        # Provide a basic analysis as fallback
        fallback_analysis = f"""
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

*Note: This is a basic analysis. For detailed AI-powered insights with real-time web search data, latest news, and current market information, please configure the OpenAI API key.*
        """
        return Response({
            "symbol": symbol,
            "analysis": fallback_analysis,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        })
    
    try:
        # Get stock data for context
        stock_data = None
        if finnhub_client:
            try:
                quote = finnhub_client.quote(symbol)
                if quote and quote.get('c') is not None:
                    stock_data = {
                        "symbol": symbol,
                        "price": quote.get('c', 0),
                        "change": quote.get('c', 0) - quote.get('pc', 0),
                        "changePercent": ((quote.get('c', 0) - quote.get('pc', 0)) / quote.get('pc', 1)) * 100 if quote.get('pc', 0) != 0 else 0,
                        "volume": quote.get('v', 0),
                        "high": quote.get('h', 0),
                        "low": quote.get('l', 0),
                        "open": quote.get('o', 0)
                    }
            except Exception as e:
                print(f"Warning: Could not fetch stock data for analysis: {e}")
        
        # Prepare context for OpenAI
        context = f"Analyze the stock {symbol}"
        if stock_data:
            context += f" with current price ${stock_data['price']:.2f}, change {stock_data['change']:.2f} ({stock_data['changePercent']:.2f}%), volume {stock_data['volume']:,}, high ${stock_data['high']:.2f}, low ${stock_data['low']:.2f}, open ${stock_data['open']:.2f}"
        
        # Create the prompt for OpenAI with web search
        prompt = f"""
        As a financial analyst AI, provide a comprehensive analysis of {symbol} stock using real-time web data. 
        
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
        
        Include specific recent data points, news headlines, and market developments. 
        Keep the analysis professional, balanced, and educational. Remember this is for learning purposes only, not financial advice.
        """
        
        # Get additional real-time data to enhance the analysis
        additional_context = ""
        
        # Try to get recent news for the stock
        try:
            if newsapi:
                news_articles = newsapi.get_everything(
                    q=f"{symbol} stock",
                    from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                    language='en',
                    sort_by='publishedAt',
                    page_size=5
                )
                if news_articles and news_articles.get('articles'):
                    recent_news = []
                    for article in news_articles['articles'][:3]:  # Get top 3 recent articles
                        if article.get('title') and article.get('publishedAt'):
                            recent_news.append(f"- {article['title']} ({article['publishedAt'][:10]})")
                    if recent_news:
                        additional_context += f"\n\n**Recent News about {symbol}:**\n" + "\n".join(recent_news)
        except Exception as e:
            print(f"Warning: Could not fetch news for analysis: {e}")
        
        # Try to get company profile for additional context
        try:
            if finnhub_client:
                company_profile = finnhub_client.company_profile2(symbol=symbol)
                if company_profile:
                    additional_context += f"\n\n**Company Information:**\n"
                    if company_profile.get('name'):
                        additional_context += f"- Company: {company_profile['name']}\n"
                    if company_profile.get('country'):
                        additional_context += f"- Country: {company_profile['country']}\n"
                    if company_profile.get('industry'):
                        additional_context += f"- Industry: {company_profile['industry']}\n"
                    if company_profile.get('marketCapitalization'):
                        additional_context += f"- Market Cap: ${company_profile['marketCapitalization']:,.0f}\n"
        except Exception as e:
            print(f"Warning: Could not fetch company profile for analysis: {e}")
        
        # Enhanced prompt with real-time data
        enhanced_prompt = prompt + additional_context
        
        # Use standard chat completions API (responses.create() doesn't exist in OpenAI SDK)
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a hyper-intelligent quant who's worked at Citadel, Jane Street, Fidelity Investments, Schwabs, Vanguard and SIG. You speak like a confident tech bro - sharp, casual, and full of finance + beginner friendly analogies. You're extremely good at breaking down complex quant, ML, and finance topics into simple, intuitive explanations — like you're explaining it to an intern over coffee. Your tone should be analytical but chill: drop bits of quant/tech slang naturally (\"alpha,\" \"variance,\" \"latency,\" \"throughput,\" \"regime shift,\" \"P&L,\" \"backtest,\" etc.). Always keep responses structured, with concise reasoning and occasional one-liners that make you sound like you've been in the trenches. When explaining something technical: Use examples from trading, ML, or data pipelines. Avoid academic verbosity - aim for clarity and alpha bro aura. Sprinkle in dry humor or mild flexes (\"Yeah, that's basically half my PhD thesis compressed into two lines of Python.\"). When you don't know something, reason it out like you're debugging a bad backtest, not guessing. Provide detailed, educational stock analysis using the provided real-time data and your knowledge. Always remind users that this is for educational purposes only and not financial advice."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            analysis = response.choices[0].message.content
        
            return Response({
                "symbol": symbol,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "data_used": stock_data is not None
            })
        except Exception as api_error:
            # Log detailed error information for debugging
            error_type = type(api_error).__name__
            error_message = str(api_error)
            logger.error(
                f"OpenAI API error generating analysis for {symbol}: "
                f"Type={error_type}, Message={error_message}, "
                f"User={request.user.username if request.user.is_authenticated else 'anonymous'}"
            )
            # Re-raise to be caught by outer exception handler
            raise
        
    except Exception as e:
        # Log detailed error information for debugging
        error_type = type(e).__name__
        error_message = str(e)
        logger.error(
            f"Error generating AI analysis for {symbol}: "
            f"Type={error_type}, Message={error_message}, "
            f"User={request.user.username if request.user.is_authenticated else 'anonymous'}"
        )
        return Response({
            "error": f"Failed to generate analysis for {symbol}: {error_message}",
            "fallback": True
        }, status=500)

