#!/usr/bin/env python3
"""
compact-ledger.py — quarterly maintenance of every workspace's
`_meta/ingested.jsonl`.

For each workspace:
  1. Load every row.
  2. Drop rows whose `raw_path` no longer exists on disk.
  3. For rows with the same `(source, key)`, keep only the latest.
  4. Write the result back, sorted by `ingested_at` ascending.
  5. Log: rows kept / rows dropped / rows merged.

Usage:
    compact-ledger.py [--workspace <ws>] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def compact_workspace(ws_dir: Path, dry_run: bool) -> dict:
    ledger = ws_dir / "_meta" / "ingested.jsonl"
    if not ledger.exists():
        return {"workspace": ws_dir.name, "kept": 0, "dropped_orphan": 0, "dropped_dup": 0}

    rows: list[dict] = []
    for line in ledger.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    # Drop orphans (raw_path missing on disk).
    kept_after_orphan: list[dict] = []
    dropped_orphan = 0
    for r in rows:
        rp = r.get("raw_path")
        if rp:
            full = ws_dir / rp
            if not full.exists():
                dropped_orphan += 1
                continue
        kept_after_orphan.append(r)

    # De-dup by (source, key); keep the latest by ingested_at.
    by_key: dict[tuple[str, str], dict] = {}
    dropped_dup = 0
    for r in kept_after_orphan:
        k = (str(r.get("source") or ""), str(r.get("source_uid") or r.get("key") or ""))
        existing = by_key.get(k)
        if existing is None:
            by_key[k] = r
        else:
            old = existing.get("ingested_at") or ""
            new = r.get("ingested_at") or ""
            if new > old:
                by_key[k] = r
            dropped_dup += 1

    final = sorted(by_key.values(), key=lambda r: r.get("ingested_at") or "")

    if not dry_run:
        ledger.write_text("\n".join(json.dumps(r) for r in final) + ("\n" if final else ""))

    return {
        "workspace": ws_dir.name,
        "kept": len(final),
        "dropped_orphan": dropped_orphan,
        "dropped_dup": dropped_dup,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    workspaces_dir = ULTRON_ROOT / "workspaces"
    if not workspaces_dir.exists():
        return 0

    results: list[dict] = []
    for ws_dir in sorted(workspaces_dir.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        if args.workspace and ws_dir.name != args.workspace:
            continue
        results.append(compact_workspace(ws_dir, args.dry_run))

    label = "[dry-run] " if args.dry_run else ""
    for r in results:
        print(
            f"{label}{r['workspace']}: kept={r['kept']} "
            f"dropped_orphan={r['dropped_orphan']} dropped_dup={r['dropped_dup']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
