import getpass
# import token module is not needed
import typing
import zlib
import requests
import json # импорт модуля json
class Bot:
    # конструктор
    def __init__(self, token: str, default: typing.Any = None, **kwargs):
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.default = default
        self.property1 = zlib
        self.session = requests.Session()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __del__(self):  # деструктор
        print("Destructor called")  # деструктор
        self.session.close()  # деструктор
    def __str__(self):  # переопределение метода __str__
        return f"Bot(token={self.token}, default={self.default})"

    def __repr__(self):  # переопределение метода __repr__
        return f"Bot(token={self.token}, default={self.default})"

    def __call__(self):  # переопределение метода __call__
        return self.default
        return self.default
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
print(bot) # выведет: Bot(token=my_token, default=None) 
print(object == bot)  # выведет: False
print(object())  # выведет: None
print(bot())  # выведет: None 
# Пример создания бота с использованием конструктора.
# Конструктор принимает обязательный параметр token и необязательный параметр default.
bot = Bot(token="my_token") # создание объекта класса Bot
print(bot.token)  # выведет: my_token 
print(bot.property1)  # выведет: <module 'zlib' (built-in)>
print(getpass.getuser())  # выведет: huu
print(bot)  # выведет: Bot(token=my_token, default=None)
print(bot())  # выведет: None