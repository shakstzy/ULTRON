"""Cursor file: ISO-8601 timestamp of latest ingested doc.updated_at.

Lock 8 of format.md.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def read_cursor(path: Path) -> str | None:
    """Return the ISO-8601 timestamp from `path`, or None if missing/empty."""
    p = Path(path)
    if not p.exists():
        return None
    s = p.read_text().strip()
    return s or None


def write_cursor(path: Path, value: str) -> None:
    """Atomic write: sibling tmp + os.replace. Creates parent dirs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=p.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(value)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
