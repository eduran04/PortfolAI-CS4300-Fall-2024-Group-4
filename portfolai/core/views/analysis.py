"""
Analysis Views - Demo Stock Analysis
=====================================

Template-based stock analysis with live market data enrichment.
"""

from datetime import datetime, timedelta
import logging
import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ._clients import finnhub_client, newsapi
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

*Note: Demo mode — template insights enriched with live market data when API keys are configured.*
"""


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
    if not newsapi or not newsapi.get('api_token'):
        return ""

    try:
        url = 'https://api.thenewsapi.com/v1/news/all'
        params = {
            'api_token': newsapi['api_token'],
            'search': f"{symbol} stock",
            'language': 'en',
            'categories': 'business',
            'limit': 5,
            'sort': 'published_at'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'error' in data or not data.get('data'):
            return ""

        articles = data.get('data', [])[:3]

        recent_news = []
        for article in articles:
            if article.get('title') and article.get('published_at'):
                title = article['title']
                date = article['published_at'][:10]
                recent_news.append(f"- {title} ({date})")

        if recent_news:
            return (
                f"\n\n**Recent News about {symbol}:**\n"
                + "\n".join(recent_news)
            )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not fetch news for analysis: %s", e)

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


def _fetch_insider_sentiment(symbol):
    """
    Fetch insider sentiment data for the given symbol.

    Args:
        symbol: Stock symbol to fetch insider sentiment for

    Returns:
        str: Formatted insider sentiment context string or empty string if unavailable
    """
    if not finnhub_client:
        return ""

    try:
        # Calculate date range (6 months ago to today)
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

        insider_data = finnhub_client.stock_insider_sentiment(
            symbol=symbol,
            _from=from_date,
            to=to_date
        )

        if not insider_data or not insider_data.get('data'):
            return ""

        context = "\n\n**Insider Sentiment (MSPR - Monthly Share Purchase Ratio):**\n"

        # Get recent months (limit to 3 most recent)
        if len(insider_data['data']) > 3:
            recent_data = insider_data['data'][-3:]
        else:
            recent_data = insider_data['data']

        if not recent_data:
            return ""

        for entry in recent_data:
            month = entry.get('month', 0)
            year = entry.get('year', 0)
            mspr = entry.get('mspr', 0)
            change = entry.get('change', 0)

            sentiment = "positive" if mspr > 0 else "negative" if mspr < 0 else "neutral"
            action = "net buying" if change > 0 else "net selling" if change < 0 else "no change"

            context += (
                f"- {year}-{month:02d}: MSPR {mspr:.2f} ({sentiment}), "
                f"Change: {change:,} shares ({action})\n"
            )

        context += (
            "\n*MSPR ranges from -100 (most negative) to 100 (most positive), "
            "signaling potential price changes in 30-90 days*"
        )

        return context
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Warning: Could not fetch insider sentiment for analysis: {e}")

    return ""


def _fetch_recommendation_trends(symbol):
    """
    Fetch analyst recommendation trends for the given symbol.

    Args:
        symbol: Stock symbol to fetch recommendations for

    Returns:
        str: Formatted recommendation trends context string or empty string if unavailable
    """
    if not finnhub_client:
        return ""

    try:
        recommendations = finnhub_client.recommendation_trends(symbol=symbol)

        if not recommendations or len(recommendations) == 0:
            return ""

        context = "\n\n**Analyst Recommendation Trends:**\n"

        # Get most recent recommendation (first in the list)
        latest = recommendations[0]

        period = latest.get('period', 'N/A')
        strong_buy = latest.get('strongBuy', 0)
        buy = latest.get('buy', 0)
        hold = latest.get('hold', 0)
        sell = latest.get('sell', 0)
        strong_sell = latest.get('strongSell', 0)

        total = strong_buy + buy + hold + sell + strong_sell

        if total == 0:
            return ""

        context += f"- Period: {period}\n"
        context += f"- Strong Buy: {strong_buy}\n"
        context += f"- Buy: {buy}\n"
        context += f"- Hold: {hold}\n"
        context += f"- Sell: {sell}\n"
        context += f"- Strong Sell: {strong_sell}\n"
        context += f"- Total Analysts: {total}\n"

        # Calculate sentiment percentages
        bullish = ((strong_buy + buy) / total * 100) if total > 0 else 0
        bearish = ((sell + strong_sell) / total * 100) if total > 0 else 0
        neutral_pct = (hold / total * 100) if total > 0 else 0

        context += (
            f"\n*Overall: {bullish:.1f}% bullish, "
            f"{neutral_pct:.1f}% neutral, {bearish:.1f}% bearish*"
        )

        return context
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Warning: Could not fetch recommendation trends for analysis: {e}")

    return ""


def _build_demo_analysis(symbol):
    """Build template analysis enriched with live market data."""
    analysis = FALLBACK_ANALYSIS.format(symbol=symbol)
    stock_data = _fetch_stock_data(symbol)

    if stock_data:
        live_section = (
            f"\n\n**Live Market Data for {symbol}:**\n"
            f"- Current Price: ${stock_data['price']:.2f}\n"
            f"- Change: {stock_data['change']:+.2f} "
            f"({stock_data['changePercent']:+.2f}%)\n"
            f"- Open: ${stock_data['open']:.2f}\n"
            f"- High: ${stock_data['high']:.2f}\n"
            f"- Low: ${stock_data['low']:.2f}\n"
            f"- Volume: {stock_data['volume']:,}\n"
        )
        analysis = live_section + analysis

    analysis += _fetch_news_context(symbol)
    analysis += _fetch_company_context(symbol)
    analysis += _fetch_insider_sentiment(symbol)
    analysis += _fetch_recommendation_trends(symbol)
    return analysis


@api_view(["GET"])
def portfolai_analysis(request):
    """
    Demo stock analysis with live market data enrichment.
    Endpoint: /api/portfolai-analysis/?symbol=AAPL
    """
    serializer = SymbolInputSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid input", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    symbol = serializer.validated_data['symbol']
    analysis = _build_demo_analysis(symbol)

    return Response({
        "symbol": symbol,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
        "fallback": True,
    })
