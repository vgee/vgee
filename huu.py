import typing
import json
import getpass
import aiogram
import requests  # type: ignore # добавлен импорт requests

class Bot:
    # конструктор
    def __init__(self, token: typing.Optional[str] = None, default: typing.Any = None, **kwargs: object) -> None:
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.default = default
        self.session = requests.Session()
        for key, value in kwargs.items():
            setattr(self, key, value)
    # метод для явного закрытия сессии
    def close(self):
        print("Session closed")
        self.session.close()
aiogram.Bot = Bot  # переопределение aiogram.Bot для использования нашего класса    

bot = Bot(token="my_token")  # создаем экземпляр Bot

print(bot.token)  # выведет: my_token
print(getpass.getuser())  # выведет: huu    
print(bot)  # выведет: <__main__.Bot object at ...>
print(json.dumps({"key": "value"}))  # выведет: '{"key": "value"}'
print(json.loads('{"key": "value"}'))  # выведет: {'key': 'value'}
bot.close()  # type: ignore # явное закрытие сессии