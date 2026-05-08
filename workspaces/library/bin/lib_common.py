"""
lib_common.py — shared helpers for library workspace ingest scripts and the curator.

Architecture (per `_shell/stages/ingest/CONTEXT.md`):
- Ingest scripts are pure CAPTURE. They download the source content and write
  ONE markdown file per item to `raw/<source>/<path>.md` carrying the universal
  frontmatter envelope (source / workspace / ingested_at / ingest_version /
  content_hash / provider_modified_at) plus per-source fields.
- NO cloud-llm calls during ingest. NO wiki writes during ingest. Wiki pages
  (`wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/`) are generated
  downstream by `/graphify --wiki` (or a future wiki-agent lint stage).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACE_SLUG = "library"
WORKSPACE = ULTRON_ROOT / "workspaces" / WORKSPACE_SLUG
RAW = WORKSPACE / "raw"
WIKI = WORKSPACE / "wiki"
META = WORKSPACE / "_meta"
BIN = WORKSPACE / "bin"

INGEST_VERSION = 1


# ---------------------------------------------------------------------------
# Slug generation — kebab-case ASCII, truncated, collision-safe
# ---------------------------------------------------------------------------

_SLUG_DROP = re.compile(r"[^\w\s-]")
_SLUG_WS = re.compile(r"[-\s]+")
_STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "but", "in", "on", "at", "to", "for",
    "with", "by", "from", "as", "is", "it",
}


def slugify(text: str, max_len: int = 60) -> str:
    if not text:
        return ""
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _SLUG_DROP.sub("", s)
    s = _SLUG_WS.sub("-", s).strip("-")
    if len(s) <= max_len:
        return s
    cut = s[:max_len]
    if "-" in cut:
        cut = cut.rsplit("-", 1)[0]
    return cut.strip("-")


def title_words_slug(title: str, n_words: int = 3) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title.lower())
    kept = [w for w in words if w not in _STOPWORDS]
    if len(kept) < n_words and words:
        kept = words
    return slugify("-".join(kept[:n_words]))


def author_slug(author_name: str) -> str:
    parts = re.findall(r"[A-Za-z]+", author_name)
    if not parts:
        return slugify(author_name)
    if len(parts) == 1:
        return slugify(parts[0])
    return slugify(f"{parts[0]}-{parts[-1]}")


def book_slug(title: str, author_name: str) -> str:
    last = re.findall(r"[A-Za-z]+", author_name)
    last_slug = slugify(last[-1]) if last else "unknown"
    return f"{last_slug}-{title_words_slug(title, n_words=3)}"


def youtube_video_slug(title: str, channel_handle: str, video_id: str = "") -> str:
    """`<channel-handle>-<title-4-words>[-<id5>]`. Channels reuse titles, so
    we append 5 chars of the YouTube id when supplied to prevent collisions."""
    base = f"{slugify(channel_handle)}-{title_words_slug(title, n_words=4)}"
    if video_id:
        suffix = re.sub(r"[^A-Za-z0-9]", "", video_id)[:5].lower()
        if suffix:
            return f"{base}-{suffix}"
    return base


def paper_slug(title: str, first_author: str, year: int | str) -> str:
    last = re.findall(r"[A-Za-z]+", first_author)
    last_slug = slugify(last[-1]) if last else "anon"
    return f"{last_slug}-{title_words_slug(title, n_words=3)}-{year}"


def article_slug(title: str, source_domain: str) -> str:
    domain = source_domain.replace("www.", "").split(".")[0]
    return f"{slugify(domain)}-{title_words_slug(title, n_words=4)}"


def reel_slug(creator_handle: str, published_at: str, video_id: str) -> str:
    handle = slugify(creator_handle.lstrip("@"))
    short_id = re.sub(r"[^A-Za-z0-9]", "", video_id)[:5].lower() or "00000"
    return f"{handle}-{published_at}-{short_id}"


# ---------------------------------------------------------------------------
# Frontmatter read/write
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(fm, dict):
        return {}, text
    return fm, m.group(2)


def render_frontmatter(fm: dict[str, Any]) -> str:
    body = yaml.safe_dump(
        fm,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=120,
    )
    return f"---\n{body}---\n"


def read_md(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_md(path: Path, fm: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = render_frontmatter(fm) + body
    if not out.endswith("\n"):
        out += "\n"
    path.write_text(out, encoding="utf-8")


# ---------------------------------------------------------------------------
# Hashing (blake3 per ULTRON convention, sha256 fallback)
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    """blake3 hex digest of the body (no frontmatter). Falls back to sha256
    when blake3 isn't available."""
    try:
        import blake3   # type: ignore
        return "blake3:" + blake3.blake3(text.encode("utf-8")).hexdigest()
    except ImportError:
        return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    if not path.exists() or path.is_dir():
        return ""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(64 * 1024), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------

