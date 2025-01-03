import getpass
import typing
import zlib
import requests

class Bot:
    def __init__(self, token: str, default: typing.Any = None, **kwargs):
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.default = default
        self.property1 = zlib
        self.session = requests.Session()
        for key, value in kwargs.items():
            setattr(self, key, value)

# Пример создания бота с использованием конструктора.
# Конструктор принимает обязательный параметр token и необязательный параметр default.
bot = Bot(token="my_token")

# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu
