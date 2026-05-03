#!/usr/bin/env python3
"""
ingest-slack.py — Slack robot, structured per the 9 locks in
_shell/stages/ingest/slack/format.md.

Skeleton mode. Set:
    IMPLEMENTATION_READY = True
at the top of the file ONLY after the activation checklist in
_shell/stages/ingest/slack/SETUP.md § 7 is green.

Forbidden behaviors (immutable contract — see format.md "Forbidden"):
1. Never delete a raw file based on Slack-side deletion.
2. Never copy attachment binaries (metadata + permalinks only).
3. Never run LLM / vision calls during ingest.
4. Never edit frontmatter post-write except deleted_messages,
   edited_messages_count, container_archived, deleted_upstream.
5. Never write outside workspaces/<ws>/raw/slack/<workspace-slug>/...
6. Never fetch full edit history (current text only).
7. Never render reactions.
8. Never render bot messages.
9. Never skip the universal pre-filter, even if a workspace allowlists
   the channel.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CREDENTIALS_DIR = ULTRON_ROOT / "_credentials"
CURSOR_DIR = ULTRON_ROOT / "_shell" / "cursors" / "slack"

# Initial backfill window if cursor is empty.
DEFAULT_LOOKBACK_DAYS = int(os.environ.get("ULTRON_SLACK_LOOKBACK_DAYS", "365"))

IMPLEMENTATION_READY = False


# ---------------------------------------------------------------------------
# Lock helpers
# ---------------------------------------------------------------------------
def lock_path_for(workspace_slug: str) -> str:
    """flock path per format.md Lock 9 — one lock per (workspace)."""
    return f"/tmp/com.adithya.ultron.ingest-slack-{workspace_slug}.lock"


def _try_lock(path: str):
    """Returns the open file handle if lock acquired, else None."""
    fh = open(path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fh
    except BlockingIOError:
        fh.close()
        return None


# ---------------------------------------------------------------------------
# Cursor (Lock 8) — per (workspace, container)
# ---------------------------------------------------------------------------
def workspace_cursor_dir(workspace_slug: str) -> Path:
    return CURSOR_DIR / workspace_slug


def cursor_path(workspace_slug: str, container_slug: str) -> Path:
    return workspace_cursor_dir(workspace_slug) / f"{container_slug}.txt"


def me_cursor_path(workspace_slug: str) -> Path:
    return workspace_cursor_dir(workspace_slug) / "me.txt"


def read_cursor(workspace_slug: str, container_slug: str) -> str | None:
    """Return latest seen Slack microsecond ts for the container, or None."""
    p = cursor_path(workspace_slug, container_slug)
    if not p.exists():
        return None
    return p.read_text().strip() or None


def write_cursor(workspace_slug: str, container_slug: str, ts: str) -> None:
    """Atomic cursor write per format.md Lock 8."""
    p = cursor_path(workspace_slug, container_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(f"{ts}\n")
    tmp.replace(p)


def read_me(workspace_slug: str) -> dict | None:
    """Return {'user_id': ..., 'canonical_slug': ...} or None."""
    p = me_cursor_path(workspace_slug)
    if not p.exists():
        return None
    out: dict = {}
    for line in p.read_text().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    if not out.get("user_id") or not out.get("canonical_slug"):
        return None
    return out


def write_me(workspace_slug: str, user_id: str,
             canonical_slug: str = "adithya-shak-kumar") -> None:
    p = me_cursor_path(workspace_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(f"user_id: {user_id}\ncanonical_slug: {canonical_slug}\n")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
def credentials_path(workspace_slug: str) -> Path:
    return CREDENTIALS_DIR / f"slack-{workspace_slug}.json"


def load_credentials(workspace_slug: str) -> dict | None:
    p = credentials_path(workspace_slug)
    if not p.exists():
        sys.stderr.write(
            f"ingest-slack: credentials missing at {p}. "
            "See _shell/stages/ingest/slack/SETUP.md § 1.\n"
        )
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"ingest-slack: credentials JSON invalid: {exc}\n")
        return None


# ---------------------------------------------------------------------------
# Workspace config + routing
# ---------------------------------------------------------------------------
def load_workspaces_config() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write("ingest-slack: missing dep pyyaml\n")
        return {}
    out: dict = {}
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if not workspaces_dir.exists():
        return out
    for ws_dir in sorted(workspaces_dir.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        cfg_path = ws_dir / "config" / "sources.yaml"
        if not cfg_path.exists():
            continue
        try:
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
        except Exception as exc:
            sys.stderr.write(
                f"ingest-slack: skipping {ws_dir.name} (bad sources.yaml): {exc}\n"
            )
            continue
        out[ws_dir.name] = cfg
    return out


def call_router(item: dict, workspaces_config: dict) -> list[str]:
    """Lazy import of route.py so the skeleton stays import-safe."""
    sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "stages" / "ingest" / "slack"))
    import route  # type: ignore
    return route.route(item, workspaces_config)


# ---------------------------------------------------------------------------
# Stub functions — bodies pending IMPLEMENTATION_READY flip
# ---------------------------------------------------------------------------
def auth_test(token: str) -> dict:
    """Slack auth.test → {user_id, user, team_id, team}. Stub."""
    raise NotImplementedError("auth_test — implement during activation pass")


def fetch_team_info(token: str) -> dict:
    """team.info → workspace metadata. Stub."""
    raise NotImplementedError("fetch_team_info — implement during activation pass")


def list_containers(token: str) -> list[dict]:
    """conversations.list types=public_channel,private_channel,im,mpim. Stub."""
    raise NotImplementedError("list_containers — implement during activation pass")


def fetch_history(token: str, channel_id: str, oldest: str | None) -> list[dict]:
    """conversations.history paginated. Stub."""
    raise NotImplementedError("fetch_history — implement during activation pass")


def fetch_thread_replies(token: str, channel_id: str, thread_ts: str) -> list[dict]:
    """conversations.replies cached per (channel,parent). Stub."""
    raise NotImplementedError(
        "fetch_thread_replies — implement during activation pass"
    )


def derive_user_slug(profile: dict) -> str:
    """Lock 2 priority order: display_name > real_name > email-stem > userid. Stub."""
    raise NotImplementedError("derive_user_slug — implement during activation pass")


def derive_workspace_slug(team_info: dict) -> str:
    """team.info name → kebab-case ASCII. Stub."""
    raise NotImplementedError("derive_workspace_slug — implement during activation pass")


def render_day(messages: list, container: dict, ws_slug: str,
               me_user_id: str) -> str:
    """Return body markdown per format.md Lock 5. Stub."""
    raise NotImplementedError("render_day — implement during activation pass")


def update_profile(container: dict, members: list, kind: str) -> None:
    """Append-only frontmatter update on the relevant _profile.md. Stub."""
    raise NotImplementedError("update_profile — implement during activation pass")


# ---------------------------------------------------------------------------
# CLI (Lock 9)
# ---------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Slack robot. Structured per format.md (the 9 locks).",
    )
    ap.add_argument("--workspace", required=True,
                    help="Slack workspace slug (e.g., eclipse-labs).")
    ap.add_argument("--containers", default=None,
                    help="Comma-separated subset of {channels,dms,group-dms}; "
                         "default: all.")
    ap.add_argument("--channel", default=None,
                    help="Single container slug (debugging).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Parse + render, no writes; cursor untouched.")
    ap.add_argument("--show", action="store_true",
                    help="In dry-run, print full rendered content.")
    ap.add_argument("--max-days", type=int, default=None,
                    help="Cap days back from cursor (validation aid).")
    ap.add_argument("--reset-cursor", action="store_true",
                    help="Wipe all cursors for the workspace; rebuild from "
                         "ULTRON_SLACK_LOOKBACK_DAYS.")
    ap.add_argument("--reset-cursor-channel", default=None,
                    help="Wipe cursor for one container only.")
    ap.add_argument("--no-attachments", action="store_true",
                    help="Skip attachment metadata extraction (fast schema-only "
                         "re-render).")
    ap.add_argument("--run-id", default=None,
                    help="Tag for ledger / log lines.")
    return ap.parse_args(argv)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    ws_slug = args.workspace

    # Concurrent-run guard.
    lock = _try_lock(lock_path_for(ws_slug))
    if lock is None:
        sys.stderr.write(
            f"ingest-slack: another run holds the lock for {ws_slug}; "
            "exiting 0 silently.\n"
        )
        return 0

    try:
        creds = load_credentials(ws_slug)
        if creds is None:
            return 0  # missing-creds path is informative-exit, not a failure

        if not IMPLEMENTATION_READY:
            sys.stderr.write(
                f"ingest-slack: skeleton — IMPLEMENTATION_READY is False. "
                "Complete the SETUP.md § 7 activation checklist before flipping.\n"
            )
            return 0

        # ---- Live ingest path ------------------------------------------------
        # Outline (full bodies pending activation):
        #   1. auth_test(creds["user_token"]); reconcile against me.txt
        #      (warn + exit 0 on mismatch; never silently swap).
        #   2. fetch_team_info; refresh workspace _profile.md.
        #   3. list_containers; iterate.
        #   4. For each container:
        #        a. read cursor (or bound by ULTRON_SLACK_LOOKBACK_DAYS).
        #        b. fetch_history paginated; collect parents + thread roots.
        #        c. fetch_thread_replies once per parent (cache within run).
        #        d. apply Lock 6 universal pre-filter.
        #        e. resolve display names via users.info (cache).
        #        f. handle message_changed / message_deleted state transitions.
        #        g. bucket by (container, local-date).
        #   5. For each (container, date) bucket:
        #        a. render_day per Lock 5.
        #        b. compute content_hash (blake3 of body markdown).
        #        c. call_router → destinations.
        #        d. write file + ledger row per destination (skip if --dry-run).
        #   6. update_profile (append-only) for each touched container.
        #   7. Append per-workspace summary to _meta/log.md.
        #   8. Advance cursors atomically per container after success.
        #   9. Write self-review.md to _shell/runs/<RUN_ID>/.
        # All forbidden behaviors at top of file MUST be enforced.

        sys.stderr.write(
            f"ingest-slack: starting workspace={ws_slug} "
            f"dry_run={args.dry_run} "
            f"lookback_days={DEFAULT_LOOKBACK_DAYS}\n"
        )
        return 0
    finally:
        try:
            lock.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
