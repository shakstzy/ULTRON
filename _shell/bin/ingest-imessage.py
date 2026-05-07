#!/usr/bin/env python3
"""
ingest-imessage.py — iMessage robot, structured per the 9 locks in
_shell/stages/ingest/imessage/format.md.

Skeleton mode. Set:
    IMPLEMENTATION_READY = True
at the top of the file ONLY after the activation checklist in
_shell/stages/ingest/imessage/SETUP.md § 7 is green.

Forbidden behaviors (immutable contract — see format.md § J):
1. Never delete a raw file based on chat.db deletion.
2. Never modify chat.db. Read-only URI mode (?mode=ro) required.
3. Never run LLM or vision calls during ingest.
4. Never edit frontmatter post-write except deleted_upstream / superseded_by.
5. Never copy attachments outside the deterministic _attachments/ path.
6. Never overwrite an existing _attachments/<id>.<ext> with different content.
7. Never skip the universal blocklist in format.md § F.
"""
from __future__ import annotations

import argparse
import datetime
import fcntl
import os
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"
ATTACHMENTS_ROOT = Path.home() / "Library" / "Messages" / "Attachments"
CURSOR_DIR = ULTRON_ROOT / "_shell" / "cursors" / "imessage"
LOCK_PATH = "/tmp/com.adithya.ultron.ingest-imessage.lock"

# Lookback window applied ONLY when --reset-cursor is used. First-run with
# an empty cursor backfills the entire chat.db (Codex finding: spec said
# full archive but constant defaulted to 365 days). Default 0 means "no
# lookback floor; use whatever the cursor or --since says."
DEFAULT_LOOKBACK_DAYS = int(os.environ.get("ULTRON_IMESSAGE_LOOKBACK_DAYS", "0"))

# Per-month attachment copy budget (LOCK 7).
ATTACHMENT_COPY_BUDGET_BYTES = 100 * 1024 * 1024  # 100 MB

# Universal blocklist (LOCK 6 / format.md § F). Strings here are matched
# against handle/balloon_bundle_id by the renderer; this list is the source
# of truth for the format-level pre-filter.
TOLL_FREE_PREFIXES = ("+1800", "+1888", "+1877", "+1866", "+1855", "+1844", "+1833")
NOREPLY_LOCALPARTS = ("verify", "noreply", "no-reply", "donotreply")
SKIP_BALLOON_BUNDLE_IDS_NO_TEXT = {
    "com.apple.messages.URLBalloonProvider",
}

IMPLEMENTATION_READY = False


# ---------------------------------------------------------------------------
# Cursor (LOCK 8) — dual-store last_rowid + last_message_date
# ---------------------------------------------------------------------------
def cursor_path(account: str = "local") -> Path:
    return CURSOR_DIR / f"{account}.txt"


def read_cursor(account: str = "local") -> dict:
    """Returns {'last_rowid': int, 'last_message_date': str | None}."""
    p = cursor_path(account)
    if not p.exists():
        return {"last_rowid": 0, "last_message_date": None}
    out: dict = {"last_rowid": 0, "last_message_date": None}
    for line in p.read_text().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if k == "last_rowid":
            try:
                out["last_rowid"] = int(v or "0")
            except ValueError:
                out["last_rowid"] = 0
        elif k == "last_message_date":
            out["last_message_date"] = v or None
    return out


