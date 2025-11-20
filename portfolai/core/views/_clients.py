"""
Shared API Client Initialization
=================================

This module initializes API clients that are shared across all view modules.
API clients are only initialized if API keys are available, ensuring graceful
degradation when APIs are not configured.
"""

import logging

import openai
import finnhub
from django.conf import settings
from ..services import (  # noqa: F401  # pylint: disable=unused-import
    MarketDataService,
    FALLBACK_STOCKS,
    FALLBACK_NEWS,
)

logger = logging.getLogger(__name__)

# Initialize API clients only if keys are available
# This ensures graceful degradation when APIs are not configured
if settings.OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
else:
    openai_client = None

if settings.FINNHUB_API_KEY:
    finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)
else:
    finnhub_client = None

# The News API client - using requests library
# Keep newsapi variable name for backward compatibility
if settings.NEWS_API_KEY:
    newsapi = {'api_token': settings.NEWS_API_KEY, 'base_url': 'https://api.thenewsapi.com'}
else:
    newsapi = None
