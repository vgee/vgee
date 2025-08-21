import unittest
from unittest.mock import patch, MagicMock
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
        self.assertFalse(self.bot.session)

    def test_invalid_token(self):
        with self.assertRaises(ValueError):
            Bot(token=None, default="test_default")

    def test_method_behavior(self):
        with patch("huu.Bot.some_method") as mock_method:
            mock_method.return_value = "mocked_result"
            result = self.bot.some_method()
            self.assertEqual(result, "mocked_result")
            mock_method.assert_called_once()

    def test_multiple_defaults(self):
        defaults = ["default1", "default2", "default3"]
        for default in defaults:
            with self.subTest(default=default):
                bot = Bot(token="test_token", default=default)
                self.assertEqual(bot(), default)

if __name__ == "__main__":
    unittest.main()
