import typing
import requests
import aiogram  # type: ignore
import tkinter as tk
from tkinter import messagebox
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Bot:
    def __init__(
        self,
        token: typing.Optional[str] = None,
        default: typing.Optional[typing.Union[int, aiogram.types.Chat]] = None,
        allow_interactive: bool = True,
        **kwargs: object
    ) -> None:
        if not token:
            if allow_interactive:
                token = input("Enter bot token: ").strip()
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
        self.token = token
        self.default = self._validate_default(default)
        self.allow_interactive = allow_interactive
        self.session = self._initialize_session()

    @staticmethod
    def _validate_default(default: typing.Optional[typing.Union[int, aiogram.types.Chat]]) -> typing.Optional[int]:
        if default is None:
            return None
        if isinstance(default, aiogram.types.Chat):
            return default.id
        return default
        raise ValueError("default must be aiogram.types.Chat or int")

    @staticmethod
    def _initialize_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Content-Type": "application/json"
        })
        return session

    def send_message(self, chat_id: int, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, str | int] = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            logging.info(f"Сообщение отправлено в чат {chat_id}: {text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
            raise

    def close(self) -> None:
        logging.info("Закрытие сессии")
        self.session.close()

    def __del__(self) -> None:
        self.close()


def run_ui(bot: Bot) -> None:
    def send() -> None:
        chat_id = entry_chat.get().strip()
        text = entry_text.get().strip()
        if not chat_id or not text:
            messagebox.showerror("Ошибка", "Chat ID и текст сообщения не могут быть пустыми.")
            return
        try:
            bot.send_message(int(chat_id), text)
            messagebox.showinfo("Успех", "Сообщение отправлено!")
        except ValueError:
            messagebox.showerror("Ошибка", "Chat ID должен быть числом.")
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
        chat_id = input("Введите Chat ID (или 'exit' для выхода): ").strip()
        if chat_id.lower() == "exit":
            break
        if not chat_id.isdigit():
            print("Ошибка: Chat ID должен быть числом.")
            continue
        text = input("Введите текст сообщения: ").strip()
        if not text:
            print("Ошибка: Текст сообщения не может быть пустым.")
            continue
        try:
            bot.send_message(int(chat_id), text)
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
