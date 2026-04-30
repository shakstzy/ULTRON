#!/usr/bin/env python3
"""
ingest-drive.py <workspace> <run_id>

Skeleton Google Drive ingest. Lists files in declared folders modified within
the lookback window, exports Google Docs to markdown via files.export, OCRs
PDFs, writes to `workspaces/<ws>/raw/drive/<YYYY-MM>/<slug>.md`.

Auth (one of):
  - OAuth: `_credentials/drive-<workspace>.json` (Google authorized-user JSON).
  - `gog` CLI delegation when `via: gog`.

Live ingest is deferred.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_source_config(workspace: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-drive: missing dep pyyaml\n")
        return None
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        return None
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    for source in cfg.get("sources", []):
        if source.get("type") == "drive":
            return source
    return None


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-drive.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]

    source = load_source_config(workspace)
    if source is None:
        sys.stderr.write(f"ingest-drive: no drive source declared for {workspace}\n")
        return 0

    cred_path = ULTRON_ROOT / "_credentials" / f"drive-{workspace}.json"
    if not cred_path.exists():
        sys.stderr.write(
            f"ingest-drive: no credentials at {cred_path}; live ingest deferred.\n"
        )
        return 0

    sys.stderr.write(
        "ingest-drive: TODO — wire google-api-python-client Drive v3, list "
        "files modified in lookback window, export Docs as markdown, OCR PDFs.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
