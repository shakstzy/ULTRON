"""Slug derivation for Granola ingest. Lock 1 of format.md.

Pure functions, no I/O.
"""
from __future__ import annotations

import re
import unicodedata

_PREFIX_RE = re.compile(r"^\s*(?:re|fwd|fw)\s*:\s*", re.IGNORECASE)
_NON_ALNUM_RUN = re.compile(r"[^a-z0-9]+")
TITLE_MAX = 60
DEFAULT_TITLE = "untitled-meeting"


def account_slug(email: str) -> str:
    """`adithya@outerscope.xyz` -> `adithya-outerscope`.

    Local-part + first domain segment, non-alnum runs collapsed to `-`.
    Empty / unparseable input → `"unknown"`.
    """
    if not email:
        return "unknown"
    local, _, domain = email.lower().strip().partition("@")
    stem = domain.split(".", 1)[0] if domain else ""
    base = f"{local}-{stem}" if stem else local
    out = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return out or "unknown"


def title_slug(title: str) -> str:
    """Lock 1 title-slug rules.

    - Strip leading `Re:` / `Fwd:` / `Fw:` prefixes (case-insensitive,
      repeat to fixed point).
    - NFKD ASCII fold.
    - Lowercase. Non-alnum runs → `-`. Strip leading / trailing `-`.
    - Truncate at 60 chars; strip trailing `-` after truncate.
    - Empty result → `"untitled-meeting"`.
    """
    if not title:
        return DEFAULT_TITLE

    # Strip Re:/Fwd:/Fw: prefixes to fixed point.
    s = title
    while True:
        new = _PREFIX_RE.sub("", s, count=1)
        if new == s:
            break
        s = new

    # NFKD fold + ASCII drop.
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _NON_ALNUM_RUN.sub("-", s).strip("-")

    if len(s) > TITLE_MAX:
        s = s[:TITLE_MAX].rstrip("-")
    return s or DEFAULT_TITLE
