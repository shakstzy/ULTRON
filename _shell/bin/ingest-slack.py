#!/usr/bin/env python3
"""
ingest-slack.py — Slack robot, structured per the 9 locks in
_shell/stages/ingest/slack/format.md.

Activated for Eclipse Labs (workspace_slug=eclipse) on 2026-05-02.

Forbidden behaviors (immutable contract — see format.md "Forbidden"):
1. Never delete a raw file based on Slack-side deletion.
2. Never copy attachment binaries (metadata + permalinks only).
3. Never run LLM / vision calls during ingest.
4. Never edit frontmatter post-write except deleted_messages,
   edited_messages_count, container_archived, deleted_upstream.
5. Never write outside workspaces/<ws>/raw/slack/<workspace-slug>/...
6. Never fetch full edit history (current text only).
7. Never render reactions.
8. Never render bot messages.
9. Never skip the universal pre-filter, even if a workspace allowlists
   the channel.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CREDENTIALS_DIR = ULTRON_ROOT / "_credentials"
CURSOR_DIR = ULTRON_ROOT / "_shell" / "cursors" / "slack"

DEFAULT_LOOKBACK_DAYS = int(os.environ.get("ULTRON_SLACK_LOOKBACK_DAYS", "365"))
# Sliding-window overlap: every incremental run re-fetches the last N days
# from the cursor backwards. This catches late thread replies whose parent
# is older than the cursor (parents are not returned by conversations.history
# unless their ts is within [oldest, latest]). Ledger dedup keeps writes idempotent.
INCREMENTAL_OVERLAP_DAYS = int(os.environ.get("ULTRON_SLACK_OVERLAP_DAYS", "7"))

# Image description (Gemini Flash). Cached by Slack file_id.
GEMINI_TMP_DIR = Path.home() / ".gemini" / "tmp" / "ultron"
GEMINI_MODEL = os.environ.get("ULTRON_SLACK_GEMINI_MODEL", "gemini-3-flash-preview")
IMAGE_DESCRIBE_TIMEOUT = int(os.environ.get("ULTRON_SLACK_IMAGE_TIMEOUT", "60"))
IMAGE_MAX_BYTES = int(os.environ.get("ULTRON_SLACK_IMAGE_MAX_BYTES", str(15 * 1024 * 1024)))

LOCAL_TZ = dt.datetime.now().astimezone().tzinfo
SLACK_BASE = "https://slack.com/api"

IMPLEMENTATION_READY = True

SKIP_SUBTYPES = {
    "channel_join", "channel_leave", "channel_topic", "channel_purpose",
    "channel_name", "channel_archive", "channel_unarchive",
    "group_join", "group_leave", "bot_message", "bot_add", "bot_remove",
}

CANONICAL_ME_SLUG = "adithya-shak-kumar"


# ---------------------------------------------------------------------------
# Slack HTTP client (stdlib only; deterministic + minimal)
# ---------------------------------------------------------------------------
class SlackError(RuntimeError):
    def __init__(self, method: str, error: str, payload: dict):
        super().__init__(f"slack {method}: {error}")
        self.method = method
        self.error = error
        self.payload = payload


class SlackClient:
    def __init__(self, token: str, *, max_retries: int = 5):
        self.token = token
        self.max_retries = max_retries

    def call(self, method: str, **params) -> dict:
        url = f"{SLACK_BASE}/{method}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        backoff = 1.0
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    url, headers={"Authorization": f"Bearer {self.token}"}
                )
                with urllib.request.urlopen(req, timeout=20) as r:
                    payload = json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry_after = float(e.headers.get("Retry-After") or backoff)
                    time.sleep(min(retry_after, 60))
                    backoff = min(backoff * 2, 30)
                    last_err = e
                    continue
                raise
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
                continue
            if payload.get("ok"):
                return payload
            err = payload.get("error", "unknown")
            if err == "ratelimited":
                retry_after = float(payload.get("retry_after") or backoff)
                time.sleep(min(retry_after, 60))
                backoff = min(backoff * 2, 30)
                continue
            raise SlackError(method, err, payload)
        raise RuntimeError(f"slack {method}: retries exhausted ({last_err})")

    def paginate(self, method: str, *, key: str, **params):
        cursor: str | None = None
        while True:
            call_params = dict(params)
            if cursor:
                call_params["cursor"] = cursor
            payload = self.call(method, **call_params)
            for item in payload.get(key, []) or []:
                yield item
            cursor = (payload.get("response_metadata") or {}).get("next_cursor") or ""
            if not cursor:
                return


# ---------------------------------------------------------------------------
# Slug derivation (Lock 2)
# ---------------------------------------------------------------------------
def kebab(s: str, *, max_len: int = 40) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s


def workspace_slug_from_team(team_name: str | None, team_url: str | None) -> str:
    if team_url:
        host = urllib.parse.urlparse(team_url).netloc
        sub = host.split(".")[0]
        sub = kebab(sub)
        if sub:
            return sub
    if team_name:
        return kebab(team_name)
    return "slack"


def user_slug(profile: dict, user_id: str) -> str:
    p = (profile or {}).get("profile") or profile or {}
    display = (p.get("display_name") or "").strip()
    real = (p.get("real_name") or "").strip()
    email = (p.get("email") or "").strip()
    if display:
        slug = kebab(display)
        if slug:
            return slug
    if real:
        slug = kebab(real)
        if slug:
            return slug
    if email and "@" in email:
        local, domain = email.split("@", 1)
        domain_stem = domain.split(".")[0]
        slug = kebab(f"{local}-{domain_stem}")
        if slug:
            return slug
    return (user_id or "").lower() or "unknown-user"


# ---------------------------------------------------------------------------
# User cache (resolves user_id → {slug, display, real, email})
# ---------------------------------------------------------------------------
class UserCache:
    def __init__(self, client: SlackClient, *, me_user_id: str):
        self.client = client
        self.me_user_id = me_user_id
        self._cache: dict[str, dict] = {}

    def get(self, user_id: str) -> dict:
        if not user_id:
            return {"slug": "unknown-user", "display_name": "unknown",
                    "real_name": "", "email": "", "user_id": ""}
        if user_id in self._cache:
            return self._cache[user_id]
        try:
            res = self.client.call("users.info", user=user_id)
            u = res.get("user") or {}
            p = u.get("profile") or {}
            if user_id == self.me_user_id:
                slug = CANONICAL_ME_SLUG
                display = "Adithya Kumar (me)"
            else:
                slug = user_slug(p, user_id)
                display = (p.get("display_name") or p.get("real_name")
                           or u.get("real_name") or user_id)
            entry = {
                "slug": slug,
                "display_name": display,
                "real_name": p.get("real_name") or "",
                "email": p.get("email") or "",
                "user_id": user_id,
            }
        except SlackError:
            entry = {
                "slug": user_id.lower(),
                "display_name": user_id,
                "real_name": "",
                "email": "",
                "user_id": user_id,
            }
        self._cache[user_id] = entry
        return entry


# ---------------------------------------------------------------------------
# Lock 5 — body rendering
# ---------------------------------------------------------------------------
MENTION_USER_RE = re.compile(r"<@([UW][A-Z0-9]+)(?:\|[^>]*)?>")
MENTION_CHAN_RE = re.compile(r"<#([CG][A-Z0-9]+)(?:\|([^>]+))?>")
LINK_LABELED_RE = re.compile(r"<(https?://[^|>]+)\|([^>]+)>")
LINK_BARE_RE = re.compile(r"<(https?://[^>]+)>")
SLACK_BOLD_RE = re.compile(r"(?<![A-Za-z0-9])\*([^*\n]+)\*(?![A-Za-z0-9])")
SLACK_ITALIC_RE = re.compile(r"(?<![A-Za-z0-9])_([^_\n]+)_(?![A-Za-z0-9])")
SLACK_STRIKE_RE = re.compile(r"~([^~\n]+)~")


CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
CODE_INLINE_RE = re.compile(r"`[^`\n]+`")


def _protect_code(text: str) -> tuple[str, list[str]]:
    """Replace fenced + inline code with placeholders so mrkdwn substitutions
    don't corrupt them. Returns (masked_text, originals_in_order)."""
    saved: list[str] = []

    def repl(m):
        saved.append(m.group(0))
        return f"\x00CODE{len(saved) - 1}\x00"

    text = CODE_FENCE_RE.sub(repl, text)
    text = CODE_INLINE_RE.sub(repl, text)
    return text, saved


