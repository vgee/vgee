import typing
import requests
import aiogram  # type: ignore
import tkinter as tk
from tkinter import messagebox


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
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

    def close(self):
        print("Session closed")
        self.session.close()

    def __del__(self):
        self.close()


def send():
    chat_id = entry_chat.get()
    text = entry_text.get()
    try:
        bot.send_message(int(chat_id), text)
        messagebox.showinfo("Успех", "Сообщение отправлено!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


bot = Bot(token="ВАШ_ТОКЕН")  # Замените на ваш токен

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
