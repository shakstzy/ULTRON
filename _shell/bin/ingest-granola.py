#!/usr/bin/env python3
"""
ingest-granola.py — Granola.ai meeting-note ingest robot.

Authoritative spec:  _shell/stages/ingest/granola/format.md (8 locks)
Workflow contract:   _shell/stages/ingest/granola/CONTEXT.md

Usage:
    ingest-granola.py [--account <email>] [--workspaces a,b,c] [--dry-run]
                      [--max-items N] [--reset-cursor] [--run-id ID]

If --account is omitted, the email from supabase.json is used.
--workspaces filters to a subset of subscribing workspaces.
--max-items caps the number of docs fetched (smoke-test convenience).
"""
from __future__ import annotations

import argparse
import fcntl
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import blake3
import yaml

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
SUBSTAGE_DIR = ULTRON_ROOT / "_shell" / "stages" / "ingest" / "granola"
INGEST_VERSION = 1

if str(SUBSTAGE_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSTAGE_DIR))

# Substage modules (resolved via sys.path above).
from auth import (  # noqa: E402
    SUPABASE_PATH, get_access_token, get_account_email, parse_user_info,
    read_supabase_raw,
)
from api import GranolaClient  # noqa: E402
from cursor import read_cursor, write_cursor  # noqa: E402
from filter import should_skip  # noqa: E402
from ledger import append_row, find_last_row  # noqa: E402
from prosemirror import render_prosemirror  # noqa: E402  (re-export check)
from render import render_body, transcript_duration_ms, build_attendees, build_calendar_event  # noqa: E402
from route import route as route_doc  # noqa: E402
from slug import account_slug, title_slug  # noqa: E402


# ---------------------------------------------------------------------------
# Workspace config discovery
# ---------------------------------------------------------------------------

def discover_workspaces(filter_slugs: set[str] | None = None) -> dict[str, dict]:
    """Return {ws_slug: parsed_sources_yaml} for every workspace that has
    a `sources.granola.folders` block."""
    out: dict[str, dict] = {}
    ws_dir = ULTRON_ROOT / "workspaces"
    if not ws_dir.is_dir():
        return out
    for child in sorted(ws_dir.iterdir()):
        if not child.is_dir():
            continue
        sources_yaml = child / "config" / "sources.yaml"
        if not sources_yaml.is_file():
            continue
        try:
            cfg = yaml.safe_load(sources_yaml.read_text()) or {}
        except yaml.YAMLError:
            continue
        sources = cfg.get("sources") or {}
        gran = sources.get("granola")
        if not gran or not gran.get("folders"):
            continue
        if filter_slugs is not None and child.name not in filter_slugs:
            continue
        out[child.name] = cfg
    return out


def all_subscribed_folders(workspaces_config: dict[str, dict]) -> set[str]:
    out: set[str] = set()
    for cfg in workspaces_config.values():
        gran = (cfg.get("sources") or {}).get("granola") or {}
        for f in gran.get("folders") or []:
            out.add(f)
    return out


# ---------------------------------------------------------------------------
# Path / hash
# ---------------------------------------------------------------------------

def created_at_local_date(iso: str) -> str:
    """`'2026-04-13T18:39:35.743Z'` → `'2026-04-13'` in local TZ."""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    return dt.strftime("%Y-%m-%d")


def created_at_local_year_month(iso: str) -> tuple[str, str]:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    return dt.strftime("%Y"), dt.strftime("%m")


def doc_filename(doc: dict) -> str:
    date = created_at_local_date(doc["created_at"])
    tslug = title_slug(doc.get("title") or "")
    docid8 = doc["id"][:8].lower()
    return f"{date}__{tslug}__{docid8}.md"


def doc_subpath(doc: dict, account_slug_value: str) -> Path:
    """Relative-to-workspace path: raw/granola/<account>/<YYYY>/<MM>/<file>.md"""
    yyyy, mm = created_at_local_year_month(doc["created_at"])
    return Path("raw") / "granola" / account_slug_value / yyyy / mm / doc_filename(doc)


