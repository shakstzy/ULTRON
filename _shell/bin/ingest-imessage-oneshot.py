#!/usr/bin/env python3
"""
ingest-imessage-oneshot.py — first-ingest tool for allowlisted iMessage
contacts AND group chats. Writes per-(target, month) markdown to workspace
`raw/imessage/`. Attachments are DESCRIBED via Gemini (vision), not copied.

Usage:
    ingest-imessage-oneshot.py --workspace personal
                              [--contact <slug>] [--group <slug>]
                              [--dry-run] [--no-descriptions]
                              [--workers 32]

Idempotency: descriptions keyed by (sha256, description_model). Re-runs
reuse existing descriptions; only new/changed binaries hit Gemini.

Parallelism: descriptions are batched in one parallel pre-pass per target
via ThreadPoolExecutor. Each worker shells to `gemini` CLI. Default 32.
On rate-limit, all workers pause via a shared cooldown event before
exponential-backoff retry. SHA-256 is computed ONCE during gather and
cached on attachment rows (Codex/Gemini round 4 finding).

Group classification is by handle count (>1 = group), not chat.style.
1:1 lookup uses HAVING COUNT(DISTINCT handle_id) = 1.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import random
import re
import sqlite3
import subprocess
import sys
import threading
import time
import unicodedata
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
DESCRIPTION_MODEL = "gemini-3-flash-preview"
DEFAULT_WORKERS = 32

TOLL_FREE_PREFIXES = ("+1800", "+1888", "+1877", "+1866", "+1855", "+1844", "+1833")
NOREPLY_LOCAL = ("verify", "noreply", "no-reply", "donotreply", "alerts",
                 "notification", "notifications", "info", "support",
                 "system", "mailer-daemon", "postmaster")
TAPBACK_NAMES = {2000: "love", 2001: "like", 2002: "dislike",
                 2003: "laugh", 2004: "emphasize", 2005: "question"}
TARGET_GUID_PREFIX_RE = re.compile(r"^(?:p:0/|bp:|p:\d+/)")
URL_BALLOON_SKIP = "com.apple.messages.URLBalloonProvider"
PHONE_NONDIGIT_RE = re.compile(r"[^\d+]")


# ---------------------------------------------------------------------------
# Time + handle helpers
# ---------------------------------------------------------------------------
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


def normalize_phone(s):
    if not s:
        return None
    digits = PHONE_NONDIGIT_RE.sub("", s)
    if not digits:
        return None
    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits
    return digits or None


def normalize_handle(h):
    if not h:
        return None
    h = h.strip()
    if "@" in h:
        return h.lower()
    return normalize_phone(h)


def is_blocked(handle):
    """Universal blocklist; checks normalized form per Codex review."""
    if not handle:
        return False
    n = normalize_handle(handle) or handle
    if "@" in n:
        local = n.split("@")[0].lower()
        if any(local.startswith(p) for p in NOREPLY_LOCAL):
            return True
        return False
    # Phone-like
    if any(n.startswith(p) for p in TOLL_FREE_PREFIXES):
        return True
    digits = PHONE_NONDIGIT_RE.sub("", n)
    # Pure digit-only handle of length <= 6 → shortcode
    raw_digits = PHONE_NONDIGIT_RE.sub("", handle)
    if raw_digits == handle and len(raw_digits) <= 6:
        return True
    if re.fullmatch(r"\d{5,6}", n):
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


def name_to_slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "unnamed"


def handle_to_slug(h):
    if not h:
        return "unknown"
    if "@" in h:
        local, domain = h.split("@", 1)
        return f"email-{name_to_slug(local)}-at-{name_to_slug(domain)}"
    digits = PHONE_NONDIGIT_RE.sub("", h)
    return f"phone-{digits}"


# ---------------------------------------------------------------------------
# Apple Contacts handle → name resolver (for group sender display)
# ---------------------------------------------------------------------------
def load_apple_contacts():
    """Returns {normalized_handle: name}. Combines phones + emails."""
    try:
        from Contacts import (  # type: ignore
            CNContactStore, CNContactFetchRequest,
            CNContactGivenNameKey, CNContactFamilyNameKey,
            CNContactNicknameKey, CNContactOrganizationNameKey,
            CNContactPhoneNumbersKey, CNContactEmailAddressesKey,
        )
    except ImportError:
        return {}

    store = CNContactStore.alloc().init()
    keys = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactNicknameKey,
            CNContactOrganizationNameKey, CNContactPhoneNumbersKey,
            CNContactEmailAddressesKey]
    req = CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
    out = {}

    def cb(contact, stop):
        given = contact.givenName() or ""
        family = contact.familyName() or ""
        nick = contact.nickname() or ""
        org = contact.organizationName() or ""
        name = (given + " " + family).strip() or nick or org or None
        if not name:
            return
        for p in contact.phoneNumbers():
            n = normalize_phone(p.value().stringValue())
            if n:
                out[n] = name
        for e in contact.emailAddresses():
            v = str(e.value() or "").strip().lower()
            if v:
                out[v] = name

    try:
        store.enumerateContactsWithFetchRequest_error_usingBlock_(req, None, cb)
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------
# Gemini description (single + parallel with shared cooldown)
# ---------------------------------------------------------------------------
PROMPT_VISION = (
    "Describe what's in this in one sentence under 100 characters. "
    "Be specific and concrete. No preamble, just the description."
)
PROMPT_TEXT = (
    "Summarize this file in two sentences under 200 characters total. "
    "Surface-level only: what is it, what's the gist."
)

ATTACHMENTS_INCLUDE = str(Path.home() / "Library" / "Messages" / "Attachments")

# Refusal patterns — cache-poison if we let them through
_REFUSAL_RE = re.compile(
    r"(cannot access|cannot describe|cannot view|unable to (access|view|read)|"
    r"outside (the |my )?(allowed )?workspace|outside the allowed|"
    r"i (don't|do not) have (permission|access)|file path is outside)",
    re.IGNORECASE,
)
# Expanded per Codex: includes 503/overload, RPM/TPM, retry-after, etc.
_RATE_LIMIT_RE = re.compile(
    r"(rate ?limit|quota|429|503|resource[_ ]exhausted|too many requests|"
    r"retry after|try again later|requests per minute|tokens per minute|"
    r"\bRPM\b|\bTPM\b|temporarily unavailable|service unavailable|"
    r"overloaded|capacity|exceeded your (current )?limit|"
    r"user rate limit|rate exceeded)",
    re.IGNORECASE,
)


def hash_source(path):
    """Compute sha256 of a file. Returns (hex, available_bool)."""
    if not path.exists():
        return None, False
    if path.is_dir():
        return None, True  # bundle, no single hash
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(64 * 1024), b""):
                h.update(chunk)
        return h.hexdigest(), True
    except OSError:
        return None, False


def kind_of(mime, src):
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


def bundle_description(src, ext):
    table = {
        ".logicx": "Logic Pro project bundle",
        ".band": "GarageBand project bundle",
        ".photoslibrary": "Apple Photos library bundle",
        ".app": "macOS application bundle",
        ".pkg": "Installer package bundle",
    }
    return table.get(ext.lower(), f"{ext.lstrip('.')} bundle")


# Shared cool-down: when ANY worker hits rate-limit, all workers wait
# until release_at_monotonic. Implemented via threading.Event signal.
_COOLDOWN_LOCK = threading.Lock()
_COOLDOWN_RELEASE_AT = [0.0]   # monotonic seconds; 0 = no cooldown


def _request_cooldown(seconds):
    with _COOLDOWN_LOCK:
        target = time.monotonic() + seconds
        if target > _COOLDOWN_RELEASE_AT[0]:
            _COOLDOWN_RELEASE_AT[0] = target


def _wait_cooldown():
    while True:
        with _COOLDOWN_LOCK:
            wait = _COOLDOWN_RELEASE_AT[0] - time.monotonic()
        if wait <= 0:
            return
        time.sleep(min(wait, 5.0))


def gemini_describe_once(path, kind, timeout=180):
    """Single Gemini CLI call. Returns (description, model, error_kind).
    error_kind: None|'rate_limit'|'refusal'|'timeout'|'failure'|'unsupported'|'missing'|'no_cli'|'empty'."""
    if kind not in ("image", "video", "text"):
        return None, None, "unsupported"
    if not path.exists() or path.is_dir():
        return None, None, "missing"
    prompt = PROMPT_VISION if kind in ("image", "video") else PROMPT_TEXT
    cmd = [
        "gemini",
        "-m", DESCRIPTION_MODEL,   # pin Flash explicitly; CLI auto-routes to Pro otherwise
        "-p", f"{prompt}\n\n@{path}",
        "-o", "text",
        "--approval-mode", "plan",
        "--include-directories", ATTACHMENTS_INCLUDE,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, None, "timeout"
    except FileNotFoundError:
        return None, None, "no_cli"

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")

    # Detect rate-limit even on returncode 0 (Gemini round 4 finding)
    if _RATE_LIMIT_RE.search(combined):
        return None, None, "rate_limit"
    if proc.returncode != 0:
        return None, None, "failure"

    desc = (proc.stdout or "").strip()
    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
    if not lines:
        return None, None, "empty"
    desc = lines[-1]
    if _REFUSAL_RE.search(desc):
        return None, None, "refusal"
    cap = 100 if kind in ("image", "video") else 200
    if len(desc) > cap:
        desc = desc[: cap - 1].rstrip() + "…"
    return desc, DESCRIPTION_MODEL, None


def gemini_describe_with_retry(path, kind, max_retries=3):
    """Single-call wrapper with exponential backoff on rate limits.
    Honors the global cooldown event."""
    delay = 5.0
    for attempt in range(max_retries + 1):
        _wait_cooldown()
        desc, model, err = gemini_describe_once(path, kind)
        if err != "rate_limit":
            return desc, model, err
        # Rate limit: signal global cooldown so other workers pause too
        sleep_for = delay + random.uniform(0, delay)
        _request_cooldown(sleep_for)
        if attempt >= max_retries:
            return desc, model, err
        time.sleep(sleep_for)
        delay = min(delay * 2, 60)
    return None, None, "rate_limit"


def parallel_describe(worklist, workers, on_progress=None):
    """Run gemini_describe_with_retry over worklist in parallel.

    worklist: list of dicts with keys {sha256, src, kind, ext}
    Returns: dict {sha256: {description, model, extracted_at, error}}
    """
    results = {}
    if not worklist:
        return results
    done_count = [0]
    total = len(worklist)

    # Startup jitter: each worker delays 0-2s before its first call,
    # spreading initial load across the API surface.
    startup_jitter_done = set()
    jitter_lock = threading.Lock()

    def task(item):
        # First-call jitter for this thread
        tid = threading.get_ident()
        with jitter_lock:
            if tid not in startup_jitter_done:
                startup_jitter_done.add(tid)
                time.sleep(random.uniform(0, 2.0))
        sha = item["sha256"]
        src = item["src"]
        kind = item["kind"]
        ext = item.get("ext") or ""
        if kind == "bundle":
            desc = bundle_description(src, ext)
            return sha, {
                "description": desc,
                "model": None,
                "extracted_at": None,
                "error": None,
            }
        desc, model, err = gemini_describe_with_retry(src, kind)
        if desc:
            return sha, {
                "description": desc,
                "model": model,
                "extracted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "error": None,
            }
        return sha, {
            "description": None,
            "model": None,
            "extracted_at": None,
            "error": err,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, item) for item in worklist]
        for fut in concurrent.futures.as_completed(futures):
            try:
                sha, payload = fut.result()
            except Exception as e:
                # Codex round 4: don't let one task crash the whole target
                done_count[0] += 1
                sys.stderr.write(f"\n  worker exception (continuing): {e}\n")
                continue
            results[sha] = payload
            done_count[0] += 1
            if on_progress and (done_count[0] % 25 == 0 or done_count[0] == total):
                on_progress(done_count[0], total)
    return results


# ---------------------------------------------------------------------------
# Prior-description cache (idempotency)
# ---------------------------------------------------------------------------
def load_prior_descriptions(month_path):
    """Read existing month file frontmatter → {sha256: (description, model, extracted_at)}."""
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
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}
    out = {}
    for a in fm.get("attachments", []) or []:
        sha = a.get("sha256")
        model = a.get("description_model")
        desc = a.get("description")
        extracted_at = a.get("extracted_at")
        if sha and desc:
            out[sha] = (desc, model, extracted_at)
    return out


# ---------------------------------------------------------------------------
# Chat resolution
# ---------------------------------------------------------------------------
def find_chats_for_handles(conn, handles):
    """Strict 1:1 chat lookup: chat must contain target handle AND have
    exactly one distinct participant. No service_name filter (SMS/iMessage/RCS all eligible).
    Codex round 4: HAVING COUNT(DISTINCT handle) = 1 prevents merging
    unrelated group chats into an individual target."""
    if not handles:
        return []
    placeholders = ",".join(["?"] * len(handles))
    rows = conn.execute(f"""
        SELECT c.ROWID
        FROM chat c
        WHERE c.ROWID IN (
            SELECT chj.chat_id
            FROM chat_handle_join chj
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE h.id IN ({placeholders})
        )
        AND (
            SELECT COUNT(DISTINCT chj2.handle_id)
            FROM chat_handle_join chj2
            WHERE chj2.chat_id = c.ROWID
        ) = 1
    """, handles).fetchall()
    return [r[0] for r in rows]


def find_chats_for_group(conn, chat_guid):
    """Return chat ROWIDs for a group, including SMS/MMS-fallback chats
    (different chat_guid but identical participant set). Gemini round 4:
    Apple Messages creates a NEW chat_guid when an iMessage group falls
    back to SMS, so single-guid lookup misses those."""
    target_handles = set()
    for (h,) in conn.execute("""
        SELECT h.id FROM chat c
        JOIN chat_handle_join chj ON chj.chat_id = c.ROWID
        JOIN handle h ON h.ROWID = chj.handle_id
        WHERE c.guid = ?
    """, (chat_guid,)):
        target_handles.add(h)
    if not target_handles:
        return []
    if len(target_handles) <= 1:
        # Defensive: not really a group; return just the guid match
        rows = conn.execute("SELECT ROWID FROM chat WHERE guid = ?", (chat_guid,)).fetchall()
        return [r[0] for r in rows]

    # Find all chats with same participant set
    matching = []
    for (cid,) in conn.execute("""
        SELECT c.ROWID FROM chat c
        WHERE c.ROWID IN (
            SELECT chj.chat_id FROM chat_handle_join chj
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE h.id IN ({})
        )
    """.format(",".join(["?"] * len(target_handles))), tuple(target_handles)):
        members = set()
        for (h,) in conn.execute("""
            SELECT h.id FROM chat_handle_join chj
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE chj.chat_id = ?
        """, (cid,)):
            members.add(h)
        if members == target_handles:
            matching.append(cid)
    return matching


def chat_handles(conn, chat_ids):
    if not chat_ids:
        return []
    ph = ",".join(["?"] * len(chat_ids))
    return [h for (h,) in conn.execute(f"""
        SELECT DISTINCT h.id
        FROM chat_handle_join chj
        JOIN handle h ON h.ROWID = chj.handle_id
        WHERE chj.chat_id IN ({ph})
        ORDER BY h.id
    """, chat_ids).fetchall()]


# ---------------------------------------------------------------------------
# Render — unified for individuals + groups
# ---------------------------------------------------------------------------
def gather_messages_and_attachments(conn, chat_ids):
    """Pull messages + attachments for chat set. SHA-256 each attachment ONCE
    here and cache on the dict. DISTINCT in queries (Codex round 4).
    """
    ph = ",".join(["?"] * len(chat_ids))
    msg_rows = list(conn.execute(f"""
        SELECT DISTINCT m.ROWID, m.guid, m.text, m.date, m.is_from_me,
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
        SELECT DISTINCT maj.message_id, a.guid, a.filename, a.transfer_name,
               a.total_bytes, a.uti, a.mime_type, a.ROWID
        FROM message_attachment_join maj
        JOIN attachment a ON maj.attachment_id = a.ROWID
        JOIN chat_message_join cmj ON cmj.message_id = maj.message_id
        WHERE cmj.chat_id IN ({ph})
    """, chat_ids))
    att_by_msg = {}
    for mid, aguid, fn, tn, sz, uti, mime, arow in att_rows:
        display_name = tn or (Path(fn).name if fn else "untitled")
        src = Path(os.path.expanduser(fn)) if fn else None
        sha256, source_available = (None, False) if src is None else hash_source(src)
        att_by_msg.setdefault(mid, []).append({
            "guid": aguid,
            "filename": display_name,
            "transfer_name": tn,
            "size_bytes": sz,
            "uti": uti,
            "mime": mime,
            "rowid": arow,
            "src_path": fn,
            "src": src,
            "sha256": sha256,
            "source_available": source_available,
            "kind": kind_of(mime, src),
        })
    return msg_rows, att_by_msg


def filter_blocked_messages(msgs):
    blocked = sum(1 for r in msgs if r[10] and is_blocked(r[10]))
    msgs = [r for r in msgs if not (r[10] and is_blocked(r[10]))]
    return msgs, blocked


def split_tapbacks(msgs):
    raw_tap = {}
    body_msgs = []
    for r in msgs:
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
            body_msgs.append(r)

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
    return body_msgs, tapbacks


def recover_attributed_bodies(msgs):
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
    return fixed, recovered, failed, skipped_url


def build_attachment_worklist(msgs, att_by_msg, prior_desc, skip_descriptions):
    """Build flat worklist of attachments needing Gemini calls.
    Reads pre-computed sha256 from att dict — NO re-hashing."""
    worklist = []
    seen_sha = set()
    for r in msgs:
        for a in att_by_msg.get(r[0], []):
            if not a["source_available"] or a["sha256"] is None:
                continue
            if a["sha256"] in seen_sha:
                continue
            seen_sha.add(a["sha256"])
            if skip_descriptions:
                continue
            if a["sha256"] in prior_desc:
                continue
            kind = a["kind"]
            if kind not in ("image", "video", "text", "bundle"):
                continue
            worklist.append({
                "sha256": a["sha256"],
                "src": a["src"],
                "kind": kind,
                "ext": Path(a["filename"]).suffix or "",
            })
    return worklist


def disambiguate_first_names(handle_to_first):
    """Given a map {handle: first_name}, detect collisions and return a
    map {handle: display_name} where collided ones get full name."""
    # Reverse map first → list of handles
    counts = {}
    for h, fn in handle_to_first.items():
        counts.setdefault(fn, []).append(h)
    out = dict(handle_to_first)
    for fn, hs in counts.items():
        if len(hs) > 1:
            # Collision; can't safely shorten — fall back to handle
            # (caller passes in full name; we'll use full name instead)
            for h in hs:
                out[h] = None  # signal: use full name
    return out


def merge_profile_stub(prof_path, new_profile):
    """Read existing profile, preserve user-edited keys (aliases, notes),
    update auto-fields. Never destroy existing content (Gemini round 4)."""
    if not prof_path.exists():
        text = "---\n" + yaml.safe_dump(new_profile, sort_keys=False) + "---\n"
        prof_path.write_text(text)
        return
    raw = prof_path.read_text()
    m = re.match(r"^---\n(.+?)\n---\n?(.*)", raw, re.DOTALL)
    if not m:
        # Malformed; back up + write fresh
        prof_path.with_suffix(".md.bak").write_text(raw)
        text = "---\n" + yaml.safe_dump(new_profile, sort_keys=False) + "---\n"
        prof_path.write_text(text)
        return
    try:
        existing = yaml.safe_load(m.group(1)) or {}
    except Exception:
        existing = {}
    body = m.group(2) or ""
    # Auto-keys we always update
    AUTO = {"slug", "contact_type", "contact_handles", "contact_name",
            "slug_derivation", "chat_guid", "members", "member_count",
            "display_name"}
    merged = dict(existing)
    for k, v in new_profile.items():
        if k in AUTO:
            merged[k] = v
        elif k not in merged:
            merged[k] = v
    # Ensure first_seen never moves earlier (snapshot oldest known)
    if "first_seen" in new_profile:
        if "first_seen" not in merged or new_profile["first_seen"] < (merged["first_seen"] or "9999"):
            merged["first_seen"] = new_profile["first_seen"]
    text = "---\n" + yaml.safe_dump(merged, sort_keys=False) + "---\n" + body
    prof_path.write_text(text)


def render_target(conn, target_cfg, target_kind, ws, out_root, dry_run,
                  workers, skip_descriptions, contacts_map):
    slug = target_cfg["slug"]
    chat_ids = []
    handles_for_target = []
    chat_guid = None

    if target_kind == "individual":
        handles_for_target = target_cfg["handles"]
        chat_ids = find_chats_for_handles(conn, handles_for_target)
    else:
        chat_guid = target_cfg["chat_guid"]
        chat_ids = find_chats_for_group(conn, chat_guid)

    if not chat_ids:
        print(f"  [{target_kind}] {slug}: no chat found")
        return None

    all_handles = chat_handles(conn, chat_ids)
    msg_rows, att_by_msg = gather_messages_and_attachments(conn, chat_ids)

    raw_msgs, tapbacks = split_tapbacks(msg_rows)
    raw_msgs, blocked = filter_blocked_messages(raw_msgs)
    msgs, recovered, failed, skipped_url = recover_attributed_bodies(raw_msgs)

    if not msgs:
        print(f"  [{target_kind}] {slug}: no renderable messages after filtering")
        return None

    # Bucket by month
    by_month = {}
    for r in msgs:
        dt = to_dt(r[3])
        if dt is None:
            continue
        key = dt.astimezone(TZ).strftime("%Y-%m")
        by_month.setdefault(key, []).append(r)

    if target_kind == "individual":
        target_dir = out_root / "individuals" / slug
    else:
        target_dir = out_root / "groups" / slug
    profiles_dir = out_root / "_profiles"
    if not dry_run:
        profiles_dir.mkdir(parents=True, exist_ok=True)

    # Load prior descriptions across ALL months for this target
    prior_combined = {}
    for month_key in by_month:
        first_dt = to_dt(by_month[month_key][0][3]).astimezone(TZ)
        year = first_dt.year
        month_dir = target_dir / str(year)
        month_path = month_dir / f"{month_key}__{slug}.md"
        prior_combined.update(load_prior_descriptions(month_path))

    worklist = build_attachment_worklist(msgs, att_by_msg, prior_combined, skip_descriptions)
    if worklist:
        print(f"  [{target_kind}] {slug}: {len(worklist)} new descriptions ({workers}x parallel)")
        def progress(done, total):
            sys.stdout.write(f"\r    ...{done}/{total} described")
            sys.stdout.flush()
            if done == total:
                sys.stdout.write("\n")
        new_descriptions = parallel_describe(worklist, workers, on_progress=progress)
    else:
        new_descriptions = {}

    # Combine prior + new for fast lookup
    all_desc = {}
    for sha, (desc, model, extracted_at) in prior_combined.items():
        all_desc[sha] = {
            "description": desc, "model": model,
            "extracted_at": extracted_at, "error": None,
        }
    all_desc.update(new_descriptions)

    # Build sender display map for groups (with first-name collision handling)
    sender_display_map = {}  # handle → (display, slug)
    if target_kind == "group":
        first_name_map = {}
        for h in all_handles:
            n = normalize_handle(h)
            name = contacts_map.get(n) if n else None
            if name:
                first_name_map[h] = name.split()[0]
        # Detect collisions
        collisions = {}
        for h, fn in first_name_map.items():
            collisions.setdefault(fn, []).append(h)
        for h in all_handles:
            n = normalize_handle(h)
            name = contacts_map.get(n) if n else None
            if name:
                fn = name.split()[0]
                if len(collisions.get(fn, [])) > 1:
                    sender_display_map[h] = (name, name_to_slug(name))  # full name
                else:
                    sender_display_map[h] = (fn, name_to_slug(name))
            else:
                sender_display_map[h] = (h or "unknown", handle_to_slug(h))

    # Profile stub
    primary_handle = handles_for_target[0] if handles_for_target else None
    first_seen_dt = to_dt(msgs[0][3]).astimezone(TZ).date()
    if target_kind == "individual":
        profile = {
            "slug": slug,
            "contact_type": "individual",
            "contact_handles": handles_for_target,
            "contact_name": " ".join(p.capitalize() for p in slug.split("-")),
            "slug_derivation": "contacts_full_name",
            "chat_guid": None,
            "first_seen": str(first_seen_dt),
            "aliases": [],
        }
        prof_filename = f"{slug}.md"
    else:
        members = []
        for h in all_handles:
            n = normalize_handle(h)
            members.append({
                "handle": h,
                "name": (contacts_map.get(n) if n else None) or None,
            })
        profile = {
            "slug": slug,
            "contact_type": "group",
            "chat_guid": chat_guid,
            "display_name": target_cfg.get("display_name") or None,
            "first_seen": str(first_seen_dt),
            "members": members,
            "member_count": len(all_handles),
        }
        prof_filename = f"group-{slug}.md"   # avoid cross-kind collision (Codex)

    if not dry_run:
        prof_path = profiles_dir / prof_filename
        merge_profile_stub(prof_path, profile)

    # Render months
    written_files = []
    total_atts_inlined = 0
    total_atts_described = 0
    total_atts_skipped = 0
    total_atts_unavailable = 0
    total_atts_reused = 0
    total_atts_errored = 0

    if target_kind == "individual":
        peer_display = slug.split("-")[0].capitalize()
    else:
        peer_display = None

    def sender_display(r):
        from_me = r[4]
        handle_id = r[10]
        if from_me:
            return "me", "me"
        if target_kind == "individual":
            return peer_display, slug
        # group
        if handle_id and handle_id in sender_display_map:
            return sender_display_map[handle_id]
        return handle_id or "unknown", handle_to_slug(handle_id)

    for month_key in sorted(by_month):
        month_msgs = by_month[month_key]
        first_dt = to_dt(month_msgs[0][3]).astimezone(TZ)
        last_dt = to_dt(month_msgs[-1][3]).astimezone(TZ)
        my_count = sum(1 for r in month_msgs if r[4])
        their_count = sum(1 for r in month_msgs if not r[4])

        year = first_dt.year
        month_dir = target_dir / str(year)
        if not dry_run:
            month_dir.mkdir(parents=True, exist_ok=True)

        # Build attachments[] frontmatter — uses cached sha256
        fm_atts = []
        for r in month_msgs:
            for a in att_by_msg.get(r[0], []):
                aid = _blake3(
                    f"{a['guid'] or a['filename']}|"
                    f"{a['size_bytes'] or 0}|{a['rowid']}".encode()
                ).hexdigest()[:16]
                if not a["source_available"]:
                    total_atts_unavailable += 1
                description = None
                model = None
                extracted_at = None
                sha256 = a["sha256"]
                if a["source_available"] and sha256:
                    if sha256 in all_desc:
                        d = all_desc[sha256]
                        description = d["description"]
                        model = d["model"]
                        extracted_at = d["extracted_at"]
                        if description:
                            if sha256 in prior_combined and sha256 not in new_descriptions:
                                total_atts_reused += 1
                            else:
                                total_atts_described += 1
                        else:
                            if d.get("error"):
                                total_atts_errored += 1
                            else:
                                total_atts_skipped += 1
                    else:
                        total_atts_skipped += 1
                _, sender_slug = sender_display(r)
                fm_atts.append({
                    "id": aid,
                    "filename": a["filename"],
                    "mime": a["mime"],
                    "size_bytes": a["size_bytes"],
                    "sender": "me" if r[4] else sender_slug,
                    "sent_at": to_dt(r[3]).astimezone(TZ).isoformat(),
                    "sha256": sha256,
                    "description": description,
                    "description_model": model,
                    "extracted_at": extracted_at,
                    "source_available": a["source_available"],
                })

        # Render body
        if target_kind == "individual":
            title = f"# {peer_display} — {first_dt.strftime('%B %Y')}"
        else:
            display_name = target_cfg.get("display_name") or slug
            title = f"# {display_name} — {first_dt.strftime('%B %Y')}"
        lines = [title, ""]
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
            sender_disp, _ = sender_display(r)
            edited = " (edited)" if dedit and dedit > 0 else ""

            atts = att_by_msg.get(rowid, [])
            for a in atts:
                kind = a["kind"]
                desc = None
                if a["sha256"] and a["sha256"] in all_desc:
                    desc = all_desc[a["sha256"]]["description"]
                if desc:
                    lines.append(f"**{dt.strftime('%H:%M')} — {sender_disp}:** [{kind}: {desc}]")
                else:
                    lines.append(f"**{dt.strftime('%H:%M')} — {sender_disp}:** [{kind}: {a['filename']}]")
                total_atts_inlined += 1
            body_text = (text or "").strip().replace("￼", "").strip()
            if body_text:
                lines.append(f"**{dt.strftime('%H:%M')} — {sender_disp}{edited}:** {body_text}")
            elif bbi and not atts:
                lines.append(f"**{dt.strftime('%H:%M')} — {sender_disp}:** [app message: {bbi}]")
            stripped = strip_target_guid(guid)
            for tname, tsender_handle, tdate in tapbacks.get(stripped, []):
                tdt = to_dt(tdate)
                if tdt is None:
                    continue
                tdt = tdt.astimezone(TZ)
                snippet = body_text.replace('"', '\\"')[:60]
                if tsender_handle == "me":
                    tsender_render = "me"
                elif target_kind == "individual" and handles_for_target and tsender_handle == handles_for_target[0]:
                    tsender_render = peer_display
                elif tsender_handle in sender_display_map:
                    tsender_render = sender_display_map[tsender_handle][0]
                else:
                    n = normalize_handle(tsender_handle)
                    nm = contacts_map.get(n) if n else None
                    tsender_render = nm.split()[0] if nm else tsender_handle
                lines.append(
                    f'**{tdt.strftime("%H:%M")} — {tsender_render}:** '
                    f'[reaction: {tname} to "{snippet}"]'
                )

        body = "\n".join(lines).rstrip() + "\n"
        ch = "blake3:" + _blake3(body.encode()).hexdigest()
        guids_in_month = len({r[1] for r in month_msgs})

        fm = {
            "source": "imessage",
            "workspace": ws,
            "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ingest_version": 1,
            "content_hash": ch,
            "provider_modified_at": last_dt.isoformat(),
            "contact_slug": slug,
            "contact_type": target_kind,
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
        if target_kind == "individual":
            fm["contact_handles"] = handles_for_target
            fm["contact_name"] = " ".join(p.capitalize() for p in slug.split("-"))
            fm["chat_guid"] = None
        else:
            fm["chat_guid"] = chat_guid
            fm["display_name"] = target_cfg.get("display_name") or None
            fm["member_count"] = len(all_handles)

        fm_text = "---\n" + yaml.safe_dump(fm, sort_keys=False, default_flow_style=False) + "---\n\n"
        out_path = month_dir / f"{month_key}__{slug}.md"
        if not dry_run:
            out_path.write_text(fm_text + body)
        written_files.append((out_path, len(month_msgs), len(fm_atts), len(body) + len(fm_text), ch))

    return {
        "slug": slug,
        "kind": target_kind,
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
        "atts_errored": total_atts_errored,
        "tapbacks_attached": sum(len(v) for v in tapbacks.values()),
    }


def append_ledger(ws_root, slug, target_kind, files, run_id="oneshot"):
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
            key = f"imessage:{target_kind}:{slug}:{month}"
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
    if appended or skipped:
        print(f"  ledger: {appended} appended, {skipped} skipped (already up-to-date)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--contact", help="filter to a single allowlisted 1:1 slug")
    ap.add_argument("--group", help="filter to a single allowlisted group slug")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-descriptions", action="store_true")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                    help=f"parallel Gemini calls (default {DEFAULT_WORKERS})")
    args = ap.parse_args()

    ws_root = ULTRON_ROOT / "workspaces" / args.workspace
    cfg_path = ws_root / "config" / "sources.yaml"
    if not cfg_path.exists():
        sys.exit(f"sources.yaml not found at {cfg_path}")
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    imsg = ((cfg.get("sources") or {}).get("imessage") or {})
    contacts = imsg.get("contacts") or []
    groups = imsg.get("groups") or []

    if args.contact:
        contacts = [c for c in contacts if c.get("slug") == args.contact]
        groups = []
    if args.group:
        groups = [g for g in groups if g.get("slug") == args.group]
        contacts = []

    if not contacts and not groups:
        sys.exit("no targets after filter")

    out_root = ws_root / "raw" / "imessage"
    print(f"workspace:    {args.workspace}")
    print(f"output:       {out_root}")
    print(f"dry-run:      {args.dry_run}")
    print(f"workers:      {args.workers}")
    print(f"contacts:     {len(contacts)}")
    print(f"groups:       {len(groups)}")

    print(f"loading Apple Contacts handle map...")
    contacts_map = load_apple_contacts()
    print(f"  {len(contacts_map)} handles mapped")

    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    skip_desc = args.no_descriptions

    def report(result):
        if not result:
            return
        print(f"\n  [{result['kind']}] {result['slug']}: {len(result['files'])} files")
        for path, mcount, acount, size, _ch in result["files"]:
            try:
                rel = path.relative_to(ULTRON_ROOT)
            except ValueError:
                rel = path
            print(f"    {rel}: {mcount} msgs, {acount} atts, {size:,} bytes")
        if result['blocked']: print(f"  blocked: {result['blocked']}")
        if result['recovered']: print(f"  attrBody recovered: {result['recovered']}")
        if result['atts_described']: print(f"  atts described: {result['atts_described']}")
        if result['atts_reused']: print(f"  atts reused: {result['atts_reused']}")
        if result['atts_errored']: print(f"  atts errored: {result['atts_errored']}")
        if result['tapbacks_attached']: print(f"  tapbacks: {result['tapbacks_attached']}")

    total_targets = len(contacts) + len(groups)
    seen = 0
    for c in contacts:
        seen += 1
        print(f"\n[{seen}/{total_targets}] individual: {c['slug']}")
        try:
            result = render_target(conn, c, "individual", args.workspace, out_root,
                                  args.dry_run, args.workers, skip_desc, contacts_map)
            report(result)
            if result and not args.dry_run:
                append_ledger(ws_root, result["slug"], "individual", result["files"])
        except Exception as e:
            sys.stderr.write(f"  ERROR rendering {c['slug']}: {e}\n")
            import traceback; traceback.print_exc(file=sys.stderr)

    for g in groups:
        seen += 1
        print(f"\n[{seen}/{total_targets}] group: {g['slug']}")
        try:
            result = render_target(conn, g, "group", args.workspace, out_root,
                                  args.dry_run, args.workers, skip_desc, contacts_map)
            report(result)
            if result and not args.dry_run:
                append_ledger(ws_root, result["slug"], "group", result["files"])
        except Exception as e:
            sys.stderr.write(f"  ERROR rendering {g['slug']}: {e}\n")
            import traceback; traceback.print_exc(file=sys.stderr)

    conn.close()
    print("\ndone")


if __name__ == "__main__":
    main()
