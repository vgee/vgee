import typing
import json
import getpass
import aiogram
import requests  # type: ignore # добавлен импорт requests

class Bot:
    # конструктор
    def __init__(self, token: typing.Optional[str] = None, default: typing.Any = None, allow_interactive: bool = True, **kwargs: object) -> None:
        if token is None:
            if allow_interactive:
        # self.session = requests.Session()  # Удалено, так как не используется
            else:
                raise ValueError("Token must be provided when interactive input is disabled.")
    # метод для явного закрытия сессии
    def close(self):
        print("Session closed")
        # self.session.close()  # Удалено, так как session не используется
aiogram.Bot = Bot  # переопределение aiogram.Bot для использования нашего класса    
            setattr(Self, key, value)
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