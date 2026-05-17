# python
"""
Telegram Bot HTTP Client Module

This module provides a lightweight HTTP client for interacting with the Telegram Bot API.
It includes comprehensive input validation, error handling, automatic retry logic,
and support for both console and GUI interfaces.

Classes:
    Bot: Main class for interacting with Telegram Bot API

Functions:
    _initialize_session: Creates and configures HTTP session
    _validate_default: Validates default chat ID value
    run_ui: Runs the bot in UI mode (tkinter)
    run_console: Runs the bot in console mode

Modules:
    For custom exception classes, see the exceptions module.
    For validation utilities, see the validators module.
    For retry logic configuration, see the retry module.

Example:
    Basic usage:
    >>> from huu import Bot
    >>> bot = Bot(token="YOUR_BOT_TOKEN", default=123456789)
    >>> bot.send_message(chat_id=123456789, text="Hello, world!")
    >>> chat_info = bot.get_chat(123456789)
    >>> bot.close()

    Using context manager:
    >>> with Bot(token="YOUR_BOT_TOKEN") as bot:
    ...     bot.send_message(chat_id=123456789, text="Hello!")

    Using custom retry configuration:
    >>> from retry import RetryConfig
    >>> config = RetryConfig(max_attempts=5)
    >>> bot = Bot(token="YOUR_BOT_TOKEN", retry_config=config)
"""
import logging
import tkinter as tk
import typing
import types as _types
from tkinter import messagebox

import requests # type: ignore

try:
    import aiogram
except ImportError:
    aiogram = _types.SimpleNamespace(types=_types.SimpleNamespace(Chat=None))

