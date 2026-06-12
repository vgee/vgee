"""
Unit tests for utility modules.

Tests the following utilities:
- Authentication and authorization (auth.py)
- Decorators (decorators.py)
- Validation module (validation.py)
- API Client (api_client.py)
"""
import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Any

from utils.auth import (
    AuthError,
    authenticate_user,
    grant_permission,
    revoke_permission,
    is_authenticated,
    check_permission,
    require_auth,
    require_permission,
    clear_auth_state,
)

from utils.decorators import (
    log_function_call,
    singleton,
    retry,
    memoize,
)

from validation import (
    ValidationError,
    validate_token,
    validate_text,
    validate_chat_id_value,
    validate_timeout,
    validate_api_response,
    extract_message_id,
)


class TestAuthentication:
    """Tests for authentication utilities."""
    
    def setup_method(self):
        """Clear auth state before each test."""
        clear_auth_state()
        if "USER_ID" in os.environ:
            del os.environ["USER_ID"]
    
    def teardown_method(self):
        """Clean up after each test."""
        clear_auth_state()
        if "USER_ID" in os.environ:
            del os.environ["USER_ID"]
    
    def test_authenticate_user(self):
        """Test user authentication."""
        authenticate_user("user_123")
        os.environ["USER_ID"] = "user_123"
        assert is_authenticated() is True
    
    def test_authenticate_user_empty_raises_error(self):
        """Test that empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            authenticate_user("")
    
    def test_is_authenticated_without_user_id_env(self):
        """Test authentication check without USER_ID set."""
        authenticate_user("user_123")
        assert is_authenticated() is False
    
    def test_is_authenticated_wrong_user(self):
        """Test authentication check for wrong user."""
        authenticate_user("user_123")
        os.environ["USER_ID"] = "user_456"
        assert is_authenticated() is False
    
    def test_grant_permission(self):
        """Test granting permissions."""
        grant_permission("user_123", "send_messages")
        assert check_permission("user_123", "send_messages") is True
    
    def test_grant_permission_multiple(self):
        """Test granting multiple permissions."""
        grant_permission("user_123", "send_messages")
        grant_permission("user_123", "admin")
        assert check_permission("user_123", "send_messages") is True
        assert check_permission("user_123", "admin") is True
    
    def test_grant_permission_empty_user_raises_error(self):
        """Test that empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            grant_permission("", "send_messages")
    
    def test_grant_permission_empty_permission_raises_error(self):
        """Test that empty permission raises ValueError."""
        with pytest.raises(ValueError, match="permission cannot be empty"):
            grant_permission("user_123", "")
    
    def test_check_permission_nonexistent_user(self):
        """Test permission check for nonexistent user."""
        assert check_permission("user_999", "send_messages") is False
    
    def test_revoke_permission(self):
        """Test revoking permissions."""
        grant_permission("user_123", "admin")
        assert check_permission("user_123", "admin") is True
        revoke_permission("user_123", "admin")
        assert check_permission("user_123", "admin") is False
    
    def test_revoke_permission_nonexistent(self):
        """Test revoking nonexistent permission doesn't raise."""
        revoke_permission("user_123", "nonexistent")  # Should not raise
    
    def test_require_auth_decorator_authenticated(self):
        """Test require_auth decorator with authenticated user."""
        authenticate_user("user_123")
        os.environ["USER_ID"] = "user_123"
        
        @require_auth
        def protected_function():
            return "success"
        
        assert protected_function() == "success"
    
    def test_require_auth_decorator_not_authenticated(self):
        """Test require_auth decorator without authentication."""
        os.environ["USER_ID"] = "user_123"
        
        @require_auth
        def protected_function():
            return "success"
        
        with pytest.raises(AuthError, match="Authentication required"):
            protected_function()
    
    def test_require_permission_decorator_with_permission(self):
        """Test require_permission decorator with permission."""
        authenticate_user("user_123")
        grant_permission("user_123", "admin")
        os.environ["USER_ID"] = "user_123"
        
        @require_permission("admin")
        def admin_function():
            return "admin_success"
        
        assert admin_function() == "admin_success"
    
    def test_require_permission_decorator_without_permission(self):
        """Test require_permission decorator without permission."""
        authenticate_user("user_123")
        os.environ["USER_ID"] = "user_123"
        
        @require_permission("admin")
        def admin_function():
            return "admin_success"
        
        with pytest.raises(AuthError, match="Permission 'admin' required"):
            admin_function()


