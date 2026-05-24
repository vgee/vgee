import unittest
from unittest.mock import patch, MagicMock
import huu
import requests # type: ignore
from exceptions import ValidationError, APIError, NetworkError
from validators import validate_token, validate_text, validate_chat_id_value, validate_timeout
from retry import RetryConfig, retry_with_backoff
from response_validators import (
    ResponseValidator, validate_api_response, validate_message_result,
    validate_chat_result, validate_user_result, extract_result
)

class TestValidation(unittest.TestCase):
    def test_validate_token_empty(self):
        with self.assertRaises(ValidationError) as context:
            validate_token("")
        self.assertIn("empty", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_too_short(self):
        with self.assertRaises(ValidationError) as context:
            validate_token("short")
        self.assertIn("short", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_non_ascii(self):
        with self.assertRaises(ValidationError) as context:
            validate_token("токен123456")
        self.assertIn("ascii", str(context.exception).lower())
        self.assertEqual(context.exception.field, "token")

    def test_validate_token_valid(self):
        validate_token("validtoken1234567890")  # Should not raise

    def test_validate_text_empty(self):
        with self.assertRaises(ValidationError):
            validate_text("")

    def test_validate_text_whitespace_only(self):
        with self.assertRaises(ValidationError):
            validate_text("   ")

    def test_validate_text_too_long(self):
        with self.assertRaises(ValidationError) as context:
            validate_text("x" * 5000)
        self.assertIn("4096", str(context.exception))
        self.assertEqual(context.exception.field, "text")

    def test_validate_text_valid(self):
        validate_text("Valid message text")  # Should not raise

    def test_validate_chat_id_value_zero(self):
        with self.assertRaises(ValidationError):
            validate_chat_id_value(0)

    def test_validate_chat_id_value_out_of_range(self):
        with self.assertRaises(ValidationError) as context:
            validate_chat_id_value(9999999999999)
        self.assertIn("range", str(context.exception).lower())
        self.assertEqual(context.exception.field, "chat_id")

    def test_validate_chat_id_value_valid(self):
        validate_chat_id_value(123456)  # Should not raise
        validate_chat_id_value(-123456)  # Negative is valid for groups

    def test_validate_timeout_non_positive(self):
        with self.assertRaises(ValidationError):
            validate_timeout(0)
        with self.assertRaises(ValidationError):
            validate_timeout(-5)

    def test_validate_timeout_too_large(self):
        with self.assertRaises(ValidationError) as context:
            validate_timeout(500)
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
        with self.assertRaises(ValidationError):
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
        
        with self.assertRaises(ValidationError):
            bot.send_message(123, "")

    @patch('huu.requests.Session')
    def test_send_message_text_too_long(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(ValidationError):
            bot.send_message(123, "x" * 5000)

    @patch('huu.requests.Session')
    def test_send_message_invalid_timeout(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(ValidationError):
            bot.send_message(123, "test", timeout=500)

    @patch('huu.requests.Session')
    def test_send_message_invalid_chat_id(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(ValidationError):
            bot.send_message(0, "test")

    @patch('huu.requests.Session')
    def test_send_message_network_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.RequestException("fail")
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        with self.assertRaises(NetworkError):
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
        
        with self.assertRaises(APIError) as context:
            bot.get_chat(999)
        self.assertEqual(context.exception.error_code, 400)

    @patch('huu.requests.Session')
    def test_get_chat_network_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout("timeout")
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        
        with self.assertRaises(NetworkError):
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

    @patch('huu.requests.Session')
    def test_get_updates_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "ok": True,
            "result": [
                {"update_id": 1, "message": {"text": "hi"}}
            ]
        }
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        bot.session = mock_session
        updates = bot.get_updates(limit=1)

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]["update_id"], 1)
        mock_session.get.assert_called_once()

    def test_get_updates_invalid_limit(self):
        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        with self.assertRaises(ValidationError):
            bot.get_updates(limit=0)

    def test_bot_repr_eq_call(self):
        bot = huu.Bot(token='validtoken1234', allow_interactive=False, default='123')
        self.assertEqual(repr(bot), 'Bot(token=validtoken1234, default=123)')
        self.assertEqual(bot(), 123)
        self.assertEqual(bot, huu.Bot(token='validtoken1234', default='123'))


class TestRetry(unittest.TestCase):
    def test_retry_config_defaults(self):
        config = RetryConfig()
        self.assertEqual(config.max_attempts, 3)
        self.assertEqual(config.initial_delay, 0.5)
        self.assertEqual(config.max_delay, 10.0)
        self.assertEqual(config.backoff_factor, 2.0)
        self.assertIn(429, config.retry_on_codes)
        self.assertIn(500, config.retry_on_codes)

    def test_retry_config_custom_values(self):
        config = RetryConfig(max_attempts=5, initial_delay=1.0, max_delay=20.0, backoff_factor=1.5)
        self.assertEqual(config.max_attempts, 5)
        self.assertEqual(config.initial_delay, 1.0)
        self.assertEqual(config.max_delay, 20.0)
        self.assertEqual(config.backoff_factor, 1.5)

    def test_retry_config_minimum_values(self):
        config = RetryConfig(max_attempts=0, initial_delay=0.0, backoff_factor=0.5)
        self.assertEqual(config.max_attempts, 1)  # Enforced minimum of 1
        self.assertEqual(config.initial_delay, 0.1)  # Enforced minimum of 0.1
        self.assertEqual(config.backoff_factor, 1.0)  # Enforced minimum of 1.0

    @patch('retry.time.sleep')
    def test_retry_success_on_first_attempt(self, mock_sleep):
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def succeeds_first():
            return "success"
        
        result = succeeds_first()
        self.assertEqual(result, "success")
        mock_sleep.assert_not_called()

    @patch('retry.time.sleep')
    def test_retry_succeeds_after_timeout(self, mock_sleep):
        attempts = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.1))
        def fails_once():
            attempts[0] += 1
            if attempts[0] == 1:
                raise requests.exceptions.Timeout("Timeout")
            return "success"
        
        result = fails_once()
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 2)
        mock_sleep.assert_called_once()

    @patch('retry.time.sleep')
    def test_retry_exhausts_attempts(self, mock_sleep):
        @retry_with_backoff(RetryConfig(max_attempts=2, initial_delay=0.1))
        def always_fails():
            raise requests.exceptions.Timeout("Timeout")
        
        with self.assertRaises(NetworkError) as context:
            always_fails()
        self.assertIn("Failed after 2 attempts", str(context.exception))

    @patch('retry.time.sleep')
    def test_retry_with_connection_error(self, mock_sleep):
        attempts = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.1))
        def fails_connection():
            attempts[0] += 1
            if attempts[0] < 3:
                raise requests.exceptions.ConnectionError("Connection failed")
            return "success"
        
        result = fails_connection()
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 3)

    @patch('retry.time.sleep')
    def test_retry_with_retriable_http_error(self, mock_sleep):
        attempts = [0]
        
        def mock_response():
            mock_resp = MagicMock()
            mock_resp.status_code = 503
            return mock_resp
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.1))
        def fails_http():
            attempts[0] += 1
            if attempts[0] < 3:
                error = requests.exceptions.HTTPError()
                error.response = mock_response()
                raise error
            return "success"
        
        result = fails_http()
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 3)

    def test_retry_non_retriable_http_error(self):
        def mock_response():
            mock_resp = MagicMock()
            mock_resp.status_code = 400
            return mock_resp
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.1))
        def fails_http():
            error = requests.exceptions.HTTPError()
            error.response = mock_response()
            raise error
        
        with self.assertRaises(requests.exceptions.HTTPError):
            fails_http()

    def test_bot_with_custom_retry_config(self):
        custom_config = RetryConfig(max_attempts=5)
        bot = huu.Bot(token='validtoken1234', allow_interactive=False, retry_config=custom_config)
        self.assertEqual(bot.retry_config.max_attempts, 5)

    def test_bot_with_default_retry_config(self):
        bot = huu.Bot(token='validtoken1234', allow_interactive=False)
        self.assertEqual(bot.retry_config.max_attempts, 3)


