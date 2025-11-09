"""
Shared API Client Initialization
=================================

This module initializes API clients that are shared across all view modules.
API clients are only initialized if API keys are available, ensuring graceful
degradation when APIs are not configured.
"""

import openai
import finnhub
from newsapi import NewsApiClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Initialize API clients only if keys are available
# This ensures graceful degradation when APIs are not configured
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else None
newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY) if settings.NEWS_API_KEY else None

# Import service classes for business logic
from ..services import MarketDataService, FALLBACK_STOCKS, FALLBACK_NEWS

