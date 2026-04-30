#!/usr/bin/env python3
"""
ingest-imessage.py <workspace> <run_id>

Skeleton iMessage ingest. Reads ~/Library/Messages/chat.db (Full Disk Access
required). Per-workspace `config.contacts` filters which phone numbers / emails
to include.

Live ingest is deferred. Schema and CLI contract are defined; reading chat.db
is left as TODO.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"


def load_source_config(workspace: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-imessage: missing dep pyyaml\n")
        return None
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        return None
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    for source in cfg.get("sources", []):
        if source.get("type") == "imessage":
            return source
    return None


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-imessage.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]

    source = load_source_config(workspace)
    if source is None:
        sys.stderr.write(f"ingest-imessage: no imessage source declared for {workspace}\n")
        return 0

    if not CHAT_DB.exists():
        sys.stderr.write(
            f"ingest-imessage: {CHAT_DB} not readable. Grant Full Disk Access to the "
            "process running this script (Terminal / launchd) under "
            "System Settings > Privacy & Security > Full Disk Access.\n"
        )
        return 0

    sys.stderr.write(
        "ingest-imessage: TODO — query chat.db (sqlite3) for messages with "
        "configured contacts, render per-day markdown.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