from exceptions import ValidationError, APIError, NetworkError
from validators import validate_token, validate_text, validate_chat_id_value, validate_timeout
from retry import RetryConfig, retry_with_backoff

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default retry configuration for API calls
DEFAULT_RETRY_CONFIG = RetryConfig(max_attempts=3, initial_delay=0.5)
class Bot:
    """
    Lightweight HTTP client for Telegram Bot API.

    This class provides methods to send messages and retrieve chat/user information
    from Telegram. It includes comprehensive input validation, error handling,
    automatic retry logic for resilient API calls, and support for context managers.

    Attributes:
        token (str): Telegram bot API token
        default (Optional[int]): Default chat ID for operations
        allow_interactive (bool): Whether to allow interactive input
        session (requests.Session): HTTP session for API calls
        retry_config (RetryConfig): Configuration for automatic retry behavior

    Example:
        >>> bot = Bot(token="YOUR_BOT_TOKEN", default=123456789)
        >>> bot.send_message(chat_id=123456789, text="Hello!")
        >>> bot.close()

        Or using context manager:
        >>> with Bot(token="YOUR_BOT_TOKEN") as bot:
        ...     bot.send_message(123456789, "Hello!")

    Raises:
        ValueError: If token is invalid or required parameters are missing
    """
    def __init__(
        self,
        token: typing.Optional[str] = None,
        default: typing.Optional[typing.Union[int, object, str]] = None,
        allow_interactive: bool = True,
        retry_config: typing.Optional[RetryConfig] = None,
        **kwargs: object
    ) -> None:
        if not token:
            if allow_interactive:
                token = input("Enter bot token: ").strip()
            else:
                raise ValidationError("Token must be provided if interactive input is not allowed", field="token")
        validate_token(token)
        self.token = token
        self.default = _validate_default(default)
        self.allow_interactive = allow_interactive
        self.retry_config = retry_config or DEFAULT_RETRY_CONFIG
        self.session = _initialize_session()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(token={self.token}, default={self.default})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bot):
            return False
        return self.token == other.token and self.default == other.default

    def __call__(self) -> typing.Optional[int]:
        return self.default

    @retry_with_backoff()
    def _make_api_call(
        self,
        url: str,
        payload: dict[str, typing.Any],
        timeout: float,
        method: str = "post",
    ) -> dict[str, typing.Any]:
        """Internal helper to make API calls with built-in retry support.
        
        Args:
            url: Full API endpoint URL
            payload: JSON payload to send
            timeout: Request timeout in seconds
            
        Returns:
            API response data dictionary
            
        Raises:
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        if method.lower() == "get":
            response = self.session.get(url, params=payload, timeout=timeout)
        else:
            response = self.session.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise APIError(
                "API request failed",
                error_code=data.get("error_code"),
                description=data.get("description"),
            )
        return data

    def send_message(self, chat_id: typing.Optional[typing.Union[int, str]], text: str, *, timeout: float = 10.0) -> None:
        """
        Sends a message to a Telegram chat.

        Args:
            chat_id (int, str, optional): Target chat ID. If None or empty, uses self.default.
            text (str): Message text. Must not be empty and must not exceed 4096 characters.
            timeout (float): Request timeout in seconds. Default 10.0, max 300.0.

        Raises:
            ValidationError: If chat_id, text, or timeout is invalid.
            APIError: If the Telegram API returns an error.
            NetworkError: If the API request fails due to network issues.

        Example:
            >>> bot.send_message(123456789, "Hello, world!")
            >>> bot.send_message(None, "Using default chat")  # Uses bot.default
        """
        validate_text(text)
        validate_timeout(timeout)
        
        actual = chat_id if chat_id is not None and str(chat_id).strip() != "" else self.default
        if actual is None:
            raise ValidationError("Chat ID must be provided either as argument or as Bot.default", field="chat_id")
        try:
            chat_int = int(actual)
        except (TypeError, ValueError):
            raise ValidationError("Chat ID must be a number", field="chat_id")
        validate_chat_id_value(chat_int)

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Union[str, int]] = {
            "chat_id": chat_int,
            "text": text
        }
        try:
            self._make_api_call(url, payload, timeout)
            logging.info(f"Сообщение отправлено в чат {chat_int}: {text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при отправке сообщения в чат {chat_int}: {e}")
            raise NetworkError(f"Failed to send message to chat {chat_int}", original_error=e)

    def get_chat(self, chat_id: typing.Optional[typing.Union[int, str]], *, timeout: float = 10.0) -> dict[str, typing.Any]:
        """
        Retrieves information about a Telegram chat.

        Args:
            chat_id (int, str, optional): Target chat ID. If None or empty, uses self.default.
            timeout (float): Request timeout in seconds. Default 10.0, max 300.0.

        Returns:
            dict: Chat information including id, type, title, first_name, username, etc.

        Raises:
            ValidationError: If chat_id is missing or invalid.
            APIError: If the Telegram API returns an error.
            NetworkError: If the API request fails due to network issues.

        Example:
            >>> chat_info = bot.get_chat(123456789)
            >>> print(chat_info["first_name"])
        """
        validate_timeout(timeout)
        
        actual = chat_id if chat_id is not None and str(chat_id).strip() != "" else self.default
        if actual is None:
            raise ValidationError("Chat ID must be provided either as argument or as Bot.default", field="chat_id")
        try:
            chat_int = int(actual)
        except (TypeError, ValueError):
            raise ValidationError("Chat ID must be a number", field="chat_id")
        validate_chat_id_value(chat_int)

        url = f"https://api.telegram.org/bot{self.token}/getChat"
        payload: dict[str, int] = {"chat_id": chat_int}
        try:
            data = self._make_api_call(url, payload, timeout, method="get")
            logging.info(f"Информация о чате {chat_int} получена")
            return data.get("result", {})
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при получении информации о чате {chat_int}: {e}")
            raise NetworkError(f"Failed to retrieve chat information for {chat_int}", original_error=e)

    def get_user(self, user_id: typing.Union[int, str], *, timeout: float = 10.0) -> dict[str, typing.Any]:
        """
        Retrieves information about a Telegram user (private chat).

        This method works for private chats with individual users. It uses the getChat
        API endpoint which returns user information when called with a user's ID.

        Args:
            user_id (int, str): The user ID.
            timeout (float): Request timeout in seconds. Default 10.0, max 300.0.

        Returns:
            dict: User information including id, is_bot, first_name, username, etc.

        Raises:
            ValidationError: If user_id is invalid.
            APIError: If the Telegram API returns an error.
            NetworkError: If the API request fails due to network issues.

        Example:
            >>> user_info = bot.get_user(987654321)
            >>> print(f"Is bot: {user_info['is_bot']}")
        """
        validate_timeout(timeout)
        
        try:
            user_int = int(user_id)
        except (TypeError, ValueError):
            raise ValidationError("User ID must be a number", field="user_id")
        validate_chat_id_value(user_int)

        return self.get_chat(user_int, timeout=timeout)

    def get_updates(
        self,
        offset: typing.Optional[int] = None,
        limit: int = 100,
        *,
        timeout: float = 10.0,
    ) -> list[dict[str, typing.Any]]:
        """
        Retrieves incoming updates for the bot.

        Args:
            offset (int, optional): Identifier of the first update to return.
            limit (int): Limits the number of updates to be retrieved. Must be 1-100.
            timeout (float): Request timeout in seconds. Default 10.0.

        Returns:
            list: List of update objects returned by Telegram.
        """
        validate_timeout(timeout)
        if not isinstance(limit, int) or not (1 <= limit <= 100):
            raise ValidationError("Limit must be an integer between 1 and 100", field="limit")

        payload: dict[str, typing.Any] = {"limit": limit}
        if offset is not None:
            payload["offset"] = offset

        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        data = self._make_api_call(url, payload, timeout, method="get")
        logging.info("Updates successfully retrieved")
        return data.get("result", [])

    def close(self) -> None:
        if getattr(self, "session", None) is not None:
            logging.info("Закрытие сессии")
            try:
                self.session.close()
            finally:
                self.session = None

    # Контекстный менеджер
    def __enter__(self) -> "Bot":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        # Пытаемся закрыть сессию при сборке мусора, но без фатальных ошибок
        try:
            self.close()
        except Exception:
            pass


def _initialize_session() -> requests.Session:
    session = requests.Session()
    if not hasattr(session, "headers") or session.headers is None:
        session.headers = {}
    elif not isinstance(session.headers, dict):
        session.headers = dict(session.headers)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Content-Type": "application/json"
    })
    return session


def _validate_default(default: typing.Optional[typing.Union[int, object, str]]) -> typing.Optional[int]:
    if default is None:
        return None
    # Если это уже int
    if isinstance(default, int):
        return default
    # Если строка с цифрами
    if isinstance(default, str) and default.isdigit():
        return int(default)
    # Duck-typing: объект с атрибутом id (int или строка содержащая число)
    if hasattr(default, "id"):
        val = getattr(default, "id")
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    raise ValueError("default must be an int, a digit string, or an object with an integer 'id' attribute")


def _validate_timeout(timeout: float) -> None:
    return validate_timeout(timeout)


def run_ui(bot: Bot) -> None:
    def send() -> None:
        chat_raw = entry_chat.get().strip()
        text = entry_text.get().strip()
        if not chat_raw and bot.default is None:
            messagebox.showerror("Ошибка", "Chat ID не указан и значение по умолчанию не задано.")
            return
        if not text:
            messagebox.showerror("Ошибка", "Текст сообщения не может быть пустым.")
            return
        try:
            chat_arg = int(chat_raw) if chat_raw else None
            bot.send_message(chat_arg, text)
            messagebox.showinfo("Успех", "Сообщение отправлено!")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    root = tk.Tk()
    root.title("Telegram Bot UI")

    tk.Label(root, text="Chat ID:").pack(pady=5)
    entry_chat = tk.Entry(root)
    entry_chat.pack(pady=5)

    tk.Label(root, text="Текст сообщения:").pack(pady=5)
    entry_text = tk.Entry(root)
    entry_text.pack(pady=5)

    tk.Button(root, text="Отправить", command=send).pack(pady=10)

    root.mainloop()


def run_console(bot: Bot) -> None:
    while True:
        chat_id = input("Введите Chat ID (или 'exit' для выхода, пусто = использовать default): ").strip()
        if chat_id.lower() == "exit":
            break
        if chat_id == "" and bot.default is None:
            print("Ошибка: Chat ID не указан и значение по умолчанию не задано.")
            continue
        if chat_id != "" and not chat_id.isdigit():
            print("Ошибка: Chat ID должен быть числом.")
            continue
        text = input("Введите текст сообщения: ").strip()
        if not text:
            print("Ошибка: Текст сообщения не может быть пустым.")
            continue
        try:
            chat_arg = int(chat_id) if chat_id != "" else None
            bot.send_message(chat_arg, text)
            print("Сообщение отправлено!")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    try:
        bot = Bot(token="ВАШ_ТОКЕН")  # Замените на ваш токен
        mode = input("Выберите режим (ui/console): ").strip().lower()
        if mode == "ui":
            run_ui(bot)
        elif mode == "console":
            run_console(bot)
        else:
            print("Ошибка: Неверный режим. Используйте 'ui' или 'console'.")
    except Exception as e:
        logging.error(f"Ошибка при запуске программы: {e}")