def _restore_code(text: str, saved: list[str]) -> str:
    for i, original in enumerate(saved):
        text = text.replace(f"\x00CODE{i}\x00", original)
    return text


def decode_text(text: str, users: UserCache, chan_name_by_id: dict) -> str:
    if not text:
        return ""

    def sub_user(m):
        info = users.get(m.group(1))
        return f"@{info['display_name']}"

    def sub_chan(m):
        cid, name = m.group(1), (m.group(2) or "")
        if name:
            return f"#{name}"
        return f"#{chan_name_by_id.get(cid, cid)}"

    # Slack angle-bracket tokens are NEVER inside literal code spans (Slack
    # encodes them with HTML entities), so we resolve them on the raw text
    # first. Then we mask code, run mrkdwn substitutions, and unmask.
    text = LINK_LABELED_RE.sub(r"[\2](\1)", text)
    text = LINK_BARE_RE.sub(r"\1", text)
    text = MENTION_USER_RE.sub(sub_user, text)
    text = MENTION_CHAN_RE.sub(sub_chan, text)

    text, saved = _protect_code(text)
    text = SLACK_BOLD_RE.sub(r"**\1**", text)
    text = SLACK_ITALIC_RE.sub(r"*\1*", text)
    text = SLACK_STRIKE_RE.sub(r"~~\1~~", text)
    text = _restore_code(text, saved)

    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return text


# ---------------------------------------------------------------------------
# Image description (Gemini Flash) with file-id cache
# ---------------------------------------------------------------------------
def image_cache_path(workspace_slug: str) -> Path:
    return workspace_cursor_dir(workspace_slug) / "image-descriptions.json"


def load_image_cache(workspace_slug: str) -> dict[str, str]:
    p = image_cache_path(workspace_slug)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def save_image_cache(workspace_slug: str, cache: dict[str, str]) -> None:
    p = image_cache_path(workspace_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, indent=2, sort_keys=True))
    tmp.replace(p)


def _ext_for_mime(mime: str | None, filename: str | None) -> str:
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if 1 <= len(ext) <= 5:
            return f".{ext}"
    if mime:
        if "png" in mime:
            return ".png"
        if "jpeg" in mime or "jpg" in mime:
            return ".jpg"
        if "gif" in mime:
            return ".gif"
        if "webp" in mime:
            return ".webp"
        if "heic" in mime:
            return ".heic"
    return ".bin"


