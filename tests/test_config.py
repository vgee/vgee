import unittest
from config import Config

class TestConfig(unittest.TestCase):
    def test_token(self):
        self.assertEqual(Config.TOKEN, "your_default_token_here")

    def test_default_setting(self):
        self.assertEqual(Config.DEFAULT_SETTING, "default_value")

if __name__ == "__main__":
    unittest.main()
