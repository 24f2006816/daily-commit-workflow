"""Validation utilities for daily log entries and files."""

import re
from datetime import datetime, timezone

from src.config import DATE_FORMAT, LOG_PREFIX, LOG_SUFFIX


def validate_entry_format(entry):
    """Validate that a single entry matches the expected format.

    Args:
        entry: A log entry string.

    Returns:
        A tuple (is_valid, error_message). error_message is None if valid.
    """
    if not entry or not entry.strip():
        return False, "Entry is empty"

    entry = entry.strip()
    pattern = rf"^{re.escape(LOG_PREFIX)} Daily run: .+ {re.escape(LOG_SUFFIX)}$"
    if not re.match(pattern, entry):
        return False, f"Entry does not match expected format: {entry!r}"

    inner = entry[len(LOG_PREFIX) + len(" Daily run: "):-len(" " + LOG_SUFFIX)]
    try:
        datetime.strptime(inner, DATE_FORMAT)
    except ValueError:
        return False, f"Invalid timestamp in entry: {inner!r}"

    return True, None


def validate_log_file(entries):
    """Validate a list of log entries.

    Args:
        entries: A list of log entry strings.

    Returns:
        A dict with:
            - 'valid': bool indicating all entries are valid
            - 'total': total number of entries
            - 'valid_count': number of valid entries
            - 'invalid_count': number of invalid entries
            - 'errors': list of (index, entry, error_message) tuples
    """
    errors = []
    valid_count = 0
    for i, entry in enumerate(entries):
        is_valid, error = validate_entry_format(entry)
        if is_valid:
            valid_count += 1
        else:
            errors.append((i, entry, error))

    return {
        "valid": len(errors) == 0,
        "total": len(entries),
        "valid_count": valid_count,
        "invalid_count": len(errors),
        "errors": errors,
    }


def check_chronological_order(entries):
    """Check that log entries are in chronological order.

    Args:
        entries: A list of log entry strings.

    Returns:
        A tuple (is_ordered, out_of_order_indices).
        out_of_order_indices is a list of indices where order is violated.
    """
    from src.daily_log import parse_entry

    timestamps = []
    for entry in entries:
        parsed = parse_entry(entry)
        if parsed and parsed["timestamp"]:
            timestamps.append(parsed["timestamp"])

    out_of_order = []
    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i - 1]:
            out_of_order.append(i)

    return len(out_of_order) == 0, out_of_order


def find_missing_dates(entries):
    """Find dates where no log entry exists (gaps in daily logging).

    Args:
        entries: A list of log entry strings.

    Returns:
        A list of date objects representing missing days.
    """
    from src.daily_log import parse_entry
    from datetime import timedelta

    dates = set()
    for entry in entries:
        parsed = parse_entry(entry)
        if parsed and parsed["timestamp"]:
            dates.add(parsed["timestamp"].date())

    if not dates:
        return []

    sorted_dates = sorted(dates)
    missing = []
    current = sorted_dates[0]
    end = sorted_dates[-1]
    while current <= end:
        if current not in dates:
            missing.append(current)
        current += timedelta(days=1)

    return missing


def detect_duplicate_entries(entries):
    """Detect duplicate log entries (same timestamp).

    Args:
        entries: A list of log entry strings.

    Returns:
        A list of (index, entry) tuples for duplicate entries.
    """
    seen = {}
    duplicates = []
    for i, entry in enumerate(entries):
        stripped = entry.strip()
        if stripped in seen:
            duplicates.append((i, stripped))
        else:
            seen[stripped] = i
    return duplicates
