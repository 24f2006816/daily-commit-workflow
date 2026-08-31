"""Configuration constants for the daily-commit-workflow."""

import os

LOG_FILE = os.environ.get("DAILY_LOG_FILE", "daily-log.txt")

LOG_PREFIX = "TDSFU"
LOG_SUFFIX = "TDSFU"

DATE_FORMAT = "%a %b %d %H:%M:%S UTC %Y"

COMMIT_MESSAGE_TEMPLATE = "Auto commit at {timestamp}"
GIT_USER_NAME = "github-actions[bot]"
GIT_USER_EMAIL = "github-actions[bot]@users.noreply.github.com"
