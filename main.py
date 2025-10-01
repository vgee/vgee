from config import Config
from huu import Bot

if __name__ == "__main__":
    # Ensure Config.DEFAULT_SETTING is of the correct type (int, Chat, or None)
    bot = Bot(token=Config.TOKEN, default=None)
    print(bot)
    bot.close()
    # bot.run() # type: ignore  
    # bot.start() # type: ignore
    