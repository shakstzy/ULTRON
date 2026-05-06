#!/usr/bin/env python3
"""
workspace-stats.py — one-line-per-workspace snapshot of every workspace.

For each `workspaces/<ws>/`, prints raw counts (broken out by source),
wiki counts (broken out by top-level type), and the latest `ingested_at`
recorded in `_meta/ingested.jsonl`.

Usage:
    workspace-stats.py [--workspace <ws>] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def count_md_by_child(root: Path) -> tuple[int, dict[str, int]]:
    """Return (total_md_in_tree, {subdir_name: count}). Total includes files at the root."""
    if not root.exists():
        return 0, {}
    total = sum(1 for _ in root.rglob("*.md"))
    breakdown: dict[str, int] = {}
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        breakdown[child.name] = sum(1 for _ in child.rglob("*.md"))
    return total, breakdown


def parse_ts(ts: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def latest_ingested_at(jsonl: Path) -> str | None:
    if not jsonl.exists():
        return None
    latest: tuple[datetime, str] | None = None
    with jsonl.open(errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ts = json.loads(line).get("ingested_at")
            except json.JSONDecodeError:
                continue
            if not ts:
                continue
            dt = parse_ts(ts)
            if dt is None:
                continue
            if latest is None or dt > latest[0]:
                latest = (dt, ts)
    return latest[1] if latest else None


def stats_for(ws_dir: Path) -> dict:
    raw_total, raw = count_md_by_child(ws_dir / "raw")
    wiki_total, wiki = count_md_by_child(ws_dir / "wiki")
    last = latest_ingested_at(ws_dir / "_meta" / "ingested.jsonl")
    return {
        "ws": ws_dir.name,
        "raw_total": raw_total,
        "raw": raw,
        "wiki_total": wiki_total,
        "wiki": wiki,
        "last_ingest": last,
    }


def fmt_breakdown(d: dict[str, int]) -> str:
    if not d:
        return ""
    return " (" + " ".join(f"{k}={v}" for k, v in d.items()) + ")"


def fmt_line(s: dict) -> str:
    last = s["last_ingest"] or "—"
    return (
        f"{s['ws']:<22} "
        f"raw={s['raw_total']}{fmt_breakdown(s['raw'])}  "
        f"wiki={s['wiki_total']}{fmt_breakdown(s['wiki'])}  "
        f"last={last}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", help="Restrict to a single workspace.")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = ap.parse_args()

    ws_root = ULTRON_ROOT / "workspaces"
    if not ws_root.exists():
        print(f"no workspaces dir: {ws_root}", file=sys.stderr)
        return 2

    rows: list[dict] = []
    for ws_dir in sorted(ws_root.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        if args.workspace and ws_dir.name != args.workspace:
            continue
        rows.append(stats_for(ws_dir))

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(fmt_line(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
