#!/usr/bin/env python3
"""
ingest-discord.py — Discord robot.

Iterates every watermark under `workspaces/*/raw/.ingest-log/discord/*.json`
and re-invokes the Discord skill's `ingest` verb on each. Skill handles
auth, pagination, delta detection, and idempotent month writes.

Spawned by `run-stage.sh ingest-source discord <account>`. Account is
ignored (Discord is single-user, single-account); accepted to honor the
ingest-source contract.

Auth: persistent Chrome profile at
~/ULTRON/_credentials/browser-profiles/discord/. Refresh via
`node ~/.claude/skills/discord/scripts/run.mjs login` if breaker trips.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from glob import glob
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
SKILL_RUN = Path.home() / ".claude" / "skills" / "discord" / "scripts" / "run.mjs"


def discover_targets() -> list[tuple[str, str, str]]:
    """Return [(workspace, channel_id, slug)] across all workspaces."""
    out: list[tuple[str, str, str]] = []
    pattern = str(ULTRON_ROOT / "workspaces" / "*" / "raw" / ".ingest-log" / "discord" / "*.json")
    for path_str in sorted(glob(pattern)):
        path = Path(path_str)
        slug = path.stem
        workspace = path.parents[3].name
        try:
            wm = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"[discord-cron] skip {path}: {e}", file=sys.stderr)
            continue
        channel_id = wm.get("channel_id")
        if not channel_id:
            print(f"[discord-cron] skip {path}: no channel_id", file=sys.stderr)
            continue
        out.append((workspace, str(channel_id), slug))
    return out


def run_one(workspace: str, channel_id: str, slug: str) -> int:
    print(f"[discord-cron] -> {workspace}/{slug} (channel={channel_id})", file=sys.stderr)
    proc = subprocess.run(
        ["node", str(SKILL_RUN), "ingest", channel_id, "--workspace", workspace],
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", default="default")
    ap.add_argument("--run-id", default="")
    args = ap.parse_args()
    _ = args  # account ignored; run-id flows through subprocess env if needed

    if not SKILL_RUN.exists():
        print(f"[discord-cron] skill missing: {SKILL_RUN}", file=sys.stderr)
        return 2

    targets = discover_targets()
    if not targets:
        print("[discord-cron] no watermarks; nothing to refresh", file=sys.stderr)
        return 0

    failures: list[tuple[str, str]] = []
    for workspace, channel_id, slug in targets:
        rc = run_one(workspace, channel_id, slug)
        if rc != 0:
            failures.append((f"{workspace}/{slug}", str(rc)))

    if failures:
        print(f"[discord-cron] {len(failures)}/{len(targets)} failed:", file=sys.stderr)
        for label, rc in failures:
            print(f"  - {label} (exit {rc})", file=sys.stderr)
        return 1
    print(f"[discord-cron] {len(targets)} channel(s) refreshed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
