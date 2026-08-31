"""Unit tests for src/daily_log.py."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from src.daily_log import (
    append_entry,
    count_entries,
    generate_entry,
    get_entries_in_range,
    get_latest_entry,
    parse_entry,
    read_entries,
)


class TestGenerateEntry(unittest.TestCase):
    """Tests for generate_entry()."""

    def test_default_timestamp(self):
        entry = generate_entry()
        self.assertTrue(entry.startswith("TDSFU Daily run:"))
        self.assertTrue(entry.endswith("TDSFU"))

    def test_specific_timestamp(self):
        ts = datetime(2025, 10, 17, 13, 2, 5, tzinfo=timezone.utc)
        entry = generate_entry(ts)
        self.assertEqual(entry, "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU")

    def test_entry_contains_utc(self):
        entry = generate_entry()
        self.assertIn("UTC", entry)

    def test_entry_prefix_suffix(self):
        entry = generate_entry()
        parts = entry.split(" Daily run: ")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "TDSFU")
        self.assertTrue(parts[1].endswith("TDSFU"))

    def test_different_timestamps_produce_different_entries(self):
        ts1 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2025, 6, 15, 12, 30, 0, tzinfo=timezone.utc)
        self.assertNotEqual(generate_entry(ts1), generate_entry(ts2))

    def test_midnight_timestamp(self):
        ts = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        entry = generate_entry(ts)
        self.assertIn("00:00:00", entry)

    def test_end_of_day_timestamp(self):
        ts = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        entry = generate_entry(ts)
        self.assertIn("23:59:59", entry)


class TestAppendEntry(unittest.TestCase):
    """Tests for append_entry()."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_append_creates_entry(self):
        entry = append_entry(self.tmpfile.name)
        self.assertIn("TDSFU", entry)
        with open(self.tmpfile.name) as f:
            content = f.read()
        self.assertIn(entry, content)

    def test_append_with_timestamp(self):
        ts = datetime(2025, 10, 17, 13, 2, 5, tzinfo=timezone.utc)
        entry = append_entry(self.tmpfile.name, ts)
        self.assertEqual(entry, "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU")

    def test_append_multiple_entries(self):
        ts1 = datetime(2025, 10, 17, 0, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2025, 10, 18, 0, 0, 0, tzinfo=timezone.utc)
        append_entry(self.tmpfile.name, ts1)
        append_entry(self.tmpfile.name, ts2)
        with open(self.tmpfile.name) as f:
            lines = f.read().strip().splitlines()
        self.assertEqual(len(lines), 2)

    def test_append_adds_newline(self):
        append_entry(self.tmpfile.name)
        with open(self.tmpfile.name) as f:
            content = f.read()
        self.assertTrue(content.endswith("\n"))

    def test_append_to_new_file(self):
        new_path = self.tmpfile.name + ".new"
        try:
            entry = append_entry(new_path)
            self.assertIn("TDSFU", entry)
            with open(new_path) as f:
                self.assertEqual(f.read().strip(), entry)
        finally:
            if os.path.exists(new_path):
                os.unlink(new_path)


