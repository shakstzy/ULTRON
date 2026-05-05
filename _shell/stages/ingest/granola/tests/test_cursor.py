"""Cursor tests — Lock 8 cursor file."""
import tempfile
import unittest
from pathlib import Path

import conftest  # noqa: F401

from cursor import read_cursor, write_cursor


class CursorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "cursors" / "granola" / "acct.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def test_read_missing_returns_none(self):
        self.assertIsNone(read_cursor(self.path))

    def test_write_then_read_roundtrip(self):
        write_cursor(self.path, "2026-04-13T18:00:00Z")
        self.assertEqual(read_cursor(self.path), "2026-04-13T18:00:00Z")

    def test_write_overwrites(self):
        write_cursor(self.path, "2026-04-01T00:00:00Z")
        write_cursor(self.path, "2026-04-13T18:00:00Z")
        self.assertEqual(read_cursor(self.path), "2026-04-13T18:00:00Z")

    def test_write_creates_parent_dirs(self):
        # Parent dirs do not exist initially; write_cursor must create them.
        deep = Path(self.tmp.name) / "a" / "b" / "c" / "cur.txt"
        write_cursor(deep, "2026-04-13T18:00:00Z")
        self.assertTrue(deep.exists())

    def test_atomic_write_no_partial_file(self):
        # Write should never leave a half-written cursor on disk.
        # Smoke check by writing repeatedly and ensuring read always returns
        # complete value, not empty / partial.
        for v in ("2026-04-13T18:00:00Z", "2026-04-13T18:01:00Z", "2026-04-13T18:02:00Z"):
            write_cursor(self.path, v)
            self.assertEqual(read_cursor(self.path), v)


if __name__ == "__main__":
    unittest.main()
