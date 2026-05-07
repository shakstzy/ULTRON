#!/usr/bin/env python3
"""
ingest-reel.py — Instagram reel/post ingest for the library workspace.

Wraps the global instagram-summary skill (`~/.claude/skills/instagram-summary/fetch.py`)
which already handles caption + visual + audio transcript via cloud-llm.
We capture its output, write raw, then re-synthesize into the library's
internalized voice via cloud-llm.

Usage:
  ingest-reel.py "https://www.instagram.com/reel/ABC123/"
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import lib_common as L

INSTAGRAM_VENV = Path.home() / ".ultron" / "instagram-summary" / ".venv" / "bin" / "python"
INSTAGRAM_FETCH = Path.home() / ".claude" / "skills" / "instagram-summary" / "fetch.py"
SHORTCODE_RE = re.compile(r"instagram\.com/(?:share/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)")


def call_instagram_summary(url: str, timeout: int = 240) -> str:
    """Run the instagram-summary fetch.py CLI and return stdout."""
    if not INSTAGRAM_VENV.exists():
        raise RuntimeError(f"instagram-summary venv missing at {INSTAGRAM_VENV}")
    if not INSTAGRAM_FETCH.exists():
        raise RuntimeError(f"instagram-summary fetch.py missing at {INSTAGRAM_FETCH}")
    proc = subprocess.run(
        [str(INSTAGRAM_VENV), str(INSTAGRAM_FETCH), url],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"instagram-summary failed: {proc.stderr.strip()[:300]}")
    return proc.stdout


def parse_instagram_output(out: str) -> dict:
    """Parse the TYPE/AUTHOR/DATE/CAPTION/TRANSCRIPT/SUMMARY block printed by fetch.py."""
    fields: dict = {"raw_output": out}
    sections: dict[str, list[str]] = {}
    current = None
    for line in out.splitlines():
        m = re.match(r"^([A-Z][A-Z_+ ]*[A-Z]):\s*(.*)$", line)
        if m and m.group(1) in {
            "TYPE", "AUTHOR", "DATE", "LIKES", "COMMENTS", "CAROUSEL",
            "CAPTION", "AUDIO TRANSCRIPT", "VISUAL+SYNTHESIS SUMMARY",
        }:
            current = m.group(1)
            sections.setdefault(current, []).append(m.group(2))
        elif current:
            sections.setdefault(current, []).append(line)
    for k, v in sections.items():
        fields[k] = "\n".join(v).strip()
    return fields


def ingest_reel(url: str, overwrite: bool = False) -> Path:
    m = SHORTCODE_RE.search(url)
    if not m:
        raise ValueError(f"could not parse instagram shortcode from {url!r}")
    shortcode = m.group(1)

    print(f"  calling instagram-summary on {shortcode}…")
    raw_out = call_instagram_summary(url)
    parsed = parse_instagram_output(raw_out)

    type_field = parsed.get("TYPE", "post").strip()
    author_handle = parsed.get("AUTHOR", "@unknown").lstrip("@").strip() or "unknown"
    date_iso = parsed.get("DATE", "")
    published_at = date_iso[:10] if len(date_iso) >= 10 else L.today()
    caption = parsed.get("CAPTION", "")
    transcript = parsed.get("AUDIO TRANSCRIPT", "")
    visual_summary = parsed.get("VISUAL+SYNTHESIS SUMMARY", "")

    slug = L.reel_slug(author_handle, published_at, shortcode)

    # Raw write
    raw_path = L.RAW / "reels" / L.slugify(author_handle) / published_at[:7] / f"{slug}.md"
    raw_meta = {
        "slug": slug,
        "instagram_type": type_field,
        "creator_handle": f"@{author_handle}",
        "url": url,
        "shortcode": shortcode,
        "published_at": published_at,
        "ingested_at": L.today(),
    }
    raw_body = (
        f"## Caption\n\n{caption or '_(none)_'}\n\n"
        f"## Audio transcript\n\n{transcript or '_(none)_'}\n\n"
        f"## Visual + synthesis (instagram-summary skill)\n\n{visual_summary or '_(none)_'}\n"
    )
    L.write_md(raw_path, raw_meta, raw_body)

    # Re-synthesize through library voice
    print(f"  re-synthesizing in library voice")
    syn = L.synthesize(
        metadata={
            "creator_handle": f"@{author_handle}",
            "type": type_field,
            "url": url,
            "published_at": published_at,
        },
        content=(
            f"CAPTION:\n{caption}\n\n"
            f"AUDIO TRANSCRIPT:\n{transcript}\n\n"
            f"VISUAL ANALYSIS:\n{visual_summary}\n"
        ),
        max_content_chars=20_000,
    )

    creator_slug = L.ensure_person_stub(f"@{author_handle}", role="speaker", domain=None)
    base_fm = {
        "type": "reel",
        "url": url,
        "creator_handle": f"@{author_handle}",
        "authors": [creator_slug],
        "caption": (caption.splitlines()[0][:200] if caption else ""),
        "duration_seconds": None,
        "published_at": published_at,
        "tags": [],
        "mentioned_concepts": [],
        "mentioned_books": [],
        "bite_size_minutes": 1,
    }
    page = L.write_entity_page("reel", slug, base_fm, syn, overwrite=overwrite)
    print(f"  wrote {page.relative_to(L.WORKSPACE)}")
    L.log_event(f"ingest-reel: {slug} ({author_handle})")
    L.log_ingest("reel", slug, "ok", {"creator": author_handle, "shortcode": shortcode})
    return page


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    try:
        ingest_reel(args.url, overwrite=args.overwrite)
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
