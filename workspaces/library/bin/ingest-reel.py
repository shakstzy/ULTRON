#!/usr/bin/env python3
"""
ingest-reel.py — capture an Instagram reel/post into the library workspace's raw/.

Pure capture: wrap the global instagram-summary skill (which already does
caption + visual + audio transcript via cloud-llm), then write ONE file at
`raw/reels/<creator>/<YYYY-MM>/<slug>.md` with the universal envelope. The
body holds caption + transcript + visual analysis sections produced by
instagram-summary. NO additional cloud-llm. NO wiki writes.

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
SOURCE = "instagram-reel"


def call_instagram_summary(url: str, timeout: int = 240) -> str:
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


def ingest_reel(url: str) -> Path:
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
    published_at = (date_iso[:19] + "Z") if len(date_iso) >= 19 else None
    published_day = (published_at or L.iso_utc())[:10]
    caption = parsed.get("CAPTION", "")
    transcript = parsed.get("AUDIO TRANSCRIPT", "")
    visual_summary = parsed.get("VISUAL+SYNTHESIS SUMMARY", "")

    slug = L.reel_slug(author_handle, published_day, shortcode)
    raw_path = L.RAW / "reels" / L.slugify(author_handle) / published_day[:7] / f"{slug}.md"

    body = (
        f"## Caption\n\n{caption or '_(none)_'}\n\n"
        f"## Audio transcript\n\n{transcript or '_(none)_'}\n\n"
        f"## Visual + synthesis (instagram-summary)\n\n{visual_summary or '_(none)_'}\n"
    )

    extra = {
        "slug": slug,
        "instagram_type": type_field,
        "creator_handle": f"@{author_handle}",
        "url": url,
        "shortcode": shortcode,
        "caption_preview": (caption.splitlines()[0][:200] if caption else ""),
    }
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=body,
        provider_modified_at=published_at,
        extra=extra,
    )
    print(f"  wrote raw/{raw_path.relative_to(L.RAW)}")
    L.log_event(f"ingest-reel: {slug} ({author_handle})")
    L.log_ingest("reel", slug, "ok", {"creator": author_handle, "shortcode": shortcode})
    return raw_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    args = ap.parse_args()
    try:
        ingest_reel(args.url)
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
