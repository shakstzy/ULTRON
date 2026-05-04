#!/usr/bin/env python3
"""
ingest-drive.py — Google Drive → workspaces/<ws>/raw/drive/...

Authoritative spec: _shell/stages/ingest/drive/format.md
Workflow: _shell/stages/ingest/drive/CONTEXT.md
Setup / activation: _shell/stages/ingest/drive/SETUP.md
Routing: _shell/stages/ingest/drive/route.py

One robot run = one upstream account. Multi-account scheduling is the
launchd / cron layer's job: one plist per account-slug.

This file is a SKELETON — IMPLEMENTATION_READY = False. The robot exits 0
with an actionable stderr message until the implementation lands AND
SETUP.md § 7 activation criteria are all green.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

# Flip to True ONLY after SETUP.md § 7 activation criteria are green.
IMPLEMENTATION_READY = False

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CREDS_DIR = ULTRON_ROOT / "_credentials"
CURSORS_DIR = ULTRON_ROOT / "_shell" / "cursors" / "drive"
LOGS_DIR = ULTRON_ROOT / "_logs"

# Lock 5: skip list for MIME types we never ingest.
MIME_SKIP_PREFIXES = ("video/", "audio/", "image/")
MIME_SKIP_EXACT = frozenset({
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-7z-compressed",
    "application/x-rar-compressed",
    "application/octet-stream",
    "application/vnd.google-apps.script",
    "application/vnd.google-apps.form",
    "application/vnd.google-apps.drawing",
    "application/vnd.google-apps.site",
})

# Lock 5: allowed MIME → drive_file_type.
MIME_ALLOWED: dict[str, str] = {
    "application/pdf": "pdf",
    "application/vnd.google-apps.document": "doc",
    "application/vnd.google-apps.spreadsheet": "sheet",
    "application/vnd.google-apps.presentation": "slide",
}

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024   # Lock 5

# Lock 9: slug derivation.
_SLUG_RUN_RE = re.compile(r"[^a-z0-9]+")
_HEX_FILTER_RE = re.compile(r"[^a-z0-9]")


def account_slug(email: str) -> str:
    """Same algorithm as Gmail (format.md Lock 1)."""
    if not email or "@" not in email:
        return ""
    local, _, domain = email.lower().partition("@")
    first_segment = domain.split(".")[0] if domain else ""
    raw = f"{local}-{first_segment}".strip("-")
    return _SLUG_RUN_RE.sub("-", raw).strip("-")


def folder_segment_slug(name: str) -> str:
    if not name:
        return "untitled-folder"
    try:
        import unicodedata
        name = unicodedata.normalize("NFKD", name)
        name = "".join(c for c in name if not unicodedata.combining(c))
    except Exception:
        pass
    name = name.encode("ascii", "ignore").decode("ascii").lower()
    name = _SLUG_RUN_RE.sub("-", name).strip("-")
    if not name:
        return "untitled-folder"
    return name[:60].rstrip("-") or "untitled-folder"


def file_slug(name: str) -> str:
    if not name:
        return "untitled-file"
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return folder_segment_slug(stem) or "untitled-file"


def file_id_short(file_id: str) -> str:
    if not file_id:
        return "00000000"
    head = file_id[:8].lower()
    return _HEX_FILTER_RE.sub("_", head)


def cred_path(account: str) -> Path:
    """Drive reuses the Gmail credential file (drive scope already granted)."""
    return CREDS_DIR / f"gmail-{account_slug(account)}.json"


def cursor_path(account: str) -> Path:
    return CURSORS_DIR / f"{account_slug(account)}.txt"


def lock_path(account: str) -> Path:
    return Path(f"/tmp/com.adithya.ultron.ingest-drive-{account_slug(account)}.lock")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Lock 8 — robot CLI."""
    p = argparse.ArgumentParser(
        prog="ingest-drive.py",
        description="Google Drive → ULTRON raw markdown. See format.md for spec.",
    )
    p.add_argument("--account", required=True, help="Upstream Gmail/Drive account email")
    p.add_argument("--workspaces", help="Comma-separated subset; default = all subscribers")
    p.add_argument("--mode", choices=("reconcile", "incremental"), default="incremental")
    p.add_argument("--dry-run", action="store_true", help="Render, don't write or mutate cursor")
    p.add_argument("--show", action="store_true", help="In dry-run, print body to stdout")
    p.add_argument("--max-files", type=int, default=0, help="Hard cap on files processed")
    p.add_argument("--folder", help="Restrict to a single designated folder ID (debugging)")
    p.add_argument("--reset-cursor", action="store_true", help="Delete cursor; force reconcile")
    p.add_argument("--no-content", action="store_true", help="Skip text extraction")
    p.add_argument("--run-id", default=time.strftime("%Y%m%dT%H%M%S"))
    return p.parse_args(argv)


