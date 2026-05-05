"""Per-workspace ingest ledger. Lock 6 of format.md.

JSONL append-only. One row per write. The latest row for a given
(source, key) is authoritative for `last_known_path` and
`last_known_content_hash`.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def load_rows(path: Path) -> list[dict]:
    """Read all rows from the ledger. Empty / missing file → []."""
    p = Path(path)
    if not p.exists():
        return []
    rows: list[dict] = []
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                # Drop unreadable rows. Lint compaction surfaces them.
                continue
    return rows


def append_row(
    ledger_path: Path,
    *,
    source: str,
    key: str,
    content_hash: str,
    path: str,
    **extra,
) -> None:
    """Append one row to the ledger at `ledger_path`.

    `path` is the recorded raw-file path. Extra keywords merge in (used
    for routed_by, run_id, etc).
    """
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "source": source,
        "key": key,
        "content_hash": content_hash,
        "path": path,
        "ingested_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    row.update(extra)
    with ledger_path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_last_row(path: Path, *, source: str, key: str) -> dict | None:
    """Latest ledger row for (source, key). None if absent."""
    rows = load_rows(path)
    for row in reversed(rows):
        if row.get("source") == source and row.get("key") == key:
            return row
    return None
