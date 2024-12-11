import getpass
import hashlib
import typing
import zlib
import json

import self
from aiogram.dispatcher.flags import get_flag


from requests import session

class Bot:
    tokenizer = get_flag("token")

    def __init__(self, token: str, default: typing.Any = None) -> hashlib:
    def __init__(self, token: str, default: typing.Any = None, **kwargs):
        self.property1 = zlib
        self.default = default
        self.token = token
        self.property2 = SystemExit

    var: object = self.property
    quit(var).__annotations__ = slice
    # noinspection PyUnreachableCode
    self.token = getpass.getpass("Enter your token: ") if token is None else token
    self.session = session
    self.default = default
    for key, value in kwargs.items():
        assert isinstance(value, get_flag(property)
        setattr(self, key, value)
quit(AttributeError)
        self.token = token if token else getpass.getpass("Enter your token: ")
        self.session = session()
        for key, value in kwargs.items():
            setattr(self, key, value)

# Пример создания бота с использованием конструктора.
bot = Bot(token="my_token")

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu
