# python
import logging
import tkinter as tk
import typing
from tkinter import messagebox

import requests # type: ignore

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Bot:
    """
    Небольшой HTTP‑клиент для отправки сообщений в Telegram через HTTP API.
    Поддерживает значение 'default' как значение chat_id по умолчанию,
    контекстный менеджер и безопасное закрытие сессии.
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
                raise ValueError("Token must be provided if interactive input is not allowed")
        self.token = token
        self.default = _validate_default(default)
        self.allow_interactive = allow_interactive
        self.session = _initialize_session()

    def send_message(self, chat_id: typing.Optional[typing.Union[int, str]], text: str, *, timeout: float = 10.0) -> None:
        """
        Отправляет сообщение. Если chat_id не передан, используется self.default.
        """
        actual = chat_id if chat_id is not None and str(chat_id).strip() != "" else self.default
        if actual is None:
            raise ValueError("Chat ID must be provided either as argument or as Bot.default")
        try:
            chat_int = int(actual)
        except (TypeError, ValueError):
            raise ValueError("Chat ID должен быть числом")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Union[str, int]] = {
            "chat_id": chat_int,
            "text": text
        }
        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            logging.info(f"Сообщение отправлено в чат {chat_int}: {text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при отправке сообщения в чат {chat_int}: {e}")
            raise

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
