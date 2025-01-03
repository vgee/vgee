import getpass
# import token module is not needed
import typing
import zlib
import requests
import json # импорт модуля json
class Bot:
    def __init__(self, token: str, default: typing.Any = None, **kwargs):
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.default = default
        self.property1 = zlib
        self.session = requests.Session()
        for key, value in kwargs.items():
            setattr(self, key, value)
x = Bot(token="my_token ")  # создание объекта класса Bot
print(x.token)  # выведет: my_token
print(x.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu' 
object = Bot(token="my_token")  # создание объекта класса Bot
# Пример создания бота с использованием конструктора.
# Конструктор принимает обязательный параметр token и необязательный параметр default.
bot = Bot(token="my_token")

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu