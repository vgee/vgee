import os

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class Config:
    TOKEN = os.getenv("BOT_TOKEN")
    DEFAULT_SETTING = os.getenv("DEFAULT_SETTING", "default_value")

    @classmethod
    def validate(cls):
        if not cls.TOKEN:
            raise ConfigError("BOT_TOKEN is not set in environment variables.")

    @classmethod
    def load(cls):
        cls.validate()
        return cls()

# Пример использования:
# try:
#     config = Config.load()
#     token = config.TOKEN
#     default_setting = config.DEFAULT_SETTING
# except ConfigError as e:
#     print(f"Configuration error: {e}")
#     exit()
