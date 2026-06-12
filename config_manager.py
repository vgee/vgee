"""
Configuration management system with environment profiles.

Supports dev, staging, and prod environments with profile-specific settings.
Loads configuration from environment variables and .env files.

Classes:
    ConfigProfile: Base class for environment profiles
    DevConfig: Development configuration
    StagingConfig: Staging configuration
    ProdConfig: Production configuration
    ConfigManager: Factory for loading profile-specific configurations
    
Example:
    >>> config = ConfigManager.load()  # Loads based on APP_ENV
    >>> token = config.TOKEN
    >>> retry_config = config.get_retry_config()
    
    >>> config = ConfigManager.for_env('prod')  # Load specific profile
    >>> timeout = config.DEFAULT_TIMEOUT
"""
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

from retry import RetryConfig


logger = logging.getLogger(__name__)


@dataclass
class ConfigProfile:
    """Base configuration profile with environment-specific settings."""
    
    # API Settings
    TOKEN: Optional[str] = None
    DEFAULT_CHAT_ID: Optional[int] = None
    API_BASE_URL: str = "https://api.telegram.org"
    
    # Timeout & Retry Settings
    DEFAULT_TIMEOUT: float = 10.0
    MAX_TIMEOUT: float = 300.0
    
    # Retry Configuration
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_INITIAL_DELAY: float = 0.5
    RETRY_MAX_DELAY: float = 10.0
    RETRY_BACKOFF_FACTOR: float = 2.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_CACHING: bool = False
    CACHE_TTL_SECONDS: int = 300
    
    # UI Settings
    ALLOW_INTERACTIVE: bool = True
    
    def __post_init__(self):
        """Load settings from environment variables after initialization."""
        self._load_from_env()
    
    def _load_from_env(self):
        """Override settings with environment variables if present."""
        if env_token := os.getenv("BOT_TOKEN"):
            self.TOKEN = env_token
        if env_chat_id := os.getenv("DEFAULT_CHAT_ID"):
            try:
                self.DEFAULT_CHAT_ID = int(env_chat_id)
            except ValueError:
                logger.warning(f"Invalid DEFAULT_CHAT_ID in environment: {env_chat_id}")
        if env_timeout := os.getenv("DEFAULT_TIMEOUT"):
            try:
                self.DEFAULT_TIMEOUT = float(env_timeout)
            except ValueError:
                logger.warning(f"Invalid DEFAULT_TIMEOUT in environment: {env_timeout}")
    
    def get_retry_config(self) -> RetryConfig:
        """Build RetryConfig from profile settings."""
        return RetryConfig(
            max_attempts=self.RETRY_MAX_ATTEMPTS,
            initial_delay=self.RETRY_INITIAL_DELAY,
            max_delay=self.RETRY_MAX_DELAY,
            backoff_factor=self.RETRY_BACKOFF_FACTOR,
        )
    
    def validate(self) -> None:
        """Validate critical configuration values."""
        if not self.TOKEN:
            raise ValueError("BOT_TOKEN is required (set via environment variable or .env file)")
        if self.DEFAULT_TIMEOUT <= 0 or self.DEFAULT_TIMEOUT > self.MAX_TIMEOUT:
            raise ValueError(f"DEFAULT_TIMEOUT must be between 0 and {self.MAX_TIMEOUT}")
        if self.RETRY_MAX_ATTEMPTS < 1:
            raise ValueError("RETRY_MAX_ATTEMPTS must be at least 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "TOKEN": self.TOKEN,
            "DEFAULT_CHAT_ID": self.DEFAULT_CHAT_ID,
            "API_BASE_URL": self.API_BASE_URL,
            "DEFAULT_TIMEOUT": self.DEFAULT_TIMEOUT,
            "MAX_TIMEOUT": self.MAX_TIMEOUT,
            "RETRY_MAX_ATTEMPTS": self.RETRY_MAX_ATTEMPTS,
            "RETRY_INITIAL_DELAY": self.RETRY_INITIAL_DELAY,
            "RETRY_MAX_DELAY": self.RETRY_MAX_DELAY,
            "RETRY_BACKOFF_FACTOR": self.RETRY_BACKOFF_FACTOR,
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FORMAT": self.LOG_FORMAT,
            "ENABLE_CACHING": self.ENABLE_CACHING,
            "CACHE_TTL_SECONDS": self.CACHE_TTL_SECONDS,
            "ALLOW_INTERACTIVE": self.ALLOW_INTERACTIVE,
        }


class DevConfig(ConfigProfile):
    """Development environment configuration."""
    def __init__(self):
        super().__init__()
        self.DEFAULT_TIMEOUT = 30.0  # Longer timeout for development
        self.LOG_LEVEL = "DEBUG"  # Verbose logging
        self.RETRY_MAX_ATTEMPTS = 5  # More retry attempts for testing
        self.ENABLE_CACHING = False  # No caching in dev
        self.ALLOW_INTERACTIVE = True
        self._load_from_env()


