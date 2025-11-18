"""
Test Helper Functions - Shared Utilities for Tests
==================================================

This module contains shared utility functions for tests to eliminate
code duplication across test files.
"""


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
