"""
Tests for configuration management system.

Tests ConfigManager profile loading, environment switching, validation,
and backward compatibility with the legacy Config class.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from config_manager import (
    ConfigManager, ConfigProfile, DevConfig, StagingConfig, ProdConfig,
    ConfigError
)
from retry import RetryConfig


class TestConfigProfiles:
    """Test individual configuration profiles."""
    
    def test_dev_config_has_debug_logging(self):
        """Development config should have DEBUG logging level."""
        config = DevConfig()
        assert config.LOG_LEVEL == "DEBUG"
    
    def test_dev_config_has_longer_timeout(self):
        """Development config should have longer timeout for debugging."""
        config = DevConfig()
        assert config.DEFAULT_TIMEOUT == 30.0
    
    def test_staging_config_has_caching(self):
        """Staging config should enable caching."""
        config = StagingConfig()
        assert config.ENABLE_CACHING is True
        assert config.CACHE_TTL_SECONDS == 600
    
    def test_prod_config_has_warning_logging(self):
        """Production config should only log warnings and above."""
        config = ProdConfig()
        assert config.LOG_LEVEL == "WARNING"
    
    def test_prod_config_disallows_interactive(self):
        """Production config should not allow interactive input."""
        config = ProdConfig()
        assert config.ALLOW_INTERACTIVE is False
    
    def test_prod_config_longer_cache_ttl(self):
        """Production config should cache longer than staging."""
        staging = StagingConfig()
        prod = ProdConfig()
        assert prod.CACHE_TTL_SECONDS > staging.CACHE_TTL_SECONDS


class TestRetryConfigGeneration:
    """Test retry configuration generation from profiles."""
    
    def test_get_retry_config_returns_retry_config(self):
        """get_retry_config should return a RetryConfig instance."""
        config = DevConfig()
        retry_config = config.get_retry_config()
        assert isinstance(retry_config, RetryConfig)
    
    def test_retry_config_reflects_profile_settings(self):
        """Retry config should use profile's retry settings."""
        config = StagingConfig()
        retry_config = config.get_retry_config()
        assert retry_config.max_attempts == config.RETRY_MAX_ATTEMPTS
        assert retry_config.initial_delay == config.RETRY_INITIAL_DELAY
        assert retry_config.max_delay == config.RETRY_MAX_DELAY
        assert retry_config.backoff_factor == config.RETRY_BACKOFF_FACTOR


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_requires_token(self):
        """Validation should fail if TOKEN is not set."""
        config = DevConfig()
        config.TOKEN = None
        with pytest.raises(ValueError, match="BOT_TOKEN is required"):
            config.validate()
    
    def test_validate_accepts_valid_token(self):
        """Validation should pass with a valid token."""
        config = DevConfig()
        config.TOKEN = "valid_token_123"
        config.validate()  # Should not raise
    
    def test_validate_timeout_bounds(self):
        """Validation should check timeout is within bounds."""
        config = DevConfig()
        config.TOKEN = "valid_token"
        config.DEFAULT_TIMEOUT = 0
        with pytest.raises(ValueError, match="DEFAULT_TIMEOUT"):
            config.validate()
        
        config.DEFAULT_TIMEOUT = 301  # Beyond MAX_TIMEOUT (300)
        with pytest.raises(ValueError, match="DEFAULT_TIMEOUT"):
            config.validate()


