"""
Input validation functions for the Telegram Bot module.

This module provides comprehensive validation for all bot parameters
including tokens, message text, chat IDs, and timeouts.
"""
import typing

from exceptions import ValidationError


def validate_token(token: typing.Optional[str]) -> None:
    """Validates that token is not empty and has reasonable length.

    Args:
        token: The bot token to validate

    Raises:
        ValidationError: If token is invalid
    """
    if not token:
        raise ValidationError("Token cannot be empty", field="token")
    token_str = str(token).strip()
    if len(token_str) < 10:
        raise ValidationError(
            "Token appears too short (minimum 10 characters)", field="token"
        )
    if not token_str.isascii():
        raise ValidationError(
            "Token must contain only ASCII characters", field="token"
        )


def validate_text(text: str) -> None:
    """Validates that message text is not empty and within limits.

    Args:
        text: The message text to validate

    Raises:
        ValidationError: If text is invalid
    """
    if not text:
        raise ValidationError("Message text cannot be empty", field="text")
    if len(text) > 4096:
        raise ValidationError(
            "Message text exceeds maximum length of 4096 characters", field="text"
        )
    if text.isspace():
        raise ValidationError(
            "Message text cannot be only whitespace", field="text"
        )


def validate_chat_id_value(chat_id: int) -> None:
    """Validates that chat_id is a valid integer.

    Args:
        chat_id: The chat ID to validate

    Raises:
        ValidationError: If chat_id is invalid
    """
    if not isinstance(chat_id, int):
        raise ValidationError("Chat ID must be an integer", field="chat_id")
    if chat_id == 0:
        raise ValidationError("Chat ID cannot be zero", field="chat_id")
    # Telegram chat IDs can be negative (for groups/channels)
    if abs(chat_id) > 999999999999:
        raise ValidationError(
            "Chat ID appears invalid (out of range)", field="chat_id"
        )


def validate_timeout(timeout: float) -> None:
    """Validates that timeout is a positive number.

    Args:
        timeout: The timeout value to validate

    Raises:
        ValidationError: If timeout is invalid
    """
    if not isinstance(timeout, (int, float)):
        raise ValidationError("Timeout must be a number", field="timeout")
    if timeout <= 0:
        raise ValidationError("Timeout must be positive", field="timeout")
    if timeout > 300:
        raise ValidationError(
            "Timeout exceeds maximum of 300 seconds", field="timeout"
        )
