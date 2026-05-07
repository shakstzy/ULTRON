#!/usr/bin/env python3
"""
ingest-whatsapp.py <workspace> <run_id>

Reads the lharries/whatsapp-mcp Go bridge SQLite (~/.local/share/whatsapp-mcp/whatsapp-bridge/store/messages.db)
and writes per-(chat, month) markdown shards to:
  workspaces/<ws>/raw/whatsapp/individuals/<slug>/<year>/<year-month>__<slug>.md
  workspaces/<ws>/raw/whatsapp/groups/<slug>/<year>/<year-month>__<slug>.md

Idempotent: months whose rendered body matches the existing content_hash are skipped.

Forbidden behaviors (mirrors ingest-imessage locks):
1. Read-only DB access (?mode=ro).
2. Never delete a raw file based on bridge-DB deletion (mark deleted_upstream instead).
3. Never run LLM/vision calls during ingest (deterministic plumbing).
4. Frontmatter is write-once except deleted_upstream / superseded_by.
"""
from __future__ import annotations

import argparse
import datetime
import fcntl
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

try:
    from blake3 import blake3
except ImportError:
    sys.stderr.write("missing dep: pip install blake3\n")
    sys.exit(2)

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
BRIDGE_DB = Path.home() / ".local/share/whatsapp-mcp/whatsapp-bridge/store/messages.db"
WHATSAPP_DEVICE_DB = Path.home() / ".local/share/whatsapp-mcp/whatsapp-bridge/store/whatsapp.db"
CONTACTS_DIR = ULTRON_ROOT / "_global" / "entities" / "people"
LOCK_PATH = "/tmp/com.adithya.ultron.ingest-whatsapp.lock"
INGEST_VERSION = 1

# Skip these JIDs entirely — they're WhatsApp internals, not real conversations.
SKIP_JIDS = {"status@broadcast"}

