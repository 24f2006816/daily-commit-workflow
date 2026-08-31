"""Unit tests for src/config.py."""

import os
import unittest


class TestConfig(unittest.TestCase):
    """Tests for configuration constants."""

    def test_log_prefix(self):
        from src.config import LOG_PREFIX
        self.assertEqual(LOG_PREFIX, "TDSFU")

    def test_log_suffix(self):
        from src.config import LOG_SUFFIX
        self.assertEqual(LOG_SUFFIX, "TDSFU")

    def test_date_format(self):
        from src.config import DATE_FORMAT
        self.assertIn("%Y", DATE_FORMAT)
        self.assertIn("UTC", DATE_FORMAT)

    def test_commit_message_template(self):
        from src.config import COMMIT_MESSAGE_TEMPLATE
        self.assertIn("{timestamp}", COMMIT_MESSAGE_TEMPLATE)
        self.assertIn("Auto commit", COMMIT_MESSAGE_TEMPLATE)

    def test_git_user_name(self):
        from src.config import GIT_USER_NAME
        self.assertEqual(GIT_USER_NAME, "github-actions[bot]")

    def test_git_user_email(self):
        from src.config import GIT_USER_EMAIL
        self.assertIn("github-actions[bot]", GIT_USER_EMAIL)

    def test_log_file_default(self):
        old = os.environ.pop("DAILY_LOG_FILE", None)
        try:
            import importlib
            import src.config
            importlib.reload(src.config)
            self.assertEqual(src.config.LOG_FILE, "daily-log.txt")
        finally:
            if old is not None:
                os.environ["DAILY_LOG_FILE"] = old
                import importlib
                importlib.reload(src.config)

    def test_log_file_from_env(self):
        old = os.environ.get("DAILY_LOG_FILE")
        os.environ["DAILY_LOG_FILE"] = "/tmp/custom-log.txt"
        try:
            import importlib
            import src.config
            importlib.reload(src.config)
            self.assertEqual(src.config.LOG_FILE, "/tmp/custom-log.txt")
        finally:
            if old is not None:
                os.environ["DAILY_LOG_FILE"] = old
            else:
                del os.environ["DAILY_LOG_FILE"]
            importlib.reload(src.config)


if __name__ == "__main__":
    unittest.main()