def write_cursor(rowid: int, message_date: str, account: str = "local") -> None:
    """Crash-safe dual-write of last_rowid + last_message_date.

    fsync the temp file AND the parent directory before renaming so a power
    loss does not leave the cursor zeroed/old (Codex + Gemini finding).
    """
    p = cursor_path(account)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w") as f:
        f.write(f"last_rowid: {rowid}\nlast_message_date: {message_date}\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(p)
    # Round-3 fix (Gemini): some macOS filesystems return EINVAL on
    # fsync(dir_fd). Wrap so the cursor write doesn't fail when the rename
    # already landed durably enough for our purposes.
    try:
        dir_fd = os.open(str(p.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass


# Mac absolute time epoch: nanoseconds since 2001-01-01T00:00:00Z (post macOS
# 10.13 chat.db). Pre-10.13 used seconds; detect by magnitude.
_MAC_EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)


_MAC_LOWER = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_MAC_UPPER = datetime.datetime(2200, 1, 1, tzinfo=datetime.timezone.utc)


def mac_absolute_to_dt(val: int | float | None) -> datetime.datetime | None:
    """Convert chat.db Mac absolute time to UTC datetime.

    Round-2 fix (Codex + Gemini): use abs(val) so pre-2001 negative dates
    don't blow up the timedelta. Round-3 fix (Gemini): magnitude-based
    detection (`> 10**11`) misclassifies values within ~100s of the 2001
    epoch as seconds and shoots them into the year 2318. Try nanoseconds
    first; if the result lands outside [2001, 2200), retry as seconds.
    """
    if val is None:
        return None
    try:
        ns_dt = _MAC_EPOCH + datetime.timedelta(seconds=float(val) / 1e9)
        if _MAC_LOWER <= ns_dt < _MAC_UPPER:
            return ns_dt
    except (OverflowError, ValueError):
        pass
    try:
        return _MAC_EPOCH + datetime.timedelta(seconds=float(val))
    except (OverflowError, ValueError):
        return None


def cursor_sanity_check(conn: sqlite3.Connection, cur: dict) -> str:
    """Returns 'rowid' if fast path is safe, 'date' if ROWID was reset/reused.

    Compares the actual `message.date` at ROWID against `last_message_date`.
    If they diverge by more than 60s, ROWID was reused after a chat.db
    rebuild (Mac migration / Messages reset / iCloud rebuild). Fall back.
    """
    rowid = cur.get("last_rowid", 0)
    expected_date = cur.get("last_message_date")
    if rowid <= 0 or expected_date is None:
        return "date"
    row = conn.execute(
        "SELECT date FROM message WHERE ROWID = ?", (rowid,)
    ).fetchone()
    if row is None:
        sys.stderr.write(
            f"ingest-imessage: ROWID {rowid} no longer present in chat.db; "
            "falling back to date-based cursor (per format.md § H).\n"
        )
        return "date"
    actual_dt = mac_absolute_to_dt(row[0])
    try:
        expected_dt = datetime.datetime.fromisoformat(expected_date)
    except ValueError:
        sys.stderr.write(
            f"ingest-imessage: stored last_message_date is not ISO 8601; "
            "falling back to date-based cursor.\n"
        )
        return "date"
    if actual_dt is None or abs((actual_dt - expected_dt).total_seconds()) > 60:
        sys.stderr.write(
            f"ingest-imessage: ROWID {rowid} date drift detected (expected "
            f"{expected_dt.isoformat()}, got "
            f"{actual_dt.isoformat() if actual_dt else 'null'}); ROWID was "
            "reused after a chat.db rebuild. Falling back to date cursor.\n"
        )
        return "date"
    return "rowid"


# ---------------------------------------------------------------------------
# Workspace config + routing
# ---------------------------------------------------------------------------
def load_workspaces_config() -> dict:
    import yaml  # type: ignore
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
        except Exception:
            continue
        out[ws_dir.name] = cfg
    return out


# Routing logic lives in _shell/stages/ingest/imessage/route.py. Imported
# lazily during a live run so the skeleton is import-safe even if the file
# moves.
def call_router(item: dict, workspaces_config: dict) -> list[str]:
    sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "stages" / "ingest" / "imessage"))
    import route  # type: ignore
    return route.route(item, workspaces_config)


# ---------------------------------------------------------------------------
# chat.db (read-only)
# ---------------------------------------------------------------------------
def open_chat_db() -> sqlite3.Connection:
    """Open chat.db read-only via URI. Forbidden behavior #2: never write."""
    uri = f"file:{CHAT_DB}?mode=ro"
    return sqlite3.connect(uri, uri=True)


# ---------------------------------------------------------------------------
# Stub functions — full bodies pending IMPLEMENTATION_READY flip
# ---------------------------------------------------------------------------
def derive_slug(handle: str, contacts_lookup) -> tuple[str, str]:
    """Return (slug, derivation_kind) per format.md § C. Stub."""
    raise NotImplementedError("derive_slug — implement during activation pass")


def render_month(messages: list, attachments: list, contact: dict) -> str:
    """Return body markdown per format.md § E. Stub."""
    raise NotImplementedError("render_month — implement during activation pass")


def copy_attachment(att: dict, dest_dir: Path, running_total: int) -> dict:
    """Per format.md § G. Returns updated attachment metadata. Stub."""
    raise NotImplementedError("copy_attachment — implement during activation pass")


def resolve_tapbacks(messages: list) -> list:
    """Per format.md § I. Stub."""
    raise NotImplementedError("resolve_tapbacks — implement during activation pass")