class TestDecorators:
    """Tests for utility decorators."""
    
    def test_log_function_call_basic(self, caplog):
        """Test log_function_call decorator."""
        @log_function_call()
        def my_function(x: int) -> int:
            return x * 2
        
        result = my_function(5)
        assert result == 10
    
    def test_log_function_call_with_exception(self, caplog):
        """Test log_function_call with exception."""
        @log_function_call()
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
    
    def test_singleton_decorator(self):
        """Test singleton decorator."""
        @singleton
        class MyClass:
            def __init__(self, value: int):
                self.value = value
        
        obj1 = MyClass(10)
        obj2 = MyClass(20)
        
        assert obj1 is obj2
        assert obj1.value == 10  # Keeps first initialization
    
    def test_retry_decorator_success(self):
        """Test retry decorator with immediate success."""
        @retry(max_attempts=3)
        def sometimes_fails():
            return "success"
        
        result = sometimes_fails()
        assert result == "success"
    
    def test_retry_decorator_eventual_success(self):
        """Test retry decorator with eventual success."""
        attempts = [0]
        
        @retry(max_attempts=3, delay=0.01)
        def eventually_succeeds():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Not ready yet")
            return "success"
        
        result = eventually_succeeds()
        assert result == "success"
        assert attempts[0] == 2
    
    def test_retry_decorator_max_attempts_exceeded(self):
        """Test retry decorator when max attempts exceeded."""
        @retry(max_attempts=2, delay=0.01)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fails()
    
    def test_memoize_decorator(self):
        """Test memoize decorator."""
        call_count = [0]
        
        @memoize
        def expensive_function(x: int) -> int:
            call_count[0] += 1
            return x * 2
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call with same args should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not called again
        
        # Different args should call function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count[0] == 2
    
    def test_memoize_clear_cache(self):
        """Test memoize cache clearing."""
        call_count = [0]
        
        @memoize
        def my_func(x: int) -> int:
            call_count[0] += 1
            return x * 2
        
        my_func(5)
        my_func(5)
        assert call_count[0] == 1
        
        my_func.clear_cache()
        
        my_func(5)
        assert call_count[0] == 2  # Function called again after cache clear


class TestValidation:
    """Tests for validation utilities."""
    
    def test_validate_token_valid(self):
        """Test valid token validation."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        validate_token(token)  # Should not raise
    
    def test_validate_token_invalid_format(self):
        """Test invalid token format (too short)."""
        with pytest.raises(ValidationError):
            validate_token("abc")
    
    def test_validate_token_empty(self):
        """Test empty token."""
        with pytest.raises(ValidationError):
            validate_token("")
    
    def test_validate_text_valid(self):
        """Test valid text validation."""
        validate_text("Hello world")  # Should not raise
    
    def test_validate_text_too_long(self):
        """Test text that's too long."""
        long_text = "x" * 5000
        with pytest.raises(ValidationError):
            validate_text(long_text)
    
    def test_validate_text_empty(self):
        """Test empty text."""
        with pytest.raises(ValidationError):
            validate_text("")
    
    def test_validate_chat_id_valid(self):
        """Test valid chat ID (integer)."""
        validate_chat_id_value(12345)  # Should not raise
        validate_chat_id_value(-123456789)  # Negative IDs allowed (groups)
    
    def test_validate_chat_id_invalid(self):
        """Test invalid chat ID."""
        with pytest.raises(ValidationError):
            validate_chat_id_value("not_a_number")
    
    def test_validate_chat_id_zero(self):
        """Test chat ID of zero."""
        with pytest.raises(ValidationError):
            validate_chat_id_value(0)
    
    def test_validate_timeout_valid(self):
        """Test valid timeout."""
        validate_timeout(5.0)  # Should not raise
        validate_timeout(30)   # Should accept int too
    
    def test_validate_timeout_invalid(self):
        """Test invalid timeout."""
        with pytest.raises(ValidationError):
            validate_timeout(0)  # Zero not allowed
        with pytest.raises(ValidationError):
            validate_timeout(-1)  # Negative not allowed
        with pytest.raises(ValidationError):
            validate_timeout(301)  # Over max
    
    def test_validate_api_response_valid(self):
        """Test valid API response validation."""
        response = {
            "ok": True,
            "result": {"message_id": 123, "text": "Hello"}
        }
        result = validate_api_response(response)
        assert result == response  # Returns entire response
    
    def test_validate_api_response_not_dict(self):
        """Test response that is not a dictionary."""
        from exceptions import APIError
        with pytest.raises(APIError):
            validate_api_response("not a dict")
    
    def test_validate_api_response_missing_ok(self):
        """Test response missing 'ok' field."""
        from exceptions import APIError
        response = {"result": {}}
        with pytest.raises(APIError):
            validate_api_response(response)
    
    def test_extract_message_id_valid(self):
        """Test valid message ID extraction."""
        result = {"message_id": 42}
        assert extract_message_id(result) == 42
    
    def test_extract_message_id_missing(self):
        """Test extraction when message_id is missing."""
        from exceptions import APIError
        result = {}
        with pytest.raises(APIError):
            extract_message_id(result)


class TestBackwardCompatibility:
    """Tests for backward compatibility of old import paths."""
    
    def test_import_from_validators_module(self):
        """Test importing from old validators module."""
        import warnings
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            from validators import validate_token
            assert validate_token is not None
    
    def test_import_from_response_validators_module(self):
        """Test importing from old response_validators module."""
        import warnings
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            from response_validators import validate_api_response
            assert validate_api_response is not None