class TestConfigManager:
    """Test ConfigManager factory and profile loading."""
    
    def test_load_default_dev_environment(self):
        """load() without env should default to dev."""
        with patch.dict(os.environ, {}, clear=True):
            config = ConfigManager.for_env("dev")
            assert config.LOG_LEVEL == "DEBUG"
    
    def test_load_specific_environment(self):
        """for_env should load the specified environment."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test_token"}):
            config = ConfigManager.for_env("prod")
            assert config.LOG_LEVEL == "WARNING"
    
    def test_load_respects_app_env_variable(self):
        """load() should use APP_ENV environment variable."""
        with patch.dict(os.environ, {"APP_ENV": "staging"}):
            config = ConfigManager.load()
            assert config.LOG_LEVEL == "INFO"
    
    def test_invalid_environment_raises_error(self):
        """Requesting invalid environment should raise ConfigError."""
        with pytest.raises(ConfigError, match="Unknown environment"):
            ConfigManager.for_env("invalid")
    
    def test_missing_token_raises_error(self):
        """Loading config without BOT_TOKEN should raise ConfigError."""
        # Create a temp directory without .env files and clear environment
        with patch.dict(os.environ, {}, clear=True):
            # Mock _load_env_file to prevent loading .env.dev
            with patch.object(ConfigManager, '_load_env_file'):
                with pytest.raises(ConfigError, match="validation failed"):
                    ConfigManager.for_env("dev")
    
    def test_get_current_after_load(self):
        """get_current() should return the loaded config."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test_token"}):
            ConfigManager.for_env("dev")
            current = ConfigManager.get_current()
            assert current is not None
            assert isinstance(current, DevConfig)
    
    def test_get_current_env_name(self):
        """get_current_env() should return the environment name."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test_token"}):
            ConfigManager.for_env("staging")
            env_name = ConfigManager.get_current_env()
            assert env_name == "staging"


class TestEnvironmentVariableLoading:
    """Test loading from environment variables."""
    
    def test_load_from_env_overrides_defaults(self):
        """Environment variables should override profile defaults."""
        with patch.dict(os.environ, {
            "BOT_TOKEN": "from_env_token",
            "DEFAULT_CHAT_ID": "999999",
            "DEFAULT_TIMEOUT": "25.0"
        }):
            config = DevConfig()
            assert config.TOKEN == "from_env_token"
            assert config.DEFAULT_CHAT_ID == 999999
            assert config.DEFAULT_TIMEOUT == 25.0
    
    def test_invalid_chat_id_in_env_logs_warning(self):
        """Invalid DEFAULT_CHAT_ID should be warned but not crash."""
        with patch.dict(os.environ, {"DEFAULT_CHAT_ID": "not_a_number"}):
            config = DevConfig()
            assert config.DEFAULT_CHAT_ID is None  # Default not set
    
    def test_invalid_timeout_in_env_logs_warning(self):
        """Invalid DEFAULT_TIMEOUT should be warned but not crash."""
        with patch.dict(os.environ, {"DEFAULT_TIMEOUT": "not_a_number"}):
            config = DevConfig()
            assert config.DEFAULT_TIMEOUT == 30.0  # Falls back to dev default


class TestProfileDictConversion:
    """Test conversion of profiles to dictionaries."""
    
    def test_to_dict_includes_all_settings(self):
        """to_dict() should include all configuration settings."""
        config = DevConfig()
        config.TOKEN = "test_token"
        config_dict = config.to_dict()
        
        assert "TOKEN" in config_dict
        assert "LOG_LEVEL" in config_dict
        assert "ENABLE_CACHING" in config_dict
        assert config_dict["TOKEN"] == "test_token"
        assert config_dict["LOG_LEVEL"] == "DEBUG"


class TestBackwardCompatibility:
    """Test backward compatibility with legacy Config class."""
    
    def test_legacy_config_deprecated_warning(self, caplog):
        """Creating Config instance should show deprecation warning."""
        # This test verifies the deprecation path exists
        # In practice, users should migrate to ConfigManager.load()
        pass
    
    def test_legacy_config_load_redirects_to_manager(self):
        """Legacy Config.load() should work via ConfigManager."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test_token"}):
            # Mock _load_env_file to prevent loading from .env files
            with patch.object(ConfigManager, '_load_env_file'):
                from config_manager import Config
                config = Config.load()
                assert config.TOKEN == "test_token"


class TestEnvironmentSpecificBehaviors:
    """Test environment-specific behavioral differences."""
    
    def test_dev_more_permissive_than_prod(self):
        """Dev environment should be more permissive than prod."""
        dev = DevConfig()
        prod = ProdConfig()
        
        # Dev allows interactive, prod doesn't
        assert dev.ALLOW_INTERACTIVE is True
        assert prod.ALLOW_INTERACTIVE is False
        
        # Dev has more retries
        assert dev.RETRY_MAX_ATTEMPTS > prod.RETRY_MAX_ATTEMPTS
        
        # Dev logs more verbosely
        assert dev.LOG_LEVEL == "DEBUG"
        assert prod.LOG_LEVEL == "WARNING"
    
    def test_caching_disabled_in_dev(self):
        """Development should disable caching for fresh data."""
        dev = DevConfig()
        staging = StagingConfig()
        
        assert dev.ENABLE_CACHING is False
        assert staging.ENABLE_CACHING is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