# ---------------------------------------------------------------------------
# CLI (LOCK 9)
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="iMessage robot. Structured per format.md (the 9 locks).",
    )
    ap.add_argument(
        "--workspaces",
        help="Comma-separated workspace slugs (default: all with imessage in sources.yaml).",
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="Parse + render, no writes, no copies.")
    ap.add_argument("--show", action="store_true",
                    help="In dry-run, print full rendered content.")
    ap.add_argument("--max-contacts", type=int, default=None,
                    help="Cap number of contacts processed (validation aid).")
    ap.add_argument("--since", default=None,
                    help="Override cursor for this run (ISO 8601 date).")
    ap.add_argument("--reset-cursor", action="store_true",
                    help="Delete cursor; re-bootstrap from ULTRON_IMESSAGE_LOOKBACK_DAYS.")
    ap.add_argument("--contact", default=None,
                    help="Ingest only one contact (debugging).")
    ap.add_argument("--no-attachments", action="store_true",
                    help="Skip attachment copy phase entirely.")
    # Compatibility with run-stage.sh `ingest-source` dispatcher, which calls
    # every ingest robot with `--account <acct> --run-id <id>`. iMessage is
    # account-less (chat.db is local) and doesn't track per-run state, so both
    # are accepted and ignored.
    ap.add_argument("--account", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--run-id", default=None, help=argparse.SUPPRESS)
    return ap.parse_args()


# ---------------------------------------------------------------------------
# Lock + main
# ---------------------------------------------------------------------------
def _try_lock(path: str):
    """Returns an open fd if lock acquired, else None (silent exit).

    Uses os.open with O_CREAT|O_RDWR so we do NOT truncate the file before
    flock (Gemini + Codex finding: `open(path, "w")` raced two parallel
    runs by clobbering each other's lock file before the flock call).
    """
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        os.close(fd)
        return None


def main() -> int:
    args = parse_args()

    # Concurrent-run guard. Per CONTEXT.md the silent exit is silent: no
    # stderr message (Codex finding: code contradicted the contract).
    lock_fd = _try_lock(LOCK_PATH)
    if lock_fd is None:
        return 0

    try:
        if not CHAT_DB.exists():
            sys.stderr.write(
                f"ingest-imessage: {CHAT_DB} not readable. Grant Full Disk Access "
                "to the process running this script. See "
                "_shell/stages/ingest/imessage/SETUP.md § 1.\n"
            )
            # Exit non-zero so cron / launchd treats setup failure as failure
            # (Codex finding: was returning 0 and hiding misconfiguration).
            return 3

        if not IMPLEMENTATION_READY:
            sys.stderr.write(
                "ingest-imessage: skeleton — IMPLEMENTATION_READY is False. "
                "Complete the SETUP.md § 7 activation checklist before flipping.\n"
            )
            return 0

        # ---- Live ingest path ------------------------------------------------
        # Outline (full bodies pending activation):
        #   1. Resolve cursor (read_cursor + cursor_sanity_check).
        #   2. Apply --reset-cursor / --since overrides.
        #   3. Open chat.db (open_chat_db).
        #   4. Build workspace config (load_workspaces_config).
        #   5. Resolve Apple Contacts via PyObjC (Contacts.framework).
        #   6. Stream messages with cursor predicate.
        #   7. Apply universal blocklist (format.md § F).
        #   8. Bucket by (contact_slug, YYYY-MM).
        #   9. For each bucket:
        #        a. resolve_tapbacks
        #        b. copy_attachment per § G (skip if --no-attachments)
        #        c. render_month per § E
        #        d. compute content_hash (blake3 of body)
        #        e. call_router for destinations
        #        f. write file + ledger row per destination (skip if --dry-run)
        #  10. Append to workspace _meta/log.md.
        #  11. Advance cursor atomically.
        # All forbidden behaviors at top of file MUST be enforced.
        cur = read_cursor()
        sys.stderr.write(
            f"ingest-imessage: starting from last_rowid={cur['last_rowid']} "
            f"last_message_date={cur['last_message_date']}\n"
        )

        try:
            conn = open_chat_db()
            mode = cursor_sanity_check(conn, cur)
            max_rowid = conn.execute("SELECT MAX(ROWID) FROM message").fetchone()[0] or 0
            sys.stderr.write(
                f"ingest-imessage: cursor mode={mode} max_rowid={max_rowid} "
                "(no writes — full backfill loop pending activation pass)\n"
            )
        finally:
            try:
                conn.close()  # type: ignore
            except Exception:
                pass

        return 0
    finally:
        try:
            os.close(lock_fd)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