def content_hash(body: str) -> str:
    return "blake3:" + blake3.blake3(body.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def build_frontmatter(*, doc: dict, ws_slug: str, account_email: str,
                      account_slug_value: str, ingested_at: str,
                      content_hash_value: str, body: str,
                      folder_titles: list[str], folders_with_ids: list[dict],
                      transcript_segments: list[dict],
                      routed_by: list[dict]) -> str:
    creator, attendees = build_attendees(doc.get("people"))
    cal = build_calendar_event(doc.get("google_calendar_event"))
    dur = transcript_duration_ms(transcript_segments)
    n_final = sum(1 for s in (transcript_segments or [])
                  if s.get("is_final", True) is not False)

    fm: dict = {
        "source": "granola",
        "workspace": ws_slug,
        "ingested_at": ingested_at,
        "ingest_version": INGEST_VERSION,
        "content_hash": content_hash_value,
        "provider_modified_at": doc.get("updated_at"),

        "account": account_email,
        "account_slug": account_slug_value,
        "document_id": doc["id"],
        "document_id_short": doc["id"][:8].lower(),
        "title": doc.get("title") or "",
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
        "folders": folders_with_ids,
        "creator": creator if creator else None,
        "attendees": attendees,
        "calendar_event": cal,
        "transcript_segment_count": n_final,
        "duration_ms": dur,
        "valid_meeting": doc.get("valid_meeting"),
        "was_trashed": doc.get("was_trashed"),
        "routed_by": routed_by,
    }
    fm_yaml = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                             default_flow_style=False).strip()
    return f"---\n{fm_yaml}\n---\n\n"


# ---------------------------------------------------------------------------
# Per-doc write (with rename / dedup handling — Lock 6)
# ---------------------------------------------------------------------------

