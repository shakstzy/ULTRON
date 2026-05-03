#!/usr/bin/env python3
"""
ingest-gmail.py — per-account Gmail ingest robot.

Authoritative spec: _shell/stages/ingest/gmail/format.md
Workflow contract:  _shell/stages/ingest/gmail/CONTEXT.md

Usage:
    ingest-gmail.py --account <email> [--workspaces a,b,c] [--dry-run]
                    [--show] [--max-items N] [--reset-cursor] [--run-id ID]

One run = one upstream account. flock-locked at
/tmp/com.adithya.ultron.ingest-gmail-<account-slug>.lock. Cursor stores the
last-seen Gmail historyId. First run uses messages.list(q=) bounded by
GMAIL_INITIAL_LOOKBACK_DAYS; subsequent runs use history.list.
"""
from __future__ import annotations

import argparse
import base64
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
INGEST_VERSION = 1
GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT = 365
PRE_FILTER_MAX_BYTES = 25 * 1024 * 1024
PDF_EXTRACT_MAX_BYTES = 10 * 1024 * 1024
SUBJECT_SLUG_MAX = 60
THREAD_ID_PREFIX_LEN = 8

# Lock 5 MIME allowlist.
ALLOWED_MIME_PREFIXES = (
    "text/plain",
    "text/html",
    "application/pdf",
    "image/",
    "multipart/",
)

# Allow `from route import route` even though _shell isn't a Python package.
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
    """`adithya@outerscope.xyz` -> `adithya-outerscope`. Lock 1."""
    local, _, domain = email.lower().strip().partition("@")
    stem = domain.split(".", 1)[0] if domain else ""
    s = f"{local}-{stem}" if stem else local
    return re.sub(r"[^a-z0-9-]+", "-", s).strip("-") or "unknown"


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


def run_log_path(account: str, run_id: str) -> Path:
    p = ULTRON_ROOT / "_logs" / f"gmail-{account_slug(account)}-{run_id}.log"
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


def collect_account_rules(account: str, workspaces_config: dict[str, dict]) -> tuple[list[str], list[str], int, bool, bool]:
    """Per-account discovery across all subscribing workspaces.
    Returns (includes, excludes, lookback_days_initial, any_match_all, any_subscription).

    `includes` / `excludes` are unioned for diagnostic / back-compat use, BUT
    build_q() must NOT apply unioned `excludes` directly — workspace-specific
    excludes belong in route.py (post-fetch). Cross-workspace exclude bleed
    was an active bug: personal's `-label:Eclipse` exclude was filtering out
    threads that eclipse explicitly included.

    `any_match_all` = at least one subscribing workspace declared no include
    rules (= match-all). build_q must omit the OR clause in that case.
    `any_subscription` = at least one workspace has a gmail account block
    matching this account. Used by main() to decide early-exit.
    """
    includes: list[str] = []
    excludes: list[str] = []
    lookback_seen: int | None = None
    any_match_all = False
    any_subscription = False

    def _record(inc, exc):
        nonlocal any_match_all
        inc = inc or []
        exc = exc or []
        if not inc:
            any_match_all = True
        includes.extend(inc)
        excludes.extend(exc)

    for ws, cfg in workspaces_config.items():
        sources = cfg.get("sources")

        # Preferred shape: sources.gmail.accounts: [{account, api_query}]
        if isinstance(sources, dict):
            block = sources.get("gmail")
            if not block:
                continue
            accounts = block.get("accounts") if isinstance(block, dict) else None
            if isinstance(accounts, list):
                for acct in accounts:
                    if isinstance(acct, str):
                        if acct == account:
                            any_subscription = True
                            api = (block.get("api_query") or {})
                            _record(api.get("include"), api.get("exclude"))
                    elif isinstance(acct, dict):
                        if (acct.get("account") or "") == account:
                            any_subscription = True
                            api = acct.get("api_query") or {}
                            _record(api.get("include"), api.get("exclude"))
                            li = acct.get("lookback_days_initial")
                            if isinstance(li, int):
                                lookback_seen = li if lookback_seen is None else max(lookback_seen, li)
            else:
                api = (block.get("api_query") or {}) if isinstance(block, dict) else {}
                if api.get("include") or api.get("exclude"):
                    any_subscription = True
                    _record(api.get("include"), api.get("exclude"))
            continue

        # Legacy shape: sources: [{type: gmail, config: {...}}]
        if isinstance(sources, list):
            for s in sources:
                if not isinstance(s, dict) or s.get("type") != "gmail":
                    continue
                conf = s.get("config") or {}
                if (conf.get("account") or "") != account:
                    continue
                any_subscription = True
                inc = [f"label:{lbl}" for lbl in (conf.get("labels") or [])]
                exc = [f"label:{lbl}" for lbl in (conf.get("exclude_labels") or [])]
                _record(inc, exc)
                li = conf.get("lookback_days_initial")
                if isinstance(li, int):
                    lookback_seen = li if lookback_seen is None else max(lookback_seen, li)

    lookback = lookback_seen if lookback_seen is not None else GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT
    return includes, excludes, lookback, any_match_all, any_subscription


