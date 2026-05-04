#!/usr/bin/env python3
"""
ingest-imessage-oneshot.py — first-ingest tool for allowlisted iMessage
contacts. Uses the proven probe engine (3-round bug-hunt loop validated)
to write per-(contact, month) markdown into a workspace's raw/imessage/.

Distinct from `ingest-imessage.py` (the cron-driven production robot,
still IMPLEMENTATION_READY=False). This script is for activation /
first-ingest of explicitly allowlisted contacts.

Usage:
    ingest-imessage-oneshot.py --workspace personal [--contact <slug>] [--dry-run]

Reads `workspaces/<ws>/config/sources.yaml` `sources.imessage.contacts`.
For each allowlisted contact (or only the one specified by --contact),
queries chat.db, applies the universal blocklist, recovers attributedBody
text, resolves tapbacks, copies attachments per format.md § G (100 MB /
month budget), and writes month files + _profiles/<slug>.md.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

from blake3 import blake3 as _blake3
from zoneinfo import ZoneInfo

import yaml  # type: ignore

try:
    import objc  # type: ignore
    from Foundation import NSData, NSUnarchiver  # type: ignore
    _HAS_NS = True
except Exception:
    _HAS_NS = False

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
DB = Path.home() / "Library" / "Messages" / "chat.db"
ATTACHMENTS_ROOT = Path.home() / "Library" / "Messages" / "Attachments"
TZ = ZoneInfo("America/Chicago")
MAC_EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_MAC_LOWER = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_MAC_UPPER = datetime.datetime(2200, 1, 1, tzinfo=datetime.timezone.utc)
ATTACHMENT_BUDGET_BYTES = 100 * 1024 * 1024

TOLL_FREE = ("+1800", "+1888", "+1877", "+1866", "+1855", "+1844", "+1833")
NOREPLY_LOCAL = ("verify", "noreply", "no-reply", "donotreply")
TAPBACK_NAMES = {2000: "love", 2001: "like", 2002: "dislike",
                 2003: "laugh", 2004: "emphasize", 2005: "question"}
TARGET_GUID_PREFIX_RE = re.compile(r"^(?:p:0/|bp:|p:\d+/)")
URL_BALLOON_SKIP = "com.apple.messages.URLBalloonProvider"


def to_dt(val):
    if val is None:
        return None
    try:
        ns_dt = MAC_EPOCH + datetime.timedelta(seconds=float(val) / 1e9)
        if _MAC_LOWER <= ns_dt < _MAC_UPPER:
            return ns_dt
    except (OverflowError, ValueError):
        pass
    try:
        return MAC_EPOCH + datetime.timedelta(seconds=float(val))
    except (OverflowError, ValueError):
        return None


def is_blocked(handle):
    if not handle:
        return False
    if any(handle.startswith(p) for p in TOLL_FREE):
        return True
    if "@" in handle and any(handle.split("@")[0].lower().startswith(p) for p in NOREPLY_LOCAL):
        return True
    if re.fullmatch(r"\d{5}", handle):
        return True
    return False


def attachment_kind(mime):
    if not mime:
        return "file"
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    return "file"


def human_size(n):
    if n is None:
        return "?"
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{int(n)}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def parse_attributed_body(blob):
    if blob is None or not _HAS_NS:
        return None
    with objc.autorelease_pool():
        try:
            data = NSData.dataWithBytes_length_(bytes(blob), len(blob))
            unarch = NSUnarchiver.alloc().initForReadingWithData_(data)
            if unarch is None:
                return None
            try:
                obj = unarch.decodeObject()
            finally:
                try:
                    unarch.finishDecoding()
                except Exception:
                    pass
        except Exception:
            return None
        if obj is None:
            return None
        if hasattr(obj, "string"):
            try:
                s = str(obj.string())
                return s if s else None
            except Exception:
                return None
        try:
            cls = obj.className() if hasattr(obj, "className") else ""
        except Exception:
            cls = ""
        if cls in ("NSString", "NSMutableString", "__NSCFString",
                   "NSCFString", "__NSCFConstantString"):
            try:
                return str(obj)
            except Exception:
                return None
        return None


def strip_target_guid(g):
    if not g:
        return None
    return TARGET_GUID_PREFIX_RE.sub("", g)


@contextmanager
def _nullctx():
    yield


def find_chats_for_handles(conn, handles):
    """Return chat ROWIDs whose participants exactly match the handle set."""
    placeholders = ",".join(["?"] * len(handles))
    rows = conn.execute(f"""
        SELECT DISTINCT c.ROWID
        FROM chat c
        JOIN chat_handle_join chj ON chj.chat_id = c.ROWID
        JOIN handle h ON h.ROWID = chj.handle_id
        WHERE c.style != 43
          AND c.service_name = 'iMessage'
          AND h.id IN ({placeholders})
    """, handles).fetchall()
    return [r[0] for r in rows]


def render_contact(conn, contact_cfg, ws, out_root, dry_run, attach_budget_bytes):
    slug = contact_cfg["slug"]
    handles = contact_cfg["handles"]
    full_archive = contact_cfg.get("full_archive", False)
    print(f"\n=== {slug} (handles={handles}, full_archive={full_archive}) ===")

    chat_ids = find_chats_for_handles(conn, handles)
    if not chat_ids:
        print(f"  no iMessage chat found for handles {handles}")
        return None

    ph = ",".join(["?"] * len(chat_ids))
    rows = list(conn.execute(f"""
        SELECT m.ROWID, m.guid, m.text, m.date, m.is_from_me,
               m.associated_message_type, m.associated_message_guid,
               m.balloon_bundle_id, m.attributedBody, m.date_edited,
               h.id AS handle_id
        FROM message m
        JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE cmj.chat_id IN ({ph})
        ORDER BY m.date ASC
    """, chat_ids))

    att_rows = list(conn.execute(f"""
        SELECT maj.message_id, a.guid, a.filename, a.transfer_name,
               a.total_bytes, a.uti, a.mime_type, a.ROWID
        FROM message_attachment_join maj
        JOIN attachment a ON maj.attachment_id = a.ROWID
        JOIN chat_message_join cmj ON cmj.message_id = maj.message_id
        WHERE cmj.chat_id IN ({ph})
    """, chat_ids))
    att_by_msg = {}
    for mid, aguid, fn, tn, sz, uti, mime, arow in att_rows:
        att_by_msg.setdefault(mid, []).append({
            "guid": aguid, "filename": fn or tn or "untitled",
            "transfer_name": tn, "size_bytes": sz, "uti": uti, "mime": mime,
            "rowid": arow, "src_path": fn,
        })

    # Tapback resolution
    raw_tap = {}
    msgs = []
    for r in rows:
        amt = r[5]
        atg = strip_target_guid(r[6])
        if amt and 2000 <= amt <= 2005:
            raw_tap.setdefault(atg, []).append({
                "type": TAPBACK_NAMES[amt],
                "sender": "me" if r[4] else (r[10] or "unknown"),
                "date": r[3], "removed": False,
            })
        elif amt and 3000 <= amt <= 3005:
            raw_tap.setdefault(atg, []).append({
                "type": TAPBACK_NAMES[amt - 1000],
                "sender": "me" if r[4] else (r[10] or "unknown"),
                "date": r[3], "removed": True,
            })
        else:
            msgs.append(r)

    tapbacks = {}
    for target, events in raw_tap.items():
        events.sort(key=lambda e: e["date"] or 0)
        latest = {}
        for e in events:
            latest[(e["sender"], e["type"])] = e
        surviving = [(e["type"], e["sender"], e["date"])
                     for e in latest.values() if not e["removed"]]
        if surviving:
            tapbacks[target] = surviving

    blocked = sum(1 for r in msgs if r[10] and is_blocked(r[10]))
    msgs = [r for r in msgs if not (r[10] and is_blocked(r[10]))]

    recovered = 0
    failed = 0
    skipped_url = 0
    fixed = []
    with (objc.autorelease_pool() if _HAS_NS else _nullctx()):
        for r in msgs:
            text, abody, bbi = r[2], r[8], r[7]
            if text is None and abody is not None:
                rec = parse_attributed_body(abody)
                if rec:
                    recovered += 1
                    r = list(r); r[2] = rec; r = tuple(r)
                else:
                    failed += 1
            if r[2] is None and r[8] is None and r[7] == URL_BALLOON_SKIP:
                skipped_url += 1
                continue
            fixed.append(r)
    msgs = fixed

    if not msgs:
        print(f"  no renderable messages after filtering")
        return None

    # Bucket by (year, month)
    by_month = {}
    for r in msgs:
        dt = to_dt(r[3])
        if dt is None:
            continue
        key = dt.astimezone(TZ).strftime("%Y-%m")
        by_month.setdefault(key, []).append(r)

    individuals_dir = out_root / "individuals" / slug
    profiles_dir = out_root / "_profiles"
    if not dry_run:
        profiles_dir.mkdir(parents=True, exist_ok=True)

    # Profile stub
    primary_handle = handles[0]
    first_seen_dt = to_dt(msgs[0][3]).astimezone(TZ).date()
    profile = {
        "slug": slug,
        "contact_type": "individual",
        "contact_handles": handles,
        "contact_name": " ".join(p.capitalize() for p in slug.split("-")),
        "slug_derivation": "contacts_full_name",
        "chat_guid": None,
        "first_seen": str(first_seen_dt),
        "aliases": [],
    }
    if not dry_run:
        prof_path = profiles_dir / f"{slug}.md"
        prof_text = "---\n" + yaml.safe_dump(profile, sort_keys=False) + "---\n"
        prof_path.write_text(prof_text)

    # Render months
    written_files = []
    bucket_attach_budget = {}
    for month_key in sorted(by_month):
        bucket_attach_budget[month_key] = attach_budget_bytes
    total_atts_inlined = 0
    total_atts_copied = 0
    total_atts_pruned = 0

    for month_key in sorted(by_month):
        month_msgs = by_month[month_key]
        first_dt = to_dt(month_msgs[0][3]).astimezone(TZ)
        last_dt = to_dt(month_msgs[-1][3]).astimezone(TZ)
        my_count = sum(1 for r in month_msgs if r[4])
        their_count = sum(1 for r in month_msgs if not r[4])

        year = first_dt.year
        month_dir = individuals_dir / str(year)
        att_dir = month_dir / "_attachments"
        if not dry_run:
            month_dir.mkdir(parents=True, exist_ok=True)

        # Render attachments + copy per § G
        running = 0
        attachment_pruned = False
        fm_atts = []
        for r in month_msgs:
            for a in att_by_msg.get(r[0], []):
                aid = _blake3(
                    f"{a['guid'] or a['filename']}|"
                    f"{a['size_bytes'] or 0}|{a['rowid']}".encode()
                ).hexdigest()[:16]
                size = a["size_bytes"] or 0
                ext = (Path(a["filename"]).suffix or "").lower() or ".bin"
                copied = False
                rel_path = None
                src_missing = False
                sha256 = None
                if a["src_path"]:
                    src = Path(os.path.expanduser(a["src_path"]))
                else:
                    src = None
                if src is None or not src.exists():
                    src_missing = True
                # Bundles (.logicx, .photoslibrary, .app, ...) come through
                # as directories. Compute on-disk size, copy via copytree.
                is_bundle = src is not None and src.is_dir()
                if is_bundle:
                    try:
                        actual_size = sum(
                            p.stat().st_size for p in src.rglob("*") if p.is_file()
                        )
                    except OSError:
                        actual_size = size or 0
                else:
                    actual_size = size or 0
                if running + actual_size > attach_budget_bytes:
                    attachment_pruned = True
                    total_atts_pruned += 1
                elif src_missing:
                    pass
                else:
                    rel_path = f"_attachments/{aid}{ext}"
                    if not dry_run:
                        att_dir.mkdir(parents=True, exist_ok=True)
                        dest = att_dir / f"{aid}{ext}"
                        if dest.exists():
                            pass  # idempotent re-run; skip copy
                        elif is_bundle:
                            shutil.copytree(src, dest)
                        else:
                            shutil.copy2(src, dest)
                        # sha256: hash file contents directly, or for
                        # bundles hash a sorted manifest of (relpath, size, sha256)
                        if is_bundle:
                            h = hashlib.sha256()
                            for p in sorted(dest.rglob("*")):
                                if p.is_file():
                                    h.update(str(p.relative_to(dest)).encode())
                                    h.update(b":")
                                    sub = hashlib.sha256()
                                    with open(p, "rb") as f:
                                        for chunk in iter(lambda: f.read(64 * 1024), b""):
                                            sub.update(chunk)
                                    h.update(sub.digest())
                                    h.update(b"\n")
                            sha256 = h.hexdigest()
                        else:
                            h = hashlib.sha256()
                            with open(dest, "rb") as f:
                                for chunk in iter(lambda: f.read(64 * 1024), b""):
                                    h.update(chunk)
                            sha256 = h.hexdigest()
                    copied = True
                    running += actual_size
                    total_atts_copied += 1
                fm_atts.append({
                    "id": aid, "filename": a["filename"], "mime": a["mime"],
                    "size_bytes": a["size_bytes"],
                    "sender": "me" if r[4] else slug,
                    "sent_at": to_dt(r[3]).astimezone(TZ).isoformat(),
                    "sha256": sha256,
                    "copied_to_raw": copied,
                    "attachment_path": rel_path,
                    "source_missing": src_missing,
                })

        # Render body
        peer_display = " ".join(p.capitalize() for p in slug.split("-"))
        lines = [f"# {peer_display} — {first_dt.strftime('%B %Y')}", ""]
        last_day = None
        for r in month_msgs:
            (rowid, guid, text, date, from_me, _amt, _atg, bbi,
             _abody, dedit, _hid) = r
            dt = to_dt(date).astimezone(TZ)
            day = dt.strftime("%Y-%m-%d (%A)")
            if day != last_day:
                if last_day is not None:
                    lines.append("")
                lines.append(f"## {day}")
                lines.append("")
                last_day = day
            sender = "me" if from_me else peer_display
            edited = " (edited)" if dedit and dedit > 0 else ""

            atts = att_by_msg.get(rowid, [])
            for a in atts:
                kind = attachment_kind(a["mime"])
                lines.append(
                    f"**{dt.strftime('%H:%M')} — {sender}:** "
                    f"[{kind}: {a['filename']}, {human_size(a['size_bytes'])}]"
                )
                total_atts_inlined += 1
            body_text = (text or "").strip().replace("￼", "").strip()
            if body_text:
                lines.append(f"**{dt.strftime('%H:%M')} — {sender}{edited}:** {body_text}")
            elif bbi and not atts:
                lines.append(f"**{dt.strftime('%H:%M')} — {sender}:** [app message: {bbi}]")
            stripped = strip_target_guid(guid)
            for tname, tsender, tdate in tapbacks.get(stripped, []):
                tdt = to_dt(tdate)
                if tdt is None:
                    continue
                tdt = tdt.astimezone(TZ)
                snippet = body_text.replace('"', '\\"')[:60]
                tsender_render = "me" if tsender == "me" else (
                    peer_display if tsender == handles[0] else tsender
                )
                lines.append(
                    f'**{tdt.strftime("%H:%M")} — {tsender_render}:** '
                    f'[reaction: {tname} to "{snippet}"]'
                )

        body = "\n".join(lines).rstrip() + "\n"
        ch = "blake3:" + _blake3(body.encode()).hexdigest()
        guids_in_month = len({r[1] for r in month_msgs})
        chat_msgid_min = min(r[0] for r in month_msgs)
        chat_msgid_max = max(r[0] for r in month_msgs)

        fm = {
            "source": "imessage",
            "workspace": ws,
            "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ingest_version": 1,
            "content_hash": ch,
            "provider_modified_at": last_dt.isoformat(),
            "contact_slug": slug,
            "contact_type": "individual",
            "contact_handles": handles,
            "contact_name": peer_display,
            "chat_guid": None,
            "month": month_key,
            "date_range": [str(first_dt.date()), str(last_dt.date())],
            "message_count": len(month_msgs),
            "my_message_count": my_count,
            "their_message_count": their_count,
            "attachments": fm_atts,
            "attachment_pruned": attachment_pruned,
            "chat_message_guids_count": guids_in_month,
            "deleted_upstream": None,
            "superseded_by": None,
        }
        fm_text = "---\n" + yaml.safe_dump(fm, sort_keys=False, default_flow_style=False) + "---\n\n"
        out_path = month_dir / f"{month_key}__{slug}.md"
        if not dry_run:
            out_path.write_text(fm_text + body)
        written_files.append((out_path, len(month_msgs), len(fm_atts), len(body) + len(fm_text)))

    return {
        "slug": slug,
        "files": written_files,
        "blocked": blocked,
        "recovered": recovered,
        "failed": failed,
        "url_balloon_skipped": skipped_url,
        "atts_inlined": total_atts_inlined,
        "atts_copied": total_atts_copied,
        "atts_pruned": total_atts_pruned,
        "tapbacks_attached": sum(len(v) for v in tapbacks.values()),
    }


def append_ledger(ws_root, slug, files):
    ledger = ws_root / "_meta" / "ingested.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ledger.open("a") as f:
        for path, msg_count, _atts, _size in files:
            month = path.stem.split("__")[0]
            row = {
                "source": "imessage",
                "key": f"imessage:individual:{slug}:{month}",
                "content_hash": None,  # filled by re-read; oneshot uses fm.content_hash
                "raw_path": str(path.relative_to(ws_root.parent.parent)),
                "ingested_at": now,
                "run_id": "oneshot",
            }
            f.write(json.dumps(row) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--contact", help="filter to single allowlisted slug")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-attachments", action="store_true",
                    help="skip attachment copy (still inline references)")
    args = ap.parse_args()

    ws_root = ULTRON_ROOT / "workspaces" / args.workspace
    cfg_path = ws_root / "config" / "sources.yaml"
    if not cfg_path.exists():
        sys.exit(f"sources.yaml not found at {cfg_path}")
    cfg = yaml.safe_load(cfg_path.read_text())
    imsg = (cfg.get("sources") or {}).get("imessage") or {}
    contacts = imsg.get("contacts") or []
    if not contacts:
        sys.exit(f"no imessage contacts allowlisted in {cfg_path}")

    if args.contact:
        contacts = [c for c in contacts if c.get("slug") == args.contact]
        if not contacts:
            sys.exit(f"--contact {args.contact} not in allowlist")

    out_root = ws_root / "raw" / "imessage"
    print(f"workspace: {args.workspace}")
    print(f"output:    {out_root}")
    print(f"dry-run:   {args.dry_run}")

    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    budget = 0 if args.no_attachments else ATTACHMENT_BUDGET_BYTES
    for c in contacts:
        result = render_contact(conn, c, args.workspace, out_root, args.dry_run, budget)
        if not result:
            continue
        print(f"\n  files written: {len(result['files'])}")
        for path, mcount, acount, size in result["files"]:
            try:
                rel = path.relative_to(ULTRON_ROOT)
            except ValueError:
                rel = path
            print(f"    {rel}: {mcount} msgs, {acount} atts, {size:,} bytes")
        print(f"  blocklisted:           {result['blocked']}")
        print(f"  attrBody recovered:    {result['recovered']}")
        print(f"  attrBody failed:       {result['failed']}")
        print(f"  url-balloon skipped:   {result['url_balloon_skipped']}")
        print(f"  attachments inlined:   {result['atts_inlined']}")
        print(f"  attachments copied:    {result['atts_copied']}")
        print(f"  attachments pruned:    {result['atts_pruned']}")
        print(f"  tapbacks attached:     {result['tapbacks_attached']}")
        if not args.dry_run:
            append_ledger(ws_root, result["slug"], result["files"])

    conn.close()
    print("\ndone")


if __name__ == "__main__":
    main()
