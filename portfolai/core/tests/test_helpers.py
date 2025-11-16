"""
Test Helper Functions - Shared Utilities for Tests
==================================================

This module contains shared utility functions for tests to eliminate
code duplication across test files.
"""

from contextlib import contextmanager
from unittest.mock import patch
from django.conf import settings
from django.urls import reverse


@contextmanager
def mock_api_keys(finnhub_key='test_key', openai_key='test_key'):
    """
    Context manager for mocking API keys in settings.

    Args:
        finnhub_key: Value for FINNHUB_API_KEY (default: 'test_key')
        openai_key: Value for OPENAI_API_KEY (default: 'test_key')

    Usage:
        with mock_api_keys():
            # Both keys set to 'test_key'
            ...

        with mock_api_keys(finnhub_key=None, openai_key=None):
            # Both keys set to None
            ...
    """
    with patch.object(settings, 'FINNHUB_API_KEY', finnhub_key):
        with patch.object(settings, 'OPENAI_API_KEY', openai_key):
            yield


@contextmanager
def mock_stock_clients(finnhub_client=None, openai_client=None):
    """
    Context manager for mocking stock data API clients.

    Args:
        finnhub_client: Mock object for finnhub_client (if None, uses a fresh mock)
        openai_client: Mock object for openai_client (if None, uses a fresh mock)

    Yields:
        tuple: (mock_finnhub, mock_openai) for further configuration

    Usage:
        with mock_stock_clients() as (mock_finnhub, mock_openai):
            mock_finnhub.quote.return_value = {'c': 150.0}
            ...
    """
    with patch('core.views.stock_data.finnhub_client') as mock_finnhub:
        with patch('core.views.stock_data.openai_client') as mock_openai:
            if finnhub_client is not None:
                mock_finnhub = finnhub_client
            if openai_client is not None:
                mock_openai = openai_client
            yield mock_finnhub, mock_openai


def create_mock_openai_response(content):
    """
    Create a mock OpenAI API response object.

    Args:
        content: The content string for the AI response

    Returns:
        Mock object matching OpenAI response structure

    Usage:
        mock_response = create_mock_openai_response('Test summary')
        mock_openai.chat.completions.create.return_value = mock_response
    """
    return type('obj', (object,), {
        'choices': [type('obj', (object,), {
            'message': type('obj', (object,), {
                'content': content
            })()
        })()]
    })()


def assert_error_response(response, test_case, expected_status=500):
    """
    Assert that a response is an error response with expected structure.

    Args:
        response: Django test client response
        test_case: TestCase instance (for assertions)
        expected_status: Expected HTTP status code (default: 500)
    """
    test_case.assertEqual(response.status_code, expected_status)
    data = response.json()
    test_case.assertIn('error', data)


def assert_successful_stock_summary(response, test_case):
    """
    Assert that a stock summary response is successful with expected structure.

    Args:
        response: Django test client response
        test_case: TestCase instance (for assertions)
    """
    test_case.assertEqual(response.status_code, 200)
    data = response.json()
    test_case.assertIn('symbol', data)
    test_case.assertIn('ai_summary', data)


def setup_stock_summary_api_error_test(client, symbol='AAPL'):
    """
    Helper to test stock summary endpoint with API error.

    This function sets up mocks for API error scenario and returns the response.

    Args:
        client: Django test client
        symbol: Stock symbol to test (default: 'AAPL')

    Returns:
        Response from the stock_summary endpoint

    Usage:
        response = setup_stock_summary_api_error_test(self.client)
        assert_error_response(response, self)
    """
    with mock_api_keys():
        with mock_stock_clients() as (mock_finnhub, _):
            mock_finnhub.quote.side_effect = Exception("API Error")
            url = reverse('stock_summary')
            return client.get(url, {'symbol': symbol})


def assert_watchlist_response_empty(response, test_case):
    """
    Assert that a watchlist response is empty.

    Args:
        response: Django test client response
        test_case: TestCase instance (for assertions)
    """
    test_case.assertEqual(response.status_code, 200)
    data = response.json()
    test_case.assertEqual(data['count'], 0)
    test_case.assertEqual(data['symbols'], [])


def assert_watchlist_response_with_items(response, test_case, expected_count, expected_symbols):
    """
    Assert that a watchlist response contains expected items.

    Args:
        response: Django test client response
        test_case: TestCase instance (for assertions)
        expected_count: Expected number of items in watchlist
        expected_symbols: List of expected symbol strings
    """
    test_case.assertEqual(response.status_code, 200)
    data = response.json()
    test_case.assertEqual(data['count'], expected_count)
    for symbol in expected_symbols:
        test_case.assertIn(symbol, data['symbols'])


def assert_fallback_response(response, test_case, expected_symbol=None):
    """
    Assert that a response is a fallback response with expected structure.

    Args:
        response: Django test client response
        test_case: TestCase instance (for assertions)
        expected_symbol: Optional expected symbol in response
    """
    test_case.assertEqual(response.status_code, 200)
    data = response.json()
    test_case.assertIn('symbol', data)
    test_case.assertTrue(data.get('fallback', False))
    if expected_symbol:
        test_case.assertEqual(data['symbol'], expected_symbol)
