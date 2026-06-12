# Configuration Management System

## Overview

VGEE now includes a powerful **environment-based configuration management system** with support for multiple profiles: `dev`, `staging`, and `prod`.

## Features

✅ **Environment Profiles** - Pre-configured settings for development, staging, and production  
✅ **Environment Variables** - Support for `.env` files and OS environment variables  
✅ **Profile-Specific Settings** - Different timeouts, retries, logging levels, and features per environment  
✅ **Easy Switching** - Switch environments with a single variable (`APP_ENV`)  
✅ **Type-Safe** - Configuration defined with type hints and validation  
✅ **Backward Compatible** - Legacy `Config` class still works (with deprecation warning)  

## Quick Start

### Basic Usage

```python
from config_manager import ConfigManager

# Load configuration based on APP_ENV (defaults to 'dev')
config = ConfigManager.load()

# Or explicitly select an environment
config = ConfigManager.for_env('prod')

# Access settings
print(config.TOKEN)
print(config.DEFAULT_TIMEOUT)
print(config.get_retry_config())
```

### With Bot

```python
from config_manager import ConfigManager
from huu import Bot

config = ConfigManager.load()
bot = Bot(token=config.TOKEN, retry_config=config.get_retry_config())
```

## Environment Profiles

### Development (`dev`)
- **Default timeout**: 30 seconds (longer for debugging)
- **Log level**: DEBUG (verbose)
- **Retries**: 5 attempts (more testing)
- **Caching**: Disabled (fresh data always)
- **Interactive**: Enabled

### Staging (`staging`)
- **Default timeout**: 15 seconds
- **Log level**: INFO
- **Retries**: 3 attempts
- **Caching**: Enabled (10 min TTL)
- **Interactive**: Disabled

### Production (`prod`)
- **Default timeout**: 10 seconds
- **Log level**: WARNING (only errors)
- **Retries**: 3 attempts with 1s initial delay
- **Caching**: Enabled (1 hour TTL)
- **Interactive**: Disabled

## Configuration Methods

### 1. Environment Variables

Set these in your shell or CI/CD system:

```bash
export APP_ENV=prod
export BOT_TOKEN=your_token_here
export DEFAULT_TIMEOUT=15
export RETRY_MAX_ATTEMPTS=3
```

### 2. .env Files

Create profile-specific files in your project root:

**`.env.dev`**
```
BOT_TOKEN=dev_test_token
DEFAULT_CHAT_ID=123456789
DEFAULT_TIMEOUT=30
RETRY_MAX_ATTEMPTS=5
```

**`.env.staging`**
```
BOT_TOKEN=staging_token
DEFAULT_TIMEOUT=15
RETRY_MAX_ATTEMPTS=3
```

**`.env.prod`**
```
BOT_TOKEN=
DEFAULT_TIMEOUT=10
RETRY_MAX_ATTEMPTS=3
```

> ⚠️ **Never commit real tokens!** Use CI/CD secrets instead.

### 3. Code Defaults

Profile classes contain sensible defaults:

```python
from config_manager import DevConfig

config = DevConfig()
config.TOKEN = "my_token"  # Set programmatically
config.validate()
```

## Priority Order

Configuration is loaded in this order (later values override earlier):

1. Profile class defaults
2. `.env.{environment}` file
3. Environment variables
4. Programmatic assignment

## Validation

Configuration is validated on load:

```python
try:
    config = ConfigManager.load()
except ConfigError as e:
    print(f"Configuration error: {e}")
```

**Validation checks:**
- ✓ BOT_TOKEN is required
- ✓ DEFAULT_TIMEOUT is between 0 and 300 seconds
- ✓ RETRY_MAX_ATTEMPTS is at least 1

## API Reference

### ConfigManager

```python
class ConfigManager:
    @classmethod
    def load(env: Optional[str] = None) -> ConfigProfile:
        """Load config for current or specified environment."""
    
    @classmethod
    def for_env(env: str) -> ConfigProfile:
        """Load config for specific environment."""
    
    @classmethod
    def get_current() -> Optional[ConfigProfile]:
        """Get currently loaded config."""
    
    @classmethod
    def get_current_env() -> Optional[str]:
        """Get currently loaded environment name."""
```

### ConfigProfile (and subclasses)

```python
class ConfigProfile:
    # API Settings
    TOKEN: Optional[str]
    DEFAULT_CHAT_ID: Optional[int]
    API_BASE_URL: str
    
    # Timeouts
    DEFAULT_TIMEOUT: float
    MAX_TIMEOUT: float
    
    # Retries
    RETRY_MAX_ATTEMPTS: int
    RETRY_INITIAL_DELAY: float
    RETRY_MAX_DELAY: float
    RETRY_BACKOFF_FACTOR: float
    
    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
    
    # Features
    ENABLE_CACHING: bool
    CACHE_TTL_SECONDS: int
    ALLOW_INTERACTIVE: bool
    
    def get_retry_config() -> RetryConfig:
        """Build RetryConfig from profile settings."""
    
    def validate() -> None:
        """Validate critical configuration values."""
    
    def to_dict() -> Dict[str, Any]:
        """Convert profile to dictionary."""
```

## Examples

### Loading Development Config

```python
import os
os.environ['APP_ENV'] = 'dev'

config = ConfigManager.load()
assert config.LOG_LEVEL == 'DEBUG'
assert config.DEFAULT_TIMEOUT == 30.0
```

### Switching Environments at Runtime

```python
# Load dev
config = ConfigManager.for_env('dev')
# ... do dev work ...

# Load prod for testing
config = ConfigManager.for_env('prod')
assert config.ALLOW_INTERACTIVE is False
```

### Accessing Retry Configuration

```python
config = ConfigManager.load()
retry_config = config.get_retry_config()

# Use with APIClient
from api_client import APIClient
client = APIClient(config.TOKEN, retry_config=retry_config)
```

## Testing

All 26 tests pass covering:
- ✓ Profile-specific defaults
- ✓ Environment variable loading
- ✓ Configuration validation
- ✓ Environment switching
- ✓ Retry config generation
- ✓ Backward compatibility

```bash
pytest test_config_manager.py -v
```

## Migration from Legacy Config

**Old way (deprecated):**
```python
from config import Config
config = Config.load()
```

**New way:**
```python
from config_manager import ConfigManager
config = ConfigManager.load()
```

The old `Config` class still works but logs a deprecation warning.

## Best Practices

1. **Use different tokens per environment**
   - Dev: test token
   - Staging: staging token
   - Prod: production token (from secrets)

2. **Never commit secrets**
   - Use CI/CD environment variables for production tokens
   - Add `.env.prod` to `.gitignore` or leave BOT_TOKEN empty

3. **Match environment in CI/CD**
   ```yaml
   env:
     APP_ENV: prod
     BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
   ```

4. **Load once, reuse globally**
   ```python
   # At app startup
   config = ConfigManager.load()
   
   # Create bot with config
   bot = Bot(token=config.TOKEN, retry_config=config.get_retry_config())
   ```

## Troubleshooting

**Q: Why is my config not loading?**
A: Check that BOT_TOKEN is set via environment variable or .env file.

**Q: How do I use production config in CI?**
A: Set `APP_ENV=prod` and `BOT_TOKEN` as environment variables in your CI/CD system.

**Q: Can I add custom configuration fields?**
A: Yes, subclass `ConfigProfile` and add fields:
```python
class CustomConfig(ConfigProfile):
    def __init__(self):
        super().__init__()
        self.CUSTOM_FIELD = "custom_value"
        self._load_from_env()
```

---

**Created:** June 2024  
**Status:** Production Ready  
**Tests:** 26/26 passing
