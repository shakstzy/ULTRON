"""Ledger tests — Lock 6 (rename + dedup semantics)."""
import json
import tempfile
import unittest
from pathlib import Path

import conftest  # noqa: F401

from ledger import append_row, find_last_row, load_rows


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ingested.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_missing_returns_empty(self):
        self.assertEqual(load_rows(self.path), [])

    def test_append_and_find_last(self):
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:11", path="raw/granola/x.md")
        last = find_last_row(self.path, source="granola", key="abc")
        self.assertEqual(last["content_hash"], "blake3:11")
        self.assertEqual(last["path"], "raw/granola/x.md")

    def test_find_last_returns_most_recent(self):
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:11", path="raw/granola/x.md")
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:22", path="raw/granola/y.md")
        last = find_last_row(self.path, source="granola", key="abc")
        self.assertEqual(last["content_hash"], "blake3:22")
        self.assertEqual(last["path"], "raw/granola/y.md")

    def test_find_last_filters_by_source(self):
        append_row(self.path, source="gmail", key="abc",
                   content_hash="blake3:gg", path="raw/gmail/x.md")
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:gn", path="raw/granola/x.md")
        last = find_last_row(self.path, source="granola", key="abc")
        self.assertEqual(last["content_hash"], "blake3:gn")

    def test_find_last_no_match(self):
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:11", path="raw/granola/x.md")
        self.assertIsNone(find_last_row(self.path, source="granola", key="zzz"))

    def test_appends_ingested_at_iso(self):
        append_row(self.path, source="granola", key="abc",
                   content_hash="blake3:11", path="raw/granola/x.md")
        last = find_last_row(self.path, source="granola", key="abc")
        # Just ensure it's set and ISO-8601-ish.
        self.assertIn("ingested_at", last)
        self.assertIn("T", last["ingested_at"])

    def test_loaded_rows_are_in_order(self):
        for i in range(3):
            append_row(self.path, source="granola", key=f"k{i}",
                       content_hash=f"blake3:{i}", path=f"p{i}")
        rows = load_rows(self.path)
        self.assertEqual([r["key"] for r in rows], ["k0", "k1", "k2"])


if __name__ == "__main__":
    unittest.main()