class TestResponseValidation(unittest.TestCase):
    def test_validate_api_response_valid_success(self):
        data = {"ok": True, "result": {"message_id": 123, "date": 1234567890}}
        result = validate_api_response(data)
        self.assertEqual(result, data)

    def test_validate_api_response_not_dict(self):
        with self.assertRaises(APIError) as context:
            validate_api_response("not a dict")
        self.assertIn("expected JSON object", str(context.exception))

    def test_validate_api_response_missing_ok_field(self):
        with self.assertRaises(APIError) as context:
            validate_api_response({"result": {}})
        self.assertIn("missing 'ok' field", str(context.exception))

    def test_validate_api_response_ok_not_bool(self):
        with self.assertRaises(APIError) as context:
            validate_api_response({"ok": "true"})
        self.assertIn("must be boolean", str(context.exception))

    def test_validate_api_response_error(self):
        with self.assertRaises(APIError) as context:
            validate_api_response({"ok": False, "error_code": 400, "description": "Bad Request"})
        self.assertIn("Bad Request", str(context.exception))
        self.assertEqual(context.exception.error_code, 400)

    def test_validate_message_result_valid(self):
        result = {"message_id": 123, "date": 1234567890, "text": "Hello"}
        validated = validate_message_result(result)
        self.assertEqual(validated["message_id"], 123)

    def test_validate_message_result_missing_message_id(self):
        with self.assertRaises(APIError) as context:
            validate_message_result({"date": 1234567890})
        self.assertIn("missing required fields", str(context.exception))

    def test_validate_message_result_missing_date(self):
        with self.assertRaises(APIError) as context:
            validate_message_result({"message_id": 123})
        self.assertIn("missing required fields", str(context.exception))

    def test_validate_message_result_negative_message_id(self):
        with self.assertRaises(APIError) as context:
            validate_message_result({"message_id": -1, "date": 1234567890})
        self.assertIn("must be positive", str(context.exception))

    def test_validate_message_result_not_dict(self):
        with self.assertRaises(APIError) as context:
            validate_message_result([])
        self.assertIn("expected object", str(context.exception))

    def test_validate_chat_result_valid_private(self):
        result = {"id": 123, "type": "private", "first_name": "John"}
        validated = validate_chat_result(result)
        self.assertEqual(validated["id"], 123)

    def test_validate_chat_result_valid_group(self):
        result = {"id": -456, "type": "group", "title": "Test Group"}
        validated = validate_chat_result(result)
        self.assertEqual(validated["id"], -456)

    def test_validate_chat_result_missing_id(self):
        with self.assertRaises(APIError) as context:
            validate_chat_result({"type": "private"})
        self.assertIn("missing required fields", str(context.exception))

    def test_validate_chat_result_missing_type(self):
        with self.assertRaises(APIError) as context:
            validate_chat_result({"id": 123})
        self.assertIn("missing required fields", str(context.exception))

    def test_validate_chat_result_invalid_type(self):
        with self.assertRaises(APIError) as context:
            validate_chat_result({"id": 123, "type": "invalid_type"})
        self.assertIn("unknown chat type", str(context.exception))

    def test_validate_user_result_valid(self):
        result = {"id": 123, "is_bot": False, "first_name": "John"}
        validated = validate_user_result(result)
        self.assertEqual(validated["id"], 123)

    def test_validate_user_result_is_bot_true(self):
        result = {"id": 123, "is_bot": True, "first_name": "BotName"}
        validated = validate_user_result(result)
        self.assertTrue(validated["is_bot"])

    def test_validate_user_result_missing_is_bot(self):
        with self.assertRaises(APIError) as context:
            validate_user_result({"id": 123, "first_name": "John"})
        self.assertIn("missing required fields", str(context.exception))

    def test_validate_user_result_empty_first_name(self):
        with self.assertRaises(APIError) as context:
            validate_user_result({"id": 123, "is_bot": False, "first_name": "   "})
        self.assertIn("cannot be empty", str(context.exception))

    def test_extract_result_valid(self):
        data = {"ok": True, "result": {"message_id": 123}}
        result = extract_result(data)
        self.assertEqual(result["message_id"], 123)

    def test_extract_result_missing(self):
        with self.assertRaises(APIError) as context:
            extract_result({"ok": True})
        self.assertIn("missing 'result' field", str(context.exception))

    def test_response_validator_send_message(self):
        data = {"ok": True, "result": {"message_id": 123, "date": 1234567890}}
        validated = ResponseValidator.validate_send_message_response(data)
        self.assertEqual(validated["message_id"], 123)

    def test_response_validator_get_chat(self):
        data = {"ok": True, "result": {"id": 456, "type": "private", "first_name": "Jane"}}
        validated = ResponseValidator.validate_get_chat_response(data)
        self.assertEqual(validated["id"], 456)

    def test_response_validator_get_user(self):
        data = {"ok": True, "result": {"id": 789, "is_bot": False, "first_name": "Bob"}}
        validated = ResponseValidator.validate_get_user_response(data)
        self.assertEqual(validated["id"], 789)

    def test_response_validator_get_user_with_type(self):
        # User response can be a chat with type='private'
        data = {"ok": True, "result": {"id": 789, "type": "private", "first_name": "Bob"}}
        validated = ResponseValidator.validate_get_user_response(data)
        self.assertEqual(validated["id"], 789)
        self.assertEqual(validated["type"], "private")


if __name__ == '__main__':
    unittest.main()