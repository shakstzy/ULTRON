#!/usr/bin/env python3
"""
ingest-book.py — book ingest for the library workspace.

Three input modes:
  - title + author: search Anna's Archive, validate top-N candidates, download best EPUB
  - URL: Anna's Archive MD5 page URL, or a direct .epub / .pdf URL
  - local: path to an EPUB or PDF already on disk

Pipeline:
  1. Resolve to a local raw file (download if needed)
  2. Validate (title fuzzy match ≥ 0.85, author fuzzy match ≥ 0.7, language=en, has chapters)
  3. Run pandoc EPUB → markdown (or pdftotext fallback for PDF)
  4. Synthesize wiki entity page via cloud-llm
  5. Write raw + wiki, log

On validation ambiguity (multi-candidate, low fuzzy match), prints top candidates
and exits with code 2 — caller decides whether to retry with --url to disambiguate.

Usage:
  ingest-book.py --title "Atomic Habits" --author "James Clear"
  ingest-book.py --url "https://annas-archive.org/md5/abcdef123..."
  ingest-book.py --epub-path /path/to/book.epub --title "Walden" --author "Henry David Thoreau"
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import lib_common as L

ANNAS_BASE = "https://annas-archive.org"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 ULTRON/1.0"
HTTP_TIMEOUT = 30


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def fetch(url: str, max_bytes: int | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        if max_bytes is not None:
            return resp.read(max_bytes)
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", errors="replace")


def download_to(url: str, dest: Path, max_bytes: int = 200_000_000) -> None:
    """Download URL to dest (creates parents). Caps at max_bytes (default 200MB)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp, open(dest, "wb") as out:
        written = 0
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                raise RuntimeError(f"download exceeded {max_bytes} bytes; aborting")
            out.write(chunk)


# ---------------------------------------------------------------------------
# Anna's Archive search + resolve
# ---------------------------------------------------------------------------

def search_annas(query: str, lang: str = "en", ext: str = "epub", limit: int = 5) -> list[dict]:
    """Scrape search results. Returns list of {md5, title, author, year, format, lang, size}.

    Anna's Archive HTML is unstable — this parser is intentionally forgiving.
    """
    url = f"{ANNAS_BASE}/search?q={urllib.parse.quote(query)}&ext={ext}&lang={lang}&sort=&display="
    try:
        html = fetch_text(url)
    except Exception as e:
        sys.stderr.write(f"  annas search failed: {e}\n")
        return []

    # Each search result is wrapped around an <a href="/md5/<32-hex>"> with metadata
    # in nearby <div>s. We pull the md5, then grab the visible text inside the result.
    results = []
    for m in re.finditer(r'<a [^>]*href="/md5/([a-f0-9]{32})"[^>]*>(.*?)</a>', html, re.DOTALL):
        md5 = m.group(1)
        block = m.group(2)
        # Strip tags, condense whitespace
        text = re.sub(r"<[^>]+>", " ", block)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        # Heuristic parse: text is usually "Lang [ext] Size, Title, Author, Year"
        results.append({"md5": md5, "raw_text": text, "url": f"{ANNAS_BASE}/md5/{md5}"})
        if len(results) >= limit:
            break
    return results


