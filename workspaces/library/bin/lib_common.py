"""
lib_common.py — shared helpers for library workspace ingest + curator scripts.

All ingest scripts (ingest-book, ingest-youtube, ingest-paper, ingest-article,
ingest-reel) and the curator (library-next) import from this module.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACE = ULTRON_ROOT / "workspaces" / "library"
RAW = WORKSPACE / "raw"
WIKI = WORKSPACE / "wiki"
META = WORKSPACE / "_meta"
BIN = WORKSPACE / "bin"

CLOUD_LLM_PATH = ULTRON_ROOT / "_shell" / "skills" / "cloud-llm"


def cloud_llm_import():
    """Lazy import of cloud-llm client (avoids hard dependency for unit tests)."""
    sys.path.insert(0, str(CLOUD_LLM_PATH))
    from client import ask_text, CloudLLMUnreachable  # type: ignore
    return ask_text, CloudLLMUnreachable


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
    """Produce a kebab-case ASCII slug.

    Steps:
    1. NFKD normalize, drop non-ASCII.
    2. Lowercase.
    3. Strip everything except word chars, spaces, hyphens.
    4. Collapse runs of whitespace/hyphen to single hyphen.
    5. Trim to max_len, never cut mid-word.
    """
    if not text:
        return ""
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _SLUG_DROP.sub("", s)
    s = _SLUG_WS.sub("-", s).strip("-")
    if len(s) <= max_len:
        return s
    # Cut at last hyphen before max_len
    cut = s[:max_len]
    if "-" in cut:
        cut = cut.rsplit("-", 1)[0]
    return cut.strip("-")


def title_words_slug(title: str, n_words: int = 3) -> str:
    """Slug from first n_words of title, dropping stopwords first."""
    words = re.findall(r"[A-Za-z0-9]+", title.lower())
    kept = [w for w in words if w not in _STOPWORDS]
    if len(kept) < n_words and words:
        # Not enough non-stopwords; fall back to raw words
        kept = words
    return slugify("-".join(kept[:n_words]))


def author_slug(author_name: str) -> str:
    """Author slug: <first>-<last> lowercase. 'James Clear' → 'james-clear'."""
    parts = re.findall(r"[A-Za-z]+", author_name)
    if not parts:
        return slugify(author_name)
    if len(parts) == 1:
        return slugify(parts[0])
    # First name + last name (skip middles for slug brevity)
    return slugify(f"{parts[0]}-{parts[-1]}")


def book_slug(title: str, author_name: str) -> str:
    """`<author-last>-<title-3-words>`. 'Atomic Habits' by James Clear → 'clear-atomic-habits'."""
    last = re.findall(r"[A-Za-z]+", author_name)
    last_slug = slugify(last[-1]) if last else "unknown"
    return f"{last_slug}-{title_words_slug(title, n_words=3)}"


def youtube_video_slug(title: str, channel_handle: str) -> str:
    """`<channel-handle>-<title-4-words>`."""
    return f"{slugify(channel_handle)}-{title_words_slug(title, n_words=4)}"


def paper_slug(title: str, first_author: str, year: int | str) -> str:
    """`<first-author-last>-<title-3-words>-<year>`."""
    last = re.findall(r"[A-Za-z]+", first_author)
    last_slug = slugify(last[-1]) if last else "anon"
    return f"{last_slug}-{title_words_slug(title, n_words=3)}-{year}"


def article_slug(title: str, source_domain: str) -> str:
    """`<source-domain-stem>-<title-4-words>`."""
    domain = source_domain.replace("www.", "").split(".")[0]
    return f"{slugify(domain)}-{title_words_slug(title, n_words=4)}"


def reel_slug(creator_handle: str, published_at: str, video_id: str) -> str:
    """`<creator-handle>-<YYYY-MM-DD>-<5char>`."""
    handle = slugify(creator_handle.lstrip("@"))
    short_id = re.sub(r"[^A-Za-z0-9]", "", video_id)[:5].lower() or "00000"
    return f"{handle}-{published_at}-{short_id}"


# ---------------------------------------------------------------------------
# Frontmatter read/write
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body). If no frontmatter, returns ({}, text)."""
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
    """Dump frontmatter dict as a YAML block with --- delimiters."""
    body = yaml.safe_dump(
        fm,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=120,
    )
    return f"---\n{body}---\n"


