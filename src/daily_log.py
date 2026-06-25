"""Core logic for generating and managing daily log entries."""

import os
import re
from datetime import datetime, timezone

from src.config import DATE_FORMAT, LOG_FILE, LOG_PREFIX, LOG_SUFFIX


def generate_entry(timestamp=None):
    """Generate a log entry string for the given timestamp.

    Args:
        timestamp: A datetime object. Defaults to current UTC time.

    Returns:
        A formatted log entry string.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    formatted = timestamp.strftime(DATE_FORMAT)
    return f"{LOG_PREFIX} Daily run: {formatted} {LOG_SUFFIX}"


def append_entry(log_file=None, timestamp=None):
    """Append a new log entry to the log file.

    Args:
        log_file: Path to the log file. Defaults to config LOG_FILE.
        timestamp: A datetime object. Defaults to current UTC time.

    Returns:
        The entry that was appended.
    """
    if log_file is None:
        log_file = LOG_FILE
    entry = generate_entry(timestamp)
    with open(log_file, "a") as f:
        f.write(entry + "\n")
    return entry


def read_entries(log_file=None):
    """Read all log entries from the log file.

    Args:
        log_file: Path to the log file. Defaults to config LOG_FILE.

    Returns:
        A list of entry strings (without trailing newlines).
    """
    if log_file is None:
        log_file = LOG_FILE
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        lines = f.read().strip().splitlines()
    return [line for line in lines if line.strip()]


def parse_entry(entry):
    """Parse a log entry into its components.

    Args:
        entry: A log entry string.

    Returns:
        A dict with keys 'prefix', 'timestamp_str', 'suffix', 'timestamp',
        or None if the entry doesn't match the expected format.
    """
    pattern = rf"^({re.escape(LOG_PREFIX)}) Daily run: (.+?) ({re.escape(LOG_SUFFIX)})$"
    match = re.match(pattern, entry.strip())
    if not match:
        return None
    prefix, timestamp_str, suffix = match.groups()
    try:
        timestamp = datetime.strptime(timestamp_str, DATE_FORMAT).replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        timestamp = None
    return {
        "prefix": prefix,
        "timestamp_str": timestamp_str,
        "suffix": suffix,
        "timestamp": timestamp,
    }


def count_entries(log_file=None):
    """Count the number of entries in the log file.

    Args:
        log_file: Path to the log file. Defaults to config LOG_FILE.

    Returns:
        The number of entries.
    """
    return len(read_entries(log_file))


def get_latest_entry(log_file=None):
    """Get the most recent log entry.

    Args:
        log_file: Path to the log file. Defaults to config LOG_FILE.

    Returns:
        The last entry string, or None if the file is empty.
    """
    entries = read_entries(log_file)
    if not entries:
        return None
    return entries[-1]


def get_entries_in_range(start_date, end_date, log_file=None):
    """Get all entries within a date range (inclusive).

    Args:
        start_date: Start date (datetime).
        end_date: End date (datetime).
        log_file: Path to the log file. Defaults to config LOG_FILE.

    Returns:
        A list of entries whose timestamps fall within the range.
    """
    entries = read_entries(log_file)
    result = []
    for entry in entries:
        parsed = parse_entry(entry)
        if parsed and parsed["timestamp"]:
            if start_date <= parsed["timestamp"] <= end_date:
                result.append(entry)
    return result
