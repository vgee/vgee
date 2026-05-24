"""
Response validation for Telegram API responses.

This module provides utilities for validating and parsing Telegram Bot API responses
to ensure data integrity and provide type safety.
"""
import logging
import typing
from typing import Any, Dict, Optional

from exceptions import APIError

logger = logging.getLogger(__name__)


def validate_api_response(data: Any) -> Dict[str, Any]:
    """Validate the basic structure of a Telegram API response.

    All Telegram API responses must be JSON objects with an "ok" field.
    If ok=true, the "result" field contains the actual data.
    If ok=false, "error_code" and "description" fields explain the error.

    Args:
        data: The parsed JSON response from Telegram API

    Returns:
        The validated data dictionary

    Raises:
        APIError: If response structure is invalid
        TypeError: If data is not a dictionary
    """
    if not isinstance(data, dict):
        raise APIError(
            "Invalid API response: expected JSON object",
            description=f"Got {type(data).__name__} instead"
        )

    if "ok" not in data:
        raise APIError(
            "Invalid API response: missing 'ok' field",
            description="Telegram API responses must contain 'ok' field"
        )

    if not isinstance(data["ok"], bool):
        raise APIError(
            "Invalid API response: 'ok' field must be boolean",
            description=f"Got {type(data['ok']).__name__} instead"
        )

    if not data["ok"]:
        error_code = data.get("error_code")
        description = data.get("description", "Unknown error")
        
        if not isinstance(error_code, int):
            logger.warning(f"API error_code is not int: {type(error_code).__name__}")
        
        if not isinstance(description, str):
            logger.warning(f"API description is not str: {type(description).__name__}")

        raise APIError(
            "Telegram API returned error",
            error_code=error_code,
            description=description
        )

    return data


def validate_message_result(result: Any) -> Dict[str, Any]:
    """Validate a Message object from sendMessage response.

    Args:
        result: The 'result' field from sendMessage response

    Returns:
        The validated message dictionary

    Raises:
        APIError: If message structure is invalid
    """
    if not isinstance(result, dict):
        raise APIError(
            "Invalid message result: expected object",
            description=f"Got {type(result).__name__} instead"
        )

    required_fields = {"message_id", "date"}
    missing_fields = required_fields - set(result.keys())
    if missing_fields:
        raise APIError(
            "Invalid message result: missing required fields",
            description=f"Missing: {', '.join(missing_fields)}"
        )

    if not isinstance(result.get("message_id"), int):
        raise APIError(
            "Invalid message result: message_id must be integer",
            description=f"Got {type(result.get('message_id')).__name__} instead"
        )

    if not isinstance(result.get("date"), int):
        raise APIError(
            "Invalid message result: date must be integer (Unix timestamp)",
            description=f"Got {type(result.get('date')).__name__} instead"
        )

    if result.get("message_id") <= 0:
        raise APIError(
            "Invalid message result: message_id must be positive",
            description=f"Got {result.get('message_id')} instead"
        )

    return result


def validate_chat_result(result: Any) -> Dict[str, Any]:
    """Validate a Chat object from getChat response.

    Args:
        result: The 'result' field from getChat response

    Returns:
        The validated chat dictionary

    Raises:
        APIError: If chat structure is invalid
    """
    if not isinstance(result, dict):
        raise APIError(
            "Invalid chat result: expected object",
            description=f"Got {type(result).__name__} instead"
        )

    required_fields = {"id", "type"}
    missing_fields = required_fields - set(result.keys())
    if missing_fields:
        raise APIError(
            "Invalid chat result: missing required fields",
            description=f"Missing: {', '.join(missing_fields)}"
        )

    if not isinstance(result.get("id"), int):
        raise APIError(
            "Invalid chat result: id must be integer",
            description=f"Got {type(result.get('id')).__name__} instead"
        )

    if not isinstance(result.get("type"), str):
        raise APIError(
            "Invalid chat result: type must be string",
            description=f"Got {type(result.get('type')).__name__} instead"
        )

    valid_types = {"private", "group", "supergroup", "channel"}
    if result.get("type") not in valid_types:
        raise APIError(
            "Invalid chat result: unknown chat type",
            description=f"Got '{result.get('type')}', expected one of: {', '.join(valid_types)}"
        )

    return result


def validate_user_result(result: Any) -> Dict[str, Any]:
    """Validate a User object from getChat response (when called with user_id).

    Args:
        result: The 'result' field from getChat response

    Returns:
        The validated user dictionary

    Raises:
        APIError: If user structure is invalid
    """
    if not isinstance(result, dict):
        raise APIError(
            "Invalid user result: expected object",
            description=f"Got {type(result).__name__} instead"
        )

    required_fields = {"id", "is_bot", "first_name"}
    missing_fields = required_fields - set(result.keys())
    if missing_fields:
        raise APIError(
            "Invalid user result: missing required fields",
            description=f"Missing: {', '.join(missing_fields)}"
        )

    if not isinstance(result.get("id"), int):
        raise APIError(
            "Invalid user result: id must be integer",
            description=f"Got {type(result.get('id')).__name__} instead"
        )

    if not isinstance(result.get("is_bot"), bool):
        raise APIError(
            "Invalid user result: is_bot must be boolean",
            description=f"Got {type(result.get('is_bot')).__name__} instead"
        )

    if not isinstance(result.get("first_name"), str):
        raise APIError(
            "Invalid user result: first_name must be string",
            description=f"Got {type(result.get('first_name')).__name__} instead"
        )

    if not result.get("first_name").strip():
        raise APIError(
            "Invalid user result: first_name cannot be empty",
            description="first_name must contain at least one non-whitespace character"
        )

    return result


def extract_result(data: Dict[str, Any]) -> Any:
    """Extract and validate the 'result' field from API response.

    Args:
        data: The validated API response dictionary

    Returns:
        The result field (can be any type depending on endpoint)

    Raises:
        APIError: If result field is missing or invalid
    """
    if "result" not in data:
        raise APIError(
            "Invalid API response: missing 'result' field",
            description="API response with ok=true must contain 'result' field"
        )

    return data["result"]


def extract_message_id(result: Dict[str, Any]) -> int:
    """Extract message_id from a message result.

    Args:
        result: A validated message dictionary

    Returns:
        The message_id

    Raises:
        APIError: If message_id is invalid
    """
    message_id = result.get("message_id")
    if not isinstance(message_id, int) or message_id <= 0:
        raise APIError(
            "Invalid message result: could not extract message_id",
            description=f"Got {message_id} of type {type(message_id).__name__}"
        )
    return message_id


def extract_chat_id(result: Dict[str, Any]) -> int:
    """Extract chat_id from a chat/user result.

    Args:
        result: A validated chat or user dictionary

    Returns:
        The chat/user id

    Raises:
        APIError: If chat id is invalid
    """
    chat_id = result.get("id")
    if not isinstance(chat_id, int):
        raise APIError(
            "Invalid result: could not extract id",
            description=f"Got {chat_id} of type {type(chat_id).__name__}"
        )
    return chat_id


class ResponseValidator:
    """Helper class for chaining validation operations."""

    @staticmethod
    def validate_send_message_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete sendMessage response."""
        validate_api_response(data)
        result = extract_result(data)
        return validate_message_result(result)

    @staticmethod
    def validate_get_chat_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete getChat response."""
        validate_api_response(data)
        result = extract_result(data)
        return validate_chat_result(result)

    @staticmethod
    def validate_get_user_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete getUser response (which uses getChat endpoint)."""
        validate_api_response(data)
        result = extract_result(data)
        # User response can be a chat with type='private' or a user object
        if "type" in result and result.get("type") == "private":
            return validate_chat_result(result)
        return validate_user_result(result)