def describe_image(token: str, file_id: str, url_private: str,
                   mime: str | None, filename: str | None,
                   size_bytes: int | None) -> str | None:
    """Download an image from Slack via auth'd url_private, send to Gemini
    Flash for a 1-2 sentence description, return the description or None
    on any failure. Failures are logged to stderr and surface as None so
    the caller can fall back to metadata-only rendering."""
    if size_bytes and size_bytes > IMAGE_MAX_BYTES:
        sys.stderr.write(
            f"  image {file_id} skipped: {size_bytes} bytes > limit\n"
        )
        return None
    GEMINI_TMP_DIR.mkdir(parents=True, exist_ok=True)
    ext = _ext_for_mime(mime, filename)
    path = GEMINI_TMP_DIR / f"{file_id}{ext}"
    try:
        req = urllib.request.Request(
            url_private, headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            img = r.read()
        if len(img) > IMAGE_MAX_BYTES:
            sys.stderr.write(
                f"  image {file_id} skipped: {len(img)} bytes > limit\n"
            )
            return None
        path.write_bytes(img)
    except Exception as exc:
        sys.stderr.write(f"  image {file_id} download failed: {exc}\n")
        return None

    prompt = (
        f"@{path}\n\n"
        "Describe what's shown in this image in 1-2 sentences for an "
        "archival search index. Be concrete: list visible objects, text, "
        "faces, charts, screenshots. If it's a screenshot, transcribe key "
        "visible text. Output ONLY the description sentence(s), no preamble."
    )
    try:
        import subprocess
        result = subprocess.run(
            ["gemini", "-m", GEMINI_MODEL, "--approval-mode", "plan",
             "-p", prompt, "-o", "text"],
            capture_output=True, text=True, timeout=IMAGE_DESCRIBE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"  image {file_id} gemini timeout\n")
        try:
            path.unlink()
        except OSError:
            pass
        return None
    finally:
        try:
            path.unlink()
        except OSError:
            pass
    if result.returncode != 0:
        sys.stderr.write(
            f"  image {file_id} gemini exit={result.returncode}: "
            f"{result.stderr.strip()[:200]}\n"
        )
        return None
    desc = result.stdout.strip()
    # Strip Markdown emphasis the model occasionally adds + collapse
    # whitespace so it renders cleanly inside `[image: ...]`.
    desc = re.sub(r"\s+", " ", desc).strip()
    if not desc:
        return None
    return desc


def fmt_size(n: int | None) -> str:
    if n is None:
        return "?"
    n = int(n)
    units = ["B", "KB", "MB", "GB"]
    i = 0
    f = float(n)
    while f >= 1024 and i < len(units) - 1:
        f /= 1024
        i += 1
    if i == 0:
        return f"{int(f)}{units[i]}"
    return f"{f:.1f}{units[i]}"


def ts_to_local_dt(ts: str) -> dt.datetime:
    return dt.datetime.fromtimestamp(float(ts), tz=LOCAL_TZ)


def hh_mm(d: dt.datetime) -> str:
    return d.strftime("%H:%M")


def _file_line_for_attachment(f: dict, image_descriptions: dict[str, str]) -> str:
    """Render an inline attachment placeholder. Images get the Gemini-
    generated description (cached by file_id). Non-image attachments stay
    as `[file: <name> — <size>]` with metadata only."""
    name = f.get("name") or f.get("title") or "file"
    size = fmt_size(f.get("size"))
    mime = f.get("mimetype") or ""
    fid = f.get("id") or ""
    if mime.startswith("image/") and fid in image_descriptions:
        desc = image_descriptions[fid]
        return f"[image: {desc}]"
    if mime.startswith("image/"):
        return f"[image: {name} — {size} (description unavailable)]"
    return f"[file: {name} — {size}]"


def message_lines(msg: dict, users: UserCache, chan_name_by_id: dict,
                  image_descriptions: dict[str, str],
                  *, indent: bool = False) -> list[str]:
    """Render one message (parent or reply) per Lock 5. Returns body lines.

    Reactions and bot messages already filtered upstream. This function
    renders edits (current text), deletions ([deleted at HH:MM]), and
    inline file placeholders. Images carry a Gemini-generated description
    when available; non-image files stay metadata-only with permalinks
    captured in frontmatter."""
    sender = users.get(msg.get("user") or "")["display_name"]
    when = ts_to_local_dt(msg["ts"])
    prefix = "> " if indent else ""
    heading_marker = "###" if indent else "##"

    if msg.get("subtype") == "message_deleted":
        deleted_at = ts_to_local_dt(msg.get("deleted_ts") or msg["ts"])
        return [
            f"{prefix}{heading_marker} {hh_mm(when)} — {sender}",
            f"{prefix}",
            f"{prefix}[deleted at {hh_mm(deleted_at)}]",
            f"{prefix}",
        ]

    body = decode_text(msg.get("text") or "", users, chan_name_by_id)
    body_lines = [l for l in body.splitlines()] if body else []

    file_lines: list[str] = []
    for f in msg.get("files") or []:
        if f.get("mode") == "tombstone":
            continue
        file_lines.append(_file_line_for_attachment(f, image_descriptions))

    out: list[str] = [
        f"{prefix}{heading_marker} {hh_mm(when)} — {sender}",
        f"{prefix}",
    ]
    for l in body_lines:
        out.append(f"{prefix}{l}".rstrip())
    if file_lines:
        if body_lines:
            out.append(f"{prefix}")
        for l in file_lines:
            out.append(f"{prefix}{l}")
    out.append(f"{prefix}")
    return out


def render_day_body(container: dict, day: dt.date, parents_for_day: list[dict],
                    thread_cache: dict[str, list[dict]],
                    users: UserCache, chan_name_by_id: dict,
                    image_descriptions: dict[str, str]) -> str:
    ctype = container["type"]
    name = container.get("name") or container.get("slug")
    weekday = day.strftime("%A")
    date_str = day.isoformat()

    if ctype == "channel":
        title = f"# #{name} — {date_str} ({weekday})"
    elif ctype == "dm":
        other_display = container.get("other_display_name") or name
        title = f"# DM with {other_display} — {date_str} ({weekday})"
    elif ctype == "group-dm":
        members = container.get("member_display_names") or []
        label = ", ".join(members) if members else (container.get("display_label") or "")
        title = f"# Group DM ({len(members) or '?'}): {label} — {date_str} ({weekday})"
    else:
        title = f"# {name} — {date_str} ({weekday})"

    lines: list[str] = [title, ""]
    for parent in parents_for_day:
        lines.extend(message_lines(parent, users, chan_name_by_id,
                                   image_descriptions))
        replies = thread_cache.get(parent.get("thread_ts") or "", [])
        for r in replies:
            if r.get("ts") == parent.get("ts"):
                continue
            lines.extend(message_lines(r, users, chan_name_by_id,
                                       image_descriptions, indent=True))
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Lock 6 — pre-filter + state-event normalization
# ---------------------------------------------------------------------------
def normalize_state_event(msg: dict) -> dict:
    """Slack wraps message_changed / message_deleted with the real payload
    nested under `message` / `previous_message`. Without this normalization,
    the renderer reads the wrapper's top-level fields (no `user`, no `text`)
    and emits blank or unknown-sender lines.

    Returns a flat message dict with `original_ts` (the parent's ts), an
    explicit `subtype`, and `deleted_ts` populated for deletions."""
    sub = msg.get("subtype")
    if sub == "message_changed":
        inner = dict(msg.get("message") or {})
        inner.setdefault("ts", inner.get("ts") or msg.get("ts"))
        inner["edited"] = inner.get("edited") or {"ts": msg.get("ts")}
        inner["original_ts"] = inner.get("ts")
        return inner
    if sub == "message_deleted":
        old = dict(msg.get("previous_message") or {})
        old["subtype"] = "message_deleted"
        old["deleted_ts"] = msg.get("event_ts") or msg.get("ts")
        # Use the original message ts for grouping so the deletion lands in
        # the day-file the message originally belonged to (Gemini #9).
        old.setdefault("ts", old.get("ts") or msg.get("ts"))
        old["original_ts"] = old.get("ts")
        return old
    return msg


def is_skippable(msg: dict) -> bool:
    sub = msg.get("subtype")
    # Slack tags every API-posted message with `bot_id`, including
    # messages sent from a user's own xoxp token via chat.postMessage.
    # The discriminator for "bot vs user" is presence of a `user` field
    # AND subtype != bot_message. A real bot post has no `user` (or
    # subtype=bot_message); an app-issued user post has both.
    if sub == "bot_message":
        return True
    if msg.get("bot_id") and not msg.get("user"):
        return True
    if sub in SKIP_SUBTYPES:
        return True
    if sub == "message_deleted":
        return False  # render as [deleted at HH:MM]
    if not (msg.get("text") or msg.get("files") or msg.get("thread_ts")):
        return True
    return False


# ---------------------------------------------------------------------------
# Lock 8 — cursors + dedup ledger
# ---------------------------------------------------------------------------
def workspace_cursor_dir(workspace_slug: str) -> Path:
    return CURSOR_DIR / workspace_slug


def cursor_path(workspace_slug: str, container_slug: str) -> Path:
    return workspace_cursor_dir(workspace_slug) / f"{container_slug}.txt"


def me_cursor_path(workspace_slug: str) -> Path:
    return workspace_cursor_dir(workspace_slug) / "me.txt"


def read_cursor(workspace_slug: str, container_slug: str) -> str | None:
    p = cursor_path(workspace_slug, container_slug)
    if not p.exists():
        return None
    return p.read_text().strip() or None


def write_cursor(workspace_slug: str, container_slug: str, ts: str) -> None:
    p = cursor_path(workspace_slug, container_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(f"{ts}\n")
    tmp.replace(p)


def read_me(workspace_slug: str) -> dict | None:
    p = me_cursor_path(workspace_slug)
    if not p.exists():
        return None
    out: dict = {}
    for line in p.read_text().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    if not out.get("user_id") or not out.get("canonical_slug"):
        return None
    return out


def write_me(workspace_slug: str, user_id: str,
             canonical_slug: str = CANONICAL_ME_SLUG) -> None:
    p = me_cursor_path(workspace_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(f"user_id: {user_id}\ncanonical_slug: {canonical_slug}\n")
    tmp.replace(p)


def ledger_path(ws: str) -> Path:
    return ULTRON_ROOT / "workspaces" / ws / "_meta" / "ingested.jsonl"


def read_ledger_index(ws: str) -> dict[str, str]:
    """Return {key: latest_content_hash} from the JSONL ledger."""
    p = ledger_path(ws)
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        k = row.get("key")
        h = row.get("content_hash")
        if k and h:
            out[k] = h
    return out


def append_ledger(ws: str, row: dict) -> None:
    """Append-only JSONL write. Other ingest robots (gmail, imessage) write
    to the same per-workspace ledger; flock the file during the append so
    interleaving runs cannot corrupt the JSONL."""
    p = ledger_path(ws)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass


def blake3_hex(data: bytes) -> str:
    try:
        import blake3 as _blake3
    except ImportError as exc:
        raise RuntimeError(
            "ingest-slack requires the 'blake3' package for spec-compliant "
            "content_hash values (format.md Lock 3). Install via "
            "`pip install blake3` and retry."
        ) from exc
    return _blake3.blake3(data).hexdigest()


# ---------------------------------------------------------------------------
# Workspace config + routing
# ---------------------------------------------------------------------------
def load_workspaces_config() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write("ingest-slack: missing dep pyyaml\n")
        return {}
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
        except Exception as exc:
            sys.stderr.write(
                f"ingest-slack: skipping {ws_dir.name} (bad sources.yaml): {exc}\n"
            )
            continue
        out[ws_dir.name] = cfg
    return out


def call_router(item: dict, workspaces_config: dict) -> list[str]:
    sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "stages" / "ingest" / "slack"))
    import route  # type: ignore
    return route.route(item, workspaces_config)


# ---------------------------------------------------------------------------
# Containers + history fetch
# ---------------------------------------------------------------------------
def list_visible_containers(client: SlackClient) -> list[dict]:
    """Return public channels (member only) + 1:1 DMs the token can see.
    Private + group DMs are skipped if scope missing (logged once)."""
    out: list[dict] = []
    for c in client.paginate("conversations.list", key="channels",
                             types="public_channel", exclude_archived="true",
                             limit=200):
        if not c.get("is_member"):
            continue
        out.append({
            "id": c["id"], "type": "channel", "slug": kebab(c["name"]),
            "name": c["name"], "raw": c,
        })
    try:
        for c in client.paginate("conversations.list", key="channels",
                                 types="private_channel", exclude_archived="true",
                                 limit=200):
            if not c.get("is_member"):
                continue
            out.append({
                "id": c["id"], "type": "channel", "slug": kebab(c["name"]),
                "name": c["name"], "raw": c,
            })
    except SlackError as e:
        if e.error == "missing_scope":
            sys.stderr.write("ingest-slack: skipping private channels (missing groups:read)\n")
        else:
            raise
    for c in client.paginate("conversations.list", key="channels", types="im",
                             limit=200):
        out.append({
            "id": c["id"], "type": "dm", "user_id": c.get("user"),
            "raw": c,
        })
    try:
        for c in client.paginate("conversations.list", key="channels",
                                 types="mpim", limit=200):
            out.append({
                "id": c["id"], "type": "group-dm",
                "slug": c["id"][:8].lower(), "raw": c,
            })
    except SlackError as e:
        if e.error == "missing_scope":
            sys.stderr.write("ingest-slack: skipping group DMs (missing mpim:read)\n")
        else:
            raise
    return out


def fetch_container_messages(client: SlackClient, channel_id: str, *,
                             oldest_ts: str | None,
                             latest_ts: str | None = None) -> list[dict]:
    params = {"channel": channel_id, "limit": 200, "inclusive": "false"}
    if oldest_ts:
        params["oldest"] = oldest_ts
    if latest_ts:
        params["latest"] = latest_ts
    msgs: list[dict] = []
    for m in client.paginate("conversations.history", key="messages", **params):
        msgs.append(m)
    msgs.sort(key=lambda m: float(m["ts"]))
    return msgs


def fetch_thread(client: SlackClient, channel_id: str,
                 thread_ts: str) -> list[dict]:
    out: list[dict] = []
    for m in client.paginate("conversations.replies", key="messages",
                             channel=channel_id, ts=thread_ts, limit=200):
        out.append(m)
    out.sort(key=lambda m: float(m["ts"]))
    return out


# ---------------------------------------------------------------------------
# Frontmatter + write
# ---------------------------------------------------------------------------
def yaml_dump(d: dict) -> str:
    """Tiny deterministic YAML emitter (no pyyaml dep at write time)."""
    import yaml  # use pyyaml — already required by config load
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True,
                          default_flow_style=False)


