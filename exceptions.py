"""
Custom exceptions for the Telegram Bot module.

This module defines the exception hierarchy for the bot application,
providing specific exception types for different error scenarios.
"""
import typing


class BotError(Exception):
    """Base exception for all bot-related errors."""

    pass


class ValidationError(BotError):
    """Raised when input validation fails.

    This exception is raised when bot parameters (token, chat_id, text, timeout)
    fail validation checks.

    Attributes:
        message (str): Description of the validation error
        field (str): Name of the field that failed validation
    """

    def __init__(self, message: str, field: typing.Optional[str] = None) -> None:
        """Initialize ValidationError.

        Args:
            message: Description of the validation error
            field: Name of the field that failed validation
        """
        self.message = message
        self.field = field
        super().__init__(message)


class APIError(BotError):
    """Raised when Telegram API returns an error.

    This exception is raised when the Telegram Bot API returns an error response
    (ok=False).

    Attributes:
        message (str): Error message from API
        error_code (int): Error code from API (if available)
        description (str): Detailed error description from API
    """

    def __init__(
        self,
        message: str,
        error_code: typing.Optional[int] = None,
        description: typing.Optional[str] = None,
    ) -> None:
        """Initialize APIError.

        Args:
            message: Error message
            error_code: Telegram API error code
            description: Detailed error description from API
        """
        self.message = message
        self.error_code = error_code
        self.description = description
        full_message = f"{message}"
        if error_code:
            full_message += f" (error_code: {error_code})"
        if description:
            full_message += f" - {description}"
        super().__init__(full_message)


class NetworkError(BotError):
    """Raised when network communication fails.

    This exception is raised when HTTP requests to the Telegram API fail due to
    network issues (connection errors, timeouts, etc.).

    Attributes:
        message (str): Description of the network error
        original_error (Exception): The original requests exception
    """

    def __init__(
        self, message: str, original_error: typing.Optional[Exception] = None
    ) -> None:
        """Initialize NetworkError.

        Args:
            message: Description of the network error
            original_error: The original requests.RequestException
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)
