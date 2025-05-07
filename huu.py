import typing
import json
import getpass
import aiogram  # type: ignore  # добавлен импорт aiogram
import requests  # type: ignore  # добавлен импорт requests
import logging  # type: ignore  # добавлен импорт logging
import asyncio  # type: ignore  # добавлен импорт asyncio

class BotError(Exception):
   """Базовый класс для ошибок бота."""
   pass

class BotTokenError(BotError):
   """Ошибка, связанная с токеном бота.

   Эта ошибка должна быть вызвана, если токен бота отсутствует, недействителен 
   или не соответствует ожидаемому формату.
   """
   pass

class Bot:
   # атрибуты класса
   __slots__ = ('__token', '__default', 'session')

   # конструктор
   def __init__(self, token: str, default: typing.Any = None, **kwargs):
       token = getpass.getpass("Enter your token: ") if token is None else token
       if not token:
           raise ValueError("Token cannot be None or empty")
       self.token = token
       self.default = default
       self.session = requests.Session()
       for key, value in kwargs.items():
           setattr(self, key, value)

   # метод для явного закрытия сессии
   def close(self):
       print("Session closed")
       self.session.close()

   # реализация контекстного менеджера
   def __enter__(self):
       return self

   def __exit__(self, exc_type, exc_value, traceback):
       self.close()

   def __repr__(self):
       token_repr = self.token if hasattr(self, 'token') else "Uninitialized"
       default_repr = self.default if hasattr(self, 'default') else "Uninitialized"
       return f"Bot(token={token_repr}, default={default_repr})"

   @property
   def token(self):
       return self.__token

   @token.setter
   def token(self, value):
       if not value:
           raise ValueError("Token cannot be None")
       self.__token = value

   def __call__(self):
       """
       Returns the default value associated with the bot.

       This method allows an instance of the Bot class to be called as a function,
       returning the value of the 'default' attribute.
       """
       return self.default

   def __eq__(self, other):
       """
       Compares two Bot instances for equality.

       Two Bot instances are considered equal if their token and default attributes are identical.
       """
       if isinstance(other, Bot):
           return self.token == other.token and self.default == other.default

import os

# Retrieve the token securely from an environment variable
with Bot(token=os.getenv("BOT_TOKEN", None)) as bot:
   # Пример создания бота с использованием конструктора, демонстрирующий обработку токена, управление сессией и доступ к свойствам.
   print(bot.token)  # выведет: my_token
   print(bot)  # выведет: Bot(token=my_token, default=None)
   print(bot == bot)  # выведет: True
   print(bot())  # выведет: None
   json.dumps({"key": "value"})  # выведет: '{"key": "value"}'
   json.loads('{"key": "value"}')  # выведет: {'key': 'value'}
# Сессия автоматически закрывается при выходе из блока with
