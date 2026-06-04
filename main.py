from config import Config
from huu import Bot

if __name__ == "__main__":
    Config.validate()
    bot = Bot(token=Config.TOKEN, default=None)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Bot stopped")
    finally:
        bot.close()
    