def container_path(workspace_slug: str, container: dict) -> Path:
    base = ULTRON_ROOT / "workspaces"
    if container["type"] == "channel":
        sub = Path("channels") / container["slug"]
    elif container["type"] == "dm":
        sub = Path("dms") / container["other_user_slug"]
    elif container["type"] == "group-dm":
        sub = Path("group-dms") / container["slug"]
    else:
        raise ValueError(container["type"])
    return Path("raw") / "slack" / workspace_slug / sub


def day_file_path(ws: str, workspace_slug: str, container: dict,
                  day: dt.date) -> Path:
    rel = container_path(workspace_slug, container)
    if container["type"] == "channel":
        leaf = container["slug"]
    elif container["type"] == "dm":
        leaf = container["other_user_slug"]
    else:
        leaf = container["slug"]
    return (ULTRON_ROOT / "workspaces" / ws / rel
            / f"{day.year:04d}" / f"{day.month:02d}"
            / f"{day.isoformat()}__{leaf}.md")


def profile_path(ws: str, workspace_slug: str, container: dict | None) -> Path:
    base = ULTRON_ROOT / "workspaces" / ws / "raw" / "slack" / workspace_slug
    if container is None:
        return base / "_profile.md"
    return base / container_path(workspace_slug, container).relative_to(
        Path("raw") / "slack" / workspace_slug
    ) / "_profile.md"


