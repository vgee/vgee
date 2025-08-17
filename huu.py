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
        default: typing.Any = None,
        allow_interactive: bool = True,
        **kwargs: object
    ) -> None:
        if token is None:
            if allow_interactive:
                token = input("Enter bot token: ")
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
        self.token = token
        self.default = default
        if self.default is not None:
            if isinstance(self.default, aiogram.types.Chat):
                self.default = self.default.id
            elif not isinstance(self.default, int):
                raise ValueError("default must be aiogram.types.Chat or int")
        self.allow_interactive = allow_interactive
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Content-Type": "application/json"
        })

    def send_message(self, chat_id: int, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Union[int, str]] = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            response = self.session.post(url, json=payload) # type: ignore
            response.raise_for_status()  # Проверка на HTTP ошибки
            logging.info(f"Сообщение отправлено в чат {chat_id}: {text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
            raise

    def close(self):
        print("Session closed")
        self.session.close()

    def __del__(self):
        self.close()


def run_ui(bot: Bot):
    def send():
        chat_id = entry_chat.get()
        text = entry_text.get()
        try:
            bot.send_message(int(chat_id), text)
            messagebox.showinfo("Успех", "Сообщение отправлено!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    root = tk.Tk()
    root.title("Telegram Bot UI")

    tk.Label(root, text="Chat ID:").pack()
    entry_chat = tk.Entry(root)
    entry_chat.pack()

    tk.Label(root, text="Текст сообщения:").pack()
    entry_text = tk.Entry(root)
    entry_text.pack()

    tk.Button(root, text="Отправить", command=send).pack()

    root.mainloop()


def run_console(bot: Bot):
    while True:
        chat_id = input("Введите Chat ID (или 'exit' для выхода): ")
        if chat_id.lower() == "exit":
            break
        try:
            chat_id = int(chat_id)
        except ValueError:
            print("Ошибка: Chat ID должен быть целым числом.")
            continue
        text = input("Введите текст сообщения: ")
        try:
            bot.send_message(chat_id, text)
            print("Сообщение отправлено!")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    bot = Bot(token="ВАШ_ТОКЕН")  # Замените на ваш токен
    mode = input("Выберите режим (ui/console): ").strip().lower()
    if mode == "ui":
        run_ui(bot)
    else:
        run_console(bot)