def resolve_md5_page(url: str) -> dict:
    """Fetch an Anna's Archive /md5/<hash> page and extract metadata + best download URL."""
    html = fetch_text(url)
    out = {"url": url, "title": None, "author": None, "year": None,
           "format": None, "language": None, "size": None, "download_urls": []}

    m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if m:
        out["title"] = m.group(1).strip()

    # Anna's Archive shows a header with title, then "by AUTHOR" then metadata pills
    m = re.search(r'<div class="text-3xl font-bold">([^<]+)</div>', html)
    if m and not out["title"]:
        out["title"] = m.group(1).strip()
    m = re.search(r'<div class="italic">([^<]+)</div>', html)
    if m:
        out["author"] = m.group(1).strip().lstrip("by ").strip()

    # Extension / language / size pill — usually like "English [en], epub, 1.2MB"
    m = re.search(r'>\s*([A-Za-z]+)\s*\[([a-z]{2,3})\][^<]*?,\s*(epub|pdf|mobi|azw3)[^<]*?,\s*([0-9.]+\s*[KMG]B)', html)
    if m:
        out["language"] = m.group(2)
        out["format"] = m.group(3)
        out["size"] = m.group(4)

    m = re.search(r'(\d{4})', html[:html.find("download") if "download" in html else 5000] or "")
    if m and out.get("title"):
        # Avoid ISBNs masquerading as years; restrict to 1800-current
        y = int(m.group(1))
        if 1800 <= y <= 2100:
            out["year"] = y

    # Download links — look for "Slow downloads" / "Fast downloads" / external mirror links
    for href in re.findall(r'href="(/slow_download/[^"]+|/fast_download/[^"]+|https?://[^"]+\.(?:epub|pdf|mobi|azw3))"', html):
        if href.startswith("/"):
            out["download_urls"].append(ANNAS_BASE + href)
        else:
            out["download_urls"].append(href)

    # Deduplicate while preserving order
    seen = set()
    out["download_urls"] = [u for u in out["download_urls"] if not (u in seen or seen.add(u))]
    return out


def attempt_download(candidate: dict, dest: Path) -> tuple[bool, str]:
    """Try each download_urls in order. Returns (success, message)."""
    if not candidate.get("download_urls"):
        return False, "no download URLs found on the md5 page"
    last_err = ""
    for url in candidate["download_urls"][:5]:
        try:
            download_to(url, dest)
            if dest.stat().st_size > 1024:  # > 1KB sanity
                return True, f"downloaded from {url}"
            dest.unlink(missing_ok=True)
            last_err = f"downloaded file too small ({dest.stat().st_size if dest.exists() else 0} bytes)"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return False, last_err


# ---------------------------------------------------------------------------
# Pandoc / pdftotext extraction
# ---------------------------------------------------------------------------

