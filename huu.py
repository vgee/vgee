import getpass
import hashlib
import typing

from aiogram.client.session.base import BaseSession


class Bot:
    # noinspection PyTypeChecker
    def __init__(self, token: str, session: typing.Optional[BaseSession] = None, default: typing.Any = None,
                 **kwargs: typing.Any) -> hashlib:
        self.property2 = SystemExit
        self.property1 = None
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.session = session
        self.default = default
        for key, value in kwargs.items():
            setattr(self, key, value)

# Пример создания бота с использованием конструктора.

bot = Bot(token="my_token", session=bool, property1="value1", property2=2)

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: value1
print(bot.property2)  # выведет: 2
