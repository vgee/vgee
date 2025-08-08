import os

class Config:
    TOKEN = os.getenv("BOT_TOKEN", "your_default_token_here")
    DEFAULT_SETTING = os.getenv("DEFAULT_SETTING", "default_value")
    PREFIX = os.getenv("PREFIX", "!")
    def __init__(self):
        if not self.TOKEN:
            raise ValueError("BOT_TOKEN is not set in the environment variables")
        else:
            print("Bot token is set")
            if not self.PREFIX:
                if self.DEFAULT_SETTING:
                    print("Prefix is set to default value")
                else:
                    raise ValueError("PREFIX is not set in the environment variables")