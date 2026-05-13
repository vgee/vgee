import unittest
from unittest.mock import patch, MagicMock
import huu
import requests

class TestValidation(unittest.TestCase):
    def test_validate_token_empty(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_token("")
        self.assertIn("empty", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_too_short(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_token("short")
        self.assertIn("short", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_non_ascii(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_token("токен123456")
        self.assertIn("ascii", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_valid(self):
        huu._validate_token("validtoken1234567890")  # Should not raise

    def test_validate_text_empty(self):
        with self.assertRaises(huu.ValidationError):
            huu._validate_text("")

    def test_validate_text_whitespace_only(self):
        with self.assertRaises(huu.ValidationError):
            huu._validate_text("   ")

    def test_validate_text_too_long(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_text("x" * 5000)
        self.assertIn("4096", str(context.exception))
        self.assertEqual(context.exception.field, "text")

    def test_validate_text_valid(self):
        huu._validate_text("Valid message text")  # Should not raise

    def test_validate_chat_id_value_zero(self):
        with self.assertRaises(huu.ValidationError):
            huu._validate_chat_id_value(0)

    def test_validate_chat_id_value_out_of_range(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_chat_id_value(9999999999999)
        self.assertIn("range", str(context.exception).lower())
        self.assertEqual(context.exception.field, "chat_id")

    def test_validate_chat_id_value_valid(self):
        huu._validate_chat_id_value(123456)  # Should not raise
        huu._validate_chat_id_value(-123456)  # Negative is valid for groups

    def test_validate_timeout_non_positive(self):
        with self.assertRaises(huu.ValidationError):
            huu._validate_timeout(0)
        with self.assertRaises(huu.ValidationError):
            huu._validate_timeout(-5)

    def test_validate_timeout_too_large(self):
        with self.assertRaises(huu.ValidationError) as context:
            huu._validate_timeout(500)
        self.assertIn("300", str(context.exception))
        self.assertEqual(context.exception.field, "timeout")

    def test_validate_timeout_valid(self):
        huu._validate_timeout(10.0)  # Should not raise
        huu._validate_timeout(300)  # Max value

class TestBot(unittest.TestCase):
    @patch('huu._initialize_session')
    @patch('huu._validate_default')
    def test_init_with_token(self, mock_validate_default, mock_init_session):
        mock_validate_default.return_value = 123
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', default=123, allow_interactive=False)
        self.assertEqual(bot.token, 'validtoken1234')
        self.assertEqual(bot.default, 123)
        self.assertEqual(bot.session, mock_session)
        self.assertFalse(bot.allow_interactive)

    def test_init_without_token_noninteractive(self):
        with self.assertRaises(ValueError):
            huu.Bot(token=None, allow_interactive=False)

    @patch('builtins.input', return_value='validtoken1234')
    @patch('huu._initialize_session')
    @patch('huu._validate_default')
    def test_init_interactive(self, mock_validate_default, mock_init_session, mock_input):
        mock_validate_default.return_value = None
        mock_init_session.return_value = MagicMock()
        bot = huu.Bot(token=None, allow_interactive=True)
        self.assertEqual(bot.token, 'validtoken1234')

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

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        bot.send_message(123, "test")
        mock_session.post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('huu.requests.Session')
    def test_send_message_empty_text(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.ValidationError):
            bot.send_message(123, "")

    @patch('huu.requests.Session')
    def test_send_message_text_too_long(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.ValidationError):
            bot.send_message(123, "x" * 5000)

    @patch('huu.requests.Session')
    def test_send_message_invalid_timeout(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.ValidationError):
            bot.send_message(123, "test", timeout=500)

    @patch('huu.requests.Session')
    def test_send_message_invalid_chat_id(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.ValidationError):
            bot.send_message(0, "test")

    @patch('huu.requests.Session')
    def test_send_message_network_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.RequestException("fail")
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        with self.assertRaises(huu.NetworkError):
            bot.send_message(123, "test")

    @patch('huu.requests.Session')
    def test_get_chat_api_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "error_code": 400,
            "description": "Chat not found"
        }
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.APIError) as context:
            bot.get_chat(999)
        self.assertEqual(context.exception.error_code, 400)

    @patch('huu.requests.Session')
    def test_get_chat_network_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout("timeout")
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.NetworkError):
            bot.get_chat(123)

    @patch('huu.requests.Session')
    def test_close(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
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

    @patch('huu.requests.Session')
    def test_get_chat_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "id": 123,
                "type": "private",
                "first_name": "John",
                "username": "johndoe"
            }
        }
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        chat_info = bot.get_chat(123)
        
        self.assertEqual(chat_info["id"], 123)
        self.assertEqual(chat_info["type"], "private")
        self.assertEqual(chat_info["first_name"], "John")
        mock_session.get.assert_called_once()

    @patch('huu.requests.Session')
    def test_get_chat_api_error_old(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "error_code": 400,
            "description": "Chat not found"
        }
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(huu.APIError) as context:
            bot.get_chat(999)
        self.assertEqual(context.exception.error_code, 400)
        self.assertIn("Chat not found", context.exception.description)

    @patch('huu.requests.Session')
    def test_get_user_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "id": 456,
                "is_bot": False,
                "first_name": "Jane",
                "username": "janedoe"
            }
        }
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        user_info = bot.get_user(456)
        
        self.assertEqual(user_info["id"], 456)
        self.assertEqual(user_info["is_bot"], False)
        self.assertEqual(user_info["first_name"], "Jane")

if __name__ == '__main__':
    unittest.main()