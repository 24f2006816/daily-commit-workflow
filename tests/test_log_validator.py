"""Unit tests for src/log_validator.py."""

import unittest
from datetime import datetime, timezone

from src.log_validator import (
    check_chronological_order,
    detect_duplicate_entries,
    find_missing_dates,
    validate_entry_format,
    validate_log_file,
)


class TestValidateEntryFormat(unittest.TestCase):
    """Tests for validate_entry_format()."""

    def test_valid_entry(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        is_valid, error = validate_entry_format(entry)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_empty_entry(self):
        is_valid, error = validate_entry_format("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error)

    def test_none_entry(self):
        is_valid, error = validate_entry_format(None)
        self.assertFalse(is_valid)

    def test_wrong_prefix(self):
        entry = "WRONG Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        is_valid, error = validate_entry_format(entry)
        self.assertFalse(is_valid)
        self.assertIn("format", error)

    def test_wrong_suffix(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 WRONG"
        is_valid, error = validate_entry_format(entry)
        self.assertFalse(is_valid)

    def test_invalid_timestamp(self):
        entry = "TDSFU Daily run: Not A Real Date TDSFU"
        is_valid, error = validate_entry_format(entry)
        self.assertFalse(is_valid)
        self.assertIn("timestamp", error.lower())

    def test_whitespace_only(self):
        is_valid, error = validate_entry_format("   ")
        self.assertFalse(is_valid)

    def test_valid_entry_with_single_digit_day(self):
        entry = "TDSFU Daily run: Sat Nov  1 04:33:14 UTC 2025 TDSFU"
        is_valid, error = validate_entry_format(entry)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_valid_entry_with_double_digit_day(self):
        entry = "TDSFU Daily run: Thu Oct 30 04:35:54 UTC 2025 TDSFU"
        is_valid, error = validate_entry_format(entry)
        self.assertTrue(is_valid)


class TestValidateLogFile(unittest.TestCase):
    """Tests for validate_log_file()."""

    def test_all_valid(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
        ]
        result = validate_log_file(entries)
        self.assertTrue(result["valid"])
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["invalid_count"], 0)
        self.assertEqual(len(result["errors"]), 0)

    def test_some_invalid(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "bad entry",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
        ]
        result = validate_log_file(entries)
        self.assertFalse(result["valid"])
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["invalid_count"], 1)
        self.assertEqual(result["errors"][0][0], 1)

    def test_empty_list(self):
        result = validate_log_file([])
        self.assertTrue(result["valid"])
        self.assertEqual(result["total"], 0)

    def test_all_invalid(self):
        entries = ["bad1", "bad2", "bad3"]
        result = validate_log_file(entries)
        self.assertFalse(result["valid"])
        self.assertEqual(result["invalid_count"], 3)

    def test_errors_contain_entry_text(self):
        entries = ["not valid"]
        result = validate_log_file(entries)
        self.assertEqual(result["errors"][0][1], "not valid")


class TestCheckChronologicalOrder(unittest.TestCase):
    """Tests for check_chronological_order()."""

    def test_ordered_entries(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
            "TDSFU Daily run: Sun Oct 19 04:36:15 UTC 2025 TDSFU",
        ]
        is_ordered, out_of_order = check_chronological_order(entries)
        self.assertTrue(is_ordered)
        self.assertEqual(out_of_order, [])

    def test_unordered_entries(self):
        entries = [
            "TDSFU Daily run: Sun Oct 19 04:36:15 UTC 2025 TDSFU",
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
        ]
        is_ordered, out_of_order = check_chronological_order(entries)
        self.assertFalse(is_ordered)
        self.assertIn(1, out_of_order)

    def test_single_entry(self):
        entries = ["TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"]
        is_ordered, out_of_order = check_chronological_order(entries)
        self.assertTrue(is_ordered)

    def test_empty_list(self):
        is_ordered, out_of_order = check_chronological_order([])
        self.assertTrue(is_ordered)

    def test_same_timestamp(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
        ]
        is_ordered, out_of_order = check_chronological_order(entries)
        self.assertTrue(is_ordered)


class TestFindMissingDates(unittest.TestCase):
    """Tests for find_missing_dates()."""

    def test_no_missing_dates(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 12:00:00 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 12:00:00 UTC 2025 TDSFU",
            "TDSFU Daily run: Sun Oct 19 12:00:00 UTC 2025 TDSFU",
        ]
        missing = find_missing_dates(entries)
        self.assertEqual(missing, [])

    def test_with_gap(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 12:00:00 UTC 2025 TDSFU",
            "TDSFU Daily run: Sun Oct 19 12:00:00 UTC 2025 TDSFU",
        ]
        missing = find_missing_dates(entries)
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].day, 18)

    def test_empty_entries(self):
        missing = find_missing_dates([])
        self.assertEqual(missing, [])

    def test_single_entry(self):
        entries = ["TDSFU Daily run: Fri Oct 17 12:00:00 UTC 2025 TDSFU"]
        missing = find_missing_dates(entries)
        self.assertEqual(missing, [])

    def test_multi_day_gap(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 12:00:00 UTC 2025 TDSFU",
            "TDSFU Daily run: Tue Oct 21 12:00:00 UTC 2025 TDSFU",
        ]
        missing = find_missing_dates(entries)
        self.assertEqual(len(missing), 3)


class TestDetectDuplicateEntries(unittest.TestCase):
    """Tests for detect_duplicate_entries()."""

    def test_no_duplicates(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
        ]
        duplicates = detect_duplicate_entries(entries)
        self.assertEqual(duplicates, [])

    def test_with_duplicates(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
        ]
        duplicates = detect_duplicate_entries(entries)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0][0], 1)

    def test_empty_list(self):
        duplicates = detect_duplicate_entries([])
        self.assertEqual(duplicates, [])

    def test_multiple_duplicates(self):
        entries = [
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
            "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU",
            "TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU",
        ]
        duplicates = detect_duplicate_entries(entries)
        self.assertEqual(len(duplicates), 2)


if __name__ == "__main__":
    unittest.main()
