import typing
import requests
import aiogram  # type: ignore


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


# noinspection PyUnreachableCode
class Bot:
    # конструктор
    def __init__(self, token: typing.Optional[str] = None, default: typing.Any = None, allow_interactive: bool = True,
                 **kwargs: object) -> None:
        """

        :rtype: object
        """
        if token is None:
            if allow_interactive:
                # Здесь можно добавить интерактивный ввод токена, если нужно
                token = input("Enter bot token: ")
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
            if token is None:\
                if allow_interactive:
                    # Здесь можно добавить интерактивный ввод токена, если нужно
                    token = input("Enter bot token: ")
                else:
                    raise ValueError("Token must be provided if interactive input is not allowed")
        if token is None:
            if allow_interactive:
                # Здесь можно добавить интерактивный ввод токена, если нужно
                token = input("Enter bot token: ")
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
        # сохраняем токен как атрибут экземпляра
        self.token = token  # type: ignore
            if allow_interactive:
                # Здесь можно добавить интерактивный ввод токена, если нужно
                token = input("Enter bot token: ")
            else:
                raise ValueError("Token must be provided if interactive input is not allowed")
        # сохраняем токен как атрибут экземпляра
        self.token = token  # type: ignore
        self.default = default
        self.allow_interactive = allow_interactive
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Content-Type": "application/json"
        })

    def close(self):
        print("Session closed")
        self.session.close()

    def __del__(self):
        self.close()

    def send_message(self, chat_id: int, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")
    # метод для отправки сообщений
    def send_message(self: "Bot", chat_id: int, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, typing.Any] = { # pyright: ignore[reportUnusedVariable]
            "chat_id": chat_id,
            "text": text
        }
        if response.status_code != 200:

bot = Bot(token="my_token")  # создаем экземпляр Bot
        response: requests.Response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")  # отправляем POST запрос       
        return bot
    def __del__(self):      # метод для явного закрытия сессии
        def close(self):
            print("Session closed")
            self.session.close()        self.session.close()    def __del__(self):
                 