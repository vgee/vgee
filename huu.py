import typing
import json
import getpass
import aiogram
import requests  # type: ignore # добавлен импорт requests


def property():
    pass  # заглушка для декоратора property 


class Bot:
    # конструктор
    @property
    def token(self):
        return self._token

    def __init__(self, token: str, default: typing.Any = None, **kwargs: object) -> None:
        self.token = getpass.getpass("Enter your token: ") if token is None else token
        self.default = default
        self.session = requests.Session()
        for key, value in kwargs.items():
            setattr(self, key, value)

    # деструктор
    def __del__(self):
        print("Destructor called")
        self.close()

    # метод для явного закрытия сессии
    def close(self):
        print("Session closed")
        self.session.close()

    def __repr__(self):
        return f'Bot(token={self.token}, default={self.default})'


    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    def __call__(self):
        return self.default

    def __eq__(self, other):
        if isinstance(other, Bot):
            return self.token == other.token and self.default == other.default
        return False


# Пример создания бота с использованием конструктора.
bot = Bot(token="my_token")
# Доступ к свойствам
print(bot.token)  # выведет: my_token
print(getpass.getuser())  # выведет: huu    
print(bot)  # выведет: Bot(token=my_token, default=None)
print(bot == bot)  # выведет: True
print(bot())  # выведет: None
json.dumps({"key": "value"})  # выведет: '{"key": "value"}'
json.loads('{"key": "value"}')  # выведет: {'key': 'value'}
bot.close()  # явное закрытие сессии
