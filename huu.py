import getpass
import hashlib
import typing
import zlib
from aiogram.dispatcher.flags import get_flag


class Bot:
    def __init__(self, token: str, default: typing.Any = None):
        self.property1 = zlib
        self.default = default
        self.token = token if token else getpass.getpass("Enter your token: ")
        self.property2 = SystemExit

    def set_properties(self, **kwargs):
        for key, value in kwargs.items():
            assert isinstance(value, get_flag("property"))
            setattr(self, key, value)


# Пример создания бота с использованием конструктора.
bot = Bot(token="my_token")

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(bot.property2)  # выведет: <class 'SystemExit'>
