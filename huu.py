# python
"""
Telegram Bot HTTP Client Module

This module provides a lightweight HTTP client for interacting with the Telegram Bot API.
It includes comprehensive input validation, error handling, and support for both console
and GUI interfaces.

Classes:
    BotError: Base exception for all bot-related errors
    ValidationError: Raised when input validation fails
    APIError: Raised when Telegram API returns an error
    NetworkError: Raised when network communication fails
    Bot: Main class for interacting with Telegram Bot API

Functions:
    _validate_token: Validates bot token format and content
    _validate_text: Validates message text for constraints
    _validate_chat_id_value: Validates chat ID format
    _validate_timeout: Validates timeout values
    _initialize_session: Creates and configures HTTP session
    _validate_default: Validates default chat ID value
    run_ui: Runs the bot in UI mode (tkinter)
    run_console: Runs the bot in console mode

Example:
    Basic usage:
    >>> bot = Bot(token="YOUR_BOT_TOKEN", default=123456789)
    >>> bot.send_message(chat_id=123456789, text="Hello, world!")
    >>> chat_info = bot.get_chat(123456789)
    >>> bot.close()

    Using context manager:
    >>> with Bot(token="YOUR_BOT_TOKEN") as bot:
    ...     bot.send_message(chat_id=123456789, text="Hello!")
"""
import logging
import tkinter as tk
import typing
from tkinter import messagebox

import requests # type: ignore

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BotError(Exception):
    """Base exception for all bot-related errors."""

    pass


class ValidationError(BotError):
    """Raised when input validation fails.

    This exception is raised when bot parameters (token, chat_id, text, timeout)
    fail validation checks.

    Attributes:
        message (str): Description of the validation error
        field (str): Name of the field that failed validation
    """

    def __init__(self, message: str, field: typing.Optional[str] = None) -> None:
        """Initialize ValidationError.

        Args:
            message: Description of the validation error
            field: Name of the field that failed validation
        """
        self.message = message
        self.field = field
        super().__init__(message)


class APIError(BotError):
    """Raised when Telegram API returns an error.

    This exception is raised when the Telegram Bot API returns an error response
    (ok=False).

    Attributes:
        message (str): Error message from API
        error_code (int): Error code from API (if available)
        description (str): Detailed error description from API
    """

    def __init__(self, message: str, error_code: typing.Optional[int] = None, description: typing.Optional[str] = None) -> None:
        """Initialize APIError.

        Args:
            message: Error message
            error_code: Telegram API error code
            description: Detailed error description from API
        """
        self.message = message
        self.error_code = error_code
        self.description = description
        full_message = f"{message}"
        if error_code:
            full_message += f" (error_code: {error_code})"
        if description:
            full_message += f" - {description}"
        super().__init__(full_message)


