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
import hashlib
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
    """Returns {phone_e164: (slug, display_name)} from Apple Contacts stubs."""
    out: dict[str, tuple[str, str]] = {}
    if not CONTACTS_DIR.exists():
        return out
    for f in CONTACTS_DIR.glob("*.md"):
        slug = f.stem
        text = f.read_text(errors="replace")
        title_m = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
        display = title_m.group(1).strip() if title_m else slug
        for phone in PHONE_RE.findall(text):
            out[phone] = (slug, display)
    return out


# ---------------------------------------------------------------------------
# whatsmeow tables: LID map + push_name fallback for unsaved contacts
# ---------------------------------------------------------------------------
def load_lid_map() -> dict:
    """Returns {lid_digits: phone_e164} from whatsmeow_lid_map."""
    out: dict[str, str] = {}
    if not WHATSAPP_DEVICE_DB.exists():
        return out
    try:
        conn = sqlite3.connect(f"file:{WHATSAPP_DEVICE_DB}?mode=ro", uri=True)
        for lid, pn in conn.execute("SELECT lid, pn FROM whatsmeow_lid_map").fetchall():
            if lid and pn and pn.isdigit():
                out[str(lid)] = "+" + pn
        conn.close()
    except sqlite3.Error:
        pass
    return out


def load_wa_contacts() -> dict:
    """Returns {phone_e164: display_name} from whatsmeow_contacts (full_name → push_name → business_name)."""
    out: dict[str, str] = {}
    if not WHATSAPP_DEVICE_DB.exists():
        return out
    try:
        conn = sqlite3.connect(f"file:{WHATSAPP_DEVICE_DB}?mode=ro", uri=True)
        rows = conn.execute(
            "SELECT their_jid, full_name, push_name, business_name FROM whatsmeow_contacts"
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        return out
    for their_jid, full_name, push_name, business_name in rows:
        phone = jid_to_phone(their_jid or "")
        if not phone:
            continue
        name = (full_name or "").strip() or (push_name or "").strip() or (business_name or "").strip()
        if name:
            out[phone] = name
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
def resolve_phone_for_jid(jid: str, lid_map: dict) -> str | None:
    """Get +E.164 phone for any JID, consulting whatsmeow_lid_map for @lid JIDs."""
    if not jid:
        return None
    if jid.endswith("@s.whatsapp.net"):
        return jid_to_phone(jid)
    if jid.endswith("@lid"):
        bare = jid.split("@", 1)[0].split(":", 1)[0]
        return lid_map.get(bare)
    return None


def name_for_phone(phone: str, contacts: dict, wa_contacts: dict) -> tuple[str, str] | None:
    """Apple Contacts stub wins; whatsmeow display_name as fallback. Returns (slug, display) or None."""
    if phone in contacts:
        return contacts[phone]
    if phone in wa_contacts:
        return slugify(wa_contacts[phone]), wa_contacts[phone]
    return None


def resolve_chat_identity(
    jid: str, chat_name: str | None, contacts: dict, wa_contacts: dict, lid_map: dict
) -> tuple[str, str, str]:
    """Returns (kind_dir, slug, display_name) where kind_dir is 'individuals' or 'groups'."""
    kind = jid_kind(jid)
    if kind == "group":
        name = chat_name or jid
        return "groups", slugify(name), name
    phone = resolve_phone_for_jid(jid, lid_map)
    if phone:
        named = name_for_phone(phone, contacts, wa_contacts)
        if named:
            return "individuals", named[0], named[1]
        return "individuals", f"phone-{phone[1:]}", phone
    # LID with no phone mapping
    bare = jid.split("@", 1)[0]
    return "individuals", f"lid-{bare}", chat_name or bare


def resolve_sender_label(
    sender_jid: str, is_from_me: bool, contacts: dict, wa_contacts: dict, lid_map: dict
) -> str:
    if is_from_me:
        return "me"
    phone = resolve_phone_for_jid(sender_jid, lid_map)
    if phone:
        named = name_for_phone(phone, contacts, wa_contacts)
        if named:
            return named[1]
        return phone
    bare = sender_jid.split("@", 1)[0] if sender_jid else "unknown"
    return f"@{bare}"


# ---------------------------------------------------------------------------
# Body rendering
# ---------------------------------------------------------------------------
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_ts(ts_str: str) -> datetime.datetime:
    """Bridge stores 'YYYY-MM-DD HH:MM:SS-05:00' style. Always returns an aware datetime
    (defaults to UTC if the source row is naive) so all downstream comparisons stay
    aware-vs-aware — Python raises TypeError when comparing naive with aware.
    """
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
    except ValueError:
        dt = datetime.datetime.fromisoformat(ts_str.replace(" ", "T"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def render_body(
    display_name: str,
    month_str: str,
    msgs: list,
    is_group: bool,
    contacts: dict,
    wa_contacts: dict,
    lid_map: dict,
) -> tuple[str, str]:
    """Returns (body_markdown, latest_iso_ts)."""
    year, mon = month_str.split("-")
    mon_name = datetime.date(int(year), int(mon), 1).strftime("%B")
    out = [f"# {display_name} — {mon_name} {year}", ""]

    last_date = None
    latest_dt: datetime.datetime | None = None
    for m in msgs:
        ts = parse_ts(m["timestamp"])
        # Compare as aware datetime (handles DST + offset edge cases that
        # break lexicographic ISO-string comparison around the fall-back hour).
        if latest_dt is None or ts > latest_dt:
            latest_dt = ts
        d = ts.date()
        if d != last_date:
            if last_date is not None:
                out.append("")
            out.append(f"## {d.isoformat()} ({WEEKDAYS[d.weekday()]})")
            out.append("")
            last_date = d
        sender = resolve_sender_label(m["sender"] or "", bool(m["is_from_me"]), contacts, wa_contacts, lid_map)
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

        # Multi-line content: keep newlines, no indent (4-space indent would trigger code blocks)
        out.append(f"**{time_str} — {sender}:** {payload}")

    out.append("")
    latest_iso = latest_dt.isoformat() if latest_dt else msgs[-1]["timestamp"]
    return "\n".join(out), latest_iso


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
    # Quote on: any control char, the YAML reserved punctuation, leading/trailing space,
    # or values that would otherwise parse as bool/null. Multi-line strings always quote
    # because PyYAML's safe_load would parse an unquoted multi-line as a parse error.
    needs_quote = (
        s == ""
        or "\n" in s
        or "\r" in s
        or s.lower() in ("yes", "no", "true", "false", "null", "~")
        or re.search(r"[:#\[\]{}&*!|>'\"%@`,]|^\s|\s$", s) is not None
    )
    if not needs_quote:
        return s
    # Single-quoted YAML: escape internal `'` by doubling. This is the only escape
    # required (no backslash sequences interpreted in single-quoted scalars).
    if "\n" in s or "\r" in s:
        # Multi-line: emit double-quoted with explicit escapes (single-quoted YAML
        # cannot represent embedded newlines as escape sequences).
        escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        return '"' + escaped + '"'
    return "'" + s.replace("'", "''") + "'"


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


def read_existing_overrides(path: Path) -> dict:
    """Pull manual overrides we must preserve across regen: deleted_upstream, superseded_by.
    Per the script's immutable contract (mirrors imessage), these two fields are
    write-once from upstream — the user (or a separate audit job) sets them.
    Regenerating the shard MUST NOT silently revert them to null.
    """
    out: dict = {"deleted_upstream": None, "superseded_by": None}
    if not path.exists():
        return out
    try:
        head = path.read_text(errors="replace").split("---", 2)
        if len(head) < 3:
            return out
        for line in head[1].splitlines():
            stripped = line.strip()
            for k in out.keys():
                if stripped.startswith(f"{k}:"):
                    raw = stripped.split(":", 1)[1].strip()
                    raw = raw.strip("'\"")
                    if raw and raw.lower() != "null":
                        out[k] = raw
    except OSError:
        pass
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workspace", nargs="?", help="legacy positional; with --account, defaults to 'personal'")
    p.add_argument("run_id", nargs="?", help="legacy positional; with --run-id, the flag wins")
    p.add_argument("--account", help="WhatsApp account (E.164, e.g. +15126601911); used by run-stage.sh dispatch")
    p.add_argument("--run-id", dest="run_id_flag")
    p.add_argument("--limit-chats", type=int, default=0, help="for dev: only ingest first N chats")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # CLI signature normalization. run-stage.sh passes `--account <acct> --run-id <id>`;
    # manual invocation passes `<workspace> <run_id>`. Either works.
    workspace = args.workspace or ("personal" if args.account else None)
    run_id = args.run_id_flag or args.run_id
    if not workspace:
        sys.stderr.write("usage: ingest-whatsapp.py <workspace> <run_id>  OR  --account <e164> --run-id <id>\n")
        return 2
    if not run_id:
        run_id = "manual-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    if not BRIDGE_DB.exists():
        sys.stderr.write(f"bridge DB missing: {BRIDGE_DB}\n")
        return 1

    # If invoked with --account, fail loud when we can't verify the bridge owns that account.
    # Prevents accidentally ingesting a different account's data into the wrong workspace OR
    # writing a workspace's data when the bridge JID is unreadable (e.g., schema drift).
    if args.account:
        bridge_phone = my_jid_phone()
        if not bridge_phone:
            sys.stderr.write(
                f"cannot verify bridge account (whatsmeow_device unreadable); refuse to ingest as {args.account}\n"
            )
            return 1
        if bridge_phone != args.account:
            sys.stderr.write(
                f"account mismatch: bridge logged in as {bridge_phone}, ingest requested for {args.account}\n"
            )
            return 1

    # exclusive lock
    lock_fd = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.stderr.write("another ingest-whatsapp run is in progress\n")
        return 1

    contacts = load_contacts()
    wa_contacts = load_wa_contacts()
    lid_map = load_lid_map()
    my_phone = my_jid_phone()
    sys.stderr.write(
        f"loaded: apple_contacts={len(contacts)} wa_contacts={len(wa_contacts)} lid_map={len(lid_map)} my_phone={my_phone}\n"
    )

    out_root = ULTRON_ROOT / "workspaces" / workspace / "raw" / "whatsapp"
    out_root.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(f"file:{BRIDGE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    chats = {row["jid"]: dict(row) for row in conn.execute("SELECT * FROM chats").fetchall()}
    msgs_per_chat: dict[str, list] = defaultdict(list)
    for row in conn.execute("SELECT * FROM messages ORDER BY chat_jid, timestamp ASC").fetchall():
        msgs_per_chat[row["chat_jid"]].append(dict(row))

    # ─── Slug-collision pre-pass ────────────────────────────────────────────────
    # Two distinct chats can resolve to the same (kind_dir, slug). Without this,
    # the second one overwrites the first's shards. Append a stable last-4-digit
    # JID suffix to ALL members of any colliding group so each gets a unique dir.
    chat_identity: dict[str, tuple[str, str, str]] = {}
    slug_to_jids: dict[tuple[str, str], list[str]] = defaultdict(list)
    for jid in msgs_per_chat:
        if jid in SKIP_JIDS or jid_kind(jid) == "broadcast" or not msgs_per_chat[jid]:
            continue
        chat = chats.get(jid, {})
        kd, slug, display = resolve_chat_identity(jid, chat.get("name"), contacts, wa_contacts, lid_map)
        chat_identity[jid] = (kd, slug, display)
        slug_to_jids[(kd, slug)].append(jid)

    for (kd, slug), jids in slug_to_jids.items():
        if len(jids) <= 1:
            continue
        # First pass: append last-4 of digit-only JID prefix as a stable, readable
        # disambiguator. Two jids can in theory share the same last-4 (rare but
        # possible — group jids carry timestamp tails), so we second-pass-validate.
        for jid in jids:
            digits = re.sub(r"\D", "", jid.split("@", 1)[0])
            suffix = digits[-4:] if len(digits) >= 4 else (digits or "x")
            kd_existing, _, display = chat_identity[jid]
            chat_identity[jid] = (kd_existing, f"{slug}-{suffix}", display)
        # Second pass: detect any post-fix slug that's STILL not unique across this
        # collision cluster, escalate those to a sha256(jid)[:8] prefix. Guaranteed
        # unique. Stable across runs (deterministic from the JID).
        suffixed_counts: dict[str, int] = defaultdict(int)
        for jid in jids:
            suffixed_counts[chat_identity[jid][1]] += 1
        if any(c > 1 for c in suffixed_counts.values()):
            for jid in jids:
                if suffixed_counts[chat_identity[jid][1]] <= 1:
                    continue
                h = hashlib.sha256(jid.encode("utf-8")).hexdigest()[:8]
                kd_existing, _, display = chat_identity[jid]
                chat_identity[jid] = (kd_existing, f"{slug}-{h}", display)
            sys.stderr.write(
                f"slug-collision: '{slug}' last-4 still ambiguous; escalated to sha256 prefix\n"
            )
        # Final assertion: every jid in this cluster now has a unique slug.
        final_slugs = {chat_identity[jid][1] for jid in jids}
        assert len(final_slugs) == len(jids), f"slug collision unresolved for '{slug}'"
        sys.stderr.write(f"slug-collision resolved on '{slug}' across {len(jids)} chats\n")

    written = 0
    skipped = 0
    chats_processed = 0

    for jid, msgs in msgs_per_chat.items():
        if jid not in chat_identity:
            continue

        kind_dir, slug, display = chat_identity[jid]
        is_group = kind_dir == "groups"

        # bucket by YYYY-MM using parsed datetime (not lexicographic substring),
        # so DST / timezone-offset edge cases route to the correct month shard.
        # Also pre-sort by parsed datetime — bridge ORDER BY is lexicographic,
        # which can mis-order messages around DST fallback when offsets differ.
        by_month: dict[str, list] = defaultdict(list)
        for m in msgs:
            try:
                ts = parse_ts(m["timestamp"])
            except (ValueError, TypeError):
                continue
            month_key = ts.strftime("%Y-%m")
            by_month[month_key].append((ts, m))
        # Sort each month's messages by parsed datetime, then drop the timestamp.
        for k in list(by_month.keys()):
            by_month[k].sort(key=lambda pair: pair[0])
            by_month[k] = [m for _, m in by_month[k]]

        for month, month_msgs in by_month.items():
            year = month[:4]
            shard_dir = out_root / kind_dir / slug / year
            shard_file = shard_dir / f"{month}__{slug}.md"

            body, latest_ts = render_body(display, month, month_msgs, is_group, contacts, wa_contacts, lid_map)
            content_hash = "blake3:" + blake3(body.encode("utf-8")).hexdigest()

            if shard_file.exists() and read_existing_hash(shard_file) == content_hash:
                skipped += 1
                continue

            # Preserve manual write-once overrides set on prior runs (per format contract).
            overrides = read_existing_overrides(shard_file)

            # date_range from parsed datetimes, not lexicographic substrings — keeps
            # the range consistent with what the body actually rendered.
            parsed_dates = []
            for m in month_msgs:
                try:
                    parsed_dates.append(parse_ts(m["timestamp"]).date().isoformat())
                except (ValueError, TypeError):
                    pass
            if parsed_dates:
                date_range = [min(parsed_dates), max(parsed_dates)]
            else:
                date_range = [month_msgs[0]["timestamp"][:10], month_msgs[-1]["timestamp"][:10]]

            fm = {
                "source": "whatsapp",
                "workspace": workspace,
                "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "ingest_version": INGEST_VERSION,
                "content_hash": content_hash,
                "provider_modified_at": latest_ts,
                "contact_slug": slug,
                "contact_type": "group" if is_group else "individual",
                "month": month,
                "date_range": date_range,
                "message_count": len(month_msgs),
                "my_message_count": sum(1 for m in month_msgs if m["is_from_me"]),
                "their_message_count": sum(1 for m in month_msgs if not m["is_from_me"]),
                "attachments": [],
                "whatsapp_chat_jid": jid,
                "whatsapp_chat_kind": "group" if is_group else "dm",
                "deleted_upstream": overrides.get("deleted_upstream"),
                "superseded_by": overrides.get("superseded_by"),
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
