import typing
import requests  # импортируем requests для работы с HTTP запросами
import self  # type: ignore # добавлен импорт requests
import aiogram  # type: ignore # добавлен импорт aiogram
class Bot:
    # конструктор
    def __init__(self, token: typing.Optional[str] = None, default: typing.Any = None, allow_interactive: bool = True, **kwargs: object) -> None:
        if token is None:
            if allow_interactive:
                # Здесь можно добавить интерактивный ввод токена, если нужно
                token = input("Enter bot token: ")
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
        # сохраняем токен как атрибут экземпляра
        self.token = token  # type: ignore
        self.default = default
        self.allow_interactive = allow_interactive
        self.session = requests.Session()  # создаем сессию requests

    # метод для явного закрытия сессии
    def close(self):
        print("Session closed")
    # метод для отправки сообщений
    def send_message(self: "Bot", chat_id: int, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Any] = {
            "chat_id": chat_id,
            "text": text
        }
        response: requests.Response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

bot = Bot(token="my_token")  # создаем экземпляр Bot