def today() -> str:
    return datetime.date.today().isoformat()


def today_year_month() -> str:
    return datetime.date.today().strftime("%Y-%m")


def iso_utc(epoch: float | None = None) -> str:
    """ISO 8601 UTC timestamp matching the convention used elsewhere in ULTRON."""
    if epoch is None:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Universal envelope — required on every raw file across every source
# ---------------------------------------------------------------------------

def universal_envelope(
    *,
    source: str,
    body: str,
    provider_modified_at: str | None = None,
    extra: dict | None = None,
) -> dict:
    """Produce the universal frontmatter envelope per
    `_shell/stages/ingest/CONTEXT.md`. Source-specific fields layer on top
    via `extra`. Caller is responsible for putting source-specific keys in
    a sensible order — this helper just guarantees the universal six are
    present and consistent."""
    fm: dict[str, Any] = {
        "source": source,
        "workspace": WORKSPACE_SLUG,
        "ingested_at": iso_utc(),
        "ingest_version": INGEST_VERSION,
        "content_hash": content_hash(body),
        "provider_modified_at": provider_modified_at,
    }
    if extra:
        fm.update(extra)
    return fm


def write_raw(
    path: Path,
    *,
    source: str,
    body: str,
    provider_modified_at: str | None = None,
    extra: dict | None = None,
) -> Path:
    """Write a raw markdown file with the universal envelope. Idempotent:
    if the same path exists with the same content_hash, this is a no-op.

    Returns the path written (or the existing path on no-op)."""
    new_hash = content_hash(body)
    if path.exists():
        existing_fm, _ = read_md(path)
        if existing_fm.get("content_hash") == new_hash:
            return path
    fm = universal_envelope(
        source=source,
        body=body,
        provider_modified_at=provider_modified_at,
        extra=extra,
    )
    write_md(path, fm, body)
    return path


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log_event(event: str) -> None:
    META.mkdir(parents=True, exist_ok=True)
    log_path = META / "log.md"
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- {ts} — {event}\n")


def log_ingest(source_type: str, slug: str, status: str, extra: dict | None = None) -> None:
    META.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "source_type": source_type,
        "slug": slug,
        "status": status,
    }
    if extra:
        rec.update(extra)
    with open(META / "ingested.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert slugify("The 7 Habits of Highly Effective People") == "the-7-habits-of-highly-effective-people"
    assert title_words_slug("The 7 Habits of Highly Effective People", 3) == "7-habits-highly"
    assert author_slug("James Clear") == "james-clear"
    assert author_slug("Yuval Noah Harari") == "yuval-harari"
    assert book_slug("Atomic Habits", "James Clear") == "clear-atomic-habits"
    assert youtube_video_slug("Optimize Your Sleep", "andrewhuberman", video_id="dQw4w9WgXcQ") == "andrewhuberman-optimize-your-sleep-dqw4w"
    assert paper_slug("Attention Is All You Need", "Ashish Vaswani", 2017) == "vaswani-attention-all-you-2017"
    assert article_slug("Do Things That Don't Scale", "paulgraham.com") == "paulgraham-do-things-that-don"
    fm0 = {"slug": "test", "tags": ["a", "b"]}
    body0 = "## TL;DR\n\nhello\n"
    rendered = render_frontmatter(fm0) + body0
    fm1, body1 = parse_frontmatter(rendered)
    assert fm1 == fm0
    assert body1.strip() == body0.strip()
    # Universal envelope sanity
    env = universal_envelope(source="test", body="hello", extra={"x": 1})
    for k in ("source", "workspace", "ingested_at", "ingest_version", "content_hash", "provider_modified_at", "x"):
        assert k in env, f"missing envelope key: {k}"
    print("lib_common self-tests OK")
