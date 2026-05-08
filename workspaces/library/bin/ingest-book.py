#!/usr/bin/env python3
"""
ingest-book.py — capture a book into the library workspace's raw/.

Pure capture: search Anna's Archive (or take a direct URL / local file),
download the EPUB (PDF fallback), extract markdown via pandoc, write ONE
file at `raw/books/<author>/<slug>.md` with the universal envelope. The
original EPUB stays alongside as `<slug>.epub` for re-extraction. NO
cloud-llm. NO wiki writes.

Three input modes:
  ingest-book.py --title "Walden" --author "Henry David Thoreau"
  ingest-book.py --url "https://annas-archive.org/md5/<32hex>"
  ingest-book.py --url "https://www.gutenberg.org/ebooks/205.epub.images" --title Walden --author "Henry David Thoreau" --skip-validation
  ingest-book.py --epub-path /path/to/book.epub --title X --author Y
"""
from __future__ import annotations

import argparse
import difflib
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
SOURCE = "book"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", errors="replace")


def download_to(url: str, dest: Path, max_bytes: int = 200_000_000) -> None:
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


def try_direct_download(url: str, hint_ext_in_url: str = "") -> Path | None:
    """Try downloading url as a book file (epub/pdf). Sniffs Content-Type and
    magic bytes when the URL doesn't end in a known extension."""
    tmp_dir = Path("/tmp") / f"library-book-{L.today()}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            ext: str | None = None
            if "epub" in ctype or ".epub" in hint_ext_in_url:
                ext = "epub"
            elif "pdf" in ctype or ".pdf" in hint_ext_in_url:
                ext = "pdf"
            if ext is None:
                first = resp.read(4)
                if first.startswith(b"PK"):
                    ext = "epub"
                elif first.startswith(b"%PDF"):
                    ext = "pdf"
                else:
                    return None
                local = tmp_dir / f"download.{ext}"
                with open(local, "wb") as out:
                    out.write(first)
                    written = len(first)
                    while True:
                        chunk = resp.read(64 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > 200_000_000:
                            raise RuntimeError("download exceeded 200MB")
                        out.write(chunk)
                if local.stat().st_size < 1024:
                    return None
                print(f"  downloaded {local.stat().st_size:,} bytes → {local}")
                return local
            local = tmp_dir / f"download.{ext}"
            with open(local, "wb") as out:
                written = 0
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > 200_000_000:
                        raise RuntimeError("download exceeded 200MB")
                    out.write(chunk)
            if local.stat().st_size < 1024:
                return None
            print(f"  downloaded {local.stat().st_size:,} bytes ({ctype}) → {local}")
            return local
    except Exception as e:
        sys.stderr.write(f"  direct download failed: {type(e).__name__}: {e}\n")
        return None


# ---------------------------------------------------------------------------
# Anna's Archive
# ---------------------------------------------------------------------------

def search_annas(query: str, lang: str = "en", ext: str = "epub", limit: int = 5) -> list[dict]:
    url = f"{ANNAS_BASE}/search?q={urllib.parse.quote(query)}&ext={ext}&lang={lang}&sort=&display="
    try:
        html = fetch_text(url)
    except Exception as e:
        sys.stderr.write(f"  annas search failed: {e}\n")
        return []
    results = []
    for m in re.finditer(r'<a [^>]*href="/md5/([a-f0-9]{32})"[^>]*>(.*?)</a>', html, re.DOTALL):
        md5 = m.group(1)
        block = m.group(2)
        text = re.sub(r"<[^>]+>", " ", block)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        results.append({"md5": md5, "raw_text": text, "url": f"{ANNAS_BASE}/md5/{md5}"})
        if len(results) >= limit:
            break
    return results


def resolve_md5_page(url: str) -> dict:
    html = fetch_text(url)
    out = {"url": url, "title": None, "author": None, "year": None,
           "format": None, "language": None, "size": None, "download_urls": []}
    m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if m:
        out["title"] = m.group(1).strip()
    m = re.search(r'<div class="text-3xl font-bold">([^<]+)</div>', html)
    if m and not out["title"]:
        out["title"] = m.group(1).strip()
    m = re.search(r'<div class="italic">([^<]+)</div>', html)
    if m:
        out["author"] = m.group(1).strip().lstrip("by ").strip()
    m = re.search(r'>\s*([A-Za-z]+)\s*\[([a-z]{2,3})\][^<]*?,\s*(epub|pdf|mobi|azw3)[^<]*?,\s*([0-9.]+\s*[KMG]B)', html)
    if m:
        out["language"] = m.group(2)
        out["format"] = m.group(3)
        out["size"] = m.group(4)
    m = re.search(r'(\d{4})', html[:5000])
    if m:
        y = int(m.group(1))
        if 1800 <= y <= 2100:
            out["year"] = y
    for href in re.findall(r'href="(/slow_download/[^"]+|/fast_download/[^"]+|https?://[^"]+\.(?:epub|pdf|mobi|azw3))"', html):
        if href.startswith("/"):
            out["download_urls"].append(ANNAS_BASE + href)
        else:
            out["download_urls"].append(href)
    seen = set()
    out["download_urls"] = [u for u in out["download_urls"] if not (u in seen or seen.add(u))]
    return out


def attempt_download(candidate: dict, dest: Path) -> tuple[bool, str]:
    if not candidate.get("download_urls"):
        return False, "no download URLs found on the md5 page"
    last_err = ""
    for url in candidate["download_urls"][:5]:
        try:
            download_to(url, dest)
            if dest.stat().st_size > 1024:
                return True, f"downloaded from {url}"
            dest.unlink(missing_ok=True)
            last_err = f"downloaded file too small"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return False, last_err


# ---------------------------------------------------------------------------
# Pandoc / pdftotext extraction
# ---------------------------------------------------------------------------

def epub_to_markdown(epub_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pandoc", "-f", "epub", "-t", "markdown", "--wrap=none", "-o", str(out_path), str(epub_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed: {proc.stderr}")


def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftotext"):
        cmd = ["pdftotext", "-layout", str(pdf_path), str(out_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0:
            return
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


def sanity_check_markdown(md_text: str) -> tuple[bool, list[str]]:
    failures = []
    if len(md_text) < 5000:
        failures.append(f"length {len(md_text)} chars, too short for a book")
    if len(md_text) > 5_000_000:
        failures.append(f"length {len(md_text)} chars, suspiciously large")
    chapters = re.findall(r"^#+ .{0,80}$", md_text, re.MULTILINE)
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
) -> Path:
    if not (title or url or epub_path):
        raise ValueError("must provide --title (with --author) or --url or --epub-path")

    if epub_path:
        local = Path(epub_path).expanduser().resolve()
        if not local.exists():
            raise FileNotFoundError(local)
        meta = {"title": title, "author": author, "year": year, "language": "en", "format": local.suffix.lstrip(".")}
    else:
        md5_url: str | None = None
        local: Path | None = None
        if url and "annas-archive.org/md5/" in url:
            md5_url = url
        elif url:
            local = try_direct_download(url, hint_ext_in_url=url.lower())
            if local is None and title and author:
                print(f"  direct download did not yield epub/pdf; falling back to annas search")
            elif local is not None:
                meta = {"title": title, "author": author, "year": year, "language": "en",
                        "format": local.suffix.lstrip(".")}
        if local is None and md5_url is None:
            if not (title and author):
                raise ValueError("URL did not resolve and no title+author for fallback search")
            print(f"  searching annas-archive for: {title} | {author}")
            results = search_annas(f"{title} {author}", limit=5)
            if not results:
                print("  no search results", file=sys.stderr)
                sys.exit(2)
            md5_url = results[0]["url"]
            print(f"  picking top result: {md5_url}")
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

    final_title = meta.get("title") or title or local.stem
    final_author = meta.get("author") or author or "Unknown"
    final_year = meta.get("year") or year
    slug = L.book_slug(final_title, final_author)
    book_dir = L.RAW / "books" / L.author_slug(final_author)
    book_dir.mkdir(parents=True, exist_ok=True)

    raw_artifact_path = book_dir / f"{slug}{local.suffix.lower()}"
    if local.resolve() != raw_artifact_path.resolve():
        shutil.copy2(local, raw_artifact_path)

    body_path = book_dir / f"{slug}.body.md"
    if raw_artifact_path.suffix.lower() == ".epub":
        epub_to_markdown(raw_artifact_path, body_path)
    elif raw_artifact_path.suffix.lower() == ".pdf":
        pdf_to_markdown(raw_artifact_path, body_path)
    else:
        raise RuntimeError(f"unsupported book format: {raw_artifact_path.suffix}")
    body = body_path.read_text(encoding="utf-8", errors="replace")
    body_path.unlink(missing_ok=True)

    if not skip_validation:
        ok, failures = sanity_check_markdown(body)
        if not ok:
            print("  ! sanity check failed:", file=sys.stderr)
            for f in failures:
                print(f"    - {f}", file=sys.stderr)
            sys.exit(2)

    raw_path = book_dir / f"{slug}.md"
    extra = {
        "slug": slug,
        "title": final_title,
        "author": final_author,
        "year": final_year,
        "isbn": isbn,
        "language": "en",
        "format": raw_artifact_path.suffix.lstrip(".").lower(),
        "source_url": url,
        "annas_md5": (meta.get("url") or "").rsplit("/", 1)[-1] if meta.get("url") else None,
        "artifact_sha256": L.file_sha256(raw_artifact_path),
    }
    provider_modified_at = f"{final_year:04d}-01-01T00:00:00Z" if isinstance(final_year, int) else None
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=body,
        provider_modified_at=provider_modified_at,
        extra=extra,
    )
    print(f"  wrote raw/{raw_path.relative_to(L.RAW)}")
    L.log_event(f"ingest-book: {slug} ({final_title!r})")
    L.log_ingest("book", slug, "ok", {"author": final_author, "format": extra["format"]})
    return raw_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--url")
    ap.add_argument("--epub-path")
    ap.add_argument("--isbn")
    ap.add_argument("--year", type=int)
    ap.add_argument("--skip-validation", action="store_true")
    args = ap.parse_args()
    try:
        ingest_book(args.title, args.author, args.url, args.epub_path,
                    args.isbn, args.year, skip_validation=args.skip_validation)
    except SystemExit:
        raise
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