# ---------------------------------------------------------------------------
# Predicate -> Gmail q= translation (best-effort superset; route.py applies
# the precise rules post-fetch)
# ---------------------------------------------------------------------------

def _predicate_to_q(p: str) -> str | None:
    p = p.strip()
    if not p:
        return None
    if p.startswith("label:"):
        return f"label:{p.split(':', 1)[1].strip()}"
    if p.startswith(("from:", "to:", "cc:")):
        role, pat = p.split(":", 1)
        # Strip wildcard noise. Gmail q= treats * literally.
        # `from:*@eclipse.audio` -> `from:eclipse.audio`
        # `from:noreply@*`       -> `from:noreply`
        # `from:*@*`             -> drop
        pat = pat.strip().replace("*", "").strip("@")
        if not pat or pat.count("*") > 0:
            return None
        return f"{role}:{pat}"
    if p.lower().startswith("subject:contains:"):
        val = p.split(":", 2)[2].strip()
        return f'subject:"{val}"' if val else None
    return None


def build_q(includes: list[str], after_ts: int | None, *, any_match_all: bool = False) -> str:
    """Build the first-run Gmail q= query.

    Excludes are deliberately NOT applied here. They are workspace-specific
    and applied accurately by route.py post-fetch. Unioning excludes across
    workspaces (the previous behaviour) caused cross-workspace bleed: e.g.
    personal's `-label:Eclipse` filtered out threads that eclipse explicitly
    included. Cost of fetching some threads we'll later route-skip is small;
    cost of silently losing mail is large.

    `any_match_all=True` => at least one workspace wants every thread for this
    account => omit the OR-include clause entirely (true match-all). The
    universal pre-filter (Lock 5) and route.py still run.
    """
    def _dedup(seq):
        seen, out = set(), []
        for x in seq:
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    parts: list[str] = []
    if not any_match_all:
        inc_q = _dedup(t for t in (_predicate_to_q(p) for p in includes) if t)
        if inc_q:
            parts.append("(" + " OR ".join(inc_q) + ")")
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
            f"  Recovery: see _credentials/INVENTORY.md."
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
            f"  Likely: refresh_token revoked or expired.\n"
            f"  Recovery: re-mint via gog (`gog auth login -a {account}`),\n"
            f"            update {cred_path.relative_to(ULTRON_ROOT)} with the new\n"
            f"            refresh_token, then re-run."
        )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _retry(fn, *, attempts: int = 3, base_sleep: float = 2.0):
    last_exc: Exception | None = None
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
# Pre-filter (Lock 5)
# ---------------------------------------------------------------------------

OOO_RE = re.compile(
    r"^(out of office|automatic reply|undeliverable|delivery (status )?notification)",
    re.IGNORECASE,
)
NOREPLY_RE = re.compile(
    r"(?:noreply|no-reply|no_reply|donotreply|do-not-reply|mailer-daemon|postmaster)@",
    re.IGNORECASE,
)
BLOCKLIST_EXACT = {
    "calendar-notification@google.com",
}
BLOCKLIST_DOMAINS = {
    "calendar.google.com",
    "bounces.amazonses.com",
    "accounts.google.com",
}


