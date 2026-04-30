#!/usr/bin/env python3
"""
new-since.py — list files in a path newer than a given timestamp or last-ingest record.

Usage:
    new-since.py --path <path> [--since <iso8601>] [--workspace <ws>]

If --workspace is given, files already recorded in workspaces/<ws>/_meta/ingested.jsonl
(by raw_path) are excluded.

If --since is given, only files with mtime >= that ISO timestamp are returned.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_ingested_paths(workspace: str) -> set[str]:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"
    if not log.exists():
        return set()
    out: set[str] = set()
    for line in log.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        rp = obj.get("raw_path")
        if rp:
            out.add(rp)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", required=True)
    ap.add_argument("--since")
    ap.add_argument("--workspace")
    args = ap.parse_args()

    root = Path(args.path)
    if not root.exists():
        sys.stderr.write(f"path not found: {root}\n")
        return 2

    since_dt: datetime | None = None
    if args.since:
        try:
            since_dt = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
            if since_dt.tzinfo is None:
                since_dt = since_dt.replace(tzinfo=timezone.utc)
        except ValueError:
            sys.stderr.write(f"bad iso timestamp: {args.since}\n")
            return 2

    ingested: set[str] = set()
    if args.workspace:
        ingested = load_ingested_paths(args.workspace)

    ws_dir: Path | None = None
    if args.workspace:
        ws_dir = ULTRON_ROOT / "workspaces" / args.workspace

    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if since_dt is not None:
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if mtime < since_dt:
                continue
        if ws_dir is not None:
            try:
                rel = str(p.relative_to(ws_dir))
            except ValueError:
                rel = str(p)
            if rel in ingested:
                continue
        print(p)

    return 0


if __name__ == "__main__":
    sys.exit(main())
