from functools import wraps
from typing import Callable, Any, Set, Dict
import os

_authenticated_users: Set[str] = set()
_user_permissions: Dict[str, Set[str]] = {}

class AuthError(Exception):
    """Custom exception for authentication errors."""
    pass

def require_auth(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not is_authenticated():
            raise PermissionError("Требуется аутентификация")
        return func(*args, **kwargs)
    return wrapper

def is_authenticated() -> bool:
    user_id = os.getenv("USER_ID")
    return user_id in _authenticated_users

def check_permission(user_id: str, permission: str) -> bool:
    return permission in _user_permissions.get(user_id, set())

def authenticate_user(user_id: str) -> None:
    _authenticated_users.add(user_id)

def grant_permission(user_id: str, permission: str) -> None:
    if user_id not in _user_permissions:
        _user_permissions[user_id] = set()
    _user_permissions[user_id].add(permission)
