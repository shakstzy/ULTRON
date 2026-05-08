#!/usr/bin/env python3
"""
ingest-article.py — capture a web article into the library workspace's raw/.

Pure capture: defuddle (or stdlib heuristic fallback) to extract clean
markdown, then write ONE file at `raw/articles/<YYYY-MM>/<slug>.md` with the
universal envelope per `_shell/stages/ingest/CONTEXT.md`. NO cloud-llm. NO
wiki writes. The wiki layer is built downstream by `/graphify --wiki`.

Usage:
  ingest-article.py "https://paulgraham.com/ds.html"
  ingest-article.py "https://example.com/post" --title "X" --author "Y"
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
SOURCE = "article"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        raw = resp.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def defuddle_extract(url: str) -> dict | None:
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
    """Stdlib fallback: <article> if present, else <body>, strip tags."""
    html = fetch_text(url)
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    article_m = re.search(r"<article[^>]*>(.*?)</article>", html, re.DOTALL | re.IGNORECASE)
    if article_m:
        body_html = article_m.group(1)
    else:
        body_m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
        body_html = body_m.group(1) if body_m else html
    body_html = re.sub(r"<(script|style|nav|footer|aside)[^>]*>.*?</\1>", " ",
                       body_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = re.sub(r"\s+", " ", text).strip()
    author_m = re.search(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)',
                         html, re.IGNORECASE)
    author = author_m.group(1) if author_m else None
    domain = urllib.parse.urlparse(url).netloc
    return {
        "title": title, "author": author, "domain": domain,
        "published": None, "description": None, "content_md": text,
    }


def ingest_article(
    url: str,
    title_override: str | None = None,
    author_override: str | None = None,
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
        raise RuntimeError(f"extracted content too short ({len(content_md)} chars); aborted")

    slug = L.article_slug(title, domain)
    ym = (published[:7] if (published and len(published) >= 7) else L.today_year_month())
    raw_path = L.RAW / "articles" / ym / f"{slug}.md"

    extra = {
        "slug": slug,
        "title": title,
        "author": author,
        "url": url,
        "source_domain": domain,
        "description": extracted.get("description"),
    }
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=content_md,
        provider_modified_at=published,
        extra=extra,
    )
    print(f"  wrote raw/{raw_path.relative_to(L.RAW)}")
    L.log_event(f"ingest-article: {slug} ({title!r})")
    L.log_ingest("article", slug, "ok", {"domain": domain})
    return raw_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--title")
    ap.add_argument("--author")
    args = ap.parse_args()
    try:
        ingest_article(args.url, args.title, args.author)
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
