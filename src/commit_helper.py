"""Helper utilities for generating git commit metadata."""

from datetime import datetime, timezone

from src.config import COMMIT_MESSAGE_TEMPLATE, GIT_USER_EMAIL, GIT_USER_NAME


def generate_commit_message(timestamp=None):
    """Generate a commit message for an auto-commit.

    Args:
        timestamp: A datetime object. Defaults to current UTC time.

    Returns:
        The formatted commit message string.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    formatted = timestamp.strftime("%a %b %d %H:%M:%S UTC %Y")
    return COMMIT_MESSAGE_TEMPLATE.format(timestamp=formatted)


def get_git_config():
    """Return the git configuration for auto-commits.

    Returns:
        A dict with 'user.name' and 'user.email'.
    """
    return {
        "user.name": GIT_USER_NAME,
        "user.email": GIT_USER_EMAIL,
    }


def validate_commit_message(message):
    """Validate a commit message matches the auto-commit format.

    Args:
        message: The commit message to validate.

    Returns:
        A tuple (is_valid, error_message). error_message is None if valid.
    """
    if not message or not message.strip():
        return False, "Commit message is empty"

    prefix = "Auto commit at "
    if not message.startswith(prefix):
        return False, f"Commit message does not start with {prefix!r}"

    timestamp_part = message[len(prefix):]
    try:
        datetime.strptime(timestamp_part, "%a %b %d %H:%M:%S UTC %Y")
    except ValueError:
        return False, f"Invalid timestamp in commit message: {timestamp_part!r}"

    return True, None
