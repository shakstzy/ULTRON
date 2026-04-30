#!/usr/bin/env python3
"""
ingest-slack.py <workspace> <run_id>

Skeleton Slack ingest. Polls channels and DMs declared in the workspace's
sources.yaml, flattens threads, writes one markdown file per thread/day to
`workspaces/<ws>/raw/slack/<YYYY-MM>/<slug>.md`.

Auth: bot token (`xoxb-...`) at `_credentials/slack-<workspace>.json` with
shape `{"token": "xoxb-...", "team_id": "T..."}`. Required scopes:
`channels:history`, `groups:history`, `im:history`, `users:read`.

Live ingest is deferred. This file establishes the contract; raises when
called without credentials.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_source_config(workspace: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-slack: missing dep pyyaml\n")
        return None
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        return None
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    for source in cfg.get("sources", []):
        if source.get("type") == "slack":
            return source
    return None


def fetch_messages(workspace: str, source: dict) -> list[dict]:
    cred_path = ULTRON_ROOT / "_credentials" / f"slack-{workspace}.json"
    if not cred_path.exists():
        sys.stderr.write(
            f"ingest-slack: no credentials at {cred_path}; live ingest deferred.\n"
        )
        return []
    raise NotImplementedError(
        "ingest-slack is a TODO. Wire slack_sdk.WebClient and paginate "
        "conversations.history per channel/DM once token provisioned."
    )


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-slack.py <workspace> <run_id>\n")
        return 2
    workspace = sys.argv[1]
    run_id = sys.argv[2]

    source = load_source_config(workspace)
    if source is None:
        sys.stderr.write(f"ingest-slack: no slack source declared for {workspace}\n")
        return 0

    try:
        messages = fetch_messages(workspace, source)
    except NotImplementedError as exc:
        sys.stderr.write(f"ingest-slack: {exc}\n")
        return 0
    except Exception as exc:
        sys.stderr.write(f"ingest-slack: error: {exc}\n")
        return 1

    sys.stderr.write(f"ingest-slack: {len(messages)} new messages for {workspace}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