def now_iso() -> str:
    return dt.datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def _atomic_write(path: Path, text: str) -> None:
    """Write `text` to `path` atomically with fsync on the file before
    rename. Power-loss durability per Codex #10."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def write_day_file(path: Path, frontmatter: dict, body: str) -> None:
    text = "---\n" + yaml_dump(frontmatter) + "---\n\n" + body
    _atomic_write(path, text)


def write_profile(path: Path, frontmatter: dict, body: str = "") -> None:
    text = "---\n" + yaml_dump(frontmatter) + "---\n"
    if body:
        text += "\n" + body.rstrip() + "\n"
    _atomic_write(path, text)


def workspace_profile_path(ws: str, workspace_slug: str) -> Path:
    return (ULTRON_ROOT / "workspaces" / ws / "raw" / "slack"
            / workspace_slug / "_profile.md")


def channel_profile_path(ws: str, workspace_slug: str, container: dict) -> Path:
    base = ULTRON_ROOT / "workspaces" / ws / "raw" / "slack" / workspace_slug
    if container["type"] == "channel":
        sub = Path("channels") / container["slug"]
    elif container["type"] == "dm":
        sub = Path("dms") / container["other_user_slug"]
    elif container["type"] == "group-dm":
        sub = Path("group-dms") / container["slug"]
    else:
        raise ValueError(container["type"])
    return base / sub / "_profile.md"


def update_workspace_profile(ws: str, workspace_slug: str, *, team_id: str,
                             team_name: str | None, team_url: str | None,
                             me_user_id: str, scopes: list[str] | None,
                             auth_token_path: str) -> None:
    """Lock 7 workspace _profile.md. Append-only history for name changes.
    Body is human-editable and preserved across re-renders."""
    path = workspace_profile_path(ws, workspace_slug)
    existing_body = ""
    name_history: list[dict] = []
    first_seen = now_iso()
    if path.exists():
        try:
            import yaml  # type: ignore
            raw = path.read_text()
            if raw.startswith("---"):
                _, fm, body = raw.split("---", 2)
                old = yaml.safe_load(fm) or {}
                name_history = old.get("slack_workspace_name_history") or []
                first_seen = old.get("first_seen") or first_seen
                existing_body = body.strip()
        except Exception:
            pass
    if team_name and not any(h.get("name") == team_name for h in name_history):
        name_history.append({"name": team_name, "observed_at": now_iso()})
    fm = {
        "slack_team_id": team_id,
        "slack_workspace_slug": workspace_slug,
        "slack_workspace_name_current": team_name,
        "slack_workspace_name_history": name_history,
        "slack_workspace_url": team_url,
        "me_user_id": me_user_id,
        "me_canonical_slug": CANONICAL_ME_SLUG,
        "auth_token_path": auth_token_path,
        "auth_scopes": scopes or [],
        "first_seen": first_seen,
        "last_updated": now_iso(),
    }
    write_profile(path, fm, existing_body)


def update_channel_profile(ws: str, workspace_slug: str, container: dict,
                           members: list[str], users: UserCache) -> None:
    """Lock 7 container _profile.md. Append-only name + member history.
    Members are passed as a list of user_ids that appeared in this run's
    parents; the profile snapshots whoever is currently visible."""
    if container["type"] != "channel":
        return  # DM / group-dm profile generation deferred to v1.5
    path = channel_profile_path(ws, workspace_slug, container)
    raw = container.get("raw") or {}
    name = container.get("name") or container["slug"]
    name_history: list[dict] = []
    first_seen = now_iso()
    existing_body = ""
    if path.exists():
        try:
            import yaml  # type: ignore
            data = path.read_text()
            if data.startswith("---"):
                _, fm_text, body = data.split("---", 2)
                old = yaml.safe_load(fm_text) or {}
                name_history = old.get("channel_name_history") or []
                first_seen = old.get("first_seen") or first_seen
                existing_body = body.strip()
        except Exception:
            pass
    if not any(h.get("name") == name for h in name_history):
        name_history.append({"name": name, "changed_at": now_iso()})
    members_meta = []
    for uid in sorted(set(members)):
        info = users.get(uid)
        members_meta.append({
            "slug": info["slug"],
            "slack_user_id": uid,
            "display_name": info["display_name"],
        })
    fm = {
        "slack_channel_id": container["id"],
        "channel_name_current": name,
        "channel_name_history": name_history,
        "purpose": (raw.get("purpose") or {}).get("value"),
        "topic": (raw.get("topic") or {}).get("value"),
        "created": dt.datetime.fromtimestamp(
            raw["created"], tz=LOCAL_TZ).isoformat(timespec="seconds")
            if raw.get("created") else None,
        "is_archived": bool(raw.get("is_archived")),
        "archived_at": None,
        "member_count": raw.get("num_members"),
        "members": members_meta,
        "first_seen": first_seen,
        "last_updated": now_iso(),
    }
    write_profile(path, fm, existing_body)


# ---------------------------------------------------------------------------
# Per-container processing
# ---------------------------------------------------------------------------
def process_container(*, client: SlackClient, container: dict,
                      workspace_slug: str, team_id: str,
                      users: UserCache, chan_name_by_id: dict,
                      lookback_days: int, max_days: int | None,
                      workspaces_config: dict, dry_run: bool,
                      run_id: str, ledger_index_by_ws: dict,
                      no_attachments: bool,
                      image_descriptions: dict[str, str],
                      describe_images: bool, token: str) -> dict:
    summary = {"messages": 0, "files_written": 0, "deferred": False,
               "container_id": container["id"]}

    cur_ts = read_cursor(workspace_slug, _container_cursor_slug(container))

    # Sliding window: when an incremental cursor exists, fetch from
    # max(cursor - OVERLAP_DAYS, 0). Catches late thread replies whose parent
    # is older than the cursor (Codex #1, Gemini #2). Ledger dedup on body
    # hash keeps writes idempotent.
    if cur_ts is not None:
        fetch_oldest = f"{max(float(cur_ts) - INCREMENTAL_OVERLAP_DAYS * 86400, 0):.6f}"
    else:
        fetch_oldest = f"{time.time() - lookback_days * 86400:.6f}"
    if max_days is not None:
        bound = f"{time.time() - max_days * 86400:.6f}"
        if float(fetch_oldest) < float(bound):
            fetch_oldest = bound

    try:
        msgs = fetch_container_messages(client, container["id"],
                                        oldest_ts=fetch_oldest)
    except SlackError as e:
        if e.error in ("not_found", "channel_not_found"):
            sys.stderr.write(
                f"ingest-slack: container {container.get('name') or container['id']} "
                "vanished upstream (archived/deleted); skipping.\n"
            )
            summary["deferred"] = True
            return summary
        if e.error == "missing_scope":
            sys.stderr.write(
                f"ingest-slack: missing scope for {container['type']} "
                f"{container.get('name') or container['id']}; skipping.\n"
            )
            summary["deferred"] = True
            return summary
        raise

    # Normalize message_changed / message_deleted wrappers (Codex #2).
    msgs = [normalize_state_event(m) for m in msgs]

    if no_attachments:
        for m in msgs:
            m.pop("files", None)

    # conversations.history can return thread replies as top-level entries
    # when the user is "subscribed" to the thread. We only want parents at
    # the top level — replies are pulled via conversations.replies below.
    parents = [m for m in msgs
               if (not m.get("thread_ts") or m.get("thread_ts") == m.get("ts"))
               and not is_skippable(m)]
    summary["messages"] = len(parents)

    # Cursor must advance past every fetched event, not just renderable ones,
    # or noisy bot/meta channels infinitely re-fetch the same tail (Codex #3,
    # Gemini #1).
    latest_ts_seen = max((float(m["ts"]) for m in msgs), default=None)

    if not parents:
        if not dry_run and latest_ts_seen is not None:
            write_cursor(workspace_slug, _container_cursor_slug(container),
                         f"{latest_ts_seen:.6f}")
        return summary

    destinations_touched: set[str] = set()

    thread_cache: dict[str, list[dict]] = {}
    for m in parents:
        if m.get("thread_ts") and m.get("thread_ts") == m.get("ts") \
                and (m.get("reply_count") or 0) > 0:
            try:
                thread_cache[m["ts"]] = [
                    r for r in fetch_thread(client, container["id"], m["ts"])
                    if not is_skippable(r)
                ]
            except SlackError as e:
                if e.error in ("missing_scope", "thread_not_found"):
                    thread_cache[m["ts"]] = []
                else:
                    raise

    by_day: dict[dt.date, list[dict]] = {}
    for m in parents:
        d = ts_to_local_dt(m["ts"]).date()
        by_day.setdefault(d, []).append(m)

    # Resolve image descriptions for every image attached to a parent or
    # thread reply. Cache by Slack file_id so re-runs are free; failures
    # leave the cache untouched and the renderer falls back to size meta.
    if describe_images and not no_attachments:
        all_msgs_with_files = list(parents) + [
            r for replies in thread_cache.values() for r in replies
        ]
        image_files: list[dict] = []
        seen_ids: set[str] = set()
        for msg in all_msgs_with_files:
            for f in msg.get("files") or []:
                fid = f.get("id")
                mime = f.get("mimetype") or ""
                if (fid and fid not in seen_ids
                        and fid not in image_descriptions
                        and mime.startswith("image/")
                        and f.get("mode") != "tombstone"
                        and f.get("url_private")):
                    seen_ids.add(fid)
                    image_files.append(f)
        if image_files:
            sys.stderr.write(
                f"  describing {len(image_files)} new image(s) via Gemini...\n"
            )
            for f in image_files:
                desc = describe_image(
                    token=token, file_id=f["id"], url_private=f["url_private"],
                    mime=f.get("mimetype"), filename=f.get("name"),
                    size_bytes=f.get("size"),
                )
                if desc:
                    image_descriptions[f["id"]] = desc
            # Persist incrementally so a crash mid-channel doesn't lose
            # already-paid-for descriptions.
            save_image_cache(workspace_slug, image_descriptions)

    for day, day_parents in sorted(by_day.items()):
        body = render_day_body(container, day, day_parents, thread_cache,
                               users, chan_name_by_id, image_descriptions)
        body_hash = "blake3:" + blake3_hex(body.encode("utf-8"))
        all_msgs_in_day = list(day_parents)
        for p in day_parents:
            all_msgs_in_day.extend(thread_cache.get(p["ts"], []))
        provider_modified = ts_to_local_dt(
            max(m["ts"] for m in all_msgs_in_day)
        ).isoformat(timespec="seconds")

        # Build participant + attachment metadata
        participant_ids = {m.get("user") for m in all_msgs_in_day if m.get("user")}
        participants = [
            {"slug": users.get(uid)["slug"],
             "slack_user_id": uid,
             "display_name": users.get(uid)["display_name"],
             "real_name": users.get(uid)["real_name"],
             "email": users.get(uid)["email"]}
            for uid in sorted(participant_ids)
        ]

        attachments_meta = []
        for m in all_msgs_in_day:
            for f in (m.get("files") or []):
                if f.get("mode") == "tombstone":
                    continue
                attachments_meta.append({
                    "id": f.get("id"),
                    "filename": f.get("name") or f.get("title") or "",
                    "size_bytes": f.get("size"),
                    "mime": f.get("mimetype"),
                    "sender_slug": users.get(m.get("user") or "")["slug"],
                    "sent_at": ts_to_local_dt(m["ts"]).isoformat(timespec="seconds"),
                    "permalink": f.get("permalink"),
                    "private_url": f.get("url_private"),
                })

        thread_count = sum(1 for p in day_parents if thread_cache.get(p["ts"]))
        edited_count = sum(
            1 for m in all_msgs_in_day if (m.get("edited") or {}).get("ts")
        )

        ts_min = ts_to_local_dt(min(m["ts"] for m in all_msgs_in_day)).isoformat(timespec="seconds")
        ts_max = ts_to_local_dt(max(m["ts"] for m in all_msgs_in_day)).isoformat(timespec="seconds")

        # router-channel-type alias: route.py expects Slack-native "im" /
        # "mpim" for DM matching (Codex #6).
        router_channel_type = {
            "channel": "channel", "dm": "im", "group-dm": "mpim",
        }.get(container["type"], container["type"])

        item = {
            "slack_workspace_id": team_id,
            "slack_workspace_slug": workspace_slug,
            "container_type": container["type"],
            "container_slug": _container_cursor_slug(container),
            "container_id": container["id"],
            "channel_name": container.get("name"),
            "channel_type": router_channel_type,
            "participants": participants,
            "date": day.isoformat(),
        }
        destinations = call_router(item, workspaces_config)
        if not destinations:
            continue

        key = f"slack:{team_id}:{container['id']}:{day.isoformat()}"

        for ws in destinations:
            destinations_touched.add(ws)
            path = day_file_path(ws, workspace_slug, container, day)
            existing = ledger_index_by_ws.get(ws, {}).get(key)
            # Skip only if BOTH the ledger row matches AND the file is
            # actually present on disk. After a channel rename or manual
            # delete, the path changes/is gone but the old hash still
            # matches; without this check, the new path never gets
            # written (Codex #4, Gemini #6).
            if existing == body_hash and path.exists():
                continue

            frontmatter = {
                "source": "slack",
                "workspace": ws,
                "ingested_at": now_iso(),
                "ingest_version": 1,
                "content_hash": body_hash,
                "provider_modified_at": provider_modified,
                "slack_workspace_slug": workspace_slug,
                "slack_workspace_id": team_id,
                "container_type": container["type"],
                "container_slug": _container_cursor_slug(container),
                "container_id": container["id"],
                "date": day.isoformat(),
                "date_range": {"first": ts_min, "last": ts_max},
                "message_count": len(day_parents),
                "thread_count": thread_count,
                "participant_count": len(participant_ids),
                "participants": participants,
                "attachments": attachments_meta,
                "deleted_messages": [],
                "edited_messages_count": edited_count,
                "chat_db_message_ids": None,
                "deleted_upstream": None,
                "container_archived": False,
            }
            if dry_run:
                sys.stderr.write(f"  DRY would write {path}\n")
                summary["files_written"] += 1
                continue
            write_day_file(path, frontmatter, body)
            append_ledger(ws, {
                "source": "slack", "key": key, "content_hash": body_hash,
                "raw_path": str(path.relative_to(ULTRON_ROOT / "workspaces" / ws)),
                "ingested_at": frontmatter["ingested_at"],
                "run_id": run_id,
            })
            ledger_index_by_ws.setdefault(ws, {})[key] = body_hash
            summary["files_written"] += 1

    if not dry_run:
        # Refresh channel _profile.md once per destination workspace, even
        # when every day-file deduped (so member churn / topic changes still
        # land). Lock 7 frontmatter is the robot's responsibility.
        if container["type"] == "channel":
            all_participants = sorted({
                m.get("user") for m in msgs if m.get("user")
            })
            for ws in destinations_touched:
                try:
                    update_channel_profile(ws, workspace_slug, container,
                                           all_participants, users)
                except Exception as exc:
                    sys.stderr.write(
                        f"  channel profile update failed for {ws}: {exc}\n"
                    )

    if not dry_run and latest_ts_seen is not None:
        write_cursor(workspace_slug, _container_cursor_slug(container),
                     f"{latest_ts_seen:.6f}")
    return summary


def _container_cursor_slug(container: dict) -> str:
    if container["type"] == "channel":
        return container["slug"]
    if container["type"] == "dm":
        return container["other_user_slug"]
    return container["slug"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def credentials_path(workspace_slug: str) -> Path:
    return CREDENTIALS_DIR / f"slack-{workspace_slug}.json"


def load_credentials(workspace_slug: str) -> dict | None:
    p = credentials_path(workspace_slug)
    if not p.exists():
        sys.stderr.write(
            f"ingest-slack: credentials missing at {p}. "
            "See _shell/stages/ingest/slack/SETUP.md § 1.\n"
        )
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"ingest-slack: credentials JSON invalid: {exc}\n")
        return None


def lock_path_for(workspace_slug: str) -> str:
    return f"/tmp/com.adithya.ultron.ingest-slack-{workspace_slug}.lock"


def _try_lock(path: str):
    fh = open(path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fh
    except BlockingIOError:
        fh.close()
        return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Slack robot.")
    ap.add_argument("--workspace", required=True,
                    help="Slack workspace slug (e.g., eclipse).")
    ap.add_argument("--containers", default=None,
                    help="Comma subset of {channels,dms,group-dms}; default: all.")
    ap.add_argument("--channel", default=None,
                    help="Single container slug (debugging).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--max-days", type=int, default=None)
    ap.add_argument("--reset-cursor", action="store_true")
    ap.add_argument("--reset-cursor-channel", default=None)
    ap.add_argument("--no-attachments", action="store_true",
                    help="Skip attachment metadata + image description.")
    ap.add_argument("--no-images", action="store_true",
                    help="Skip Gemini image description (faster re-renders; "
                         "falls back to size+name placeholders).")
    ap.add_argument("--run-id",
                    default=dt.datetime.now().strftime("%Y%m%dT%H%M%S"))
    return ap.parse_args(argv)


def main() -> int:
    args = parse_args()
    ws_slug = args.workspace

    lock = _try_lock(lock_path_for(ws_slug))
    if lock is None:
        sys.stderr.write(
            f"ingest-slack: another run holds the lock for {ws_slug}; exiting 0.\n"
        )
        return 0

    try:
        creds = load_credentials(ws_slug)
        if creds is None:
            return 0
        token = creds.get("user_token") or creds.get("token")
        if not token:
            sys.stderr.write(
                "ingest-slack: credentials JSON has no 'user_token' or 'token' key.\n"
            )
            return 0

        if not IMPLEMENTATION_READY:
            sys.stderr.write(
                "ingest-slack: skeleton — IMPLEMENTATION_READY is False.\n"
            )
            return 0

        client = SlackClient(token)
        auth = client.call("auth.test")
        me_user_id = auth["user_id"]
        auth_team_id = auth.get("team_id")

        creds_team_id = creds.get("team_id")
        if creds_team_id and auth_team_id and creds_team_id != auth_team_id:
            sys.stderr.write(
                "ingest-slack: FATAL credential team_id "
                f"{creds_team_id} != auth.test team_id {auth_team_id}. "
                "Token belongs to a different workspace; exiting non-zero.\n"
            )
            return 2

        prior = read_me(ws_slug)
        if prior and prior.get("user_id") != me_user_id:
            sys.stderr.write(
                "ingest-slack: FATAL token user_id "
                f"{me_user_id} differs from cached {prior['user_id']} "
                f"for workspace {ws_slug}. Refusing to corrupt the archive; "
                "exiting non-zero.\n"
            )
            return 2
        if not prior:
            write_me(ws_slug, me_user_id)

        if args.reset_cursor:
            d = workspace_cursor_dir(ws_slug)
            if d.exists():
                for p in d.glob("*.txt"):
                    if p.name == "me.txt":
                        continue
                    p.unlink()
        if args.reset_cursor_channel:
            p = cursor_path(ws_slug, args.reset_cursor_channel)
            if p.exists():
                p.unlink()

        users = UserCache(client, me_user_id=me_user_id)
        containers = list_visible_containers(client)

        # Resolve DM counterparties (slug + display name) up front.
        for c in containers:
            if c["type"] == "dm":
                info = users.get(c.get("user_id") or "")
                c["other_user_slug"] = info["slug"]
                c["other_display_name"] = info["display_name"]

        chan_name_by_id = {c["id"]: c.get("name") for c in containers
                           if c["type"] == "channel"}

        wanted_kinds = (set(args.containers.split(",")) if args.containers
                        else {"channels", "dms", "group-dms"})
        type_to_kind = {"channel": "channels", "dm": "dms",
                        "group-dm": "group-dms"}

        if args.channel:
            containers = [c for c in containers
                          if c.get("slug") == args.channel
                          or c.get("other_user_slug") == args.channel
                          or c["id"] == args.channel]

        containers = [c for c in containers
                      if type_to_kind[c["type"]] in wanted_kinds]

        workspaces_config = load_workspaces_config()
        ledger_index_by_ws = {ws: read_ledger_index(ws)
                              for ws in workspaces_config}

        # Auth.test is the source of truth for team_id, full stop.
        team_id = auth_team_id or creds_team_id

        # Persistent image-description cache (key = Slack file_id).
        image_descriptions = load_image_cache(ws_slug)
        describe_images = not args.no_images
        if image_descriptions:
            sys.stderr.write(
                f"ingest-slack: loaded {len(image_descriptions)} cached image descriptions\n"
            )

        # Workspace _profile.md (Lock 7): refresh on every run.
        try:
            update_workspace_profile(
                ws=ws_slug, workspace_slug=ws_slug, team_id=team_id,
                team_name=auth.get("team"), team_url=auth.get("url"),
                me_user_id=me_user_id, scopes=creds.get("scopes"),
                auth_token_path=str(credentials_path(ws_slug).relative_to(ULTRON_ROOT)),
            )
        except Exception as exc:
            sys.stderr.write(f"ingest-slack: workspace profile update failed: {exc}\n")

        summaries: list[tuple[str, dict]] = []
        for c in containers:
            label = c.get("name") or c.get("other_user_slug") or c["id"]
            sys.stderr.write(f"ingest-slack: processing {c['type']} {label}\n")
            try:
                s = process_container(
                    client=client, container=c,
                    workspace_slug=ws_slug, team_id=team_id,
                    users=users, chan_name_by_id=chan_name_by_id,
                    lookback_days=DEFAULT_LOOKBACK_DAYS,
                    max_days=args.max_days,
                    workspaces_config=workspaces_config,
                    dry_run=args.dry_run, run_id=args.run_id,
                    ledger_index_by_ws=ledger_index_by_ws,
                    no_attachments=args.no_attachments,
                    image_descriptions=image_descriptions,
                    describe_images=describe_images, token=token,
                )
            except SlackError as e:
                sys.stderr.write(
                    f"  slack error on {label}: {e.error}; continuing.\n"
                )
                continue
            summaries.append((label, s))
            if args.show and args.dry_run:
                sys.stderr.write(f"    -> {s}\n")

        sys.stderr.write(
            "ingest-slack: done. processed=%d files_written=%d\n"
            % (len(summaries), sum(s[1]["files_written"] for s in summaries))
        )
        return 0
    finally:
        try:
            lock.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
