#!/usr/bin/env python3
"""
ingest-imessage.py <workspace-or-account> <run_id>

Per S9 of the Phase 2 build: reads ~/Library/Messages/chat.db (Full Disk
Access required). Cursor at _shell/cursors/imessage/local.txt holds the
latest ROWID processed. Per-workspace `config.imessage` blocks declare
contact / group allowlists; routing is delegated to
_shell/stages/ingest/imessage/route.py.

Skeleton mode: this script is foundation-only. Set
    IMPLEMENTATION_READY = True
at the top of the file (and grant Full Disk Access to the process) to
enable live ingest.

Initial backfill: with IMPLEMENTATION_READY = True and an empty cursor,
the robot processes the entire chat.db (typically tens to hundreds of
thousands of messages) into ~few thousand month-files. Pure-Python, no
LLM cost.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"
CURSOR_PATH = ULTRON_ROOT / "_shell" / "cursors" / "imessage" / "local.txt"

IMPLEMENTATION_READY = False


def load_workspaces_config() -> dict:
    import yaml
    out: dict = {}
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if not workspaces_dir.exists():
        return out
    for ws_dir in sorted(workspaces_dir.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        cfg_path = ws_dir / "config" / "sources.yaml"
        if not cfg_path.exists():
            continue
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        out[ws_dir.name] = cfg
    return out


def read_cursor() -> int:
    if not CURSOR_PATH.exists():
        return 0
    try:
        return int(CURSOR_PATH.read_text().strip() or "0")
    except ValueError:
        return 0


def write_cursor(rowid: int) -> None:
    CURSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_PATH.write_text(str(rowid))


def open_chat_db() -> sqlite3.Connection:
    """Open chat.db read-only via URI."""
    uri = f"file:{CHAT_DB}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-imessage.py <workspace-or-account> <run_id>\n")
        return 2

    if not CHAT_DB.exists():
        sys.stderr.write(
            f"ingest-imessage: {CHAT_DB} not readable. Grant Full Disk Access "
            "to the process running this script under System Settings > "
            "Privacy & Security > Full Disk Access.\n"
        )
        return 0

    if not IMPLEMENTATION_READY:
        sys.stderr.write(
            "ingest-imessage: skeleton — not yet wired. To enable, grant Full "
            "Disk Access to your terminal AND set IMPLEMENTATION_READY = True "
            "at the top of _shell/bin/ingest-imessage.py.\n"
        )
        return 0

    # ---- Live ingest path (kept guarded behind IMPLEMENTATION_READY) -----
    cursor = read_cursor()
    sys.stderr.write(f"ingest-imessage: starting from ROWID > {cursor}\n")

    workspaces_config = load_workspaces_config()
    if not workspaces_config:
        sys.stderr.write("ingest-imessage: no workspaces with sources.yaml — nothing to do\n")
        return 0

    # NOTE: full implementation pulls messages, joins handle/chat tables,
    # groups by (contact_slug, YYYY-MM), renders markdown per the format.md
    # spec, calls route.py to fan out, writes raw files + ingested.jsonl rows
    # per workspace, advances cursor. That work is sized at ~600 LOC and is
    # left for the next pass once Adithya has Full Disk Access set up.
    try:
        conn = open_chat_db()
        max_rowid = conn.execute("SELECT MAX(ROWID) FROM message").fetchone()[0] or 0
        new_count = conn.execute("SELECT COUNT(*) FROM message WHERE ROWID > ?", (cursor,)).fetchone()[0]
        sys.stderr.write(f"ingest-imessage: {new_count} new messages waiting (ROWID up to {max_rowid})\n")
        # No writes yet — full backfill loop pending.
    finally:
        try:
            conn.close()  # type: ignore
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