def is_blocklisted_email(addr: str) -> bool:
    addr = (addr or "").lower().strip()
    if not addr:
        return False
    if addr in BLOCKLIST_EXACT:
        return True
    if NOREPLY_RE.search(addr):
        return True
    for d in BLOCKLIST_DOMAINS:
        if addr.endswith("@" + d):
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


def all_attachments_outside_allowlist(thread_payload: dict) -> bool:
    """True iff thread has at least one attachment AND every attachment's
    MIME is outside the allowlist."""
    saw = False
    for msg in thread_payload.get("messages", []):
        for part in walk_parts(msg.get("payload") or {}):
            if not part.get("filename"):
                continue
            saw = True
            mime = (part.get("mimeType") or "").lower()
            allowed = any(
                mime == prefix or (prefix.endswith("/") and mime.startswith(prefix))
                for prefix in ALLOWED_MIME_PREFIXES
            )
            if allowed:
                return False
    return saw


def pre_filter_skip(thread_payload: dict) -> str | None:
    """Return a skip reason string, or None to keep."""
    if total_attachment_size(thread_payload) > PRE_FILTER_MAX_BYTES:
        return "size>25MB"

    msgs = thread_payload.get("messages", [])
    if not msgs:
        return "empty-thread"

    first_subj = header_val(msgs[0], "Subject") or ""
    if OOO_RE.match(first_subj):
        return "out-of-office"

    label_set: set[str] = set()
    for m in msgs:
        for lbl in m.get("labelIds") or []:
            label_set.add(lbl)
    if label_set and label_set.issubset({"SPAM", "TRASH"}):
        return "labels-all-spam-or-trash"

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

    if all_attachments_outside_allowlist(thread_payload):
        return "all-attachments-outside-mime-allowlist"

    return None


# ---------------------------------------------------------------------------
# Thread parsing helpers
# ---------------------------------------------------------------------------

def header_val(message: dict, name: str) -> str | None:
    for h in (message.get("payload") or {}).get("headers", []):
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return None


def walk_parts(payload: dict):
    if not payload:
        return
    yield payload
    for sub in payload.get("parts") or []:
        yield from walk_parts(sub)


def decode_part_body(part: dict) -> str:
    body = (part.get("body") or {}).get("data") or ""
    if not body:
        return ""
    pad = "=" * (-len(body) % 4)
    raw = base64.urlsafe_b64decode(body + pad)
    return raw.decode("utf-8", errors="replace")


def extract_message_text(message: dict) -> str:
    """Prefer text/plain; fall back to html2text(text/html). Skip parts that are
    file attachments (they're rendered separately as ### Attachment blocks)."""
    plain_chunks: list[str] = []
    html_chunks: list[str] = []
    for part in walk_parts(message.get("payload") or {}):
        if part.get("filename"):
            continue
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
        return h2t.handle("\n".join(html_chunks)).strip()
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
    m = ON_WROTE_RE.search(body)
    if m:
        body = body[: m.start()].rstrip()
    lines = body.splitlines()
    while lines and QUOTE_LINE_RE.match(lines[-1]):
        lines.pop()
    return "\n".join(lines).rstrip()


def strip_signature(body: str) -> str:
    """Cut at first canonical RFC 3676 '-- ' delimiter. NO heuristic stripping."""
    if not body:
        return body
    m = SIGNATURE_DELIM_RE.search(body)
    if m:
        return body[: m.start()].rstrip()
    return body


