"""
Authentication and authorization utilities.

Provides decorators and utilities for:
- User authentication verification
- Permission-based access control
- Secure function decoration

Classes:
    AuthError: Authentication/authorization error

Decorators:
    require_auth: Ensure user is authenticated

Functions:
    is_authenticated: Check if user is authenticated
    check_permission: Check if user has specific permission
    authenticate_user: Register a user as authenticated
    grant_permission: Grant a permission to a user

Example:
    >>> authenticate_user("user_123")
    >>> grant_permission("user_123", "send_messages")
    >>> 
    >>> @require_auth
    ... def send_message(text: str) -> None:
    ...     # User must be authenticated to reach here
    ...     pass
    >>>
    >>> os.environ["USER_ID"] = "user_123"
    >>> send_message("Hello!")  # Works
"""
from functools import wraps
from typing import Callable, Any, Set, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Exception raised for authentication/authorization errors.
    
    Attributes:
        message: Description of the authentication error
        user_id: The user ID that failed authentication (optional)
        permission: The permission that was required (optional)
    """
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        permission: Optional[str] = None
    ) -> None:
        """Initialize AuthError.
        
        Args:
            message: Error message
            user_id: User ID involved in the error
            permission: Permission that was required
        """
        self.message = message
        self.user_id = user_id
        self.permission = permission
        super().__init__(self.message)


# Global state for authentication
_authenticated_users: Set[str] = set()
_user_permissions: Dict[str, Set[str]] = {}


def is_authenticated() -> bool:
    """Check if the current user (from USER_ID env var) is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
        
    Example:
        >>> authenticate_user("user_123")
        >>> os.environ["USER_ID"] = "user_123"
        >>> is_authenticated()
        True
    """
    user_id = os.getenv("USER_ID")
    if user_id is None:
        logger.debug("USER_ID environment variable not set")
        return False
    
    is_auth = user_id in _authenticated_users
    logger.debug(f"User {user_id} authentication check: {is_auth}")
    return is_auth


def check_permission(user_id: str, permission: str) -> bool:
    """Check if a user has a specific permission.
    
    Args:
        user_id: The user ID to check
        permission: The permission to verify
        
    Returns:
        True if user has permission, False otherwise
        
    Raises:
        ValueError: If user_id or permission is empty
        
    Example:
        >>> grant_permission("user_123", "send_messages")
        >>> check_permission("user_123", "send_messages")
        True
        >>> check_permission("user_123", "admin")
        False
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not permission:
        raise ValueError("permission cannot be empty")
    
    has_permission = permission in _user_permissions.get(user_id, set())
    logger.debug(f"User {user_id} permission check for '{permission}': {has_permission}")
    return has_permission


def authenticate_user(user_id: str) -> None:
    """Register a user as authenticated.
    
    Args:
        user_id: The user ID to authenticate
        
    Raises:
        ValueError: If user_id is empty
        
    Example:
        >>> authenticate_user("user_123")
        >>> is_authenticated()  # Returns True if USER_ID env var is "user_123"
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    _authenticated_users.add(user_id)
    logger.info(f"User {user_id} authenticated")


def grant_permission(user_id: str, permission: str) -> None:
    """Grant a specific permission to a user.
    
    Args:
        user_id: The user ID to grant permission to
        permission: The permission to grant
        
    Raises:
        ValueError: If user_id or permission is empty
        
    Example:
        >>> grant_permission("user_123", "send_messages")
        >>> grant_permission("user_123", "admin")
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not permission:
        raise ValueError("permission cannot be empty")
    
    if user_id not in _user_permissions:
        _user_permissions[user_id] = set()
    
    _user_permissions[user_id].add(permission)
    logger.info(f"Granted permission '{permission}' to user {user_id}")


def revoke_permission(user_id: str, permission: str) -> None:
    """Revoke a specific permission from a user.
    
    Args:
        user_id: The user ID to revoke permission from
        permission: The permission to revoke
        
    Raises:
        ValueError: If user_id or permission is empty
        
    Example:
        >>> revoke_permission("user_123", "admin")
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not permission:
        raise ValueError("permission cannot be empty")
    
    if user_id in _user_permissions:
        _user_permissions[user_id].discard(permission)
        logger.info(f"Revoked permission '{permission}' from user {user_id}")


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require authentication before function execution.
    
    Checks if the current user (from USER_ID env var) is authenticated.
    Raises AuthError if not authenticated.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that checks authentication
        
    Raises:
        AuthError: If user is not authenticated
        
    Example:
        >>> @require_auth
        ... def send_message(text: str) -> None:
        ...     print(f"Sending: {text}")
        >>> 
        >>> os.environ["USER_ID"] = "user_123"
        >>> authenticate_user("user_123")
        >>> send_message("Hello!")  # Works
        Sending: Hello!
        >>> 
        >>> os.environ["USER_ID"] = "user_456"
        >>> send_message("Goodbye")  # Raises AuthError
        AuthError: Authentication required
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user_id = os.getenv("USER_ID")
        if not is_authenticated():
            logger.warning(f"Unauthorized access attempt by user {user_id} to {func.__name__}")
            raise AuthError(
                "Authentication required",
                user_id=user_id
            )
        logger.debug(f"Authenticated user {user_id} executing {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


def require_permission(permission: str) -> Callable:
    """Decorator to require a specific permission before function execution.
    
    Checks if the current user has the required permission.
    Raises AuthError if permission is not granted.
    
    Args:
        permission: The required permission name
        
    Returns:
        Decorator function
        
    Raises:
        AuthError: If user lacks required permission
        
    Example:
        >>> @require_permission("send_messages")
        ... def send_message(text: str) -> None:
        ...     print(f"Sending: {text}")
        >>> 
        >>> os.environ["USER_ID"] = "user_123"
        >>> authenticate_user("user_123")
        >>> grant_permission("user_123", "send_messages")
        >>> send_message("Hello!")  # Works
        Sending: Hello!
        >>> 
        >>> @require_permission("admin")
        ... def delete_message(msg_id: int) -> None:
        ...     pass
        >>> delete_message(123)  # Raises AuthError
        AuthError: Permission 'admin' required
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            user_id = os.getenv("USER_ID")
            if not user_id or not check_permission(user_id, permission):
                logger.warning(
                    f"User {user_id} lacks required permission '{permission}' "
                    f"to execute {func.__name__}"
                )
                raise AuthError(
                    f"Permission '{permission}' required",
                    user_id=user_id,
                    permission=permission
                )
            logger.debug(f"User {user_id} has permission '{permission}' to execute {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def clear_auth_state() -> None:
    """Clear all authentication state (useful for testing).
    
    WARNING: This removes all authenticated users and permissions.
    Only use in testing scenarios.
    
    Example:
        >>> clear_auth_state()  # All users and permissions cleared
    """
    global _authenticated_users, _user_permissions
    _authenticated_users.clear()
    _user_permissions.clear()
    logger.info("Authentication state cleared")