PHONE_RE = re.compile(r"\+\d{7,15}")


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    """kebab-case lowercase, alphanumeric + hyphen only, no leading/trailing/double hyphen."""
    s = re.sub(r"[^\w\s-]", "", (text or "").lower(), flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


# ---------------------------------------------------------------------------
# Contacts: build phone -> (slug, display_name) map by scanning _global/entities/people/
# ---------------------------------------------------------------------------
def load_contacts() -> dict:
    """Returns {phone_e164: (slug, display_name)}."""
    out: dict[str, tuple[str, str]] = {}
    if not CONTACTS_DIR.exists():
        return out
    for f in CONTACTS_DIR.glob("*.md"):
        slug = f.stem
        text = f.read_text(errors="replace")
        # display name = `title:` field if present, else slug
        title_m = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
        display = title_m.group(1).strip() if title_m else slug
        # collect all E.164 phone numbers in the file
        for phone in PHONE_RE.findall(text):
            # last-write wins (rare collisions don't matter much)
            out[phone] = (slug, display)
    return out


# ---------------------------------------------------------------------------
# JID parsing
# ---------------------------------------------------------------------------
def jid_kind(jid: str) -> str:
    """'group' | 'dm' | 'lid' | 'broadcast' | 'other'"""
    if jid.endswith("@g.us"):
        return "group"
    if jid.endswith("@s.whatsapp.net"):
        return "dm"
    if jid.endswith("@lid"):
        return "lid"
    if jid.endswith("@broadcast") or jid == "status@broadcast":
        return "broadcast"
    return "other"


def jid_to_phone(jid: str) -> str | None:
    """Extract +E.164 from `15126601911@s.whatsapp.net` or `15126601911:51@s.whatsapp.net`."""
    if "@s.whatsapp.net" not in jid:
        return None
    digits = jid.split("@", 1)[0].split(":", 1)[0]
    if digits.isdigit():
        return "+" + digits
    return None


def my_jid_phone() -> str | None:
    if not WHATSAPP_DEVICE_DB.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{WHATSAPP_DEVICE_DB}?mode=ro", uri=True)
        row = conn.execute("SELECT jid FROM whatsmeow_device LIMIT 1").fetchone()
        conn.close()
        if row:
            return jid_to_phone(row[0])
    except sqlite3.Error:
        pass
    return None


# ---------------------------------------------------------------------------
# Display + slug resolution per chat
# ---------------------------------------------------------------------------
def resolve_chat_identity(jid: str, chat_name: str | None, contacts: dict) -> tuple[str, str, str]:
    """
    Returns (kind_dir, slug, display_name) where kind_dir is 'individuals' or 'groups'.
    """
    kind = jid_kind(jid)
    if kind == "group":
        name = chat_name or jid
        return "groups", slugify(name), name
    # dm or lid → individuals folder
    phone = jid_to_phone(jid)
    if phone and phone in contacts:
        slug, display = contacts[phone]
        return "individuals", slug, display
    if phone:
        return "individuals", f"phone-{phone[1:]}", phone
    # LID-only contact (no phone resolved)
    bare = jid.split("@", 1)[0]
    return "individuals", f"lid-{bare}", chat_name or bare


def resolve_sender_label(sender_jid: str, is_from_me: bool, my_phone: str | None, contacts: dict) -> str:
    if is_from_me:
        return "me"
    phone = jid_to_phone(sender_jid)
    if phone:
        if phone in contacts:
            return contacts[phone][1]
        return phone
    bare = sender_jid.split("@", 1)[0]
    return f"@{bare}"


# ---------------------------------------------------------------------------
# Body rendering
# ---------------------------------------------------------------------------
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_ts(ts_str: str) -> datetime.datetime:
    """Bridge stores 'YYYY-MM-DD HH:MM:SS-05:00' style. Try ISO first, fall back to a manual parse."""
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except ValueError:
        # SQLite sometimes prints with space instead of T
        return datetime.datetime.fromisoformat(ts_str.replace(" ", "T"))


def render_body(display_name: str, month_str: str, msgs: list, is_group: bool, my_phone: str | None, contacts: dict) -> tuple[str, str]:
    """Returns (body_markdown, latest_iso_ts)."""
    year, mon = month_str.split("-")
    mon_name = datetime.date(int(year), int(mon), 1).strftime("%B")
    out = [f"# {display_name} — {mon_name} {year}", ""]

    last_date = None
    latest_ts = None
    for m in msgs:
        ts = parse_ts(m["timestamp"])
        latest_ts = ts.isoformat() if (latest_ts is None or ts.isoformat() > latest_ts) else latest_ts
        d = ts.date()
        if d != last_date:
            out.append(f"## {d.isoformat()} ({WEEKDAYS[d.weekday()]})")
            out.append("")
            last_date = d
        sender = resolve_sender_label(m["sender"] or "", bool(m["is_from_me"]), my_phone, contacts)
        time_str = ts.strftime("%H:%M")

        content = (m["content"] or "").rstrip()
        media = m["media_type"] or ""
        filename = m["filename"] or ""
        if media and not content:
            payload = f"[{media}: {filename}]" if filename else f"[{media}]"
        elif media and content:
            tag = f"[{media}: {filename}]" if filename else f"[{media}]"
            payload = f"{tag} {content}"
        else:
            payload = content if content else "[empty]"

        # Indent multi-line content by 2 spaces under the bold header
        if "\n" in payload:
            lines = payload.split("\n")
            payload = lines[0] + "\n" + "\n".join("    " + ln for ln in lines[1:])

        out.append(f"**{time_str} — {sender}:** {payload}")

    out.append("")
    return "\n".join(out), latest_ts or msgs[-1]["timestamp"]


# ---------------------------------------------------------------------------
# Frontmatter writer (manual to avoid PyYAML dep)
# ---------------------------------------------------------------------------
def fm_value(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, list):
        if not v:
            return "[]"
        # all simple strings → flow-style array
        return "[" + ", ".join(_yaml_str(x) for x in v) + "]"
    return _yaml_str(v)


def _yaml_str(s) -> str:
    s = str(s)
    if re.search(r"[:#\[\]{}&*!|>'\"%@`,]|^\s|\s$", s) or s == "" or s.lower() in ("yes", "no", "true", "false", "null"):
        return "'" + s.replace("'", "''") + "'"
    return s


def render_frontmatter(d: dict) -> str:
    lines = ["---"]
    for k, v in d.items():
        lines.append(f"{k}: {fm_value(v)}")
    lines.append("---")
    return "\n".join(lines)


def read_existing_hash(path: Path) -> str | None:
    try:
        head = path.read_text(errors="replace").split("---", 2)
        if len(head) < 3:
            return None
        for line in head[1].splitlines():
            line = line.strip()
            if line.startswith("content_hash:"):
                return line.split(":", 1)[1].strip().strip("'\"")
    except OSError:
        return None
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workspace")
    p.add_argument("run_id")
    p.add_argument("--limit-chats", type=int, default=0, help="for dev: only ingest first N chats")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not BRIDGE_DB.exists():
        sys.stderr.write(f"bridge DB missing: {BRIDGE_DB}\n")
        return 1

    # exclusive lock
    lock_fd = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.stderr.write("another ingest-whatsapp run is in progress\n")
        return 1

    contacts = load_contacts()
    my_phone = my_jid_phone()
    sys.stderr.write(f"contacts loaded: {len(contacts)} phone mappings; my_phone={my_phone}\n")

    out_root = ULTRON_ROOT / "workspaces" / args.workspace / "raw" / "whatsapp"
    out_root.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(f"file:{BRIDGE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    chats = {row["jid"]: dict(row) for row in conn.execute("SELECT * FROM chats").fetchall()}
    msgs_per_chat: dict[str, list] = defaultdict(list)
    for row in conn.execute("SELECT * FROM messages ORDER BY chat_jid, timestamp ASC").fetchall():
        msgs_per_chat[row["chat_jid"]].append(dict(row))

    written = 0
    skipped = 0
    chats_processed = 0

    for jid, msgs in msgs_per_chat.items():
        if jid in SKIP_JIDS or jid_kind(jid) == "broadcast":
            continue
        if not msgs:
            continue

        chat = chats.get(jid, {})
        kind_dir, slug, display = resolve_chat_identity(jid, chat.get("name"), contacts)
        is_group = kind_dir == "groups"

        # bucket by YYYY-MM
        by_month: dict[str, list] = defaultdict(list)
        for m in msgs:
            month_key = m["timestamp"][:7]
            by_month[month_key].append(m)

        for month, month_msgs in by_month.items():
            year = month[:4]
            shard_dir = out_root / kind_dir / slug / year
            shard_file = shard_dir / f"{month}__{slug}.md"

            body, latest_ts = render_body(display, month, month_msgs, is_group, my_phone, contacts)
            content_hash = "blake3:" + blake3(body.encode("utf-8")).hexdigest()

            if shard_file.exists() and read_existing_hash(shard_file) == content_hash:
                skipped += 1
                continue

            fm = {
                "source": "whatsapp",
                "workspace": args.workspace,
                "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "ingest_version": INGEST_VERSION,
                "content_hash": content_hash,
                "provider_modified_at": latest_ts,
                "contact_slug": slug,
                "contact_type": "group" if is_group else "individual",
                "month": month,
                "date_range": [month_msgs[0]["timestamp"][:10], month_msgs[-1]["timestamp"][:10]],
                "message_count": len(month_msgs),
                "my_message_count": sum(1 for m in month_msgs if m["is_from_me"]),
                "their_message_count": sum(1 for m in month_msgs if not m["is_from_me"]),
                "attachments": [],
                "whatsapp_chat_jid": jid,
                "whatsapp_chat_kind": "group" if is_group else "dm",
                "deleted_upstream": None,
                "superseded_by": None,
            }
            text = render_frontmatter(fm) + "\n\n" + body

            if args.dry_run:
                sys.stdout.write(f"[dry-run] would write {shard_file} ({len(month_msgs)} msgs)\n")
            else:
                shard_dir.mkdir(parents=True, exist_ok=True)
                shard_file.write_text(text)
            written += 1

        chats_processed += 1
        if args.limit_chats and chats_processed >= args.limit_chats:
            break

    sys.stderr.write(f"ingest-whatsapp: wrote={written} skipped={skipped} chats={chats_processed}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
