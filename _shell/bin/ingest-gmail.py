#!/usr/bin/env python3
"""
ingest-gmail.py — per-(source, account) Gmail ingest robot.

Usage:
    ingest-gmail.py --account <email> [--run-id <id>] [--dry-run] [--max-items N]

Contract (Phase 2/3):
    1. Load _credentials/gmail-<account-slug>.json (gog-derived authorized-user
       JSON with refresh_token + shared client_id/client_secret).
    2. Walk every workspaces/*/config/sources.yaml; collect every gmail block
       that mentions this account. Build a union Gmail q= query (best-effort
       server-side filter; route.py does precise routing post-fetch).
    3. Read cursor at _shell/cursors/gmail/<account-slug>.txt.
       - First run / empty cursor: use the largest workspace
         lookback_days_initial value (default 365).
       - Subsequent runs: use the cursor's "after:" timestamp directly.
    4. Paginate users.threads.list. For each thread:
       a. Fetch full thread via users.threads.get(format='full').
       b. Apply deterministic pre-filter (size, OOO, blocklist, labels, .ics).
       c. Convert HTML→markdown (html2text), strip quoted history + signatures.
       d. Compute blake3 content_hash of the body.
       e. Build universal frontmatter envelope + Gmail-specific fields.
       f. Call route.py:route(thread, workspaces_config) → destination workspaces.
       g. For each destination: write the markdown file at
          workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<file>.md
          (stable path => idempotent re-runs overwrite the same file).
       h. Append ledger row to workspaces/<ws>/_meta/ingested.jsonl
          (skip if same key + same content_hash already present).
    5. Advance cursor to the latest internalDate seen.
    6. Append summary to each affected workspace's _meta/log.md.

Errors:
    - Auth failure (401/403/invalid_grant): fast-fail with recovery message.
    - Rate-limit (429/userRateLimitExceeded): exponential backoff, max 3 retries.
    - Per-thread errors: log to _logs/gmail-errors-<date>.log, continue.
    - Network errors: 1 retry, then abort.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr, parsedate_to_datetime
from html import unescape
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
INGEST_VERSION = 1
GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT = 365
PRE_FILTER_MAX_BYTES = 25 * 1024 * 1024
SUBJECT_SLUG_MAX = 60
THREAD_ID_PREFIX_LEN = 8

# Per-thread soft cap: avoid pathological signature loops eating the whole run.
PER_THREAD_TIMEOUT_S = 30

# Allow `from _shell.stages.ingest.gmail.route import route`-style import even
# though _shell isn't a Python package (no __init__.py). Slot the route.py dir
# directly onto sys.path.
_ROUTE_DIR = ULTRON_ROOT / "_shell" / "stages" / "ingest" / "gmail"
if str(_ROUTE_DIR) not in sys.path:
    sys.path.insert(0, str(_ROUTE_DIR))

import yaml  # noqa: E402
import blake3  # noqa: E402
import html2text  # noqa: E402
from route import route as route_thread  # noqa: E402


# ---------------------------------------------------------------------------
# Account slug + paths
# ---------------------------------------------------------------------------

def account_slug(email: str) -> str:
    """`adithya@outerscope.xyz` -> `adithya-outerscope`."""
    local, _, domain = email.lower().strip().partition("@")
    stem = domain.split(".", 1)[0] if domain else ""
    s = f"{local}-{stem}" if stem else local
    return re.sub(r"[^a-z0-9-]", "-", s).strip("-") or "unknown"


def cred_path_for(account: str) -> Path:
    return ULTRON_ROOT / "_credentials" / f"gmail-{account_slug(account)}.json"


def cursor_path_for(account: str) -> Path:
    p = ULTRON_ROOT / "_shell" / "cursors" / "gmail" / f"{account_slug(account)}.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def errors_log_path() -> Path:
    p = ULTRON_ROOT / "_logs" / f"gmail-errors-{datetime.now().strftime('%Y-%m-%d')}.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Workspace config loading
# ---------------------------------------------------------------------------

def load_all_workspaces_config() -> dict[str, dict]:
    """Returns {ws_slug: parsed_sources_yaml_dict}."""
    out: dict[str, dict] = {}
    ws_dir = ULTRON_ROOT / "workspaces"
    if not ws_dir.exists():
        return out
    for ws_path in sorted(ws_dir.iterdir()):
        if not ws_path.is_dir() or ws_path.name.startswith("_"):
            continue
        cfg_path = ws_path / "config" / "sources.yaml"
        if not cfg_path.exists():
            continue
        try:
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
        except yaml.YAMLError as exc:
            sys.stderr.write(f"ingest-gmail: skipping {ws_path.name} (bad sources.yaml: {exc})\n")
            continue
        if isinstance(cfg, dict):
            out[ws_path.name] = cfg
    return out


def collect_account_rules(account: str, workspaces_config: dict[str, dict]) -> tuple[list[str], list[str], int]:
    """For this account, return (combined_includes, combined_excludes, initial_lookback_days).

    Tolerates:
      * NEW shape:  sources.gmail.accounts = [{account, api_query: {include, exclude}}]
      * LEGACY:     sources: [{type: gmail, config: {account, labels, exclude_labels, lookback_days_initial}}]
    """
    includes: list[str] = []
    excludes: list[str] = []
    lookback_seen: int | None = None  # None until any workspace specifies a value

    for ws, cfg in workspaces_config.items():
        sources = cfg.get("sources")

        # NEW dict shape
        if isinstance(sources, dict):
            block = sources.get("gmail")
            if not block:
                continue
            accounts = block.get("accounts") if isinstance(block, dict) else None
            if isinstance(accounts, list):
                for acct in accounts:
                    if isinstance(acct, str):
                        if acct == account:
                            api = (block.get("api_query") or {})
                            includes.extend(api.get("include") or [])
                            excludes.extend(api.get("exclude") or [])
                    elif isinstance(acct, dict):
                        if (acct.get("account") or "") == account:
                            api = acct.get("api_query") or {}
                            includes.extend(api.get("include") or [])
                            excludes.extend(api.get("exclude") or [])
                            li = acct.get("lookback_days_initial")
                            if isinstance(li, int):
                                lookback_seen = li if lookback_seen is None else max(lookback_seen, li)
            else:
                # Top-level api_query (no accounts list): apply if any account matches.
                api = (block.get("api_query") or {}) if isinstance(block, dict) else {}
                if api.get("include") or api.get("exclude"):
                    includes.extend(api.get("include") or [])
                    excludes.extend(api.get("exclude") or [])
            continue

        # LEGACY list shape
        if isinstance(sources, list):
            for s in sources:
                if not isinstance(s, dict) or s.get("type") != "gmail":
                    continue
                conf = s.get("config") or {}
                if (conf.get("account") or "") != account:
                    continue
                # Translate labels[]/exclude_labels[] to label: predicates.
                for lbl in conf.get("labels") or []:
                    includes.append(f"label:{lbl}")
                for lbl in conf.get("exclude_labels") or []:
                    excludes.append(f"label:{lbl}")
                li = conf.get("lookback_days_initial")
                if isinstance(li, int):
                    lookback_seen = li if lookback_seen is None else max(lookback_seen, li)

    lookback = lookback_seen if lookback_seen is not None else GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT
    return includes, excludes, lookback


# ---------------------------------------------------------------------------
# Predicate -> Gmail q= translation
# ---------------------------------------------------------------------------

def _predicate_to_q(p: str) -> str | None:
    """Translate one ULTRON predicate to a Gmail q= clause; None = untranslatable.

    Translations are best-effort superset filters; route.py applies the precise
    rule downstream. We drop predicates that would translate to something Gmail
    interprets ambiguously (anything with a wildcard left in the result).
    """
    p = p.strip()
    if not p:
        return None
    if p.startswith("label:"):
        return f"label:{p.split(':', 1)[1].strip()}"
    if p.startswith(("from:", "to:", "cc:")):
        role, pat = p.split(":", 1)
        pat = pat.strip()
        # Strip wildcard noise. Gmail q= treats * literally.
        # `from:*@eclipse.audio` -> `from:eclipse.audio`
        # `from:noreply@*`       -> `from:noreply`
        # `from:*@*`             -> drop (no signal)
        pat = pat.replace("*", "").strip("@")
        if not pat or pat.count("*") > 0:
            return None
        return f"{role}:{pat}"
    if p.lower().startswith("subject:contains:"):
        val = p.split(":", 2)[2].strip()
        return f'subject:"{val}"' if val else None
    # subject:regex:..., any:..., others — best handled post-fetch by route.py.
    return None


def build_q(includes: list[str], excludes: list[str], after_ts: int | None) -> str:
    # Dedupe while preserving first-seen order.
    def _dedup(seq):
        seen, out = set(), []
        for x in seq:
            if x and x not in seen:
                seen.add(x); out.append(x)
        return out

    inc_q = _dedup(t for t in (_predicate_to_q(p) for p in includes) if t)
    exc_q = _dedup(t for t in (_predicate_to_q(p) for p in excludes) if t)
    parts: list[str] = []
    if inc_q:
        parts.append("(" + " OR ".join(inc_q) + ")")
    for e in exc_q:
        parts.append(f"-{e}")
    parts.append("-in:trash")
    parts.append("-in:spam")
    if after_ts:
        parts.append(f"after:{after_ts}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Gmail API client
# ---------------------------------------------------------------------------

def build_service(account: str):
    cred_path = cred_path_for(account)
    if not cred_path.exists():
        raise SystemExit(
            f"ingest-gmail: no credentials at {cred_path.relative_to(ULTRON_ROOT)}.\n"
            f"  Recovery: see _shell/docs/runbook-gmail.md (\"wiring a new account\")."
        )

    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    info = json.loads(cred_path.read_text())
    cred_kwargs = {
        "client_id": info["client_id"],
        "client_secret": info["client_secret"],
        "refresh_token": info["refresh_token"],
        "token_uri": info.get("token_uri", "https://oauth2.googleapis.com/token"),
    }
    creds = Credentials.from_authorized_user_info(cred_kwargs)
    try:
        creds.refresh(Request())
    except Exception as exc:
        raise SystemExit(
            f"ingest-gmail: auth failed for {account}: {exc}\n"
            f"  Likely cause: refresh_token revoked or expired.\n"
            f"  Recovery: re-mint via gog (`gog auth login -a {account}`),\n"
            f"            update {cred_path.relative_to(ULTRON_ROOT)} with the new\n"
            f"            refresh_token, then re-run."
        )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _retry(fn, *, attempts: int = 3, base_sleep: float = 2.0):
    """Exponential backoff for 429 / userRateLimitExceeded / transient 5xx."""
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            from googleapiclient.errors import HttpError
            transient = False
            if isinstance(exc, HttpError):
                status = getattr(exc.resp, "status", None)
                if status in (429, 500, 502, 503, 504):
                    transient = True
            if not transient or i == attempts - 1:
                last_exc = exc
                break
            time.sleep(base_sleep * (2 ** i))
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Pre-filter
# ---------------------------------------------------------------------------

OOO_RE = re.compile(r"^(out of office|automatic reply|undeliverable)\b", re.IGNORECASE)
NOREPLY_RE = re.compile(r"(noreply|no-reply|no_reply)@", re.IGNORECASE)
BLOCKLIST_DOMAINS = {
    "calendar-notification@google.com",
    "calendar.google.com",
    "bounces.amazonses.com",
    "accounts.google.com",
}


def is_blocklisted_email(addr: str) -> bool:
    addr = (addr or "").lower()
    if NOREPLY_RE.search(addr):
        return True
    for d in BLOCKLIST_DOMAINS:
        if addr.endswith("@" + d) or addr == d:
            return True
    return False


def total_attachment_size(thread_payload: dict) -> int:
    total = 0
    for msg in thread_payload.get("messages", []):
        for part in walk_parts(msg.get("payload", {})):
            sz = (part.get("body") or {}).get("size") or 0
            total += sz
    return total


def has_only_ics_attachments(thread_payload: dict) -> bool:
    has_attach = False
    only_ics = True
    for msg in thread_payload.get("messages", []):
        for part in walk_parts(msg.get("payload", {})):
            if part.get("filename"):
                has_attach = True
                if part.get("mimeType") != "text/calendar" and not part["filename"].lower().endswith(".ics"):
                    only_ics = False
    return has_attach and only_ics


def pre_filter_skip(thread_payload: dict) -> str | None:
    """Return a skip reason or None to keep."""
    if total_attachment_size(thread_payload) > PRE_FILTER_MAX_BYTES:
        return "size>25MB"

    msgs = thread_payload.get("messages", [])
    if not msgs:
        return "empty-thread"

    # Subject of the FIRST message
    first_subj = header_val(msgs[0], "Subject") or ""
    if OOO_RE.match(first_subj):
        return "out-of-office"

    label_set: set[str] = set()
    for m in msgs:
        for lbl in m.get("labelIds") or []:
            label_set.add(lbl)
    if "SPAM" in label_set or "TRASH" in label_set:
        return "labeled-spam-or-trash"

    # All-from-blocklist check (every message's From is blocklisted).
    all_blocked = True
    saw_any = False
    for m in msgs:
        frm = header_val(m, "From") or ""
        _, addr = parseaddr(frm)
        if not addr:
            continue
        saw_any = True
        if not is_blocklisted_email(addr):
            all_blocked = False
            break
    if saw_any and all_blocked:
        return "all-senders-blocklisted"

    if has_only_ics_attachments(thread_payload):
        return "calendar-invite-only"

    return None


# ---------------------------------------------------------------------------
# Thread parsing
# ---------------------------------------------------------------------------

def header_val(message: dict, name: str) -> str | None:
    for h in (message.get("payload") or {}).get("headers", []):
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return None


def walk_parts(payload: dict):
    """Yield every part (recursively) from a Gmail message payload."""
    if not payload:
        return
    yield payload
    for sub in payload.get("parts") or []:
        yield from walk_parts(sub)


def decode_part_body(part: dict) -> str:
    import base64
    body = (part.get("body") or {}).get("data") or ""
    if not body:
        return ""
    pad = "=" * (-len(body) % 4)
    raw = base64.urlsafe_b64decode(body + pad)
    return raw.decode("utf-8", errors="replace")


def extract_message_text(message: dict) -> str:
    """Prefer text/plain; fall back to html2text(text/html)."""
    plain_chunks: list[str] = []
    html_chunks: list[str] = []
    for part in walk_parts(message.get("payload") or {}):
        mime = part.get("mimeType", "")
        if mime == "text/plain":
            plain_chunks.append(decode_part_body(part))
        elif mime == "text/html":
            html_chunks.append(decode_part_body(part))
    if plain_chunks:
        return "\n".join(c for c in plain_chunks if c).strip()
    if html_chunks:
        h2t = html2text.HTML2Text()
        h2t.body_width = 0
        h2t.ignore_links = False
        h2t.ignore_images = True
        return h2t.handle(unescape("\n".join(html_chunks))).strip()
    return ""


QUOTE_LINE_RE = re.compile(r"^\s*>")
ON_WROTE_RE = re.compile(
    r"^\s*On\s+.+?\s+wrote:\s*$"
    r"|^\s*On\s+\w+,\s+\w+\s+\d+,\s+\d{4}\s+at\s+\d+:\d+\s+\w+.*?wrote:\s*$",
    re.MULTILINE,
)
SIGNATURE_DELIM_RE = re.compile(r"^-- ?$", re.MULTILINE)


def strip_quoted_history(body: str) -> str:
    if not body:
        return body
    # Cut at "On <date> ... wrote:" if present.
    m = ON_WROTE_RE.search(body)
    if m:
        body = body[: m.start()].rstrip()
    # Drop trailing blocks of '> ' lines.
    lines = body.splitlines()
    while lines and QUOTE_LINE_RE.match(lines[-1]):
        lines.pop()
    body = "\n".join(lines).rstrip()
    return body


def strip_signature(body: str) -> str:
    if not body:
        return body
    m = SIGNATURE_DELIM_RE.search(body)
    if m:
        return body[: m.start()].rstrip()
    return body


def parse_participants(thread_payload: dict, account: str) -> list[dict]:
    """Aggregate participants across the thread with role tags."""
    seen: dict[str, dict] = {}
    for msg in thread_payload.get("messages", []):
        for role_header, role_tag in (("From", "from"), ("To", "to"), ("Cc", "cc")):
            raw = header_val(msg, role_header) or ""
            for part in raw.split(","):
                name, addr = parseaddr(part.strip())
                if not addr:
                    continue
                key = addr.lower()
                ent = seen.setdefault(key, {"name": name or "", "email": addr, "roles": []})
                if role_tag not in ent["roles"]:
                    ent["roles"].append(role_tag)
                if not ent["name"] and name:
                    ent["name"] = name
    return list(seen.values())


def parse_attachments(thread_payload: dict) -> list[dict]:
    out: list[dict] = []
    for msg in thread_payload.get("messages", []):
        for part in walk_parts(msg.get("payload") or {}):
            fn = part.get("filename") or ""
            if not fn:
                continue
            body = part.get("body") or {}
            out.append({
                "id": body.get("attachmentId", "")[:8] or "",
                "filename": fn,
                "size_bytes": body.get("size") or 0,
                "mime": part.get("mimeType", ""),
            })
    return out


def thread_dates(thread_payload: dict) -> tuple[datetime | None, datetime | None]:
    msgs = thread_payload.get("messages", [])
    if not msgs:
        return None, None
    def dt(msg) -> datetime | None:
        ts = msg.get("internalDate")
        if ts:
            try:
                return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            except Exception:
                pass
        d = header_val(msg, "Date")
        if d:
            try:
                return parsedate_to_datetime(d)
            except Exception:
                return None
        return None
    dates = [d for d in (dt(m) for m in msgs) if d is not None]
    if not dates:
        return None, None
    return min(dates), max(dates)


# ---------------------------------------------------------------------------
# Slug + path
# ---------------------------------------------------------------------------

SUBJECT_PREFIX_RE = re.compile(
    r"^(?:re|fwd?|fw|aw)\s*:\s*|^\[(?:external|confidential)\]\s*|^auto\s*:\s*",
    re.IGNORECASE,
)


def subject_slug(subject: str) -> str:
    s = subject or ""
    while True:
        m = SUBJECT_PREFIX_RE.match(s)
        if not m:
            break
        s = s[m.end():].strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip()).strip("-").lower()
    return (s[:SUBJECT_SLUG_MAX].rstrip("-")) or "no-subject"


def relative_thread_path(account: str, first_dt: datetime, subj_slug: str, thread_id: str) -> Path:
    return Path(
        "raw/gmail",
        account_slug(account),
        f"{first_dt.year:04d}",
        f"{first_dt.month:02d}",
        f"{first_dt.strftime('%Y-%m-%d')}__{subj_slug}__{thread_id[:THREAD_ID_PREFIX_LEN]}.md",
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_thread_markdown(thread_payload: dict, account: str) -> tuple[str, str]:
    """Returns (body_markdown, subject)."""
    msgs = thread_payload.get("messages", [])
    if not msgs:
        return "", ""
    subject = header_val(msgs[0], "Subject") or "(no subject)"
    out_lines: list[str] = [f"# {subject}", ""]
    for msg in msgs:
        from_raw = header_val(msg, "From") or ""
        name, addr = parseaddr(from_raw)
        date_hdr = header_val(msg, "Date") or ""
        try:
            dt = parsedate_to_datetime(date_hdr)
            if dt is not None:
                date_disp = dt.astimezone().strftime("%Y-%m-%d %H:%M")
            else:
                date_disp = date_hdr
        except Exception:
            date_disp = date_hdr

        body = extract_message_text(msg)
        body = strip_quoted_history(body)
        body = strip_signature(body)
        body = body.strip()

        attachments = []
        for part in walk_parts(msg.get("payload") or {}):
            fn = part.get("filename") or ""
            if fn:
                sz = (part.get("body") or {}).get("size") or 0
                attachments.append((fn, sz))

        header_line = f"## {date_disp} — {name or addr or 'unknown'}"
        if addr:
            header_line += f" <{addr}>"
        out_lines.append(header_line)
        out_lines.append("")
        if body:
            out_lines.append(body)
            out_lines.append("")
        if attachments:
            out_lines.append(
                "**Attachments:** "
                + ", ".join(f"{fn} ({sz} bytes)" for fn, sz in attachments)
            )
            out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n", subject


# ---------------------------------------------------------------------------
# Frontmatter envelope
# ---------------------------------------------------------------------------

def build_frontmatter(*, workspace: str, account: str, thread_payload: dict,
                      thread_id: str, body_markdown: str, ingested_at: datetime) -> str:
    msgs = thread_payload.get("messages", [])
    subject = (header_val(msgs[0], "Subject") if msgs else "") or "(no subject)"
    first_dt, last_dt = thread_dates(thread_payload)
    participants = parse_participants(thread_payload, account)
    labels: list[str] = []
    seen_labels: set[str] = set()
    for m in msgs:
        for lbl in m.get("labelIds") or []:
            if lbl not in seen_labels:
                seen_labels.add(lbl)
                labels.append(lbl)
    msg_ids = [header_val(m, "Message-ID") or "" for m in msgs]
    msg_ids = [m for m in msg_ids if m]

    h = blake3.blake3(body_markdown.encode("utf-8")).hexdigest()

    fm = {
        "source": "gmail",
        "workspace": workspace,
        "ingested_at": ingested_at.replace(microsecond=0).isoformat(),
        "ingest_version": INGEST_VERSION,
        "content_hash": f"blake3:{h}",
        "provider_modified_at": (last_dt.replace(microsecond=0).isoformat()
                                 if last_dt else ingested_at.replace(microsecond=0).isoformat()),
        "account": account,
        "thread_id": thread_id,
        "message_ids": msg_ids,
        "subject": subject,
        "participants": participants,
        "labels": labels,
        "first_message": (first_dt.replace(microsecond=0).isoformat()
                          if first_dt else None),
        "last_message": (last_dt.replace(microsecond=0).isoformat()
                         if last_dt else None),
        "message_count": len(msgs),
        "attachments": parse_attachments(thread_payload),
    }
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---\n"


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------

def ledger_path(workspace: str) -> Path:
    return ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"


def ledger_has(workspace: str, key: str, content_hash: str) -> bool:
    """Return True if a row with the same key + hash already exists."""
    p = ledger_path(workspace)
    if not p.exists():
        return False
    needle_key = f'"key":"{key}"'
    needle_hash = f'"content_hash":"{content_hash}"'
    try:
        with p.open() as f:
            for line in f:
                if needle_key in line and needle_hash in line:
                    return True
    except OSError:
        pass
    return False


def ledger_append(workspace: str, record: dict) -> None:
    p = ledger_path(workspace)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Cursor
# ---------------------------------------------------------------------------

def read_cursor(account: str) -> int | None:
    """Cursor stores the latest internalDate (epoch seconds) we've seen.

    Returns None if missing/empty. Raises ValueError on garbage so the user
    knows to delete it.
    """
    p = cursor_path_for(account)
    if not p.exists():
        return None
    raw = p.read_text().strip()
    if not raw:
        return None
    try:
        ts = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"ingest-gmail: cursor at {p.relative_to(ULTRON_ROOT)} is corrupt "
            f"(value={raw!r}). Delete it and re-run; ingest will fall back to the "
            f"workspace lookback_days_initial."
        ) from exc
    if ts < 0:
        raise ValueError(f"cursor {p} has negative value {ts!r}")
    return ts


def write_cursor(account: str, epoch_seconds: int) -> None:
    p = cursor_path_for(account)
    p.write_text(str(epoch_seconds) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--account", required=True, help="Gmail address, e.g. adithya@outerscope.xyz")
    ap.add_argument("--run-id", default=datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
    ap.add_argument("--dry-run", action="store_true", help="Fetch + render but write nothing to disk; do not advance cursor.")
    ap.add_argument("--show", action="store_true", help="(dry-run only) print the rendered frontmatter + body to stdout for inspection.")
    ap.add_argument("--max-items", type=int, default=None, help="Hard cap on threads processed this run.")
    args = ap.parse_args()

    account: str = args.account.strip()
    if "@" not in account:
        sys.stderr.write(f"ingest-gmail: --account must be an email; got {account!r}\n")
        return 2

    # 1. Cursor
    try:
        cursor_ts = read_cursor(account)
    except ValueError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2

    workspaces_config = load_all_workspaces_config()
    if not workspaces_config:
        sys.stderr.write("ingest-gmail: no workspaces with sources.yaml found\n")
        return 0

    includes, excludes, lookback_days = collect_account_rules(account, workspaces_config)
    if not includes and not excludes:
        sys.stderr.write(f"ingest-gmail: no workspace subscribes to {account}; nothing to do\n")
        return 0

    # First-run window
    if cursor_ts is None:
        after_dt = datetime.now(tz=timezone.utc) - timedelta(days=lookback_days)
        after_ts = int(after_dt.timestamp())
        sys.stderr.write(
            f"ingest-gmail: first run for {account}; using lookback_days_initial={lookback_days} "
            f"(after={after_dt.isoformat()})\n"
        )
    else:
        after_ts = cursor_ts
        sys.stderr.write(
            f"ingest-gmail: incremental run for {account}; cursor "
            f"after_ts={cursor_ts} ({datetime.fromtimestamp(cursor_ts, tz=timezone.utc).isoformat()})\n"
        )

    q = build_q(includes, excludes, after_ts)
    sys.stderr.write(f"ingest-gmail: q={q!r}\n")

    svc = build_service(account)

    # 2. Paginate users.threads.list
    page_token: str | None = None
    page_size = 100
    threads_seen: list[dict] = []
    cap = args.max_items if args.max_items else float("inf")
    while True:
        kwargs = {"userId": "me", "q": q, "maxResults": page_size}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = _retry(lambda: svc.users().threads().list(**kwargs).execute())
        for t in resp.get("threads", []) or []:
            threads_seen.append(t)
            if len(threads_seen) >= cap:
                break
        if len(threads_seen) >= cap:
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    sys.stderr.write(f"ingest-gmail: matched {len(threads_seen)} thread(s) (cap={args.max_items or 'none'})\n")

    written_per_ws: dict[str, int] = {}
    skipped_count = 0
    error_count = 0
    latest_internal_ms: int | None = cursor_ts * 1000 if cursor_ts else None
    ingested_at = datetime.now(timezone.utc)

    for tref in threads_seen:
        tid = tref.get("id")
        if not tid:
            continue
        try:
            thread_payload = _retry(lambda: svc.users().threads().get(
                userId="me", id=tid, format="full"
            ).execute())
        except Exception as exc:
            error_count += 1
            with errors_log_path().open("a") as f:
                f.write(f"{datetime.now(timezone.utc).isoformat()} thread.get tid={tid} {type(exc).__name__}: {exc}\n")
            continue

        skip_reason = pre_filter_skip(thread_payload)
        if skip_reason:
            skipped_count += 1
            sys.stderr.write(f"  skip tid={tid[:8]} reason={skip_reason}\n")
            continue

        # Build a thread payload for route.py
        msgs = thread_payload.get("messages", [])
        subject = (header_val(msgs[0], "Subject") if msgs else "") or ""
        labels: list[str] = []
        seen: set[str] = set()
        for m in msgs:
            for lbl in m.get("labelIds") or []:
                if lbl not in seen:
                    seen.add(lbl); labels.append(lbl)
        participants = parse_participants(thread_payload, account)
        thread_for_route = {
            "account": account,
            "subject": subject,
            "labels": labels,
            "participants": participants,
        }
        destinations = route_thread(thread_for_route, workspaces_config)
        if not destinations:
            sys.stderr.write(f"  skip tid={tid[:8]} reason=no-route\n")
            skipped_count += 1
            continue

        # Render once, write per destination.
        first_dt, last_dt = thread_dates(thread_payload)
        if first_dt is None:
            first_dt = ingested_at
        body_md, _ = render_thread_markdown(thread_payload, account)
        # Track latest internalDate for cursor advancement.
        for m in msgs:
            ts = m.get("internalDate")
            if ts:
                try:
                    ts_int = int(ts)
                    if latest_internal_ms is None or ts_int > latest_internal_ms:
                        latest_internal_ms = ts_int
                except ValueError:
                    pass

        for ws in destinations:
            fm = build_frontmatter(
                workspace=ws,
                account=account,
                thread_payload=thread_payload,
                thread_id=tid,
                body_markdown=body_md,
                ingested_at=ingested_at,
            )
            content = fm + body_md
            content_hash_match = re.search(r'content_hash:\s*(\S+)', fm)
            content_hash = content_hash_match.group(1) if content_hash_match else ""

            # Skip if ledger already records this exact hash.
            ledger_key = f"gmail:{tid}"
            already = ledger_has(ws, ledger_key, content_hash)

            rel = relative_thread_path(account, first_dt, subject_slug(subject), tid)
            full_path = ULTRON_ROOT / "workspaces" / ws / rel

            if args.dry_run:
                sys.stderr.write(
                    f"  DRY ws={ws} tid={tid[:8]} -> {rel} "
                    f"(hash={content_hash[:24]}{'…' if len(content_hash) > 24 else ''}, "
                    f"already_in_ledger={already})\n"
                )
                # In dry-run, print full content to stdout so the operator can
                # inspect what WOULD be written.
                if args.show:
                    print(f"\n========== DRY-RUN ws={ws} path={rel} ==========")
                    print(content)
                    print("========== END DRY-RUN ==========\n")
                written_per_ws[ws] = written_per_ws.get(ws, 0) + 1
                continue

            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

            if not already:
                ledger_append(ws, {
                    "source": "gmail",
                    "key": ledger_key,
                    "content_hash": content_hash,
                    "raw_path": str(rel),
                    "ingested_at": ingested_at.isoformat(),
                    "run_id": args.run_id,
                })
            written_per_ws[ws] = written_per_ws.get(ws, 0) + 1

    # 3. Cursor + log summary
    if not args.dry_run and latest_internal_ms is not None:
        new_cursor = latest_internal_ms // 1000
        if cursor_ts is None or new_cursor > cursor_ts:
            write_cursor(account, new_cursor)

    if not args.dry_run:
        for ws, count in sorted(written_per_ws.items()):
            log_path = ULTRON_ROOT / "workspaces" / ws / "_meta" / "log.md"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a") as f:
                f.write(
                    f"- {ingested_at.replace(microsecond=0).isoformat()} "
                    f"gmail/{account_slug(account)} "
                    f"+{count} thread(s) "
                    f"(skipped={skipped_count}, errors={error_count}, "
                    f"run_id={args.run_id})\n"
                )

    sys.stderr.write(
        f"ingest-gmail: done. "
        f"matched={len(threads_seen)} skipped={skipped_count} errors={error_count} "
        f"written={dict(written_per_ws)} dry_run={args.dry_run}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
