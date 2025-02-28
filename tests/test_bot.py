import unittest
from huu import Bot

class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(token="test_token", default="test_default")

    def test_token(self):
        self.assertEqual(self.bot.token, "test_token")

    def test_default(self):
        self.assertEqual(self.bot(), "test_default")

    def test_repr(self):
        self.assertEqual(repr(self.bot), "Bot(token=test_token, default=test_default)")

    def test_eq(self):
        other_bot = Bot(token="test_token", default="test_default")
        self.assertTrue(self.bot == other_bot)

    def test_close(self):
        self.bot.close()
        self.new_method()

    def new_method(self):
        self.assertFalse(self.bot.session)

if __name__ == "__main__":
    unittest.main()