class NetworkError(BotError):
    """Raised when network communication fails.

    This exception is raised when HTTP requests to the Telegram API fail due to
    network issues (connection errors, timeouts, etc.).

    Attributes:
        message (str): Description of the network error
        original_error (Exception): The original requests exception
    """

    def __init__(self, message: str, original_error: typing.Optional[Exception] = None) -> None:
        """Initialize NetworkError.

        Args:
            message: Description of the network error
            original_error: The original requests.RequestException
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)


def _validate_token(token: typing.Optional[str]) -> None:
    """Validates that token is not empty and has reasonable length.

    Args:
        token: The bot token to validate

    Raises:
        ValidationError: If token is invalid
    """
    if not token:
        raise ValidationError("Token cannot be empty", field="token")
    token_str = str(token).strip()
    if len(token_str) < 10:
        raise ValidationError("Token appears too short (minimum 10 characters)", field="token")
    if not token_str.isascii():
        raise ValidationError("Token must contain only ASCII characters", field="token")


def _validate_text(text: str) -> None:
    """Validates that message text is not empty and within limits.

    Args:
        text: The message text to validate

    Raises:
        ValidationError: If text is invalid
    """
    if not text:
        raise ValidationError("Message text cannot be empty", field="text")
    if len(text) > 4096:
        raise ValidationError("Message text exceeds maximum length of 4096 characters", field="text")
    if text.isspace():
        raise ValidationError("Message text cannot be only whitespace", field="text")


def _validate_chat_id_value(chat_id: int) -> None:
    """Validates that chat_id is a valid integer.

    Args:
        chat_id: The chat ID to validate

    Raises:
        ValidationError: If chat_id is invalid
    """
    if not isinstance(chat_id, int):
        raise ValidationError("Chat ID must be an integer", field="chat_id")
    if chat_id == 0:
        raise ValidationError("Chat ID cannot be zero", field="chat_id")
    # Telegram chat IDs can be negative (for groups/channels)
    if abs(chat_id) > 999999999999:
        raise ValidationError("Chat ID appears invalid (out of range)", field="chat_id")


def _validate_timeout(timeout: float) -> None:
    """Validates that timeout is a positive number.

    Args:
        timeout: The timeout value to validate

    Raises:
        ValidationError: If timeout is invalid
    """
    if not isinstance(timeout, (int, float)):
        raise ValidationError("Timeout must be a number", field="timeout")
    if timeout <= 0:
        raise ValidationError("Timeout must be positive", field="timeout")
    if timeout > 300:
        raise ValidationError("Timeout exceeds maximum of 300 seconds", field="timeout")


class Bot:
    """
    Lightweight HTTP client for Telegram Bot API.

    This class provides methods to send messages and retrieve chat/user information
    from Telegram. It includes comprehensive input validation, error handling, and
    support for context managers.

    Attributes:
        token (str): Telegram bot API token
        default (Optional[int]): Default chat ID for operations
        allow_interactive (bool): Whether to allow interactive input
        session (requests.Session): HTTP session for API calls

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
        **kwargs: object
    ) -> None:
        if not token:
            if allow_interactive:
                token = input("Enter bot token: ").strip()
            else:
                raise ValidationError("Token must be provided if interactive input is not allowed", field="token")
        _validate_token(token)
        self.token = token
        self.default = _validate_default(default)
        self.allow_interactive = allow_interactive
        self.session = _initialize_session()

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
        _validate_text(text)
        _validate_timeout(timeout)
        
        actual = chat_id if chat_id is not None and str(chat_id).strip() != "" else self.default
        if actual is None:
            raise ValidationError("Chat ID must be provided either as argument or as Bot.default", field="chat_id")
        try:
            chat_int = int(actual)
        except (TypeError, ValueError):
            raise ValidationError("Chat ID must be a number", field="chat_id")
        _validate_chat_id_value(chat_int)

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Union[str, int]] = {
            "chat_id": chat_int,
            "text": text
        }
        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise APIError("Failed to send message", description=data.get("description"))
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
        _validate_timeout(timeout)
        
        actual = chat_id if chat_id is not None and str(chat_id).strip() != "" else self.default
        if actual is None:
            raise ValidationError("Chat ID must be provided either as argument or as Bot.default", field="chat_id")
        try:
            chat_int = int(actual)
        except (TypeError, ValueError):
            raise ValidationError("Chat ID must be a number", field="chat_id")
        _validate_chat_id_value(chat_int)

        url = f"https://api.telegram.org/bot{self.token}/getChat"
        payload: dict[str, int] = {"chat_id": chat_int}
        try:
            response = self.session.get(url, params=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise APIError(
                    "Failed to get chat information",
                    error_code=data.get("error_code"),
                    description=data.get("description")
                )
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
        _validate_timeout(timeout)
        
        try:
            user_int = int(user_id)
        except (TypeError, ValueError):
            raise ValidationError("User ID must be a number", field="user_id")
        _validate_chat_id_value(user_int)

        return self.get_chat(user_int, timeout=timeout)

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
