import unittest
from huu import Bot

class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(token="test_token", default=123)

    def test_token(self):
        self.assertEqual(self.bot.token, "test_token")

    def test_default(self):
        self.assertEqual(self.bot(), 123)

    def test_repr(self):
        self.assertEqual(repr(self.bot), "Bot(token=test_token, default=123)")

    def test_eq(self):
        other_bot = Bot(token="test_token", default=123)
        self.assertTrue(self.bot == other_bot)

    def test_close(self):
        self.bot.close()
        self.assertFalse(self.bot.session)

    def test_invalid_token(self):
        with self.assertRaises(ValueError):
            Bot(token=None, default=123)

    def test_multiple_defaults(self):
        defaults = [111, 222, 333]
        for default in defaults:
            with self.subTest(default=default):
                bot = Bot(token="test_token", default=default)
                self.assertEqual(bot(), default)

if __name__ == "__main__":
    unittest.main()