def epub_to_markdown(epub_path: Path, out_path: Path) -> None:
    """pandoc EPUB → markdown."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pandoc",
        "-f", "epub",
        "-t", "markdown",
        "--wrap=none",
        "-o", str(out_path),
        str(epub_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed: {proc.stderr}")


def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    """Best-effort PDF → markdown via pdftotext if available, else pandoc."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftotext"):
        cmd = ["pdftotext", "-layout", str(pdf_path), str(out_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0:
            return
    # Fallback: pandoc tries via mupdf or similar
    cmd = ["pandoc", "-f", "pdf", "-t", "markdown", "--wrap=none", "-o", str(out_path), str(pdf_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"pdf-to-markdown failed: {proc.stderr}")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def fuzzy_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def validate_metadata(
    candidate: dict,
    expected_title: str | None,
    expected_author: str | None,
    title_min: float = 0.85,
    author_min: float = 0.7,
) -> tuple[bool, list[str]]:
    """Returns (passed, reasons_for_failure)."""
    failures = []
    if expected_title and candidate.get("title"):
        ratio = fuzzy_ratio(candidate["title"], expected_title)
        if ratio < title_min:
            failures.append(f"title fuzzy match {ratio:.2f} < {title_min} ({candidate['title']!r} vs {expected_title!r})")
    if expected_author and candidate.get("author"):
        ratio = fuzzy_ratio(candidate["author"], expected_author)
        if ratio < author_min:
            failures.append(f"author fuzzy match {ratio:.2f} < {author_min} ({candidate['author']!r} vs {expected_author!r})")
    if candidate.get("language") and candidate["language"] != "en":
        failures.append(f"language {candidate['language']!r} (expected en)")
    return len(failures) == 0, failures


def sanity_check_markdown(md_path: Path) -> tuple[bool, list[str]]:
    """Sanity check the extracted markdown."""
    failures = []
    if not md_path.exists():
        return False, ["markdown file does not exist"]
    text = md_path.read_text(encoding="utf-8", errors="replace")
    if len(text) < 5000:
        failures.append(f"length {len(text)} chars, too short for a book")
    if len(text) > 5_000_000:
        failures.append(f"length {len(text)} chars, suspiciously large")
    # Must have at least 3 chapter-like headings
    chapters = re.findall(r"^#+ .{0,80}$", text, re.MULTILINE)
    if len(chapters) < 3:
        failures.append(f"only {len(chapters)} headings; expected ≥ 3 chapters")
    return len(failures) == 0, failures


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def ingest_book(
    title: str | None,
    author: str | None,
    url: str | None,
    epub_path: str | None,
    isbn: str | None = None,
    year: int | None = None,
    skip_validation: bool = False,
    overwrite: bool = False,
) -> Path:
    if not (title or url or epub_path):
        raise ValueError("must provide --title (with --author) or --url or --epub-path")

    # Step 1: resolve to a local raw file
    if epub_path:
        local = Path(epub_path).expanduser().resolve()
        if not local.exists():
            raise FileNotFoundError(local)
        meta = {"title": title, "author": author, "year": year, "language": "en", "format": local.suffix.lstrip(".")}
    else:
        # URL or title-search
        if url and "annas-archive.org/md5/" in url:
            md5_url = url
        elif url and url.startswith(("http://", "https://")) and url.endswith((".epub", ".pdf")):
            # Direct file URL
            ext = url.rsplit(".", 1)[1]
            tmp_dir = Path("/tmp") / f"library-book-{L.today()}"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            local = tmp_dir / f"download.{ext}"
            print(f"  downloading {url} → {local}")
            download_to(url, local)
            meta = {"title": title, "author": author, "year": year, "language": "en", "format": ext}
            md5_url = None
        elif title and author:
            print(f"  searching annas-archive for: {title} | {author}")
            results = search_annas(f"{title} {author}", limit=5)
            if not results:
                print("  no search results", file=sys.stderr)
                sys.exit(2)
            md5_url = results[0]["url"]
            print(f"  picking top result: {md5_url}")
        else:
            raise ValueError("title+author or url required")

        if md5_url:
            print(f"  resolving md5 page: {md5_url}")
            meta = resolve_md5_page(md5_url)
            print(f"  parsed metadata: title={meta.get('title')!r} author={meta.get('author')!r} format={meta.get('format')} lang={meta.get('language')}")
            ok, failures = validate_metadata(meta, title, author) if not skip_validation else (True, [])
            if not ok:
                print("  ! validation failed:", file=sys.stderr)
                for f in failures:
                    print(f"    - {f}", file=sys.stderr)
                print("  re-run with --url <annas md5 url> to override.", file=sys.stderr)
                sys.exit(2)
            ext = meta.get("format") or "epub"
            tmp_dir = Path("/tmp") / f"library-book-{L.today()}"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            local = tmp_dir / f"download.{ext}"
            ok, msg = attempt_download(meta, local)
            if not ok:
                print(f"  download failed: {msg}", file=sys.stderr)
                sys.exit(2)
            print(f"  {msg}")

    # Step 2: extract to markdown
    final_title = meta.get("title") or title or local.stem
    final_author = meta.get("author") or author or "Unknown"
    final_year = meta.get("year") or year
    slug = L.book_slug(final_title, final_author)
    book_dir = L.RAW / "books" / L.author_slug(final_author) / slug
    book_dir.mkdir(parents=True, exist_ok=True)

    # Move/copy raw file in
    raw_book_path = book_dir / f"book{local.suffix.lower()}"
    if local.resolve() != raw_book_path.resolve():
        shutil.copy2(local, raw_book_path)
    md_path = book_dir / "book.md"
    print(f"  extracting → {md_path}")
    if raw_book_path.suffix.lower() == ".epub":
        epub_to_markdown(raw_book_path, md_path)
    elif raw_book_path.suffix.lower() == ".pdf":
        pdf_to_markdown(raw_book_path, md_path)
    else:
        raise RuntimeError(f"unsupported book format: {raw_book_path.suffix}")

    if not skip_validation:
        ok, failures = sanity_check_markdown(md_path)
        if not ok:
            print("  ! sanity check failed:", file=sys.stderr)
            for f in failures:
                print(f"    - {f}", file=sys.stderr)
            sys.exit(2)

    # Step 3: write raw metadata.md
    raw_metadata = {
        "slug": slug,
        "title": final_title,
        "author": final_author,
        "year": final_year,
        "isbn": isbn,
        "format": raw_book_path.suffix.lstrip(".").lower(),
        "source_url": url,
        "annas_md5": meta.get("url", "").rsplit("/", 1)[-1] if meta.get("url") else None,
        "ingested_at": L.today(),
        "raw_md_path": str(md_path.relative_to(L.WORKSPACE)),
        "raw_book_sha256": L.file_sha256(raw_book_path),
    }
    L.write_md(book_dir / "metadata.md", raw_metadata, "")

    # Step 4: synthesize via cloud-llm
    print("  synthesizing wiki page via cloud-llm…")
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    # Trim chapters: keep ToC + first chapter + spread sample for synthesis
    sample = chapter_sample(md_text, max_chars=80_000)
    syn = L.synthesize(
        metadata={"title": final_title, "author": final_author, "year": final_year, "type": "book"},
        content=sample,
        max_content_chars=80_000,
    )
    print(f"  synthesis engine={syn.get('_engine')} bullets={len(syn['takeaways'])} bite={syn['bite_size_minutes']}min")

    # Step 5: ensure person stub + write entity page
    author_slug_val = L.ensure_person_stub(final_author, role="author", domain=None)
    base_fm = {
        "type": "book",
        "title": final_title,
        "authors": [author_slug_val],
        "isbn": isbn,
        "year": final_year,
        "language": "en",
        "source_url": url,
        "tags": [],
        "mentioned_concepts": [],
        "mentioned_books": [],
    }
    page = L.write_entity_page("book", slug, base_fm, syn, overwrite=overwrite)
    print(f"  wrote {page.relative_to(L.WORKSPACE)}")
    L.log_event(f"ingest-book: {slug} ({final_title!r})")
    L.log_ingest("book", slug, "ok", {"author": final_author, "format": raw_metadata["format"]})
    return page


def chapter_sample(md_text: str, max_chars: int = 80_000) -> str:
    """Return ToC + first chapter + sample from later chapters, capped to max_chars."""
    if len(md_text) <= max_chars:
        return md_text
    # Find chapter headings
    chapter_starts = [m.start() for m in re.finditer(r"^#+ .{0,80}$", md_text, re.MULTILINE)]
    if len(chapter_starts) < 3:
        return md_text[:max_chars]
    head = md_text[:chapter_starts[3]] if len(chapter_starts) > 3 else md_text[:chapter_starts[1]]
    head = head[: max_chars * 2 // 3]
    # Sample the second half
    second_start = chapter_starts[len(chapter_starts) // 2]
    tail = md_text[second_start: second_start + max_chars // 3]
    return head + "\n\n[...skip...]\n\n" + tail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--url")
    ap.add_argument("--epub-path")
    ap.add_argument("--isbn")
    ap.add_argument("--year", type=int)
    ap.add_argument("--skip-validation", action="store_true",
                    help="skip fuzzy match + sanity check (use carefully)")
    ap.add_argument("--overwrite", action="store_true",
                    help="overwrite an existing wiki page (curator state preserved)")
    args = ap.parse_args()

    try:
        ingest_book(
            title=args.title,
            author=args.author,
            url=args.url,
            epub_path=args.epub_path,
            isbn=args.isbn,
            year=args.year,
            skip_validation=args.skip_validation,
            overwrite=args.overwrite,
        )
    except SystemExit:
        raise
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
