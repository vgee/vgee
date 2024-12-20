import getpass
import typing
import zlib
from requests import session

class Bot:
    def __init__(self, token: str, default: typing.Any = None, **kwargs):
        self.property1 = zlib
        self.default = default
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
