"""
Backward compatibility module for response validation.

DEPRECATED: This module is maintained for backward compatibility only.
Please import from validation module instead:

    from validation import (
        validate_api_response,
        validate_message_result,
        validate_chat_result,
        validate_user_result,
        extract_result,
        extract_message_id,
        extract_chat_id,
        ResponseValidator,
    )

This module will be removed in a future version.
"""
import logging

from validation import (
    validate_api_response,
    validate_message_result,
    validate_chat_result,
    validate_user_result,
    extract_result,
    extract_message_id,
    extract_chat_id,
    ResponseValidator,
)

logger = logging.getLogger(__name__)

# Log deprecation warning on import
logger.warning(
    "response_validators module is deprecated and maintained for backward compatibility only. "
    "Please import from validation module instead."
)

# Re-export for backward compatibility
__all__ = [
    "validate_api_response",
    "validate_message_result",
    "validate_chat_result",
    "validate_user_result",
    "extract_result",
    "extract_message_id",
    "extract_chat_id",
    "ResponseValidator",
]
