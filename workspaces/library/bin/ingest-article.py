#!/usr/bin/env python3
"""
ingest-article.py — web article ingest for the library workspace.

Usage:
  ingest-article.py "https://paulgraham.com/ds.html"
  ingest-article.py "https://example.com/post" --title "X" --author "Y"

Pipeline:
  1. Fetch URL via defuddle (preferred) or stdlib HTTP + heuristic readability
  2. Synthesize wiki entity page via cloud-llm
  3. Write raw + wiki, log
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import lib_common as L

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 ULTRON-library/1.0"
HTTP_TIMEOUT = 30


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        raw = resp.read()
    # Try utf-8, then fallback
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def defuddle_extract(url: str) -> dict | None:
    """Returns {title, content_md, domain} or None if defuddle unavailable/failed."""
    if not shutil.which("defuddle"):
        return None
    try:
        proc = subprocess.run(
            ["defuddle", "parse", url, "--json"],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        sys.stderr.write(f"  defuddle threw: {e}\n")
        return None
    if proc.returncode != 0:
        sys.stderr.write(f"  defuddle failed: {proc.stderr.strip()[:200]}\n")
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return {
        "title": data.get("title"),
        "author": data.get("author"),
        "domain": data.get("domain"),
        "published": data.get("published"),
        "description": data.get("description"),
        "content_md": data.get("markdownContent") or data.get("content") or "",
    }


def heuristic_extract(url: str) -> dict:
    """Stdlib fallback when defuddle is absent. Strips tags, picks <article> if present."""
    html = fetch_text(url)
    # Title from <title>
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    # Try <article>; fall back to <body>
    article_m = re.search(r"<article[^>]*>(.*?)</article>", html, re.DOTALL | re.IGNORECASE)
    if article_m:
        body_html = article_m.group(1)
    else:
        body_m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
        body_html = body_m.group(1) if body_m else html
    # Drop scripts and styles
    body_html = re.sub(r"<(script|style|nav|footer|aside)[^>]*>.*?</\1>", " ", body_html, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = re.sub(r"\s+", " ", text).strip()
    # Author meta
    author_m = re.search(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)', html, re.IGNORECASE)
    author = author_m.group(1) if author_m else None
    # Domain
    domain = urllib.parse.urlparse(url).netloc
    return {
        "title": title,
        "author": author,
        "domain": domain,
        "published": None,
        "description": None,
        "content_md": text,
    }


def ingest_article(
    url: str,
    title_override: str | None = None,
    author_override: str | None = None,
    overwrite: bool = False,
) -> Path:
    print(f"  extracting {url}")
    extracted = defuddle_extract(url)
    if not extracted:
        print("  defuddle unavailable; using heuristic extractor")
        extracted = heuristic_extract(url)

    title = title_override or extracted.get("title") or "(untitled)"
    author = author_override or extracted.get("author")
    domain = extracted.get("domain") or urllib.parse.urlparse(url).netloc
    published = extracted.get("published")
    content_md = extracted.get("content_md") or ""

    if len(content_md) < 200:
        raise RuntimeError(f"extracted content too short ({len(content_md)} chars); article ingest aborted")

    slug = L.article_slug(title, domain)

    # Raw write
    ym = L.today_year_month()
    raw_path = L.RAW / "articles" / ym / f"{slug}.md"
    raw_meta = {
        "slug": slug,
        "title": title,
        "author": author,
        "url": url,
        "source_domain": domain,
        "published_at": published,
        "ingested_at": L.today(),
    }
    L.write_md(raw_path, raw_meta, content_md)

    print(f"  synthesizing wiki page via cloud-llm…")
    syn = L.synthesize(
        metadata={"title": title, "author": author, "url": url, "domain": domain, "type": "article"},
        content=content_md,
        max_content_chars=60_000,
    )

    # Author stub (optional)
    author_slugs = []
    if author:
        author_slugs.append(L.ensure_person_stub(author, role="author", domain=None))

    base_fm = {
        "type": "article",
        "title": title,
        "authors": author_slugs,
        "source_domain": domain,
        "url": url,
        "published_at": published,
        "tags": [],
        "mentioned_concepts": [],
        "mentioned_books": [],
    }
    page = L.write_entity_page("article", slug, base_fm, syn, overwrite=overwrite)
    print(f"  wrote {page.relative_to(L.WORKSPACE)}")
    L.log_event(f"ingest-article: {slug} ({title!r})")
    L.log_ingest("article", slug, "ok", {"domain": domain})
    return page


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    try:
        ingest_article(args.url, args.title, args.author, args.overwrite)
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