class TestReadEntries(unittest.TestCase):
    """Tests for read_entries()."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_read_empty_file(self):
        entries = read_entries(self.tmpfile.name)
        self.assertEqual(entries, [])

    def test_read_single_entry(self):
        ts = datetime(2025, 10, 17, 13, 2, 5, tzinfo=timezone.utc)
        append_entry(self.tmpfile.name, ts)
        entries = read_entries(self.tmpfile.name)
        self.assertEqual(len(entries), 1)
        self.assertIn("Oct 17", entries[0])

    def test_read_multiple_entries(self):
        for day in range(1, 4):
            ts = datetime(2025, 10, day, 0, 0, 0, tzinfo=timezone.utc)
            append_entry(self.tmpfile.name, ts)
        entries = read_entries(self.tmpfile.name)
        self.assertEqual(len(entries), 3)

    def test_read_nonexistent_file(self):
        entries = read_entries("/tmp/nonexistent_test_file_xyz.txt")
        self.assertEqual(entries, [])

    def test_read_skips_blank_lines(self):
        with open(self.tmpfile.name, "w") as f:
            f.write("TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU\n")
            f.write("\n")
            f.write("TDSFU Daily run: Sat Oct 18 04:33:37 UTC 2025 TDSFU\n")
        entries = read_entries(self.tmpfile.name)
        self.assertEqual(len(entries), 2)


class TestParseEntry(unittest.TestCase):
    """Tests for parse_entry()."""

    def test_parse_valid_entry(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        result = parse_entry(entry)
        self.assertIsNotNone(result)
        self.assertEqual(result["prefix"], "TDSFU")
        self.assertEqual(result["suffix"], "TDSFU")
        self.assertIsNotNone(result["timestamp"])
        self.assertEqual(result["timestamp"].year, 2025)
        self.assertEqual(result["timestamp"].month, 10)
        self.assertEqual(result["timestamp"].day, 17)

    def test_parse_invalid_entry(self):
        result = parse_entry("not a valid entry")
        self.assertIsNone(result)

    def test_parse_empty_string(self):
        result = parse_entry("")
        self.assertIsNone(result)

    def test_parse_partial_format(self):
        result = parse_entry("TDSFU Daily run: invalid timestamp TDSFU")
        self.assertIsNotNone(result)
        self.assertIsNone(result["timestamp"])

    def test_parse_extracts_timestamp_string(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        result = parse_entry(entry)
        self.assertEqual(result["timestamp_str"], "Fri Oct 17 13:02:05 UTC 2025")

    def test_parse_with_whitespace(self):
        entry = "  TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU  "
        result = parse_entry(entry)
        self.assertIsNotNone(result)

    def test_parse_wrong_prefix(self):
        entry = "WRONG Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        result = parse_entry(entry)
        self.assertIsNone(result)

    def test_parse_wrong_suffix(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 WRONG"
        result = parse_entry(entry)
        self.assertIsNone(result)

    def test_parse_timestamp_timezone(self):
        entry = "TDSFU Daily run: Fri Oct 17 13:02:05 UTC 2025 TDSFU"
        result = parse_entry(entry)
        self.assertEqual(result["timestamp"].tzinfo, timezone.utc)


class TestCountEntries(unittest.TestCase):
    """Tests for count_entries()."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_count_empty(self):
        self.assertEqual(count_entries(self.tmpfile.name), 0)

    def test_count_several(self):
        for day in range(1, 6):
            ts = datetime(2025, 10, day, 0, 0, 0, tzinfo=timezone.utc)
            append_entry(self.tmpfile.name, ts)
        self.assertEqual(count_entries(self.tmpfile.name), 5)


class TestGetLatestEntry(unittest.TestCase):
    """Tests for get_latest_entry()."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_latest_from_empty_file(self):
        self.assertIsNone(get_latest_entry(self.tmpfile.name))

    def test_latest_returns_last(self):
        ts1 = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2025, 10, 2, 0, 0, 0, tzinfo=timezone.utc)
        append_entry(self.tmpfile.name, ts1)
        append_entry(self.tmpfile.name, ts2)
        latest = get_latest_entry(self.tmpfile.name)
        parsed = parse_entry(latest)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["timestamp"].day, 2)

    def test_latest_nonexistent_file(self):
        self.assertIsNone(get_latest_entry("/tmp/nonexistent_xyz_abc.txt"))


class TestGetEntriesInRange(unittest.TestCase):
    """Tests for get_entries_in_range()."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        self.tmpfile.close()
        for day in range(1, 11):
            ts = datetime(2025, 10, day, 12, 0, 0, tzinfo=timezone.utc)
            append_entry(self.tmpfile.name, ts)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_range_all(self):
        start = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 10, 10, 23, 59, 59, tzinfo=timezone.utc)
        entries = get_entries_in_range(start, end, self.tmpfile.name)
        self.assertEqual(len(entries), 10)

    def test_range_subset(self):
        start = datetime(2025, 10, 3, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 10, 5, 23, 59, 59, tzinfo=timezone.utc)
        entries = get_entries_in_range(start, end, self.tmpfile.name)
        self.assertEqual(len(entries), 3)

    def test_range_no_match(self):
        start = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        entries = get_entries_in_range(start, end, self.tmpfile.name)
        self.assertEqual(len(entries), 0)

    def test_range_single_day(self):
        start = datetime(2025, 10, 5, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 10, 5, 23, 59, 59, tzinfo=timezone.utc)
        entries = get_entries_in_range(start, end, self.tmpfile.name)
        self.assertEqual(len(entries), 1)


if __name__ == "__main__":
    unittest.main()
