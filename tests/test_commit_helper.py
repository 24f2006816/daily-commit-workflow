"""Unit tests for src/commit_helper.py."""

import unittest
from datetime import datetime, timezone

from src.commit_helper import (
    generate_commit_message,
    get_git_config,
    validate_commit_message,
)


class TestGenerateCommitMessage(unittest.TestCase):
    """Tests for generate_commit_message()."""

    def test_default_timestamp(self):
        msg = generate_commit_message()
        self.assertTrue(msg.startswith("Auto commit at "))
        self.assertIn("UTC", msg)

    def test_specific_timestamp(self):
        ts = datetime(2025, 10, 17, 13, 2, 5, tzinfo=timezone.utc)
        msg = generate_commit_message(ts)
        self.assertEqual(msg, "Auto commit at Fri Oct 17 13:02:05 UTC 2025")

    def test_different_timestamps(self):
        ts1 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        self.assertNotEqual(
            generate_commit_message(ts1), generate_commit_message(ts2)
        )

    def test_message_format(self):
        ts = datetime(2026, 6, 15, 8, 30, 0, tzinfo=timezone.utc)
        msg = generate_commit_message(ts)
        self.assertRegex(msg, r"^Auto commit at \w+ \w+ \d+ \d+:\d+:\d+ UTC \d+$")


class TestGetGitConfig(unittest.TestCase):
    """Tests for get_git_config()."""

    def test_returns_dict(self):
        config = get_git_config()
        self.assertIsInstance(config, dict)

    def test_has_user_name(self):
        config = get_git_config()
        self.assertIn("user.name", config)
        self.assertEqual(config["user.name"], "github-actions[bot]")

    def test_has_user_email(self):
        config = get_git_config()
        self.assertIn("user.email", config)
        self.assertIn("github-actions", config["user.email"])

    def test_config_keys(self):
        config = get_git_config()
        self.assertEqual(set(config.keys()), {"user.name", "user.email"})


class TestValidateCommitMessage(unittest.TestCase):
    """Tests for validate_commit_message()."""

    def test_valid_message(self):
        msg = "Auto commit at Fri Oct 17 13:02:05 UTC 2025"
        is_valid, error = validate_commit_message(msg)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_empty_message(self):
        is_valid, error = validate_commit_message("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_none_message(self):
        is_valid, error = validate_commit_message(None)
        self.assertFalse(is_valid)

    def test_wrong_prefix(self):
        msg = "Manual commit at Fri Oct 17 13:02:05 UTC 2025"
        is_valid, error = validate_commit_message(msg)
        self.assertFalse(is_valid)
        self.assertIn("Auto commit at", error)

    def test_invalid_timestamp(self):
        msg = "Auto commit at not-a-real-date"
        is_valid, error = validate_commit_message(msg)
        self.assertFalse(is_valid)
        self.assertIn("timestamp", error.lower())

    def test_roundtrip_with_generate(self):
        ts = datetime(2025, 10, 17, 13, 2, 5, tzinfo=timezone.utc)
        msg = generate_commit_message(ts)
        is_valid, error = validate_commit_message(msg)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_whitespace_only(self):
        is_valid, error = validate_commit_message("   ")
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