def read_md(path: Path) -> tuple[dict[str, Any], str]:
    """Read a markdown file, return (frontmatter, body)."""
    if not path.exists():
        return {}, ""
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_md(path: Path, fm: dict[str, Any], body: str) -> None:
    """Write a markdown file with frontmatter + body. Creates parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = render_frontmatter(fm) + body
    if not out.endswith("\n"):
        out += "\n"
    path.write_text(out, encoding="utf-8")


# ---------------------------------------------------------------------------
# Hashing for change detection
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    """SHA-256 hex digest of the body text only (no frontmatter)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    """SHA-256 of a file. Empty string on missing/error."""
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
# Today / dates
# ---------------------------------------------------------------------------

def today() -> str:
    return datetime.date.today().isoformat()


def today_year_month() -> str:
    return datetime.date.today().strftime("%Y-%m")


# ---------------------------------------------------------------------------
# Logging to _meta/log.md
# ---------------------------------------------------------------------------

def log_event(event: str) -> None:
    """Append a one-line event to _meta/log.md with timestamp."""
    META.mkdir(parents=True, exist_ok=True)
    log_path = META / "log.md"
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- {ts} — {event}\n")


def log_ingest(source_type: str, slug: str, status: str, extra: dict | None = None) -> None:
    """Append a structured ingest event to _meta/ingested.jsonl."""
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
# Cloud LLM synthesis — used by all ingest scripts
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = """\
You are the wiki agent for Adithya's personal nonfiction library workspace. The
voice is INTERNALIZED and SCANNABLE — Adithya thinking out loud after finishing
the source, not academic, not a book report.

Given the raw source content below, produce a wiki entity page with these
sections in this exact order, separated by blank lines, no other commentary:

## TL;DR
1-3 sentences. The core idea, in Adithya's voice.

## Key takeaways
3-7 bullets. Each bullet is one idea Adithya can carry to dinner conversation.
Specific, concrete, internalized. NOT a back-cover blurb.

## Quote
Exactly one direct quote, ≤ 15 words, in quotation marks, attributed:
"<quote>" — <Author>, <chapter / page / timestamp>
If no single line landed hard, omit this section entirely.

## Why it matters
1-2 sentences tying the source to something an ambitious 25-year-old in tech
would care about. Concrete, not generic.

## Tags
Comma-separated kebab-case topic tags, 2-6 of them. Format:
TAGS: tag-one, tag-two, tag-three

## Mentioned concepts
Comma-separated kebab-case concept slugs that this source touches. 0-8 of them.
Format:
CONCEPTS: concept-one, concept-two

## Bite size
Estimated minutes for Adithya to read your TL;DR + key takeaways aloud.
Format (integer only):
BITE_SIZE_MINUTES: 4

Do NOT reproduce paragraphs of source material. Do NOT include the source title
as a heading. Start your response with `## TL;DR`.

---SOURCE METADATA---
{metadata}

---SOURCE CONTENT---
{content}
"""


def synthesize(metadata: dict, content: str, max_content_chars: int = 60_000) -> dict:
    """Call cloud-llm with the synthesis prompt; parse the structured output.

    Returns dict with keys: tldr, takeaways, quote, why_matters, tags,
    concepts, bite_size_minutes, body (full markdown body with all sections),
    raw_response (debug).
    """
    ask_text, CloudLLMUnreachable = cloud_llm_import()

    truncated = content[:max_content_chars]
    if len(content) > max_content_chars:
        truncated += "\n\n[...content truncated for context budget...]"

    prompt = SYNTHESIS_PROMPT.format(
        metadata=yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False),
        content=truncated,
    )

    try:
        result = ask_text(prompt)
    except CloudLLMUnreachable as e:
        raise RuntimeError(f"cloud-llm unreachable during synthesis: {e}")

    raw = result.get("output", "") if isinstance(result, dict) else str(result)
    parsed = parse_synthesis(raw)
    parsed["raw_response"] = raw
    parsed["_engine"] = result.get("engine") if isinstance(result, dict) else None
    return parsed


