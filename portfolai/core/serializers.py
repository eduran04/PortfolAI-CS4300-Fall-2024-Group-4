"""
Serializers for API input validation and sanitization.

Provides proper validation and sanitization for user inputs
to prevent malicious payloads and ensure data integrity.
"""
import re

from rest_framework import serializers


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

    def validate_symbol(self, value):
        """
        Validate and sanitize the symbol input.

        Args:
            value: The raw symbol input

        Returns:
            str: Sanitized and validated symbol (uppercase, stripped)

        Raises:
            serializers.ValidationError: If symbol format is invalid
        """
        if not value:
            raise serializers.ValidationError("Symbol cannot be empty")

        # Strip whitespace and convert to uppercase
        symbol = value.strip().upper()

        # Validate symbol contains only alphanumeric characters and dots
        # (some exchanges use dots, e.g., BRK.A, BRK.B)
        if not re.match(r'^[A-Z0-9.]+$', symbol):
            raise serializers.ValidationError(
                "Symbol must contain only letters, numbers, and dots"
            )

        # Additional security: prevent potential injection patterns
        # Reject symbols that look suspicious (e.g., containing SQL keywords)
        suspicious_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
            r'[<>"\';\\]',  # Prevent HTML/script injection characters
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, symbol, re.IGNORECASE):
                raise serializers.ValidationError(
                    "Symbol contains invalid characters"
                )

        # Validate reasonable length (most stock symbols are 1-5 chars,
        # but some can be longer, so we allow up to 10)
        if len(symbol) > 10:
            raise serializers.ValidationError(
                "Symbol must be 10 characters or less"
            )

        return symbol

    def create(self, validated_data):
        """
        Not implemented - this serializer is for validation only.

        Raises:
            NotImplementedError: This serializer is for validation only
        """
        raise NotImplementedError(
            "This serializer is for input validation only, not for creating objects"
        )

    def update(self, instance, validated_data):
        """
        Not implemented - this serializer is for validation only.

        Raises:
            NotImplementedError: This serializer is for validation only
        """
        raise NotImplementedError(
            "This serializer is for input validation only, not for updating objects"
        )