class StagingConfig(ConfigProfile):
    """Staging environment configuration."""
    def __init__(self):
        super().__init__()
        self.DEFAULT_TIMEOUT = 15.0
        self.LOG_LEVEL = "INFO"
        self.RETRY_MAX_ATTEMPTS = 3
        self.ENABLE_CACHING = True  # Enable caching in staging
        self.CACHE_TTL_SECONDS = 600  # 10 minutes
        self.ALLOW_INTERACTIVE = False
        self._load_from_env()


class ProdConfig(ConfigProfile):
    """Production environment configuration."""
    def __init__(self):
        super().__init__()
        self.DEFAULT_TIMEOUT = 10.0  # Standard timeout
        self.LOG_LEVEL = "WARNING"  # Only warn and above
        self.RETRY_MAX_ATTEMPTS = 3
        self.RETRY_INITIAL_DELAY = 1.0  # Slightly longer initial delay
        self.ENABLE_CACHING = True  # Always cache in production
        self.CACHE_TTL_SECONDS = 3600  # 1 hour
        self.ALLOW_INTERACTIVE = False
        self._load_from_env()


class ConfigError(Exception):
    """Configuration error exception."""
    pass


class ConfigManager:
    """Factory for loading environment-specific configurations."""
    
    _PROFILES = {
        "dev": DevConfig,
        "staging": StagingConfig,
        "prod": ProdConfig,
    }
    
    _current_profile: Optional[str] = None
    _current_config: Optional[ConfigProfile] = None
    
    @classmethod
    def load(cls, env: Optional[str] = None) -> ConfigProfile:
        """
        Load configuration for the specified or current environment.
        
        Args:
            env: Environment name ('dev', 'staging', 'prod'). 
                 If None, reads from APP_ENV environment variable (defaults to 'dev').
        
        Returns:
            ConfigProfile instance for the environment.
            
        Raises:
            ConfigError: If environment is invalid or token is missing.
        """
        if env is None:
            env = os.getenv("APP_ENV", "dev").lower()
        
        return cls.for_env(env)
    
    @classmethod
    def for_env(cls, env: str) -> ConfigProfile:
        """
        Load configuration for a specific environment.
        
        Args:
            env: Environment name ('dev', 'staging', 'prod').
            
        Returns:
            ConfigProfile instance for the environment.
            
        Raises:
            ConfigError: If environment is invalid or token is missing.
        """
        env = env.lower()
        
        if env not in cls._PROFILES:
            raise ConfigError(f"Unknown environment: {env}. Choose from {list(cls._PROFILES.keys())}")
        
        # Load .env file for the environment
        cls._load_env_file(env)
        
        # Create profile instance
        profile_class = cls._PROFILES[env]
        config = profile_class()
        
        # Validate configuration
        try:
            config.validate()
        except ValueError as e:
            raise ConfigError(f"Configuration validation failed for {env}: {e}")
        
        cls._current_profile = env
        cls._current_config = config
        
        logger.info(f"Loaded {env} configuration (timeout={config.DEFAULT_TIMEOUT}s, retries={config.RETRY_MAX_ATTEMPTS})")
        return config
    
    @classmethod
    def _load_env_file(cls, env: str) -> None:
        """
        Load environment-specific .env file if it exists.
        
        Args:
            env: Environment name ('dev', 'staging', 'prod').
        """
        env_file = Path.cwd() / f".env.{env}"
        
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Only set non-empty values to avoid overriding env vars with empty strings
                                if value:
                                    os.environ[key] = value
                logger.debug(f"Loaded environment variables from {env_file}")
            except Exception as e:
                logger.warning(f"Failed to load {env_file}: {e}")
        else:
            logger.debug(f"No .env file found at {env_file}")
    
    @classmethod
    def get_current(cls) -> Optional[ConfigProfile]:
        """Get the currently loaded configuration profile."""
        return cls._current_config
    
    @classmethod
    def get_current_env(cls) -> Optional[str]:
        """Get the currently loaded environment name."""
        return cls._current_profile


# Backward compatibility with old Config class
class Config(ConfigProfile):
    """Deprecated: Use ConfigManager.load() instead."""
    
    def __init__(self):
        super().__init__()
        logger.warning("Config class is deprecated. Use ConfigManager.load() instead.")
    
    @classmethod
    def load(cls):
        """Deprecated: Use ConfigManager.load() instead."""
        logger.warning("Config.load() is deprecated. Use ConfigManager.load() instead.")
        try:
            config = ConfigManager.load()
            # Return self-instance for compatibility
            instance = cls()
            for key, value in config.to_dict().items():
                setattr(instance, key, value)
            return instance
        except ConfigError as e:
            raise e