_TAGS_RE = re.compile(r"^TAGS\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_CONCEPTS_RE = re.compile(r"^CONCEPTS\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_BITE_RE = re.compile(r"^BITE_SIZE_MINUTES\s*:\s*(\d+)", re.MULTILINE | re.IGNORECASE)


def parse_synthesis(raw: str) -> dict:
    """Extract structured fields from the LLM's synthesis output.

    Tolerant: missing sections produce empty values rather than raising.
    """
    out = {
        "tldr": "",
        "takeaways": [],
        "quote": "",
        "why_matters": "",
        "tags": [],
        "concepts": [],
        "bite_size_minutes": 5,
        "body": "",
    }

    # Section split by `## ` headers
    sections = re.split(r"\n##\s+", "\n" + raw)
    section_map: dict[str, str] = {}
    for s in sections:
        s = s.strip()
        if not s:
            continue
        if "\n" in s:
            head, body = s.split("\n", 1)
        else:
            head, body = s, ""
        section_map[head.strip().lower()] = body.strip()

    out["tldr"] = section_map.get("tl;dr", section_map.get("tldr", "")).strip()

    takeaways_raw = section_map.get("key takeaways", "")
    out["takeaways"] = [
        line.lstrip("-*•").strip()
        for line in takeaways_raw.splitlines()
        if line.lstrip("-*•").strip()
    ]

    out["quote"] = section_map.get("quote", "").strip()
    out["why_matters"] = section_map.get("why it matters", "").strip()

    # Tags / concepts / bite_size_minutes — search the full raw for the inline
    # markers (LLM may put them inside their own sections or jam them at end).
    m = _TAGS_RE.search(raw)
    if m:
        out["tags"] = [t.strip() for t in m.group(1).split(",") if t.strip()]
    m = _CONCEPTS_RE.search(raw)
    if m:
        out["concepts"] = [c.strip() for c in m.group(1).split(",") if c.strip()]
    m = _BITE_RE.search(raw)
    if m:
        try:
            out["bite_size_minutes"] = int(m.group(1))
        except ValueError:
            pass

    out["body"] = render_body(out)
    return out


def render_body(s: dict) -> str:
    """Render the structured synthesis dict back as a markdown body."""
    parts: list[str] = []
    if s["tldr"]:
        parts.append(f"## TL;DR\n\n{s['tldr']}")
    if s["takeaways"]:
        bullets = "\n".join(f"- {t}" for t in s["takeaways"])
        parts.append(f"## Key takeaways\n\n{bullets}")
    if s["quote"]:
        parts.append(f"## Quote\n\n{s['quote']}")
    if s["why_matters"]:
        parts.append(f"## Why it matters\n\n{s['why_matters']}")
    parts.append("## Connections\n\n_(none yet — populated as the corpus grows)_")
    parts.append("## Backlinks\n\n_(auto-built by `_shell/bin/build-backlinks.py`)_")
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Wiki page write — common to all ingest scripts
# ---------------------------------------------------------------------------

def write_entity_page(
    entity_type: str,
    slug: str,
    base_frontmatter: dict,
    synthesis_dict: dict,
    overwrite: bool = False,
) -> Path:
    """Write a wiki entity page from base_frontmatter + synthesis result.

    base_frontmatter must already contain type-specific fields. This adds
    common curator/wiki fields and merges in synthesis-derived tags/concepts/
    bite_size.

    Returns the path written.
    """
    page_path = WIKI / "entities" / _entity_folder(entity_type) / f"{slug}.md"

    # Merge synthesis-derived fields (do not overwrite explicit base values)
    fm = dict(base_frontmatter)
    fm.setdefault("slug", slug)
    fm.setdefault("type", entity_type)
    fm.setdefault("read_status", "ingested")
    fm.setdefault("delivered_at", None)
    fm.setdefault("delivery_count", 0)
    fm.setdefault("ingested_at", today())
    fm.setdefault("last_touched", today())
    if synthesis_dict.get("tags") and not fm.get("tags"):
        fm["tags"] = synthesis_dict["tags"]
    if synthesis_dict.get("concepts") and not fm.get("mentioned_concepts"):
        fm["mentioned_concepts"] = synthesis_dict["concepts"]
    if synthesis_dict.get("bite_size_minutes") and not fm.get("bite_size_minutes"):
        fm["bite_size_minutes"] = int(synthesis_dict["bite_size_minutes"])

    body = synthesis_dict.get("body") or render_body(synthesis_dict)

    if page_path.exists() and not overwrite:
        # Update mode — preserve curator-owned fields, refresh wiki-agent fields.
        existing_fm, existing_body = read_md(page_path)
        for k in ("read_status", "delivered_at", "delivery_count"):
            if k in existing_fm:
                fm[k] = existing_fm[k]
        # Hash compare body — skip if no meaningful change
        if content_hash(body) == content_hash(existing_body):
            return page_path
        fm["last_touched"] = today()

    write_md(page_path, fm, body)
    return page_path


def _entity_folder(entity_type: str) -> str:
    """Map entity type singular → folder name plural."""
    return {
        "book": "books",
        "paper": "papers",
        "article": "articles",
        "podcast": "podcasts",
        "lecture": "lectures",
        "youtube-video": "youtube-videos",
        "youtube-channel": "youtube-channels",
        "reel": "reels",
        "person": "people",
    }.get(entity_type, entity_type + "s")


# ---------------------------------------------------------------------------
# Person stub creation
# ---------------------------------------------------------------------------

def ensure_person_stub(
    canonical_name: str,
    role: str | list[str],
    domain: str | None = None,
) -> str:
    """Create or update a workspace-local person stub. Returns the slug."""
    slug = author_slug(canonical_name)
    page_path = WIKI / "entities" / "people" / f"{slug}.md"

    if isinstance(role, str):
        role = [role]

    if page_path.exists():
        fm, body = read_md(page_path)
        roles = set(fm.get("role") or [])
        roles.update(role)
        fm["role"] = sorted(roles)
        if domain and not fm.get("domain"):
            fm["domain"] = domain
        fm["last_touched"] = today()
        write_md(page_path, fm, body)
        return slug

    fm = {
        "slug": slug,
        "type": "person",
        "canonical_name": canonical_name,
        "role": role,
        "domain": domain,
        "last_touched": today(),
    }
    body = (
        "## Context\n\n"
        f"_(stub created during ingest of related source on {today()})_\n\n"
        "## Authored / hosted\n\n"
        "_(populated as the wiki agent processes more sources)_\n\n"
        "## Backlinks\n\n"
        "_(auto-built by `_shell/bin/build-backlinks.py`)_\n"
    )
    write_md(page_path, fm, body)
    return slug


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Sanity: slug functions
    assert slugify("The 7 Habits of Highly Effective People") == "the-7-habits-of-highly-effective-people"
    assert title_words_slug("The 7 Habits of Highly Effective People", 3) == "7-habits-highly"
    assert author_slug("James Clear") == "james-clear"
    assert author_slug("Yuval Noah Harari") == "yuval-harari"
    assert book_slug("Atomic Habits", "James Clear") == "clear-atomic-habits"
    assert youtube_video_slug("Optimize Your Sleep", "andrewhuberman") == "andrewhuberman-optimize-your-sleep"
    assert paper_slug("Attention Is All You Need", "Ashish Vaswani", 2017) == "vaswani-attention-all-you-2017"
    assert article_slug("Do Things That Don't Scale", "paulgraham.com") == "paulgraham-do-things-that-don"
    # Frontmatter roundtrip
    fm0 = {"slug": "test", "tags": ["a", "b"]}
    body0 = "## TL;DR\n\nhello\n"
    rendered = render_frontmatter(fm0) + body0
    fm1, body1 = parse_frontmatter(rendered)
    assert fm1 == fm0
    assert body1.strip() == body0.strip()
    print("lib_common self-tests OK")