def write_doc_for_workspace(
    *,
    workspace_root: Path,
    rel_path: Path,
    body: str,
    full_markdown: str,
    doc_id: str,
    ch: str,
    routed_by: list[dict],
    dry_run: bool,
    log: list[str],
) -> str:
    """Write the rendered markdown for a single (workspace, doc) pair.

    Handles Lock 6 rename/dedup:
      - Same key + same hash + same path → skip.
      - Same key + same hash + DIFFERENT path → move file, ledger row.
      - Same key + different hash → overwrite at new path; remove old if path differs.
    Returns "wrote" / "moved" / "skipped" / "overwrote".
    """
    ledger_path = workspace_root / "_meta" / "ingested.jsonl"
    abs_path = workspace_root / rel_path
    rel_str = str(rel_path)

    last = find_last_row(ledger_path, source="granola", key=doc_id)

    if last and last.get("content_hash") == ch and last.get("path") == rel_str:
        if abs_path.exists():
            log.append(f"skip-unchanged {doc_id[:8]} {rel_str}")
            return "skipped"

    # Determine action and prepare filesystem state.
    action: str
    old_rel = last.get("path") if last else None
    old_abs = workspace_root / old_rel if old_rel else None

    if last and last.get("content_hash") == ch and old_rel and old_rel != rel_str:
        # Rename: same hash, different path → move.
        action = "moved"
        if not dry_run:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            if old_abs and old_abs.exists():
                os.replace(old_abs, abs_path)
            else:
                abs_path.write_text(full_markdown, encoding="utf-8")
    elif last and last.get("content_hash") != ch and old_rel and old_rel != rel_str:
        # Overwrite at new path; remove orphan old file.
        action = "overwrote"
        if not dry_run:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(full_markdown, encoding="utf-8")
            if old_abs and old_abs.exists():
                try:
                    old_abs.unlink()
                except OSError:
                    pass
    elif last and last.get("content_hash") != ch:
        # Same path, different hash → overwrite in place.
        action = "overwrote"
        if not dry_run:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(full_markdown, encoding="utf-8")
    else:
        # First write for this key.
        action = "wrote"
        if not dry_run:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(full_markdown, encoding="utf-8")

    if not dry_run:
        append_row(
            ledger_path,
            source="granola",
            key=doc_id,
            content_hash=ch,
            path=rel_str,
            routed_by=routed_by,
            action=action,
        )
    log.append(f"{action} {doc_id[:8]} {rel_str}")
    return action


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", default=None,
                    help="Granola account email; default = email in supabase.json")
    ap.add_argument("--workspaces", default=None,
                    help="Comma-separated workspace allowlist")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-items", type=int, default=None,
                    help="Cap on docs ingested this run (for smoke testing)")
    ap.add_argument("--reset-cursor", action="store_true")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    account_email = args.account or get_account_email()
    if not account_email:
        print("could not resolve Granola account email", file=sys.stderr)
        return 2
    acct_slug = account_slug(account_email)
    run_id = args.run_id or datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    ws_filter: set[str] | None = (
        {s.strip() for s in args.workspaces.split(",") if s.strip()}
        if args.workspaces else None
    )

    log_path = ULTRON_ROOT / "_logs" / f"granola-{acct_slug}-{run_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    run_log: list[str] = [
        f"granola ingest start  account={account_email}  run_id={run_id}  dry_run={args.dry_run}"
    ]

    # flock
    lock_path = f"/tmp/com.adithya.ultron.ingest-granola-{acct_slug}.lock"
    lock_fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"another ingest-granola is running for {acct_slug}; exiting",
                  file=sys.stderr)
            return 0

        # Workspaces
        workspaces_config = discover_workspaces(ws_filter)
        if not workspaces_config:
            run_log.append("no subscribing workspace; nothing to do")
            log_path.write_text("\n".join(run_log) + "\n")
            return 0
        subscribed = all_subscribed_folders(workspaces_config)
        run_log.append(f"workspaces: {sorted(workspaces_config.keys())}")
        run_log.append(f"subscribed folders: {sorted(subscribed)}")

        # Cursor
        cursor_path = ULTRON_ROOT / "_shell" / "cursors" / "granola" / f"{acct_slug}.txt"
        if args.reset_cursor and cursor_path.exists():
            cursor_path.unlink()
        cursor = None if args.reset_cursor else read_cursor(cursor_path)
        run_log.append(f"cursor: {cursor!r}")

        # API
        client = GranolaClient()

        # Folders → doc_id → folder_titles map
        folders = client.list_folders()  # {folder_id: folder_dict}
        doc_to_folder_titles: dict[str, list[str]] = {}
        doc_to_folder_objs: dict[str, list[dict]] = {}
        subscribed_doc_ids: set[str] = set()
        for fid, f in folders.items():
            title = f.get("title") or f.get("name") or ""
            for did in f.get("document_ids") or []:
                doc_to_folder_titles.setdefault(did, []).append(title)
                doc_to_folder_objs.setdefault(did, []).append({"id": fid, "title": title})
                if title in subscribed:
                    subscribed_doc_ids.add(did)
        run_log.append(f"subscribed doc count: {len(subscribed_doc_ids)}")

        if not subscribed_doc_ids:
            run_log.append("no docs match subscribed folders; done")
            log_path.write_text("\n".join(run_log) + "\n")
            return 0

        # Cap (smoke-test)
        ids_list = sorted(subscribed_doc_ids)
        if args.max_items:
            ids_list = ids_list[:args.max_items]

        # Fetch docs
        docs = client.get_documents_batch(ids_list)
        run_log.append(f"fetched {len(docs)} docs")

        # Cursor filter (incremental)
        if cursor:
            before = len(docs)
            docs = [d for d in docs if (d.get("updated_at") or "") > cursor]
            run_log.append(f"cursor filter: {before} → {len(docs)}")

        # Ingest loop
        max_updated_at = cursor or ""
        wrote_count = 0
        skipped_count = 0
        ingest_at_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        for doc in docs:
            doc_id = doc.get("id")
            if not doc_id:
                continue
            doc["folder_titles"] = doc_to_folder_titles.get(doc_id, [])
            folders_with_ids = doc_to_folder_objs.get(doc_id, [])

            # Transcript fetch (catch + continue)
            try:
                transcript_segments = client.get_transcript(doc_id)
            except Exception as e:
                run_log.append(f"  transcript-fail {doc_id[:8]}: {e}")
                continue

            # Pre-filter
            skip, reason = should_skip(doc, transcript_segments, subscribed)
            if skip:
                run_log.append(f"  skip {doc_id[:8]} {reason}")
                skipped_count += 1
                continue

            # Render body
            body = render_body(doc, transcript_segments, sorted(subscribed))
            ch = content_hash(body)

            # Route
            decisions = route_doc(doc, workspaces_config)
            if not decisions:
                run_log.append(f"  unrouted {doc_id[:8]}")
                continue

            # Filename / path
            rel_path = doc_subpath(doc, acct_slug)

            # Per workspace
            for d in decisions:
                ws_slug = d["workspace"]
                workspace_root = ULTRON_ROOT / "workspaces" / ws_slug
                # Frontmatter is workspace-scoped (records routed_by for this ws).
                this_routed = [d]
                fm = build_frontmatter(
                    doc=doc, ws_slug=ws_slug,
                    account_email=account_email,
                    account_slug_value=acct_slug,
                    ingested_at=ingest_at_iso,
                    content_hash_value=ch,
                    body=body,
                    folder_titles=doc["folder_titles"],
                    folders_with_ids=folders_with_ids,
                    transcript_segments=transcript_segments,
                    routed_by=this_routed,
                )
                full_md = fm + body
                action = write_doc_for_workspace(
                    workspace_root=workspace_root,
                    rel_path=rel_path,
                    body=body,
                    full_markdown=full_md,
                    doc_id=doc_id,
                    ch=ch,
                    routed_by=this_routed,
                    dry_run=args.dry_run,
                    log=run_log,
                )
                if action == "skipped":
                    skipped_count += 1
                else:
                    wrote_count += 1

            ua = doc.get("updated_at") or ""
            if ua > max_updated_at:
                max_updated_at = ua

        # Advance cursor
        if not args.dry_run and max_updated_at and max_updated_at != cursor:
            write_cursor(cursor_path, max_updated_at)
            run_log.append(f"cursor advanced to {max_updated_at}")

        run_log.append(f"done; wrote={wrote_count} skipped={skipped_count}")
        log_path.write_text("\n".join(run_log) + "\n")
        print("\n".join(run_log[-12:]))
        return 0
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
