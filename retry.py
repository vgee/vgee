"""
Retry logic for API calls.

This module provides utilities for retrying failed API requests with
exponential backoff strategy.
"""
import logging
import time
import typing
from typing import Callable, TypeVar, Any

import requests

from exceptions import NetworkError

T = TypeVar('T')

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_attempts (int): Maximum number of attempts (minimum 1)
        initial_delay (float): Initial delay between retries in seconds (minimum 0.1)
        max_delay (float): Maximum delay between retries in seconds
        backoff_factor (float): Multiplier for exponential backoff (minimum 1.0)
        retry_on_codes (set): HTTP status codes to retry on
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 0.5,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        retry_on_codes: typing.Optional[typing.Set[int]] = None,
    ) -> None:
        """Initialize RetryConfig.

        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            initial_delay: Initial delay in seconds (default: 0.5)
            max_delay: Maximum delay in seconds (default: 10.0)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
            retry_on_codes: HTTP status codes to retry on (default: 429, 500, 502, 503, 504)
        """
        self.max_attempts = max(1, max_attempts)
        self.initial_delay = max(0.1, initial_delay)
        self.max_delay = max(self.initial_delay, max_delay)
        self.backoff_factor = max(1.0, backoff_factor)
        self.retry_on_codes = retry_on_codes or {429, 500, 502, 503, 504}


def retry_with_backoff(
    config: typing.Optional[RetryConfig] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying functions with exponential backoff.

    Args:
        config: RetryConfig instance with retry settings. If None, uses defaults.

    Returns:
        Decorator function

    Example:
        @retry_with_backoff()
        def fetch_data():
            response = requests.get('https://api.example.com/data')
            response.raise_for_status()
            return response.json()
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: typing.Optional[Exception] = None
            delay = config.initial_delay

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.Timeout as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed with timeout: {e}"
                    )
                    if attempt < config.max_attempts:
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                except requests.exceptions.ConnectionError as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed with connection error: {e}"
                    )
                    if attempt < config.max_attempts:
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                except requests.exceptions.HTTPError as e:
                    last_exception = e
                    status_code = e.response.status_code if e.response else None
                    if status_code in config.retry_on_codes and attempt < config.max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{config.max_attempts} failed with HTTP {status_code}: {e}"
                        )
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    logger.error(f"Attempt {attempt}/{config.max_attempts} failed: {e}")
                    if attempt < config.max_attempts:
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        raise

            if last_exception:
                raise NetworkError(
                    f"Failed after {config.max_attempts} attempts",
                    original_error=last_exception,
                )
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper

    return decorator


def should_retry(exception: Exception, retry_on_codes: typing.Set[int]) -> bool:
    """Determine if an exception should trigger a retry.

    Args:
        exception: The exception to check
        retry_on_codes: HTTP status codes to retry on

    Returns:
        True if should retry, False otherwise
    """
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response is not None:
            return exception.response.status_code in retry_on_codes
    return False
