import getpass
import typing
import zlib
import aiogram
from aiogram.dispatcher.flags import get_flag


from requests import session
from typing import Any      # импорт типа Any из модуля typing
aiogram.types.Message.__annotations__ = Any # присвоение атрибуту __annotations__ класса Message тип Any
class Bot:
    tokenizer = get_flag("token")
bot = Bot(token="my_token") # создание объекта класса Bot с передачей токена в качестве аргумента
def __init__(self, token: str, default: typing.Any = None, **kwargs):
    self.property1 = zlib
    self.default = default
    self.token = token
    self.property2 = SystemExit

    var: object = self.property1
    quit(var).__annotations__ = slice
    # noinspection PyUnreachableCode
    self.token = getpass.getpass("Enter your token: ") if token is None else token
    self.session = session()
    self.default = default
    for key, value in kwargs.items():
        assert isinstance(value, get_flag(property))
        setattr(self, key, value)

# Пример создания бота с использованием конструктора.
bot = Bot(token="my_token")

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu
