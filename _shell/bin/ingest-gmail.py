#!/usr/bin/env python3
"""
ingest-gmail.py <workspace> <run_id>

Skeleton Gmail ingest. Pulls threads matching the workspace's Gmail filter
config, writes one markdown file per thread to
`workspaces/<ws>/raw/gmail/<YYYY-MM>/<slug>.md`, appends to
`_meta/ingested.jsonl`.

Auth (one of):
  - OAuth: `_credentials/gmail-<workspace>.json` (Google authorized-user JSON
    with refresh_token).
  - `gog` CLI delegation: if the source's config has `via: gog` and the gog
    CLI is on PATH, this script shells out to `gog gmail messages` for
    authentication-free fetches across the 4 Workspace accounts. (Not yet
    implemented.)

Live ingest is deferred per Adithya. This file establishes the contract; the
OAuth path is unimplemented (raises NotImplementedError on call) until
credentials are provisioned.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_source_config(workspace: str) -> dict | None:
    """Return the gmail source block from sources.yaml, or None if absent."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-gmail: missing dep pyyaml\n")
        return None
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        return None
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    for source in cfg.get("sources", []):
        if source.get("type") == "gmail":
            return source
    return None


def append_ingested(workspace: str, record: dict) -> None:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(json.dumps(record) + "\n")


def fetch_threads_via_oauth(workspace: str, source: dict) -> list[dict]:
    """OAuth path. Reads ~/_credentials/gmail-<ws>.json, calls Gmail API."""
    from googleapiclient.discovery import build  # noqa: F401
    from google.oauth2.credentials import Credentials  # noqa: F401

    cred_path = ULTRON_ROOT / "_credentials" / f"gmail-{workspace}.json"
    if not cred_path.exists():
        sys.stderr.write(
            f"ingest-gmail: no credentials at {cred_path}; "
            "live ingest deferred. See sources.yaml + bootstrap docs.\n"
        )
        return []

    raise NotImplementedError(
        "ingest-gmail OAuth path is a TODO. Wire google-api-python-client + "
        "Credentials.from_authorized_user_file once Adithya provisions tokens."
    )


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-gmail.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]
    run_id = sys.argv[2]

    source = load_source_config(workspace)
    if source is None:
        sys.stderr.write(f"ingest-gmail: no gmail source declared for {workspace}\n")
        return 0

    via = source.get("config", {}).get("via", "oauth")
    if via == "gog":
        sys.stderr.write("ingest-gmail: via=gog path not yet implemented\n")
        return 0

    try:
        threads = fetch_threads_via_oauth(workspace, source)
    except NotImplementedError as exc:
        sys.stderr.write(f"ingest-gmail: {exc}\n")
        return 0
    except Exception as exc:  # broad: skeleton phase
        sys.stderr.write(f"ingest-gmail: error: {exc}\n")
        return 1

    yyyymm = datetime.now().strftime("%Y-%m")
    raw_dir = ULTRON_ROOT / "workspaces" / workspace / "raw" / "gmail" / yyyymm
    raw_dir.mkdir(parents=True, exist_ok=True)

    for thread in threads:
        slug = thread.get("slug") or f"thread-{thread.get('id', 'unknown')}"
        md_path = raw_dir / f"{slug}.md"
        md_path.write_text(thread.get("markdown", ""))
        append_ingested(workspace, {
            "raw_path": str(md_path.relative_to(ULTRON_ROOT / "workspaces" / workspace)),
            "source_id": source.get("id", "gmail"),
            "source_uid": f"gmail:thread:{thread.get('id', '')}",
            "content_hash": thread.get("content_hash", ""),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "wiki_updates": [],
            "run_id": run_id,
        })

    sys.stderr.write(f"ingest-gmail: {len(threads)} new threads for {workspace}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
