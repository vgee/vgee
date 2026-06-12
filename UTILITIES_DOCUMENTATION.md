# VGEE Utilities Documentation

Comprehensive documentation for the VGEE project's utility modules.

## Table of Contents

1. [Overview](#overview)
2. [Modules](#modules)
3. [Authentication & Authorization](#authentication--authorization)
4. [Decorators](#decorators)
5. [Validation](#validation)
6. [Configuration Management](#configuration-management)
7. [API Client](#api-client)
8. [Best Practices](#best-practices)
9. [Migration Guide](#migration-guide)

## Overview

The `utils` package provides reusable utilities for the VGEE Telegram bot project:

- **Authentication/Authorization**: User authentication and permission management
- **Decorators**: Logging, singleton, retry, and memoization patterns
- **Validation**: Input validation, response validation, and data extraction
- **Configuration**: Environment-specific configuration with profiles
- **API Client**: HTTP client with automatic retries and response validation

### Quick Start

```python
from utils import (
    authenticate_user, require_auth,
    validate_token, validate_text,
    ConfigManager, APIClient,
    log_function_call, singleton
)

# Configure application
config = ConfigManager.create("dev")

# Authenticate user
authenticate_user("user_123")

# Use protected function
@require_auth
def send_message(text: str):
    validate_text(text)
    # ... send message logic

# Use decorators
@log_function_call()
@singleton
class DatabaseConnection:
    def __init__(self):
        self.connected = True
```

## Modules

### Module Structure

```
utils/
├── __init__.py          # Public API exports
├── auth.py              # Authentication & authorization
├── decorators.py        # Utility decorators
└── (validation.py)      # Imported from root level
```

**Root-Level Modules** (imported by utils package):

```
vgee/
├── validation.py        # Input & response validation
├── config_manager.py    # Configuration management
├── api_client.py        # HTTP client
├── validators.py        # Backward compatibility shim (DEPRECATED)
└── response_validators.py # Backward compatibility shim (DEPRECATED)
```

### Importing

**Recommended import style:**

```python
from utils import (
    # Auth
    authenticate_user,
    require_auth,
    require_permission,
    grant_permission,
    revoke_permission,
    is_authenticated,
    check_permission,
    clear_auth_state,
    # Decorators
    log_function_call,
    singleton,
    retry,
    memoize,
)

# Root-level modules (when needed)
from validation import validate_token, validate_text, ResponseValidator
from config_manager import ConfigManager
from api_client import APIClient
```

**Legacy imports (deprecated):**

```python
# ❌ Avoid these - they log deprecation warnings
from validators import validate_token
from response_validators import validate_api_response
```

---

## Authentication & Authorization

Module: `utils/auth.py`

Provides user authentication and permission management with decorators.

### Classes

#### `AuthError`

Exception for authentication/authorization failures.

```python
class AuthError(Exception):
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        permission: Optional[str] = None
    ) -> None:
        ...
```

**Attributes:**
- `message` (str): Error message
- `user_id` (str): User ID involved in error (optional)
- `permission` (str): Required permission (optional)

**Example:**

```python
from utils.auth import AuthError

try:
    some_protected_operation()
except AuthError as e:
    print(f"Auth error: {e.message}")
    if e.user_id:
        print(f"User: {e.user_id}")
    if e.permission:
        print(f"Required permission: {e.permission}")
```

### Functions

#### `authenticate_user(user_id: str) -> None`

Register a user as authenticated.

**Parameters:**
- `user_id` (str): The user ID to authenticate

**Raises:**
- `ValueError`: If user_id is empty

**Example:**

```python
from utils.auth import authenticate_user

authenticate_user("user_123")
authenticate_user("telegram_user_456")
```

#### `is_authenticated() -> bool`

Check if the current user (from `USER_ID` environment variable) is authenticated.

**Returns:**
- `bool`: True if authenticated, False otherwise

**Example:**

```python
from utils.auth import is_authenticated
import os

os.environ["USER_ID"] = "user_123"
if is_authenticated():
    print("User is authenticated")
else:
    print("User is not authenticated")
```

#### `grant_permission(user_id: str, permission: str) -> None`

Grant a specific permission to a user.

**Parameters:**
- `user_id` (str): The user ID to grant permission to
- `permission` (str): The permission name to grant

**Raises:**
- `ValueError`: If user_id or permission is empty

**Example:**

```python
from utils.auth import grant_permission

grant_permission("user_123", "send_messages")
grant_permission("user_123", "admin")
grant_permission("user_123", "delete_messages")
```

#### `check_permission(user_id: str, permission: str) -> bool`

Check if a user has a specific permission.

**Parameters:**
- `user_id` (str): The user ID to check
- `permission` (str): The permission to verify

**Returns:**
- `bool`: True if user has permission, False otherwise

**Raises:**
- `ValueError`: If user_id or permission is empty

**Example:**

```python
from utils.auth import check_permission

if check_permission("user_123", "send_messages"):
    print("User can send messages")

if check_permission("user_123", "admin"):
    print("User is admin")
```

#### `revoke_permission(user_id: str, permission: str) -> None`

Revoke a specific permission from a user.

**Parameters:**
- `user_id` (str): The user ID to revoke permission from
- `permission` (str): The permission to revoke

**Raises:**
- `ValueError`: If user_id or permission is empty

**Example:**

```python
from utils.auth import revoke_permission

revoke_permission("user_123", "admin")
```

#### `clear_auth_state() -> None`

Clear all authentication state (useful for testing).

**Warning:** Removes all authenticated users and permissions.

**Example:**

```python
from utils.auth import clear_auth_state

# In test teardown
clear_auth_state()
```

### Decorators

#### `@require_auth`

Decorator to require authentication before function execution.

Checks if the current user (from `USER_ID` env var) is authenticated.

**Raises:**
- `AuthError`: If user is not authenticated

**Example:**

```python
from utils.auth import require_auth, authenticate_user
import os

@require_auth
def send_message(text: str) -> None:
    print(f"Sending: {text}")

# Setup
os.environ["USER_ID"] = "user_123"
authenticate_user("user_123")

# Works
send_message("Hello!")

# Fails if user not authenticated
os.environ["USER_ID"] = "user_456"
send_message("Goodbye")  # Raises AuthError
```

#### `@require_permission(permission: str)`

Decorator to require a specific permission before function execution.

**Parameters:**
- `permission` (str): The required permission name

**Raises:**
- `AuthError`: If user lacks required permission

**Example:**

```python
from utils.auth import (
    require_permission,
    authenticate_user,
    grant_permission
)
import os

@require_permission("admin")
def delete_user(user_id: str) -> None:
    print(f"Deleting user {user_id}")

# Setup
os.environ["USER_ID"] = "admin_user"
authenticate_user("admin_user")
grant_permission("admin_user", "admin")

# Works
delete_user("user_123")

# Fails without permission
os.environ["USER_ID"] = "regular_user"
authenticate_user("regular_user")
delete_user("user_456")  # Raises AuthError
```

---

## Decorators

Module: `utils/decorators.py`

Provides common utility decorators for logging, singleton pattern, retry logic, and memoization.

### Decorators

#### `@log_function_call(log_args: bool = False, log_result: bool = True)`

Decorator to log function calls, arguments, and return values.

**Parameters:**
- `log_args` (bool): Whether to log argument counts (default False)
- `log_result` (bool): Whether to log result type (default True)

**Example:**

```python
from utils.decorators import log_function_call
import logging

logging.basicConfig(level=logging.INFO)

@log_function_call()
def process_data(data: dict) -> str:
    return "processed"

process_data({"key": "value"})
# Logs: "Calling process_data"
# Logs: "process_data returned str"

@log_function_call(log_args=True)
def expensive_operation(x: int, y: int) -> int:
    return x + y

expensive_operation(5, 10)
# Logs: "Calling expensive_operation with 2 args, 0 kwargs"
# Logs: "expensive_operation returned int"
```

#### `@singleton`

Decorator to ensure only one instance of a class exists.

**Example:**

```python
from utils.decorators import singleton

@singleton
class DatabaseConnection:
    def __init__(self, host: str):
        self.host = host

# First call creates instance
db1 = DatabaseConnection("localhost")

# Second call returns same instance
db2 = DatabaseConnection("otherhost")

assert db1 is db2  # Same object
assert db1.host == "localhost"  # Original init preserved
```

#### `@retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,))`

Decorator to retry a function with exponential backoff.

**Parameters:**
- `max_attempts` (int): Maximum retry attempts (default 3)
- `delay` (float): Initial delay in seconds (default 1.0)
- `backoff` (float): Multiplier for delay after each attempt (default 2.0)
- `exceptions` (tuple): Exception types to catch (default all)

**Example:**

```python
from utils.decorators import retry
import random

@retry(max_attempts=3, delay=0.5)
def flaky_operation():
    if random.random() < 0.5:
        raise ConnectionError("Network error")
    return "success"

# Retries up to 3 times with exponential backoff
result = flaky_operation()

# Catch specific exceptions
@retry(max_attempts=2, exceptions=(ConnectionError, TimeoutError))
def api_call():
    return "data"
```

#### `@memoize`

Decorator to cache function results (memoization).

Works with hashable arguments only. Adds `clear_cache()` method.

**Example:**

```python
from utils.decorators import memoize

call_count = 0

@memoize
def fibonacci(n: int) -> int:
    global call_count
    call_count += 1
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# First call
result = fibonacci(10)  # call_count = 20+

# Subsequent call with same args uses cache
result = fibonacci(10)  # call_count unchanged

# Clear cache
fibonacci.clear_cache()
result = fibonacci(10)  # call_count increases again
```

---

## Validation

Module: `validation.py` (root level, imported by utils package)

Comprehensive validation for input parameters, API responses, and data extraction.

### Input Validators

Validate user input before processing.

#### `validate_token(token: Optional[str]) -> None`

Validate bot API token format and length.

**Parameters:**
- `token` (str): The bot token to validate

**Raises:**
- `ValidationError`: If token is invalid

**Example:**

```python
from validation import validate_token, ValidationError

try:
    validate_token("123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    print("Token is valid")
except ValidationError as e:
    print(f"Token error: {e}")
```

#### `validate_text(text: str) -> None`

Validate message text content and length.

**Parameters:**
- `text` (str): The message text to validate

**Raises:**
- `ValidationError`: If text is invalid (empty, whitespace-only, or too long)

**Constraints:**
- Must not be empty
- Must not be only whitespace
- Maximum length: 4096 characters

**Example:**

```python
from validation import validate_text

validate_text("Hello, world!")  # OK
validate_text("")  # Raises ValidationError
validate_text("   ")  # Raises ValidationError (whitespace-only)
validate_text("x" * 5000)  # Raises ValidationError (too long)
```

#### `validate_chat_id_value(chat_id: int) -> None`

Validate chat ID is a valid integer within acceptable range.

**Parameters:**
- `chat_id` (int): The chat ID to validate

**Raises:**
- `ValidationError`: If chat_id is invalid

**Notes:**
- Telegram chat IDs can be negative (for groups/channels)
- Must be non-zero

**Example:**

```python
from validation import validate_chat_id_value

validate_chat_id_value(123456789)  # User chat
validate_chat_id_value(-1001234567890)  # Group/channel (negative)
validate_chat_id_value(0)  # Raises ValidationError
validate_chat_id_value(-999999999999999)  # Raises ValidationError (too large)
```

#### `validate_timeout(timeout: float) -> None`

Validate timeout is a positive number within limits.

**Parameters:**
- `timeout` (float): The timeout value in seconds

**Raises:**
- `ValidationError`: If timeout is invalid

**Constraints:**
- Must be positive (> 0)
- Maximum: 300 seconds

**Example:**

```python
from validation import validate_timeout

validate_timeout(10.0)  # OK
validate_timeout(0)  # Raises ValidationError
validate_timeout(-1)  # Raises ValidationError
validate_timeout(301)  # Raises ValidationError
```

### Response Validators

Validate Telegram API responses.

#### `validate_api_response(data: Any) -> Dict[str, Any]`

Validate basic structure of a Telegram API response.

All Telegram API responses must be JSON objects with an "ok" field:
- If `ok=true`: "result" field contains the actual data
- If `ok=false`: "error_code" and "description" explain the error

**Parameters:**
- `data` (dict): The parsed JSON response from Telegram API

**Returns:**
- `dict`: The full response object if valid

**Raises:**
- `APIError`: If response structure is invalid

**Example:**

```python
from validation import validate_api_response

response = {
    "ok": True,
    "result": {"message_id": 123, "text": "Hello"}
}
validate_api_response(response)  # OK

# Error response
error_response = {
    "ok": False,
    "error_code": 400,
    "description": "Bad Request"
}
validate_api_response(error_response)  # OK (valid structure)
```

#### `validate_message_result(result: Any) -> Dict[str, Any]`

Validate message result structure from Telegram API.

**Example:**

```python
from validation import validate_message_result

result = {
    "message_id": 123,
    "date": 1234567890,
    "text": "Hello"
}
validate_message_result(result)  # OK
```

#### `validate_chat_result(result: Any) -> Dict[str, Any]`

Validate chat result structure from Telegram API.

**Example:**

```python
from validation import validate_chat_result

result = {
    "id": 123456789,
    "type": "private",
    "username": "john_doe"
}
validate_chat_result(result)  # OK
```

#### `validate_user_result(result: Any) -> Dict[str, Any]`

Validate user result structure from Telegram API.

**Example:**

```python
from validation import validate_user_result

result = {
    "id": 123456789,
    "is_bot": False,
    "first_name": "John"
}
validate_user_result(result)  # OK
```

### Result Extractors

Safely extract data from API responses.

#### `extract_result(data: Dict[str, Any]) -> Any`

Extract the "result" field from an API response.

**Parameters:**
- `data` (dict): The API response

**Returns:**
- Any: The result field value

**Raises:**
- `APIError`: If "result" field is missing

**Example:**

```python
from validation import extract_result

response = {
    "ok": True,
    "result": {"message_id": 123}
}
result = extract_result(response)
# result = {"message_id": 123}
```

#### `extract_message_id(result: Dict[str, Any]) -> int`

Extract message ID from a message result.

**Parameters:**
- `result` (dict): The message result

**Returns:**
- int: The message ID

**Raises:**
- `APIError`: If message_id is missing

**Example:**

```python
from validation import extract_message_id

result = {"message_id": 42, "text": "Hello"}
msg_id = extract_message_id(result)
# msg_id = 42
```

#### `extract_chat_id(result: Dict[str, Any]) -> int`

Extract chat ID from a chat result.

**Parameters:**
- `result` (dict): The chat result

**Returns:**
- int: The chat ID

**Raises:**
- `APIError`: If chat id is missing

**Example:**

```python
from validation import extract_chat_id

result = {"id": 123456789, "type": "private"}
chat_id = extract_chat_id(result)
# chat_id = 123456789
```

### ResponseValidator Helper Class

Convenient class for chaining multiple validations.

**Methods:**

- `validate_send_message_response(response)`: Validate sendMessage response
- `validate_get_chat_response(response)`: Validate getChat response
- `validate_get_user_response(response)`: Validate getUser response
- And more...

**Example:**

```python
from validation import ResponseValidator

response = {
    "ok": True,
    "result": {"message_id": 123}
}

# Chain validations
result = ResponseValidator.validate_send_message_response(response)
# result contains the message data, fully validated
```

---

## Configuration Management

Module: `config_manager.py` (root level, imported by utils package)

Environment-specific configuration with dev/staging/production profiles.

### ConfigManager Factory

#### `ConfigManager.create(environment: str) -> ConfigProfile`

Factory function to create configuration for a specific environment.

**Parameters:**
- `environment` (str): One of "dev", "staging", "prod"

**Returns:**
- `ConfigProfile`: Configuration object for the environment

**Raises:**
- `ValueError`: If environment is unknown

**Example:**

```python
from config_manager import ConfigManager

# Create configuration
config = ConfigManager.create("dev")
config = ConfigManager.create("staging")
config = ConfigManager.create("prod")
```

### Configuration Profiles

Configuration classes with environment-specific defaults.

#### `DevConfig`

Development environment configuration.

**Default Settings:**
- Debug mode: ON
- Timeout: 5 seconds
- Retry attempts: 3
- Log level: DEBUG

**Example:**

```python
from config_manager import DevConfig

config = DevConfig()
print(config.debug)  # True
print(config.timeout)  # 5.0
print(config.max_retries)  # 3
```

#### `StagingConfig`

Staging environment configuration.

**Default Settings:**
- Debug mode: OFF
- Timeout: 10 seconds
- Retry attempts: 5
- Log level: INFO

**Example:**

```python
from config_manager import StagingConfig

config = StagingConfig()
print(config.debug)  # False
print(config.timeout)  # 10.0
```

#### `ProdConfig`

Production environment configuration.

**Default Settings:**
- Debug mode: OFF
- Timeout: 30 seconds
- Retry attempts: 3
- Log level: WARNING

**Example:**

```python
from config_manager import ProdConfig

config = ProdConfig()
print(config.debug)  # False
print(config.timeout)  # 30.0
```

### Environment Variables

Configuration can be overridden by environment variables.

**Priority Order (lowest to highest):**
1. Profile class defaults
2. .env.{environment} file (non-empty values only)
3. Environment variables

**Example:**

```bash
# .env.dev file
BOT_TOKEN=
DEBUG=false
TIMEOUT=15

# Environment variable
export BOT_TOKEN="123456:ABC-DEF..."
export DEBUG=true

# Result: BOT_TOKEN from env var, TIMEOUT=15 from .env, DEBUG=true from env var
```

### Configuration Files

Create `.env.dev`, `.env.staging`, `.env.prod` files:

```bash
# .env.dev
BOT_TOKEN=
DEBUG=true
TIMEOUT=5
MAX_RETRIES=3
LOG_LEVEL=DEBUG

# .env.staging
BOT_TOKEN=
DEBUG=false
TIMEOUT=10
MAX_RETRIES=5
LOG_LEVEL=INFO

# .env.prod
BOT_TOKEN=
DEBUG=false
TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=WARNING
```

---

## API Client

Module: `api_client.py` (root level, imported by utils package)

HTTP client with automatic retries and response validation.

### APIClient Class

#### `APIClient(base_url: str, token: str, timeout: float = 10.0, max_retries: int = 3)`

Initialize API client.

**Parameters:**
- `base_url` (str): Base URL for API endpoints
- `token` (str): Authentication token
- `timeout` (float): Request timeout in seconds (default 10)
- `max_retries` (int): Maximum retry attempts (default 3)

**Example:**

```python
from api_client import APIClient

client = APIClient(
    base_url="https://api.telegram.org",
    token="123456:ABC-DEF...",
    timeout=5,
    max_retries=3
)
```

### Methods

#### `post(endpoint: str, data: Dict) -> Dict`

Make POST request to API endpoint.

**Parameters:**
- `endpoint` (str): API endpoint (e.g., "bot{token}/sendMessage")
- `data` (dict): Request body

**Returns:**
- `dict`: Validated response

**Raises:**
- `ValidationError`: If response validation fails
- `APIError`: If API request fails

**Example:**

```python
from api_client import APIClient

client = APIClient("https://api.telegram.org", token)

response = client.post(
    f"bot{token}/sendMessage",
    {"chat_id": 123, "text": "Hello"}
)
```

#### `get(endpoint: str, params: Dict) -> Dict`

Make GET request to API endpoint.

**Parameters:**
- `endpoint` (str): API endpoint
- `params` (dict): Query parameters

**Returns:**
- `dict`: Validated response

**Raises:**
- `ValidationError`: If response validation fails
- `APIError`: If API request fails

**Example:**

```python
response = client.get(
    f"bot{token}/getChat",
    {"chat_id": 123}
)
```

---

## Best Practices

### 1. Authentication

Always authenticate users before allowing operations:

```python
from utils.auth import authenticate_user, require_auth
import os

@require_auth
def protected_operation():
    user_id = os.getenv("USER_ID")
    # ... perform operation for user

# Authenticate on login
authenticate_user("user_123")
```

### 2. Permissions

Use role-based access control:

```python
from utils.auth import require_permission, grant_permission

@require_permission("admin")
def delete_user(user_id):
    # ... delete user

# Grant permissions based on roles
grant_permission("user_123", "admin")
grant_permission("user_456", "view_reports")
```

### 3. Input Validation

Always validate user input:

```python
from validation import validate_text, validate_chat_id_value

def send_message(chat_id: int, text: str):
    validate_chat_id_value(chat_id)
    validate_text(text)
    # ... send message
```

### 4. Configuration Management

Use ConfigManager for environment-specific settings:

```python
from config_manager import ConfigManager
import os

env = os.getenv("ENVIRONMENT", "dev")
config = ConfigManager.create(env)

# Use config settings
if config.debug:
    print("Debug mode enabled")
```

### 5. Logging

Use decorators for automatic logging:

```python
from utils.decorators import log_function_call

@log_function_call(log_args=True)
def process_request(request_id, data):
    # ... process request
    return result
```

### 6. Caching

Use memoize for expensive operations:

```python
from utils.decorators import memoize

@memoize
def get_user_profile(user_id):
    # ... fetch from database
    return profile

# First call fetches from DB
profile1 = get_user_profile(123)

# Second call uses cache
profile2 = get_user_profile(123)

# Clear cache if needed
get_user_profile.clear_cache()
```

### 7. Retries

Use retry decorator for unreliable operations:

```python
from utils.decorators import retry

@retry(max_attempts=3, delay=1, backoff=2)
def call_external_api():
    # ... API call
    return data
```

### 8. Singletons

Use singleton for shared resources:

```python
from utils.decorators import singleton

@singleton
class DatabasePool:
    def __init__(self, connection_string):
        self.connect(connection_string)
    
    def connect(self, conn_str):
        # ... establish connection
        pass

# All references point to same instance
db1 = DatabasePool("postgres://...")
db2 = DatabasePool("mysql://...")
assert db1 is db2
```

---

## Migration Guide

### From Old Validators Module

**Before (deprecated):**

```python
from validators import validate_token, validate_text
from response_validators import validate_api_response
```

**After (recommended):**

```python
from validation import validate_token, validate_text, validate_api_response
```

Both work identically, but the new imports are cleaner and don't trigger deprecation warnings.

### From Old Auth Module

If you were managing auth manually:

**Before:**

```python
import os

if user_id in authenticated_users:
    # Allow operation
    pass
```

**After:**

```python
from utils.auth import authenticate_user, is_authenticated
import os

# Authenticate on login
authenticate_user(user_id)

# Check authentication
os.environ["USER_ID"] = user_id
if is_authenticated():
    # Allow operation
    pass
```

### From Manual Config Management

**Before:**

```python
import os

debug = os.getenv("DEBUG", "false") == "true"
timeout = float(os.getenv("TIMEOUT", "10"))
```

**After:**

```python
from config_manager import ConfigManager

config = ConfigManager.create("dev")
debug = config.debug
timeout = config.timeout
```

---

## Testing

All utilities include comprehensive test coverage:

```bash
# Run utilities tests
pytest tests/test_utils.py -v

# Run specific test class
pytest tests/test_utils.py::TestAuthentication -v

# Run with coverage
pytest tests/test_utils.py --cov=utils --cov-report=html
```

**Test Statistics:**
- 41 tests total
- Coverage: Auth, Decorators, Validation modules
- All tests passing ✅

---

## Contributing

When adding new utilities:

1. Add implementation to appropriate module (auth, decorators, etc.)
2. Add comprehensive docstrings with examples
3. Write unit tests in `tests/test_utils.py`
4. Update this documentation
5. Ensure all tests pass: `pytest tests/test_utils.py`

---

## Changelog

### Version 1.0 (Current)

- ✅ Consolidated validation modules
- ✅ Enhanced auth module with decorators and logging
- ✅ Improved decorators with retry and memoize
- ✅ Created utils package with public API
- ✅ Comprehensive test coverage (41 tests)
- ✅ Full documentation with examples

### Deprecated

- `validators.py` - Use `validation` module instead
- `response_validators.py` - Use `validation` module instead
