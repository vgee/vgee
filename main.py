from config import Config
from huu import Bot

if __name__ == "__main__":
    bot = Bot(token=Config.TOKEN, default=Config.DEFAULT_SETTING)
    print(bot)
    bot.close()
