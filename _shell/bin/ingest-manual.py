#!/usr/bin/env python3
"""
ingest-manual.py <workspace> <run_id>

Manual-source ingest. Watches a workspace's `raw/<source>/_inbox/` directory
for new files dropped by Adithya (markdown notes, PDF exports, CSV exports,
screenshots). For each file:

  1. Slugifies the filename and adds a YYYY-MM-DD prefix if absent.
  2. Moves it to `raw/<source>/<YYYY-MM>/<slug>.md` (or `.<ext>` for non-md).
  3. Appends an `ingested.jsonl` record with source_uid = `manual:<basename>`
     so re-ingesting the same filename is a no-op.

Multiple manual sources per workspace are supported — the source_id is read
from `sources.yaml` and each source's `watch_path` is processed independently.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    out_chars: list[str] = []
    for ch in name.lower():
        if ch.isalnum() or ch in "-._":
            out_chars.append(ch)
        elif ch in " /\\":
            out_chars.append("-")
    slug = "".join(out_chars).strip("-._")
    return slug or "manual"


def load_manual_sources(workspace: str) -> list[dict]:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-manual: missing dep pyyaml\n")
        return []
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        return []
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    return [s for s in cfg.get("sources", []) if s.get("type") == "manual"]


def existing_uids(workspace: str) -> set[str]:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"
    if not log.exists():
        return set()
    out: set[str] = set()
    for line in log.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        uid = obj.get("source_uid")
        if uid:
            out.add(uid)
    return out


def append_ingested(workspace: str, record: dict) -> None:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(json.dumps(record) + "\n")


def process_source(workspace: str, source: dict, run_id: str, seen: set[str]) -> int:
    source_id = source.get("id", "manual")
    config = source.get("config", {}) or {}
    watch_rel = config.get("watch_path", f"raw/{source_id}/_inbox/")

    ws_dir = ULTRON_ROOT / "workspaces" / workspace
    inbox = ws_dir / watch_rel
    if not inbox.exists():
        sys.stderr.write(f"ingest-manual: no inbox at {inbox}\n")
        return 0

    files = [p for p in inbox.iterdir() if p.is_file() and not p.name.startswith(".")]
    if not files:
        return 0

    # Output path template: usually `raw/<source>/{YYYY-MM}/`. Source declares it explicitly.
    out_template = source.get("output_path", f"raw/{source_id}/{{YYYY-MM}}/")

    yyyymm = datetime.now().strftime("%Y-%m")
    out_dir_rel = out_template.replace("{YYYY-MM}", yyyymm).rstrip("/")
    out_dir = ws_dir / out_dir_rel
    out_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    for path in files:
        uid = f"manual:{source_id}:{path.name}"
        if uid in seen:
            continue
        slug = slugify(path.stem)
        ext = path.suffix or ".md"
        # Avoid collisions in destination dir.
        dst = out_dir / f"{slug}{ext}"
        n = 2
        while dst.exists():
            dst = out_dir / f"{slug}-{n}{ext}"
            n += 1
        shutil.move(str(path), str(dst))
        append_ingested(workspace, {
            "raw_path": str(dst.relative_to(ws_dir)),
            "source_id": source_id,
            "source_uid": uid,
            "content_hash": "",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "wiki_updates": [],
            "run_id": run_id,
        })
        seen.add(uid)
        processed += 1

    sys.stderr.write(f"ingest-manual: {source_id}: {processed} new files\n")
    return processed


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-manual.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]
    run_id = sys.argv[2]

    sources = load_manual_sources(workspace)
    if not sources:
        sys.stderr.write(f"ingest-manual: no manual sources for {workspace}\n")
        return 0

    seen = existing_uids(workspace)
    total = 0
    for source in sources:
        total += process_source(workspace, source, run_id, seen)
    sys.stderr.write(f"ingest-manual: {total} total new files for {workspace}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
