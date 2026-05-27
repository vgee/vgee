"""
API client abstraction for VGEE Telegram bot.

Provides a small APIClient class that manages a requests.Session, applies retry
logic, and validates responses using response_validators. This decouples HTTP
logic from the Bot class for improved modularity and testability.
"""
from __future__ import annotations

import logging
import typing
from typing import Any, Dict, Optional

import requests

from retry import RetryConfig, retry_with_backoff
from response_validators import validate_api_response
from exceptions import APIError, NetworkError

logger = logging.getLogger(__name__)


class APIClient:
    """Simple API client wrapping requests.Session with retry and response validation.

    Attributes:
        token: Bot token used to build request URLs (optional)
        retry_config: RetryConfig used for transient failures
        session: requests.Session instance
    """

    def __init__(self, token: Optional[str] = None, retry_config: Optional[RetryConfig] = None) -> None:
        self.token = token
        self.retry_config = retry_config or RetryConfig()
        self.session = requests.Session()
        # Ensure headers exist and are dict-like
        if not hasattr(self.session, "headers") or self.session.headers is None:
            self.session.headers = {}
        elif not isinstance(self.session.headers, dict):
            self.session.headers = dict(self.session.headers)
        self.session.headers.update({
            "User-Agent": "VGEE-Bot/1.0",
            "Content-Type": "application/json",
        })

    def close(self) -> None:
        try:
            if getattr(self, "session", None) is not None:
                self.session.close()
        finally:
            self.session = None

    def _raw_request(self, method: str, url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        try:
            if method.lower() == "get":
                resp = self.session.get(url, params=payload, timeout=timeout)
            else:
                resp = self.session.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Validate structure and raise APIError on invalid/error responses
            validate_api_response(data)
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during API request: {e}")
            raise NetworkError("API request failed", original_error=e)
        except APIError:
            # Re-raise APIError as-is
            raise
        except Exception as e:
            logger.exception("Unexpected error during API request")
            raise NetworkError("Unexpected error during API request", original_error=e)

    def _request_with_retry(self, method: str, url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        # Wrap the raw request with the retry decorator using this instance's config
        wrapper = retry_with_backoff(self.retry_config)(self._raw_request)
        return wrapper(method, url, payload, timeout)

    def post(self, url: str, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        return self._request_with_retry("post", url, payload, timeout)

    def get(self, url: str, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        return self._request_with_retry("get", url, payload, timeout)
