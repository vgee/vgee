import os

class Config:
    TOKEN = os.getenv("BOT_TOKEN", "your_default_token_here")
    DEFAULT_SETTING = os.getenv("DEFAULT_SETTING", "default_value")