def acquire_flock(path: Path):
    """Per-account flock. Concurrent invocation exits 0 silently."""
    import fcntl

    fh = open(path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.stderr.write(f"ingest-drive: another run holds {path}; exiting 0.\n")
        fh.close()
        sys.exit(0)
    return fh


def load_workspace_configs() -> dict[str, dict]:
    """Walk workspaces/*/config/sources.yaml; return {ws: parsed-yaml}."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("ingest-drive: missing dep pyyaml; install once before activation.\n")
        return {}
    out: dict[str, dict] = {}
    ws_root = ULTRON_ROOT / "workspaces"
    if not ws_root.exists():
        return out
    for ws_dir in ws_root.iterdir():
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        cfg = ws_dir / "config" / "sources.yaml"
        if not cfg.exists():
            continue
        try:
            out[ws_dir.name] = yaml.safe_load(cfg.read_text()) or {}
        except yaml.YAMLError as e:
            sys.stderr.write(f"ingest-drive: {ws_dir.name}/sources.yaml unreadable: {e}\n")
    return out


def designated_folders_for(account: str, workspaces: dict[str, dict]) -> list[dict]:
    """Return list of {workspace, folder_id, folder_name, exclude_subfolders}
    that this account is responsible for ingesting."""
    out: list[dict] = []
    for ws, cfg in workspaces.items():
        block = (cfg.get("sources") or {}).get("drive") if isinstance(cfg.get("sources"), dict) else None
        if not block:
            continue
        for acct in block.get("accounts") or []:
            if not isinstance(acct, dict):
                continue
            if (acct.get("account") or "").lower() != account.lower():
                continue
            for folder in acct.get("folders") or []:
                if not isinstance(folder, dict) or not folder.get("id"):
                    continue
                out.append({
                    "workspace": ws,
                    "folder_id": folder["id"],
                    "folder_name": folder.get("name") or "",
                    "exclude_subfolders": [
                        e.get("id") for e in (folder.get("exclude_subfolders") or [])
                        if isinstance(e, dict) and e.get("id")
                    ],
                })
    return out


def reconcile(args: argparse.Namespace, designated: list[dict]) -> int:
    """Lock 6 — full reconciliation."""
    raise NotImplementedError(
        "reconcile() is the Lock 6 algorithm. See format.md § Lock 6:\n"
        "  1. Enumerate Drive side recursively under each designated folder.\n"
        "  2. Apply Lock 5 pre-filter.\n"
        "  3. Walk raw/drive/<account-slug>/, read frontmatter, build raw_set.\n"
        "  4. Compute deltas (new / modified / moved / removed).\n"
        "  5. Apply: hard-deletes FIRST (atomic), then ingest/re-ingest.\n"
        "  6. Persist new changes.list page token to cursor.\n"
    )


def incremental(args: argparse.Namespace, designated: list[dict]) -> int:
    """Lock 7 — cursor-driven changes.list event stream."""
    raise NotImplementedError(
        "incremental() is the Lock 7 fast-path. See format.md § Lock 7:\n"
        "  1. Read cursor (changes.list page token).\n"
        "  2. changes.list(pageToken=cursor, includeRemoved=true), follow nextPageToken.\n"
        "  3. Per event: classify (added / modified / moved-out / trashed / hard-deleted).\n"
        "  4. Apply ingests + hard-deletes per Lock 6 semantics.\n"
        "  5. Persist nextPageToken (or newStartPageToken) to cursor.\n"
    )


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    cred = cred_path(args.account)
    if not cred.exists():
        sys.stderr.write(
            f"ingest-drive: missing credential at {cred}. "
            "See SETUP.md § 1 for OAuth provisioning.\n"
        )
        return 0

    workspaces = load_workspace_configs()
    if args.workspaces:
        keep = set(args.workspaces.split(","))
        workspaces = {k: v for k, v in workspaces.items() if k in keep}

    designated = designated_folders_for(args.account, workspaces)
    if args.folder:
        designated = [d for d in designated if d["folder_id"] == args.folder]
    if not designated:
        sys.stderr.write(
            f"ingest-drive: no designated folders declared for {args.account} "
            "in any workspace's sources.yaml. See SETUP.md § 3.\n"
        )
        return 0

    if not IMPLEMENTATION_READY:
        sys.stderr.write(
            "ingest-drive: IMPLEMENTATION_READY = False. Robot is a skeleton. "
            "See SETUP.md § 7 for the activation procedure.\n"
            f"  account: {args.account}\n"
            f"  designated folders ({len(designated)}):\n"
        )
        for d in designated:
            sys.stderr.write(
                f"    - {d['workspace']}: {d['folder_name'] or '(unnamed)'} "
                f"({d['folder_id']})\n"
            )
        return 0

    CURSORS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset_cursor and cursor_path(args.account).exists():
        cursor_path(args.account).unlink()

    fh = acquire_flock(lock_path(args.account))
    try:
        if args.mode == "reconcile" or not cursor_path(args.account).exists():
            return reconcile(args, designated)
        return incremental(args, designated)
    finally:
        fh.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
