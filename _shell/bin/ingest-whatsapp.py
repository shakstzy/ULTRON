#!/usr/bin/env python3
"""
ingest-whatsapp.py <workspace> <run_id>

Skeleton WhatsApp ingest. Watches `workspaces/<ws>/raw/whatsapp/_inbox/` for
.zip exports (WhatsApp's "Export chat" feature). Parses _chat.txt and inlines
media references.

Live ingest is deferred.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-whatsapp.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]

    inbox = ULTRON_ROOT / "workspaces" / workspace / "raw" / "whatsapp" / "_inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    zips = sorted(inbox.glob("*.zip"))
    if not zips:
        sys.stderr.write(f"ingest-whatsapp: no exports in {inbox}\n")
        return 0

    sys.stderr.write(
        f"ingest-whatsapp: TODO — found {len(zips)} export(s); implement "
        "_chat.txt parsing + media inlining.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
