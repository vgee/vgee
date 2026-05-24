# VGEE Project

VGEE (Very Good Example Environment) is a sample project to demonstrate various coding practices and testing strategies. It includes a Telegram bot HTTP client with comprehensive input validation, error handling, automatic retry logic, response validation, and testing.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Core Methods](#core-methods)
  - [Input Validation](#input-validation)
  - [Response Validation](#response-validation)
  - [Retry Logic](#retry-logic)
  - [UI/Console Modes](#uiconsole-modes)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Configuration](#configuration)
- [Contacts](#contacts)

## Features

- **Telegram Bot Client** - HTTP-based client for sending messages and retrieving chat/user information
- **Input Validation** - Comprehensive validation for tokens, chat IDs, messages, and timeouts
- **Response Validation** - Validates Telegram API responses for data integrity and type safety
- **Automatic Retry Logic** - Exponential backoff retry mechanism for resilient API calls
- **Multiple Interfaces** - Console and GUI (tkinter) modes for interacting with the bot
- **Context Manager Support** - Proper resource management with context managers
- **Extensive Testing** - 65+ unit tests covering core functionality and edge cases
- **Type Hints** - Full type annotations for better IDE support and code clarity
- **Logging** - Detailed logging for debugging and monitoring


## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/vgee.git
cd vgee
```

1. Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Quick Start

### Basic Usage (Python)

```python
from huu import Bot

# Create a bot instance
bot = Bot(token="YOUR_BOT_TOKEN", default=123456789)

# Send a message
bot.send_message(chat_id=123456789, text="Hello, world!")

# Get chat information
chat_info = bot.get_chat(123456789)
print(chat_info)

# Close the session
bot.close()
```

### Using Context Manager

```python
from huu import Bot

with Bot(token="YOUR_BOT_TOKEN") as bot:
    bot.send_message(chat_id=123456789, text="Hello!")
    # Session is automatically closed when exiting the context
```

## Usage

### Core Methods

#### `send_message(chat_id, text, *, timeout=10.0)`

Sends a message to a Telegram chat.

**Parameters:**

- `chat_id` (int or str, optional): The target chat ID. If not provided, uses `Bot.default`
- `text` (str): The message text (max 4096 characters)
- `timeout` (float): Request timeout in seconds (default: 10.0, max: 300)

**Example:**

```python
bot.send_message(123456789, "Hello, Telegram!")
```

#### `get_chat(chat_id, *, timeout=10.0)`

Retrieves information about a chat.

**Parameters:**

- `chat_id` (int or str, optional): The target chat ID. If not provided, uses `Bot.default`
- `timeout` (float): Request timeout in seconds

**Returns:** Dictionary with chat information (id, type, title, first_name, username, etc.)

**Example:**

```python
chat_info = bot.get_chat(123456789)
print(chat_info["first_name"])  # Get user's first name
```

#### `get_user(user_id, *, timeout=10.0)`

Retrieves information about a user (for private chats).

**Parameters:**

- `user_id` (int or str): The user ID
- `timeout` (float): Request timeout in seconds

**Returns:** Dictionary with user information

**Example:**

```python
user_info = bot.get_user(987654321)
print(user_info["is_bot"])  # Check if it's a bot
```

### Input Validation

All methods include comprehensive input validation:

**Token Validation:**

- Must not be empty
- Must be at least 10 characters
- Must contain only ASCII characters

**Message Text Validation:**

- Must not be empty
- Must not exceed 4096 characters (Telegram limit)
- Cannot be whitespace-only

**Chat ID Validation:**

- Must be an integer
- Cannot be zero
- Must be within valid range (supports negative IDs for groups/channels)

**Timeout Validation:**

- Must be a positive number
- Cannot exceed 300 seconds

**Invalid Input Example:**

```python
# These will raise ValueError with descriptive messages
bot.send_message(0, "test")              # Chat ID cannot be zero
bot.send_message(123, "")                # Message cannot be empty
bot.send_message(123, "x" * 5000)        # Message too long
bot.send_message(123, "test", timeout=500) # Timeout too large
```

### Response Validation

All responses from the Telegram API are automatically validated to ensure data integrity and type safety:

**Automatic Validation Includes:**

- **Basic Response Structure** - All responses must have an "ok" boolean field
- **Error Responses** - Validates error_code and description fields when ok=false
- **Message Results** - Validates message_id (positive integer) and date (Unix timestamp)
- **Chat Results** - Validates id, type (private/group/supergroup/channel), and required fields
- **User Results** - Validates id, is_bot (boolean), and first_name (non-empty string)

**Validation Examples:**

```python
# Invalid response structures are caught automatically
try:
    bot.send_message(123, "Hello")
except APIError as e:
    # Catches malformed responses, missing fields, type mismatches, etc.
    print(f"Response validation failed: {e.description}")
```

**Custom Validation Usage:**

```python
from response_validators import ResponseValidator

# Manually validate API responses if needed
response_data = {"ok": True, "result": {...}}
validated = ResponseValidator.validate_send_message_response(response_data)

# Or validate individual parts
from response_validators import validate_chat_result
chat_info = validate_chat_result(result_dict)
```

### Retry Logic

The bot includes automatic retry logic with exponential backoff to handle transient network issues:

**Default Retry Behavior:**

- Maximum 3 retry attempts
- Initial delay: 0.5 seconds
- Exponential backoff multiplier: 2.0x
- Automatic retry on: timeouts, connection errors, and HTTP 429/5xx errors

**Retryable Errors:**

- `requests.exceptions.Timeout` - Connection or read timeout
- `requests.exceptions.ConnectionError` - Network connectivity issues
- HTTP Status 429 (Too Many Requests)
- HTTP Status 500-504 (Server errors)

**Non-Retryable Errors:**

- HTTP Status 400-403 (Client errors like invalid token)
- JSON decode errors
- `ValidationError` (input validation failures)

**Customizing Retry Behavior:**

```python
from retry import RetryConfig

# Create custom retry configuration
retry_config = RetryConfig(
    max_attempts=5,           # Try up to 5 times
    initial_delay=1.0,        # Wait 1 second before first retry
    max_delay=30.0,           # Cap delay at 30 seconds
    backoff_factor=3.0,       # Increase delay by 3x each time
    retry_on_codes={429, 500, 502, 503, 504}  # Which HTTP codes to retry
)

# Use custom config when creating bot
bot = Bot(token="YOUR_TOKEN", retry_config=retry_config)
```

**Example with Retry:**

```python
# With default retry config, this will retry up to 3 times automatically
try:
    bot.send_message(123456789, "Hello!")  # Network glitch on first try, succeeds on retry
except NetworkError as e:
    print(f"Failed after all retries: {e}")
```

### UI/Console Modes

The bot can be run in two interactive modes:

#### Console Mode

```bash
python huu.py
# Select 'console' when prompted
# Enter Chat ID (or leave empty to use default)
# Enter message text
# Type 'exit' to quit
```

#### UI Mode (Tkinter)

```bash
python huu.py
# Select 'ui' when prompted
# Use the graphical interface to send messages
```

## Project Structure

vgee/
├── main.py              # Entry point for the bot
├── huu.py              # Core Bot class and utilities
├── config.py           # Configuration management
├── test_huu.py         # Comprehensive unit tests (30+ tests)
├── requirements.txt    # Project dependencies
├── README.md          # This file
├── utils/
│   ├── auth.py        # Authentication utilities
│   └── decorators.py  # Reusable decorators
└── tests/
    ├── test_bot.py    # Bot functionality tests
    └── test_config.py # Configuration tests

```

## Testing

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest test_huu.py -v
```

### Test Coverage

The project includes 30+ tests covering:

- Bot initialization and configuration
- Message sending with valid and invalid inputs
- Chat and user information retrieval
- Input validation for all parameters
- Error handling and edge cases
- Session management and cleanup
- Context manager functionality

## Configuration

### Environment Variables

The bot uses environment variables for configuration:

```bash
# Set the bot token
export BOT_TOKEN="your_bot_token_here"

# Set optional default chat ID
export DEFAULT_SETTING="your_default_setting"
```

### Config Class

```python
from config import Config, ConfigError

try:
    Config.validate()  # Validates BOT_TOKEN is set
    token = Config.TOKEN
    default_setting = Config.DEFAULT_SETTING
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Always use context managers** for resource management:

   ```python
   with Bot(token="YOUR_TOKEN") as bot:
       bot.send_message(chat_id, "Message")
   ```

2. **Validate external inputs** before calling bot methods

3. **Handle exceptions** appropriately:

   ```python
   try:
       bot.send_message(chat_id, text)
   except ValueError as e:
       print(f"Invalid input: {e}")
   except requests.exceptions.RequestException as e:
       print(f"Network error: {e}")
   ```

4. **Use reasonable timeouts** based on your network conditions

5. **Monitor logs** for debugging issues

## Contacts

If you have any questions or need further information, please contact us at <support@example.com>.
