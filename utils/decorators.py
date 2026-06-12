"""
Utility decorators for common patterns.

Provides decorators for:
- Logging function calls and results
- Ensuring only one instance exists (singleton)

Decorators:
    log_function_call: Log function calls, arguments, and results
    singleton: Ensure only one instance of a class exists

Example:
    >>> @log_function_call
    ... def expensive_operation(x: int) -> int:
    ...     return x ** 2
    >>> 
    >>> expensive_operation(5)  # Logs the call and result
    25
    
    >>> @singleton
    ... class DatabaseConnection:
    ...     def __init__(self):
    ...         self.connected = True
    >>> 
    >>> db1 = DatabaseConnection()
    >>> db2 = DatabaseConnection()
    >>> db1 is db2  # Same instance
    True
"""
from functools import wraps
import logging
from typing import Callable, Type, Any, TypeVar, Dict

logger = logging.getLogger(__name__)

T = TypeVar('T')


def log_function_call(
    log_args: bool = False,
    log_result: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to log function calls, arguments, and return values.
    
    Logs function entry and exit, without exposing sensitive data.
    Can be configured to include/exclude arguments and results.
    
    Args:
        log_args: Whether to log argument counts (default True)
        log_result: Whether to log result type (default True)
        
    Returns:
        Decorator function
        
    Example:
        >>> @log_function_call()
        ... def process_data(data: dict) -> str:
        ...     return "processed"
        >>> process_data({"key": "value"})
        # Logs: Calling process_data with 1 args
        # Logs: process_data returned str
        'processed'
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log function entry
            func_name = func.__name__
            try:
                if log_args:
                    arg_repr = f"{len(args)} args"
                    kwarg_repr = f"{len(kwargs)} kwargs"
                    logger.info(f"Calling {func_name} with {arg_repr}, {kwarg_repr}")
                else:
                    logger.debug(f"Calling {func_name}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log function exit
                if log_result:
                    result_type = type(result).__name__
                    logger.info(f"{func_name} returned {result_type}")
                else:
                    logger.debug(f"{func_name} completed successfully")
                
                return result
            except Exception as e:
                logger.error(
                    f"Error in {func_name}: {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


def singleton(cls: Type[T]) -> Callable[..., T]:
    """Decorator to ensure only one instance of a class exists.
    
    Implements the singleton pattern using a decorator.
    The first instantiation creates the instance, subsequent calls return the same instance.
    
    Args:
        cls: The class to make a singleton
        
    Returns:
        Wrapper function that returns singleton instance
        
    Example:
        >>> @singleton
        ... class DatabaseConnection:
        ...     def __init__(self, host: str):
        ...         self.host = host
        ...         logger.info(f"Connecting to {host}")
        >>> 
        >>> db1 = DatabaseConnection("localhost")
        # Logs: Connecting to localhost
        >>> db2 = DatabaseConnection("otherhost")
        # No log - instance already exists
        >>> db1 is db2  # Same instance
        True
        >>> db1.host
        'localhost'
    """
    instances: Dict[Type, Any] = {}
    
    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:
            logger.debug(f"Creating singleton instance of {cls.__name__}")
            instances[cls] = cls(*args, **kwargs)
        else:
            logger.debug(f"Returning existing singleton instance of {cls.__name__}")
        return instances[cls]
    
    return get_instance


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to retry a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts (default 3)
        delay: Initial delay between retries in seconds (default 1.0)
        backoff: Backoff multiplier for each retry (default 2.0)
        exceptions: Tuple of exceptions to catch (default all Exceptions)
        
    Returns:
        Decorator function
        
    Example:
        >>> @retry(max_attempts=3, delay=0.5)
        ... def flaky_operation():
        ...     import random
        ...     if random.random() < 0.5:
        ...         raise ConnectionError("Network error")
        ...     return "success"
        >>> flaky_operation()  # Retries up to 3 times with exponential backoff
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts in {func.__name__}: {e}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}, "
                        f"retrying in {current_delay:.1f}s: {e}"
                    )
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to cache function results (memoization).
    
    Caches results based on arguments. Works with hashable arguments only.
    
    Args:
        func: The function to memoize
        
    Returns:
        Memoized function
        
    Example:
        >>> @memoize
        ... def fibonacci(n: int) -> int:
        ...     if n <= 1:
        ...         return n
        ...     return fibonacci(n - 1) + fibonacci(n - 2)
        >>> 
        >>> fibonacci(10)  # Cached for subsequent calls
        55
    """
    cache: Dict[tuple, Any] = {}
    
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Create cache key from arguments
        key = (args, tuple(sorted(kwargs.items())))
        
        if key in cache:
            logger.debug(f"{func.__name__} returning cached result for {key}")
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        logger.debug(f"{func.__name__} cached result for {key}")
        return result
    
    # Add cache management methods
    def clear_cache() -> None:
        """Clear the memoization cache."""
        cache.clear()
        logger.info(f"Cleared cache for {func.__name__}")
    
    wrapper.clear_cache = clear_cache  # type: ignore
    return wrapper
