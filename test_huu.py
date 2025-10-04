import unittest
from unittest.mock import patch, MagicMock
import huu
import requests

class TestBot(unittest.TestCase):
    @patch('huu._initialize_session')
    @patch('huu._validate_default')
    def test_init_with_token(self, mock_validate_default, mock_init_session):
        mock_validate_default.return_value = 123
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        bot = huu.Bot(token='token', default=123, allow_interactive=False)
        self.assertEqual(bot.token, 'token')
        self.assertEqual(bot.default, 123)
        self.assertEqual(bot.session, mock_session)
        self.assertFalse(bot.allow_interactive)

    def test_init_without_token_noninteractive(self):
        with self.assertRaises(ValueError):
            huu.Bot(token=None, allow_interactive=False)

    @patch('builtins.input', return_value='token')
    @patch('huu._initialize_session')
    @patch('huu._validate_default')
    def test_init_interactive(self, mock_validate_default, mock_init_session, mock_input):
        mock_validate_default.return_value = None
        mock_init_session.return_value = MagicMock()
        bot = huu.Bot(token=None, allow_interactive=True)
        self.assertEqual(bot.token, 'token')

    @patch('huu.requests.Session')
    def test_initialize_session(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        session = huu._initialize_session()
        self.assertEqual(session, mock_session)
        self.assertIn("User-Agent", session.headers)
        self.assertIn("Content-Type", session.headers)

    def test_validate_default_none(self):
        self.assertIsNone(huu._validate_default(None))

    def test_validate_default_int(self):
        self.assertEqual(huu._validate_default(123), 123)

    def test_validate_default_aiogram_chat(self):
        class DummyChat:
            id = 42
        dummy = DummyChat()
        with patch('huu.aiogram.types.Chat', DummyChat):
            self.assertEqual(huu._validate_default(dummy), 42)

    @patch('huu.requests.Session')
    def test_send_message_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='token', allow_interactive=False)
        bot.session = mock_session
        bot.send_message(123, "test")
        mock_session.post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('huu.requests.Session')
    def test_send_message_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.RequestException("fail")
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='token', allow_interactive=False)
        bot.session = mock_session
        with self.assertRaises(requests.exceptions.RequestException):
            bot.send_message(123, "test")

    @patch('huu.requests.Session')
    def test_close(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        bot = huu.Bot(token='token', allow_interactive=False)
        bot.session = mock_session
        bot.close()
        mock_session.close.assert_called_once()

    @patch('huu.tk.Tk')
    def test_run_ui(self, mock_tk):
        bot = MagicMock()
        root = MagicMock()
        mock_tk.return_value = root
        with patch('huu.tk.Label'), patch('huu.tk.Entry'), patch('huu.tk.Button'), patch('huu.messagebox'):
            huu.run_ui(bot)
        root.mainloop.assert_called_once()

    @patch('builtins.input', side_effect=['exit'])
    def test_run_console_exit(self, mock_input):
        bot = MagicMock()
        huu.run_console(bot)
        bot.send_message.assert_not_called()

    @patch('builtins.input', side_effect=['notanumber', 'exit'])
    def test_run_console_invalid_chat_id(self, mock_input):
        bot = MagicMock()
        huu.run_console(bot)
        bot.send_message.assert_not_called()

    @patch('builtins.input', side_effect=['123', '', 'exit'])
    def test_run_console_empty_text(self, mock_input):
        bot = MagicMock()
        huu.run_console(bot)
        bot.send_message.assert_not_called()

    @patch('builtins.input', side_effect=['123', 'hello', 'exit'])
    def test_run_console_success(self, mock_input):
        bot = MagicMock()
        huu.run_console(bot)
        bot.send_message.assert_called_once_with(123, 'hello')

if __name__ == '__main__':
    unittest.main()