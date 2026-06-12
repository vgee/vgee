"""
Utility modules for VGEE bot.

This package provides authentication, validation, configuration, and decoration utilities.

Modules:
    auth: Authentication and authorization decorators
    decorators: Common utility decorators (logging, singleton, retry, memoize)
    validation: Input, response, and result validation (consolidated from validators)
    config_manager: Environment-specific configuration management
    api_client: HTTP client with retry and validation

Public API:
    From auth:
        - AuthError
        - require_auth
        - require_permission
        - authenticate_user
        - grant_permission
        - revoke_permission
        - is_authenticated
        - check_permission
        - clear_auth_state
    
    From decorators:
        - log_function_call
        - singleton
        - retry
        - memoize
    
    From validation:
        - ValidationError
        - validate_token
        - validate_text
        - validate_chat_id
        - validate_response_format
        - validate_api_response
        - extract_message_id
        - extract_user_id
        - ResponseValidator
    
    From config_manager:
        - ConfigManager
        - ConfigProfile
        - DevConfig
        - StagingConfig
        - ProdConfig
    
    From api_client:
        - APIClient

Backward Compatibility:
    Old import paths still work but are deprecated:
    - from validators import validate_token  -> from validation import validate_token
    - from response_validators import validate_api_response  -> from validation import validate_api_response

Example:
    >>> from utils.auth import require_auth, authenticate_user
    >>> from utils.config_manager import ConfigManager
    >>> from utils.validation import validate_token
    >>> from utils.decorators import log_function_call
    >>> 
    >>> config = ConfigManager.create("dev")
    >>> authenticate_user("user_123")
    >>> 
    >>> @require_auth
    ... @log_function_call()
    ... def send_message(text: str) -> dict:
    ...     return {"status": "sent"}
"""

# Import public API
from utils.auth import (
    AuthError,
    require_auth,
    require_permission,
    authenticate_user,
    grant_permission,
    revoke_permission,
    is_authenticated,
    check_permission,
    clear_auth_state,
)

from utils.decorators import (
    log_function_call,
    singleton,
    retry,
    memoize,
)

try:
    from validation import (
        ValidationError,
        validate_token,
        validate_text,
        validate_chat_id_value,
        validate_timeout,
        validate_api_response,
        validate_message_result,
        validate_chat_result,
        validate_user_result,
        extract_result,
        extract_message_id,
        extract_chat_id,
        ResponseValidator,
    )
except ImportError:
    # Fallback for imports if modules aren't available
    ValidationError = None
    validate_token = None
    validate_text = None
    validate_chat_id_value = None
    validate_timeout = None
    validate_api_response = None
    validate_message_result = None
    validate_chat_result = None
    validate_user_result = None
    extract_result = None
    extract_message_id = None
    extract_chat_id = None
    ResponseValidator = None

try:
    from config_manager import (
        ConfigManager,
        ConfigProfile,
        DevConfig,
        StagingConfig,
        ProdConfig,
    )
except ImportError:
    ConfigManager = None
    ConfigProfile = None
    DevConfig = None
    StagingConfig = None
    ProdConfig = None

try:
    from api_client import APIClient
except ImportError:
    APIClient = None

__all__ = [
    # Auth
    "AuthError",
    "require_auth",
    "require_permission",
    "authenticate_user",
    "grant_permission",
    "revoke_permission",
    "is_authenticated",
    "check_permission",
    "clear_auth_state",
    # Decorators
    "log_function_call",
    "singleton",
    "retry",
    "memoize",
    # Validation
    "ValidationError",
    "validate_token",
    "validate_text",
    "validate_chat_id",
    "validate_response_format",
    "validate_api_response",
    "extract_message_id",
    "extract_user_id",
    "ResponseValidator",
    # Configuration
    "ConfigManager",
    "ConfigProfile",
    "DevConfig",
    "StagingConfig",
    "ProdConfig",
    # API Client
    "APIClient",
]
