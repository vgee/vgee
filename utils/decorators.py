from functools import wraps
import logging
from typing import Callable, Type, Any

def log_function_call(func: Callable) -> Callable:
    """Log function calls, arguments, and return values without exposing sensitive data."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(__name__)
        arg_repr = f"{len(args)} args"
        kwarg_repr = f"{len(kwargs)} kwargs"
        try:
            logger.info(f"Calling {func.__name__} with {arg_repr}, {kwarg_repr}")
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} returned {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper

def singleton(cls: Type) -> Callable:
    """Ensure only one instance of a class exists."""
    instances = {}
    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance
