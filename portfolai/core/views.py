from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import openai
import finnhub
from newsapi import NewsApiClient
from django.conf import settings
import requests
from datetime import datetime, timedelta
import random

# Initialize API clients only if keys are available
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else None
newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY) if settings.NEWS_API_KEY else None

# Fallback data for when APIs are not available
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


def landing(request):
    """Landing page view"""
    return render(request, "landing.html")


def trading_dashboard(request):
    """Trading dashboard view"""
    return render(request, "home.html")


@api_view(["GET"])
def hello_api(request):
    return Response({"message": "Hello from Django + Basecoat + DRF!"})


@api_view(["GET"])
def stock_summary(request):
    """
    Example: /api/stock/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "AAPL").strip().upper()
    
    # Handle empty or whitespace symbols
    if not symbol:
        symbol = "AAPL"

    # Check if API keys are available
    if not settings.FINNHUB_API_KEY or not finnhub_client or not settings.OPENAI_API_KEY or not openai_client:
        # Return fallback data when APIs are not available
        if symbol in FALLBACK_STOCKS:
            stock_data = FALLBACK_STOCKS[symbol]
            fallback_summary = f"""
**PortfolAI Stock Summary for {symbol}**

**Company:** {stock_data['name']}
**Current Price:** ${stock_data['price']:.2f}
**Change:** ${stock_data['change']:.2f} ({stock_data['changePercent']:.2f}%)

**Summary:**
This is a demo stock summary for educational purposes. The data shown is sample data for demonstration. For real-time analysis and AI-powered insights, please configure the required API keys.

**Key Metrics:**
- Price: ${stock_data['price']:.2f}
- Change: {stock_data['changePercent']:.2f}%
- Market Cap: Not available (demo data)