def parse_participants(thread_payload: dict, account: str) -> list[dict]:
    """Aggregate participants across the thread with role tags. Lock 3."""
    seen: dict[str, dict] = {}
    for msg in thread_payload.get("messages", []):
        for role_header, role_tag in (("From", "from"), ("To", "to"), ("Cc", "cc"), ("Bcc", "bcc")):
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
    """Lock 3. Includes message_index for each attachment."""
    out: list[dict] = []
    for idx, msg in enumerate(thread_payload.get("messages", [])):
        for part in walk_parts(msg.get("payload") or {}):
            fn = part.get("filename") or ""
            if not fn:
                continue
            body = part.get("body") or {}
            out.append({
                "id": (body.get("attachmentId") or "")[:8] or "",
                "filename": fn,
                "size_bytes": body.get("size") or 0,
                "mime": part.get("mimeType", ""),
                "message_index": idx,
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
# Slug + path (Lock 1)
# ---------------------------------------------------------------------------

SUBJECT_PREFIX_RE = re.compile(
    r"^(?:re|fwd?|fw|aw|res|tr)\s*:\s*"
    r"|^\[(?:external|ext|confidential|spam)\]\s*"
    r"|^auto\s*:\s*",
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
# PDF text extraction (Lock 4 rule 6) — pdftotext preferred, markitdown fallback
# ---------------------------------------------------------------------------

def extract_pdf_text(pdf_bytes: bytes) -> str | None:
    """Try pdftotext, then markitdown. Return None on any failure. No LLM."""
    if not pdf_bytes:
        return None
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        tmp_path = f.name
    try:
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", tmp_path, "-"],
                capture_output=True, timeout=30, text=True, check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        try:
            result = subprocess.run(
                ["markitdown", tmp_path],
                capture_output=True, timeout=60, text=True, check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return None


def fetch_attachment_bytes(svc, message_id: str, attachment_id: str) -> bytes | None:
    if not attachment_id or not message_id:
        return None
    try:
        resp = _retry(lambda: svc.users().messages().attachments().get(
            userId="me", messageId=message_id, id=attachment_id
        ).execute())
    except Exception:
        return None
    data = resp.get("data") or ""
    if not data:
        return None
    try:
        pad = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + pad)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Markdown rendering (Lock 4)
# ---------------------------------------------------------------------------

def render_thread_markdown(thread_payload: dict, account: str, svc=None) -> tuple[str, str]:
    """Render thread to markdown body + return subject. svc=None disables PDF
    extraction (used for dry-run inspection)."""
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
            date_disp = dt.astimezone().strftime("%Y-%m-%d %H:%M %Z") if dt else date_hdr
        except Exception:
            date_disp = date_hdr

        body = extract_message_text(msg)
        body = strip_quoted_history(body)
        body = strip_signature(body)
        body = body.strip()

        header_line = f"## {date_disp} — {name or addr or 'unknown'}"
        if addr:
            header_line += f" <{addr}>"
        out_lines.append(header_line)
        out_lines.append("")
        if body:
            out_lines.append(body)
            out_lines.append("")

        # Lock 4 rules 6 + 7: ### Attachment per file.
        for part in walk_parts(msg.get("payload") or {}):
            fn = part.get("filename") or ""
            if not fn:
                continue
            mime = (part.get("mimeType") or "").lower()
            sz = (part.get("body") or {}).get("size") or 0
            att_id = (part.get("body") or {}).get("attachmentId")
            inline_data = (part.get("body") or {}).get("data")

            extracted: str | None = None
            if mime == "application/pdf" and sz <= PDF_EXTRACT_MAX_BYTES and svc is not None:
                pdf_bytes: bytes | None = None
                if inline_data:
                    try:
                        pad = "=" * (-len(inline_data) % 4)
                        pdf_bytes = base64.urlsafe_b64decode(inline_data + pad)
                    except Exception:
                        pdf_bytes = None
                if pdf_bytes is None and att_id:
                    pdf_bytes = fetch_attachment_bytes(svc, msg.get("id", ""), att_id)
                if pdf_bytes:
                    extracted = extract_pdf_text(pdf_bytes)

            out_lines.append(f"### Attachment: {fn}")
            out_lines.append(extracted if extracted else "Binary attachment, content not extracted.")
            out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n", subject


# ---------------------------------------------------------------------------
# Frontmatter (Locks 2 + 3)
# ---------------------------------------------------------------------------

def build_frontmatter(*, workspace: str, account: str, thread_payload: dict,
                      thread_id: str, body_markdown: str, ingested_at: datetime,
                      routed_by: list[dict],
                      deleted_upstream: str | None = None) -> str:
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
        "account_slug": account_slug(account),
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
        "routed_by": list(routed_by),
        "deleted_upstream": deleted_upstream,
    }
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---\n"


# ---------------------------------------------------------------------------
# Ledger (Lock 6)
# ---------------------------------------------------------------------------

def ledger_path(workspace: str) -> Path:
    return ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"


def ledger_has(workspace: str, key: str, content_hash: str) -> bool:
    p = ledger_path(workspace)
    if not p.exists():
        return False
    try:
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("key") == key and rec.get("content_hash") == content_hash:
                    return True
    except OSError:
        pass
    return False


def ledger_append(workspace: str, record: dict) -> None:
    p = ledger_path(workspace)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------
# Cursor (Lock 7) — stores Gmail historyId as decimal text
# ---------------------------------------------------------------------------

def read_cursor(account: str) -> str | None:
    p = cursor_path_for(account)
    if not p.exists():
        return None
    raw = p.read_text().strip()
    if not raw:
        return None
    try:
        int(raw)  # validate
    except ValueError as exc:
        raise ValueError(
            f"ingest-gmail: cursor at {p.relative_to(ULTRON_ROOT)} is corrupt "
            f"(value={raw!r}). Delete it and re-run; ingest will fall back to the "
            f"GMAIL_INITIAL_LOOKBACK_DAYS lookback window."
        ) from exc
    return raw


def write_cursor(account: str, history_id: str) -> None:
    p = cursor_path_for(account)
    p.write_text(str(history_id) + "\n")


def reset_cursor(account: str) -> None:
    p = cursor_path_for(account)
    if p.exists():
        p.unlink()


# ---------------------------------------------------------------------------
# Thread-id collection (first run + incremental)
# ---------------------------------------------------------------------------

def collect_threads_first_run(svc, q: str, max_items: int | None) -> set[str]:
    """messages.list(q=) → dedupe to threadIds. Lock 7."""
    page_token: str | None = None
    thread_ids: set[str] = set()
    cap: float = max_items if max_items else float("inf")

    while True:
        kwargs = {"userId": "me", "q": q, "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = _retry(lambda: svc.users().messages().list(**kwargs).execute())
        for m in resp.get("messages", []) or []:
            tid = m.get("threadId")
            if tid:
                thread_ids.add(tid)
            if len(thread_ids) >= cap:
                break
        if len(thread_ids) >= cap:
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return thread_ids


def collect_history_events(svc, start_history_id: str, max_items: int | None) -> tuple[set[str], set[str], set[str]]:
    """history.list → (added_thread_ids, deleted_thread_ids,
    label_changed_thread_ids). Lock 7."""
    added: set[str] = set()
    deleted: set[str] = set()
    labelled: set[str] = set()
    page_token: str | None = None
    cap: float = max_items if max_items else float("inf")

    while True:
        kwargs = {
            "userId": "me",
            "startHistoryId": start_history_id,
            "historyTypes": ["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"],
            "maxResults": 500,
        }
        if page_token:
            kwargs["pageToken"] = page_token

        try:
            resp = _retry(lambda: svc.users().history().list(**kwargs).execute())
        except Exception as exc:
            from googleapiclient.errors import HttpError
            if isinstance(exc, HttpError) and getattr(exc.resp, "status", None) == 404:
                sys.stderr.write(
                    "ingest-gmail: history.list returned 404 (cursor too old). "
                    "Re-run with --reset-cursor to backfill from the lookback window.\n"
                )
                raise SystemExit(3)
            raise

        for h in resp.get("history", []) or []:
            for evt in h.get("messagesAdded") or []:
                m = evt.get("message") or {}
                tid = m.get("threadId")
                if tid:
                    added.add(tid)
            for evt in h.get("messagesDeleted") or []:
                m = evt.get("message") or {}
                tid = m.get("threadId")
                if tid:
                    deleted.add(tid)
            for evt in h.get("labelsAdded") or []:
                m = evt.get("message") or {}
                tid = m.get("threadId")
                if tid:
                    labelled.add(tid)
            for evt in h.get("labelsRemoved") or []:
                m = evt.get("message") or {}
                tid = m.get("threadId")
                if tid:
                    labelled.add(tid)

        if (len(added) + len(deleted) + len(labelled)) >= cap:
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    # If a thread is in `added`, drop it from `labelled` (will be processed
    # via the normal pipeline anyway).
    labelled -= added
    return added, deleted, labelled


# ---------------------------------------------------------------------------
# Per-thread processing
# ---------------------------------------------------------------------------

def find_existing_raw_files(thread_id: str, account: str, workspaces_config: dict) -> list[tuple[str, Path]]:
    """Locate existing raw/gmail files for this thread, across workspaces."""
    out: list[tuple[str, Path]] = []
    suffix = f"__{thread_id[:THREAD_ID_PREFIX_LEN]}.md"
    for ws in workspaces_config:
        base = ULTRON_ROOT / "workspaces" / ws / "raw" / "gmail" / account_slug(account)
        if not base.exists():
            continue
        for p in base.rglob(f"*{suffix}"):
            out.append((ws, p))
    return out


def mark_deleted_upstream(thread_id: str, account: str, workspaces_config: dict, when: datetime) -> int:
    """Set deleted_upstream in frontmatter for every raw copy of this thread.
    Returns count of files updated. Lock 7 + Forbidden #1."""
    updated = 0
    iso = when.replace(microsecond=0).isoformat()
    for ws, path in find_existing_raw_files(thread_id, account, workspaces_config):
        try:
            text = path.read_text()
        except OSError:
            continue
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            continue
        try:
            fm = yaml.safe_load(text[4:end]) or {}
        except yaml.YAMLError:
            continue
        if fm.get("deleted_upstream"):
            continue
        fm["deleted_upstream"] = iso
        body = text[end + len("\n---\n"):]
        new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
        path.write_text(f"---\n{new_fm}---\n{body}")
        updated += 1
    return updated


def process_thread(svc, tid: str, account: str, workspaces_config: dict,
                   ingested_at: datetime, args, run_log) -> dict[str, int]:
    """Fetch, pre-filter, render, route, write. Returns per-workspace write counts."""
    written: dict[str, int] = {}

    try:
        thread_payload = _retry(lambda: svc.users().threads().get(
            userId="me", id=tid, format="full"
        ).execute())
    except Exception as exc:
        with errors_log_path().open("a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} thread.get tid={tid} {type(exc).__name__}: {exc}\n")
        run_log.write(f"  ERROR tid={tid[:8]} {type(exc).__name__}: {exc}\n")
        return written

    skip_reason = pre_filter_skip(thread_payload)
    if skip_reason:
        run_log.write(f"  skip tid={tid[:8]} reason={skip_reason}\n")
        return written

    msgs = thread_payload.get("messages", [])
    subject = (header_val(msgs[0], "Subject") if msgs else "") or ""
    labels: list[str] = []
    seen: set[str] = set()
    for m in msgs:
        for lbl in m.get("labelIds") or []:
            if lbl not in seen:
                seen.add(lbl)
                labels.append(lbl)
    participants = parse_participants(thread_payload, account)
    thread_for_route = {
        "account": account,
        "subject": subject,
        "labels": labels,
        "participants": participants,
    }
    destinations = route_thread(thread_for_route, workspaces_config)
    if not destinations:
        run_log.write(f"  skip tid={tid[:8]} reason=no-route\n")
        return written

    # Filter destinations by --workspaces if set.
    if args.workspaces:
        wanted = {w.strip() for w in args.workspaces.split(",") if w.strip()}
        destinations = [d for d in destinations if d.get("workspace") in wanted]
        if not destinations:
            run_log.write(f"  skip tid={tid[:8]} reason=workspaces-filter\n")
            return written

    first_dt, _ = thread_dates(thread_payload)
    if first_dt is None:
        first_dt = ingested_at
    body_md, _ = render_thread_markdown(thread_payload, account, svc=None if args.dry_run else svc)

    routed_by_list = list(destinations)

    for d in destinations:
        ws = d.get("workspace")
        if not ws:
            continue
        fm = build_frontmatter(
            workspace=ws,
            account=account,
            thread_payload=thread_payload,
            thread_id=tid,
            body_markdown=body_md,
            ingested_at=ingested_at,
            routed_by=routed_by_list,
        )
        content = fm + body_md
        m = re.search(r"^content_hash:\s*(\S+)", fm, re.MULTILINE)
        content_hash = m.group(1) if m else ""
        ledger_key = f"gmail:{tid}"
        already = ledger_has(ws, ledger_key, content_hash)

        rel = relative_thread_path(account, first_dt, subject_slug(subject), tid)
        full_path = ULTRON_ROOT / "workspaces" / ws / rel

        if args.dry_run:
            run_log.write(
                f"  DRY ws={ws} tid={tid[:8]} -> {rel} "
                f"hash={content_hash[:24]} already_in_ledger={already}\n"
            )
            if args.show:
                print(f"\n========== DRY-RUN ws={ws} path={rel} ==========")
                print(content)
                print("========== END DRY-RUN ==========\n")
            written[ws] = written.get(ws, 0) + 1
            continue

        if already:
            run_log.write(f"  skip ws={ws} tid={tid[:8]} reason=ledger-match\n")
            continue

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        ledger_append(ws, {
            "source": "gmail",
            "key": ledger_key,
            "content_hash": content_hash,
            "raw_path": str(rel),
            "ingested_at": ingested_at.isoformat(),
            "run_id": args.run_id,
        })
        written[ws] = written.get(ws, 0) + 1
        run_log.write(f"  WRITE ws={ws} tid={tid[:8]} -> {rel}\n")

    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def acquire_lock(account: str):
    """flock the account-specific lock file. Returns the open fd or None."""
    lock_path = Path("/tmp") / f"com.adithya.ultron.ingest-gmail-{account_slug(account)}.lock"
    fd = open(lock_path, "w")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fd.close()
        return None
    return fd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--account", required=True, help="Gmail address, e.g. adithya@outerscope.xyz")
    ap.add_argument("--workspaces", default=None,
                    help="Comma-separated subset; default = every subscribing workspace.")
    ap.add_argument("--run-id", default=datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
    ap.add_argument("--dry-run", action="store_true",
                    help="Fetch + render but write nothing; cursor untouched.")
    ap.add_argument("--show", action="store_true",
                    help="(dry-run only) print rendered output to stdout.")
    ap.add_argument("--max-items", type=int, default=None, help="Hard cap on threads processed.")
    ap.add_argument("--reset-cursor", action="store_true",
                    help="Delete cursor; rebuild from lookback window.")
    args = ap.parse_args()

    account: str = args.account.strip()
    if "@" not in account:
        sys.stderr.write(f"ingest-gmail: --account must be an email; got {account!r}\n")
        return 2

    # flock — Lock 7
    lock_fd = acquire_lock(account)
    if lock_fd is None:
        sys.stderr.write(f"ingest-gmail: lock held for {account}; another instance running\n")
        return 0

    run_log = run_log_path(account, args.run_id).open("a")
    run_log.write(f"\n=== run_id={args.run_id} account={account} dry_run={args.dry_run} ===\n")

    if args.reset_cursor:
        reset_cursor(account)
        sys.stderr.write(f"ingest-gmail: cursor reset for {account}\n")
        run_log.write("cursor reset\n")

    try:
        cursor_history_id = read_cursor(account)
    except ValueError as exc:
        sys.stderr.write(str(exc) + "\n")
        run_log.write(f"FATAL cursor: {exc}\n")
        run_log.close()
        return 2

    workspaces_config = load_all_workspaces_config()
    if not workspaces_config:
        sys.stderr.write("ingest-gmail: no workspaces with sources.yaml found\n")
        run_log.close()
        return 0

    includes, excludes, _ = collect_account_rules(account, workspaces_config)
    if not includes and not excludes:
        sys.stderr.write(f"ingest-gmail: no workspace subscribes to {account}; nothing to do\n")
        run_log.close()
        return 0

    svc = build_service(account)
    ingested_at = datetime.now(timezone.utc)

    added_tids: set[str] = set()
    deleted_tids: set[str] = set()
    labelled_tids: set[str] = set()

    if cursor_history_id is None:
        lookback_days = int(os.environ.get("GMAIL_INITIAL_LOOKBACK_DAYS", str(GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT)))
        after_dt = datetime.now(tz=timezone.utc) - timedelta(days=lookback_days)
        after_ts = int(after_dt.timestamp())
        q = build_q(includes, excludes, after_ts)
        sys.stderr.write(f"ingest-gmail: first run for {account}; lookback={lookback_days}d q={q!r}\n")
        run_log.write(f"first-run lookback={lookback_days} q={q!r}\n")
        added_tids = collect_threads_first_run(svc, q, args.max_items)
    else:
        sys.stderr.write(f"ingest-gmail: incremental run for {account}; startHistoryId={cursor_history_id}\n")
        run_log.write(f"incremental startHistoryId={cursor_history_id}\n")
        added_tids, deleted_tids, labelled_tids = collect_history_events(svc, cursor_history_id, args.max_items)

    sys.stderr.write(
        f"ingest-gmail: tids added={len(added_tids)} deleted={len(deleted_tids)} "
        f"label-changed={len(labelled_tids)} (cap={args.max_items or 'none'})\n"
    )

    written_per_ws: dict[str, int] = {}

    cap = args.max_items if args.max_items else None

    def take(s: set[str], remaining: int | None) -> list[str]:
        items = sorted(s)
        if remaining is None:
            return items
        return items[:remaining]

    remaining = cap
    process_added = take(added_tids, remaining)
    if remaining is not None:
        remaining -= len(process_added)
    process_labelled = take(labelled_tids, remaining)
    if remaining is not None:
        remaining -= len(process_labelled)
    process_deleted = take(deleted_tids, remaining)

    for tid in process_added + process_labelled:
        per = process_thread(svc, tid, account, workspaces_config, ingested_at, args, run_log)
        for ws, n in per.items():
            written_per_ws[ws] = written_per_ws.get(ws, 0) + n

    deleted_marked = 0
    if not args.dry_run:
        for tid in process_deleted:
            n = mark_deleted_upstream(tid, account, workspaces_config, ingested_at)
            deleted_marked += n
            run_log.write(f"  DELETE-MARK tid={tid[:8]} updated={n} file(s)\n")
    else:
        for tid in process_deleted:
            run_log.write(f"  DRY DELETE-MARK tid={tid[:8]}\n")

    # Advance cursor — Lock 7
    if not args.dry_run:
        try:
            profile = _retry(lambda: svc.users().getProfile(userId="me").execute())
            new_cursor = str(profile.get("historyId") or "")
            if new_cursor:
                write_cursor(account, new_cursor)
                run_log.write(f"cursor -> {new_cursor}\n")
        except Exception as exc:
            sys.stderr.write(f"ingest-gmail: failed to advance cursor: {exc}\n")
            run_log.write(f"FATAL cursor advance: {exc}\n")

    if not args.dry_run:
        for ws, count in sorted(written_per_ws.items()):
            log_path = ULTRON_ROOT / "workspaces" / ws / "_meta" / "log.md"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a") as f:
                f.write(
                    f"- {ingested_at.replace(microsecond=0).isoformat()} "
                    f"gmail/{account_slug(account)} "
                    f"+{count} thread(s) "
                    f"(deleted_marked={deleted_marked}, run_id={args.run_id})\n"
                )

    sys.stderr.write(
        f"ingest-gmail: done. account={account} "
        f"written={dict(written_per_ws)} deleted_marked={deleted_marked} "
        f"dry_run={args.dry_run}\n"
    )
    run_log.write(
        f"=== done written={dict(written_per_ws)} deleted_marked={deleted_marked} ===\n"
    )
    run_log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
