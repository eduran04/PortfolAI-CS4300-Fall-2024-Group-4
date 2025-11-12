"""
Serializers for API input validation and sanitization.

Provides proper validation and sanitization for user inputs
to prevent malicious payloads and ensure data integrity.
"""
import re
from typing import Any

from rest_framework import serializers

# Pre-compiled regex patterns for performance
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9.]+$')
SQL_KEYWORD_PATTERN = re.compile(
    r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
    re.IGNORECASE
)
INJECTION_CHAR_PATTERN = re.compile(r'[<>"\';\\]')


class SymbolInputSerializer(serializers.Serializer):
    """
    Serializer for stock symbol input validation.

    Validates and sanitizes stock symbol inputs to prevent
    malicious payloads and ensure proper format.
    """
    symbol = serializers.CharField(
        required=True,
        max_length=10,
        min_length=1,
        help_text="Stock symbol (1-10 alphanumeric characters)"
    )

    def validate_symbol(self, value: str) -> str:
        """
        Validate and sanitize the symbol input.

        Args:
            value: The raw symbol input

        Returns:
            str: Sanitized and validated symbol (uppercase, stripped)

        Raises:
            serializers.ValidationError: If symbol format is invalid
        """
        # Strip whitespace and convert to uppercase first
        symbol = value.strip().upper()

        # Check for empty string after stripping
        if not symbol:
            raise serializers.ValidationError("Symbol cannot be empty")

        # Validate symbol contains only alphanumeric characters and dots
        # (some exchanges use dots, e.g., BRK.A, BRK.B)
        if not SYMBOL_PATTERN.match(symbol):
            raise serializers.ValidationError(
                "Symbol must contain only letters, numbers, and dots"
            )

        # Additional security: prevent potential injection patterns
        # Reject symbols that look suspicious (e.g., containing SQL keywords)
        if SQL_KEYWORD_PATTERN.search(symbol):
            raise serializers.ValidationError(
                "Symbol contains invalid characters"
            )

        if INJECTION_CHAR_PATTERN.search(symbol):
            raise serializers.ValidationError(
                "Symbol contains invalid characters"
            )

        return symbol

    def create(self, validated_data: dict[str, Any]) -> None:
        """
        Not implemented - this serializer is for validation only.

        Args:
            validated_data: Validated input data

        Raises:
            NotImplementedError: This serializer is for validation only
        """
        raise NotImplementedError(
            "This serializer is for input validation only, not for creating objects"
        )

    def update(self, instance: Any, validated_data: dict[str, Any]) -> None:
        """
        Not implemented - this serializer is for validation only.

        Args:
            instance: Object instance to update
            validated_data: Validated input data

        Raises:
            NotImplementedError: This serializer is for validation only
        """
        raise NotImplementedError(
            "This serializer is for input validation only, not for updating objects"
        )
