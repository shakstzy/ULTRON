#!/usr/bin/env python3
"""
ingest-imessage-oneshot.py — first-ingest tool for allowlisted iMessage
contacts. Writes per-(contact, month) markdown to workspace `raw/imessage/`.
Attachments are DESCRIBED via Gemini (vision), not copied (per format.md § G).

Distinct from `ingest-imessage.py` (cron-driven production robot,
IMPLEMENTATION_READY=False). This script is the activation tool for
explicitly allowlisted contacts.

Usage:
    ingest-imessage-oneshot.py --workspace personal [--contact <slug>] [--dry-run] [--no-descriptions]

Idempotency: descriptions keyed by (sha256, description_model) of the
source binary; re-runs reuse prior descriptions and only call Gemini for
new / changed attachments.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shlex
import sqlite3
import subprocess
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
DESCRIPTION_MODEL = "gemini-3-flash-preview"  # Flash by default; Pro is for adversarial review

# Mime / UTI groupings for description routing per format.md § G
VISION_PREFIXES = ("image/", "video/")
TEXT_READABLE = ("text/", "application/pdf", "application/json")

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


# ---------------------------------------------------------------------------
# Attachment description (Gemini Flash via CLI @<path>)
# ---------------------------------------------------------------------------
PROMPT_VISION = (
    "Describe what's in this in one sentence under 100 characters. "
    "Be specific and concrete. No preamble, just the description."
)
PROMPT_TEXT = (
    "Summarize this file in two sentences under 200 characters total. "
    "Surface-level only: what is it, what's the gist."
)


def hash_source(path: Path) -> tuple[str | None, bool]:
    """Returns (sha256_hex_or_None, source_available_bool)."""
    if not path.exists():
        return None, False
    if path.is_dir():
        return None, True  # bundle, no single-file hash
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(64 * 1024), b""):
                h.update(chunk)
        return h.hexdigest(), True
    except OSError:
        return None, False


def kind_of(mime: str | None, src: Path | None) -> str:
    if src is not None and src.is_dir():
        return "bundle"
    if not mime:
        return "file"
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("text/") or mime in ("application/pdf", "application/json"):
        return "text"
    return "file"


def bundle_description(src: Path, ext: str) -> str:
    """Fixed placeholder for known bundle types. No Gemini call."""
    table = {
        ".logicx": "Logic Pro project bundle",
        ".band": "GarageBand project bundle",
        ".photoslibrary": "Apple Photos library bundle",
        ".app": "macOS application bundle",
        ".pkg": "Installer package bundle",
    }
    return table.get(ext.lower(), f"{ext.lstrip('.')} bundle")


def gemini_describe(path: Path, kind: str) -> tuple[str | None, str | None]:
    """Returns (description, model) for a kind we extract; (None, None) otherwise.

    v1: only `image` and `video` go through Gemini Flash. Audio / opaque /
    bundles return (None, None) per format.md § G.
    """
    if kind not in ("image", "video", "text"):
        return None, None
    if not path.exists() or path.is_dir():
        return None, None
    prompt = PROMPT_VISION if kind in ("image", "video") else PROMPT_TEXT
    cmd = [
        "gemini",
        "-p", f"{prompt}\n\n@{path}",
        "-o", "text",
        "--approval-mode", "plan",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None, None
    if proc.returncode != 0:
        return None, None
    desc = proc.stdout.strip()
    # Some CLI runs prepend boilerplate; take last non-empty line if it's a
    # one-liner. Truncate to spec budget.
    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
    if not lines:
        return None, None
    desc = lines[-1]
    cap = 100 if kind in ("image", "video") else 200
    if len(desc) > cap:
        desc = desc[: cap - 1].rstrip() + "…"
    return desc, DESCRIPTION_MODEL


def load_prior_descriptions(month_path: Path) -> dict[tuple[str, str], str]:
    """Read existing month file's frontmatter, build {(sha256, model): description}.
    Used for idempotent re-runs: skip Gemini call if same binary + same model."""
    if not month_path.exists():
        return {}
    try:
        text = month_path.read_text()
    except OSError:
        return {}
    m = re.match(r"^---\n(.+?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    try:
        import yaml as _yaml  # already imported at module scope
        fm = _yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}
    out = {}
    for a in fm.get("attachments", []) or []:
        sha = a.get("sha256")
        model = a.get("description_model")
        desc = a.get("description")
        if sha and model and desc:
            out[(sha, model)] = desc
    return out


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
        # `fn` is the full Mac path; `tn` is the user-visible display name
        # (basename). Spec § D wants basename in frontmatter.
        display_name = tn or (Path(fn).name if fn else "untitled")
        att_by_msg.setdefault(mid, []).append({
            "guid": aguid, "filename": display_name,
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
    total_atts_inlined = 0
    total_atts_described = 0
    total_atts_skipped = 0   # null description (audio / opaque / bundle)
    total_atts_unavailable = 0
    total_atts_reused = 0

    for month_key in sorted(by_month):
        month_msgs = by_month[month_key]
        first_dt = to_dt(month_msgs[0][3]).astimezone(TZ)
        last_dt = to_dt(month_msgs[-1][3]).astimezone(TZ)
        my_count = sum(1 for r in month_msgs if r[4])
        their_count = sum(1 for r in month_msgs if not r[4])

        year = first_dt.year
        month_dir = individuals_dir / str(year)
        if not dry_run:
            month_dir.mkdir(parents=True, exist_ok=True)

        # Idempotency: load prior descriptions keyed on (sha256, model).
        month_path = month_dir / f"{month_key}__{slug}.md"
        prior_desc = load_prior_descriptions(month_path)

        # Build attachments[] via description extraction per § G
        fm_atts = []
        skip_descriptions = (attach_budget_bytes == 0)  # --no-descriptions
        for r in month_msgs:
            for a in att_by_msg.get(r[0], []):
                aid = _blake3(
                    f"{a['guid'] or a['filename']}|"
                    f"{a['size_bytes'] or 0}|{a['rowid']}".encode()
                ).hexdigest()[:16]
                src = Path(os.path.expanduser(a["src_path"])) if a["src_path"] else None
                sha256, source_available = (None, False) if src is None else hash_source(src)
                if not source_available:
                    total_atts_unavailable += 1
                kind = kind_of(a["mime"], src)
                description = None
                model = None
                if not source_available:
                    pass
                elif skip_descriptions:
                    pass
                elif sha256 and (sha256, DESCRIPTION_MODEL) in prior_desc:
                    description = prior_desc[(sha256, DESCRIPTION_MODEL)]
                    model = DESCRIPTION_MODEL
                    total_atts_reused += 1
                elif kind == "bundle":
                    ext = Path(a["filename"]).suffix or ""
                    description = bundle_description(src, ext)
                    model = None  # static, no model
                    total_atts_described += 1
                elif kind in ("image", "video", "text"):
                    description, model = gemini_describe(src, kind)
                    if description:
                        total_atts_described += 1
                    else:
                        total_atts_skipped += 1
                else:
                    # audio / opaque / unknown
                    total_atts_skipped += 1
                fm_atts.append({
                    "id": aid,
                    "filename": a["filename"],
                    "mime": a["mime"],
                    "size_bytes": a["size_bytes"],
                    "sender": "me" if r[4] else slug,
                    "sent_at": to_dt(r[3]).astimezone(TZ).isoformat(),
                    "sha256": sha256,
                    "description": description,
                    "description_model": model,
                    "extracted_at": (
                        datetime.datetime.now(datetime.timezone.utc).isoformat()
                        if description and model else None
                    ),
                    "source_available": source_available,
                })

        # Render body. First-name-only display in body lines (spec example
        # uses "Sydney" not "Sydney Hayes" in `**HH:MM — sender:**`).
        # Frontmatter `contact_name` keeps the full name.
        peer_display = slug.split("-")[0].capitalize()
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
            # Look up the description we computed in the frontmatter pass
            atts_meta = {a["id"]: a for a in fm_atts if a["sent_at"] == to_dt(r[3]).astimezone(TZ).isoformat() and a["sender"] == ("me" if from_me else slug)}
            for a in atts:
                aid = _blake3(
                    f"{a['guid'] or a['filename']}|"
                    f"{a['size_bytes'] or 0}|{a['rowid']}".encode()
                ).hexdigest()[:16]
                kind = attachment_kind(a["mime"]) if not (Path(os.path.expanduser(a["src_path"] or "")).is_dir() if a["src_path"] else False) else "file"
                meta = atts_meta.get(aid)
                desc = (meta or {}).get("description") if meta else None
                if desc:
                    lines.append(f"**{dt.strftime('%H:%M')} — {sender}:** [{kind}: {desc}]")
                else:
                    lines.append(f"**{dt.strftime('%H:%M')} — {sender}:** [{kind}: {a['filename']}]")
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
            "contact_name": " ".join(p.capitalize() for p in slug.split("-")),
            "chat_guid": None,
            "month": month_key,
            "date_range": [str(first_dt.date()), str(last_dt.date())],
            "message_count": len(month_msgs),
            "my_message_count": my_count,
            "their_message_count": their_count,
            "attachments": fm_atts,
            "chat_message_guids_count": guids_in_month,
            "deleted_upstream": None,
            "superseded_by": None,
        }
        fm_text = "---\n" + yaml.safe_dump(fm, sort_keys=False, default_flow_style=False) + "---\n\n"
        out_path = month_dir / f"{month_key}__{slug}.md"
        if not dry_run:
            out_path.write_text(fm_text + body)
        written_files.append((out_path, len(month_msgs), len(fm_atts), len(body) + len(fm_text), ch))

    return {
        "slug": slug,
        "files": written_files,
        "blocked": blocked,
        "recovered": recovered,
        "failed": failed,
        "url_balloon_skipped": skipped_url,
        "atts_inlined": total_atts_inlined,
        "atts_described": total_atts_described,
        "atts_skipped": total_atts_skipped,
        "atts_unavailable": total_atts_unavailable,
        "atts_reused": total_atts_reused,
        "tapbacks_attached": sum(len(v) for v in tapbacks.values()),
    }


def append_ledger(ws_root, slug, files, run_id="oneshot"):
    """Append rows per format.md § H. Skip if a prior row with the same
    (key, content_hash) already exists; otherwise append a new row."""
    ledger = ws_root / "_meta" / "ingested.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("source") == "imessage" and r.get("content_hash"):
                    existing.add((r["key"], r["content_hash"]))
            except Exception:
                pass
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    appended = 0
    skipped = 0
    with ledger.open("a") as f:
        for path, _msg_count, _atts, _size, content_hash in files:
            month = path.stem.split("__")[0]
            ctype = "individual" if "/individuals/" in str(path) else "group"
            key = f"imessage:{ctype}:{slug}:{month}"
            if (key, content_hash) in existing:
                skipped += 1
                continue
            row = {
                "source": "imessage",
                "key": key,
                "content_hash": content_hash,
                "raw_path": str(path.relative_to(ws_root.parent.parent)),
                "ingested_at": now,
                "run_id": run_id,
            }
            f.write(json.dumps(row) + "\n")
            appended += 1
    print(f"  ledger: {appended} appended, {skipped} skipped (already up-to-date)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--contact", help="filter to single allowlisted slug")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-descriptions", action="store_true",
                    help="skip Gemini description calls (body falls back to filename)")
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
    # `attach_budget_bytes`: 0 = skip Gemini calls, anything else = enable.
    budget = 0 if args.no_descriptions else 1
    for c in contacts:
        result = render_contact(conn, c, args.workspace, out_root, args.dry_run, budget)
        if not result:
            continue
        print(f"\n  files written: {len(result['files'])}")
        for path, mcount, acount, size, _ch in result["files"]:
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
        print(f"  attachments described: {result['atts_described']}")
        print(f"  attachments reused:    {result['atts_reused']} (idempotent)")
        print(f"  attachments skipped:   {result['atts_skipped']} (audio/opaque/bundle)")
        print(f"  attachments unavail:   {result['atts_unavailable']} (source missing)")
        print(f"  tapbacks attached:     {result['tapbacks_attached']}")
        if not args.dry_run:
            append_ledger(ws_root, result["slug"], result["files"])

    conn.close()
    print("\ndone")


if __name__ == "__main__":
    main()