*Note: This is fallback data for demonstration purposes. Configure API keys for real-time analysis.*
            """
            return Response({
                "symbol": symbol,
                "company": {"name": stock_data['name']},
                "quote": {
                    "c": stock_data['price'],
                    "pc": stock_data['price'] - stock_data['change'],
                    "o": stock_data['price'] - stock_data['change'],
                    "h": stock_data['price'] + abs(stock_data['change']),
                    "l": stock_data['price'] - abs(stock_data['change']),
                    "v": 1000000
                },
                "ai_summary": fallback_summary,
                "fallback": True
            })
        else:
            return Response({"error": f"No data available for symbol {symbol} (API not configured)"}, status=404)

    try:
        # Fetch stock quote from Finnhub
        quote = finnhub_client.quote(symbol)
        company = finnhub_client.company_profile2(symbol=symbol)

        # Ask OpenAI to summarize
        summary_prompt = f"Summarize this stock data for {symbol}: {quote}"
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        ai_summary = response.choices[0].message.content

        return Response({
            "symbol": symbol,
            "company": company,
            "quote": quote,
            "ai_summary": ai_summary
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_stock_data(request):
    """
    Get basic stock data for search functionality
    Example: /api/stock-data/?symbol=AAPL
    """
    symbol = request.GET.get("symbol", "").strip().upper()
    
    if not symbol:
        return Response({"error": "Symbol parameter is required"}, status=400)
    
    # Check if API key is available, if not use fallback data
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        if symbol in FALLBACK_STOCKS:
            stock_data = FALLBACK_STOCKS[symbol]
            return Response({
                "symbol": symbol,
                "name": stock_data['name'],
                "price": stock_data['price'],
                "change": stock_data['change'],
                "changePercent": stock_data['changePercent'],
                "open": stock_data['price'] - stock_data['change'],
                "high": stock_data['price'] + abs(stock_data['change']),
                "low": stock_data['price'] - abs(stock_data['change']),
                "volume": 1000000,
                "marketCap": 0,
                "peRatio": 0,
                "yearHigh": stock_data['price'] + abs(stock_data['change']),
                "yearLow": stock_data['price'] - abs(stock_data['change']),
                "fallback": True
            })
        else:
            return Response({"error": f"No data available for symbol {symbol} (API not configured)"}, status=404)
    
    try:
        # Fetch stock quote from Finnhub
        quote = finnhub_client.quote(symbol)
        
        # Check if quote data is valid
        if not quote or quote.get('c') is None:
            # Try fallback data if available
            if symbol in FALLBACK_STOCKS:
                stock_data = FALLBACK_STOCKS[symbol]
                return Response({
                    "symbol": symbol,
                    "name": stock_data['name'],
                    "price": stock_data['price'],
                    "change": stock_data['change'],
                    "changePercent": stock_data['changePercent'],
                    "open": stock_data['price'] - stock_data['change'],
                    "high": stock_data['price'] + abs(stock_data['change']),
                    "low": stock_data['price'] - abs(stock_data['change']),
                    "volume": 1000000,
                    "marketCap": 0,
                    "peRatio": 0,
                    "yearHigh": stock_data['price'] + abs(stock_data['change']),
                    "yearLow": stock_data['price'] - abs(stock_data['change']),
                    "fallback": True
                })
            return Response({"error": f"No data found for symbol {symbol}"}, status=404)
        
        # Try to get company profile, but don't fail if it's not available
        company = {}
        try:
            company = finnhub_client.company_profile2(symbol=symbol)
        except Exception as e:
            print(f"Warning: Could not fetch company profile for {symbol}: {e}")
            company = {}
        
        # Calculate price change and percentage
        current_price = quote.get('c', 0)
        previous_close = quote.get('pc', 0)
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
        
        return Response({
            "symbol": symbol,
            "name": company.get('name', symbol),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "open": quote.get('o', 0),
            "high": quote.get('h', 0),
            "low": quote.get('l', 0),
            "volume": quote.get('v', 0),
            "marketCap": company.get('marketCapitalization', 0),
            "peRatio": company.get('pe', 0),
            "yearHigh": quote.get('h', 0),  # Using current high as year high for now
            "yearLow": quote.get('l', 0),   # Using current low as year low for now
        })
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        # Try fallback data if available
        if symbol in FALLBACK_STOCKS:
            stock_data = FALLBACK_STOCKS[symbol]
            return Response({
                "symbol": symbol,
                "name": stock_data['name'],
                "price": stock_data['price'],
                "change": stock_data['change'],
                "changePercent": stock_data['changePercent'],
                "open": stock_data['price'] - stock_data['change'],
                "high": stock_data['price'] + abs(stock_data['change']),
                "low": stock_data['price'] - abs(stock_data['change']),
                "volume": 1000000,
                "marketCap": 0,
                "peRatio": 0,
                "yearHigh": stock_data['price'] + abs(stock_data['change']),
                "yearLow": stock_data['price'] - abs(stock_data['change']),
                "fallback": True
            })
        return Response({"error": f"Failed to fetch data for {symbol}: {str(e)}"}, status=500)


@api_view(["GET"])
def get_market_movers(request):
    """
    Get top gainers and losers from the market
    Example: /api/market-movers/
    """
    # Check if API key is available, if not use fallback data
    if not settings.FINNHUB_API_KEY or not finnhub_client:
        # Create market movers from fallback data
        fallback_stocks = list(FALLBACK_STOCKS.values())
        fallback_stocks.sort(key=lambda x: x['changePercent'], reverse=True)
        
        gainers = fallback_stocks[:5]
        losers = fallback_stocks[-5:][::-1]
        
        return Response({
            "gainers": gainers,
            "losers": losers,
            "fallback": True
        })
    
    try:
        # Get stock symbols for major companies
        major_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
        
        market_data = []
        
        for symbol in major_symbols:
            try:
                quote = finnhub_client.quote(symbol)
                
                # Check if quote data is valid
                if not quote or quote.get('c') is None:
                    continue
                
                # Try to get company profile, but don't fail if it's not available
                company = {}
                try:
                    company = finnhub_client.company_profile2(symbol=symbol)
                except:
                    company = {}
                
                current_price = quote.get('c', 0)
                previous_close = quote.get('pc', 0)
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                
                market_data.append({
                    "symbol": symbol,
                    "name": company.get('name', symbol),
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2)
                })
            except Exception as e:
                print(f"Warning: Could not fetch data for {symbol}: {e}")
                continue  # Skip symbols that fail
        
        # Sort by change percentage
        market_data.sort(key=lambda x: x['changePercent'], reverse=True)
        
        # Get top 5 gainers and losers
        gainers = market_data[:5]
        losers = market_data[-5:][::-1]  # Reverse to get worst performers first
        
        return Response({
            "gainers": gainers,
            "losers": losers
        })
        
    except Exception as e:
        print(f"Error fetching market data: {str(e)}")
        # Return fallback data on error
        fallback_stocks = list(FALLBACK_STOCKS.values())
        fallback_stocks.sort(key=lambda x: x['changePercent'], reverse=True)
        
        gainers = fallback_stocks[:5]
        losers = fallback_stocks[-5:][::-1]
        
        return Response({
            "gainers": gainers,
            "losers": losers,
            "fallback": True
        })


@api_view(["GET"])
def get_news(request):
    """
    Get financial news from NewsAPI.org
    Example: /api/news/?symbol=AAPL (optional)
    """
    symbol = request.GET.get("symbol", "").upper()
    
    # Check if API key is available, if not use fallback data
    if not settings.NEWS_API_KEY or not newsapi:
        return Response({
            "articles": FALLBACK_NEWS,
            "totalResults": len(FALLBACK_NEWS),
            "fallback": True
        })
    
    try:
        if symbol:
            # Get company-specific news using everything endpoint
            try:
                # Use today's date for better results
                from_date = datetime.now().strftime('%Y-%m-%d')
                articles = newsapi.get_everything(
                    q=f"{symbol} stock",
                    from_param=from_date,
                    language='en',
                    sort_by='popularity',  # Use popularity as recommended in docs
                    page_size=10
                )
            except Exception as e:
                print(f"Warning: News API failed for {symbol}: {e}")
                # Fallback to top headlines for business category
                articles = newsapi.get_top_headlines(
                    category='business',
                    language='en',
                    page_size=10
                )
        else:
            # Get general financial market news using top headlines
            try:
                articles = newsapi.get_top_headlines(
                    category='business',
                    language='en',
                    page_size=10
                )
            except Exception as e:
                print(f"Warning: News API top headlines failed: {e}")
                # Fallback to everything endpoint
                articles = newsapi.get_everything(
                    q='stock market OR finance OR economy',
                    language='en',
                    sort_by='popularity',
                    page_size=10
                )
        
        # Check if we got valid articles
        if not articles or 'articles' not in articles:
            print("No articles found in NewsAPI response")
            return Response({
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            })
        
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
            return Response({
                "articles": FALLBACK_NEWS,
                "totalResults": len(FALLBACK_NEWS),
                "fallback": True
            })
        
        return Response({
            "articles": news_items,
            "totalResults": articles.get('totalResults', 0)
        })
        
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        # Return fallback news on error
        return Response({
            "articles": FALLBACK_NEWS,
            "totalResults": len(FALLBACK_NEWS),
            "fallback": True
        })


@api_view(["GET"])
def portfolai_analysis(request):
    """
    Get AI-powered stock analysis using OpenAI
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
        
        # Try using the Responses API with web search capabilities first
        try:
            response = openai_client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=enhanced_prompt
            )
            analysis = response.output_text
        except Exception as e:
            print(f"Web search API failed, falling back to standard chat API: {e}")
            # Fallback to standard chat completions API
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst AI assistant. Provide detailed, educational stock analysis using the provided real-time data and your knowledge. Always remind users that this is for educational purposes only and not financial advice."},
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
        
    except Exception as e:
        print(f"Error generating AI analysis for {symbol}: {str(e)}")
        return Response({
            "error": f"Failed to generate analysis for {symbol}: {str(e)}",
            "fallback": True
        }, status=500)
