"""
Backward compatibility module for input validation.

DEPRECATED: This module is maintained for backward compatibility only.
Please import from validation module instead:

    from validation import validate_token, validate_text, validate_chat_id_value, validate_timeout

This module will be removed in a future version.
"""
import logging

from validation import (
    validate_token,
    validate_text,
    validate_chat_id_value,
    validate_timeout,
)

logger = logging.getLogger(__name__)

# Log deprecation warning on import
logger.warning(
    "validators module is deprecated and maintained for backward compatibility only. "
    "Please import from validation module instead."
)

# Re-export for backward compatibility
__all__ = [
    "validate_token",
    "validate_text",
    "validate_chat_id_value",
    "validate_timeout",
]
