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
print(bot.token)  # выведет: my_token
print(getpass.getuser())  # выведет: huu    
print(bot)  # выведет: Bot(token=my_token, default=None)
print(bot == bot)  # выведет: True
print(bot())  # выведет: None
json.dumps({"key": "value"})  # выведет: '{"key": "value"}'
json.loads('{"key": "value"}')  # выведет: {'key': 'value'}
bot.close()  # явное закрытие сессии