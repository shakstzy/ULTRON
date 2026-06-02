#!/usr/bin/env python3
"""
ingest-book.py — capture a book into the library workspace's raw/.

Pure capture: search Anna's Archive (or take a direct URL / local file),
download the EPUB (PDF fallback), extract markdown via pandoc, write a
nested layout at `raw/books/<author>/<book-slug>/` with:
    source.epub               # original artifact (gitignored)
    _full.md                  # standardized full body with universal envelope

Stage 02 (`stage-extract-book.py`) re-extracts when needed; stage 03
(`stage-chapterize-book.py`) splits _full.md into per-chapter files.
Passing `--whole-book` sets `whole_book: true` so stage 03 skips this book
and the curator serves it as a single bite.

Four input modes:
  ingest-book.py --title "Walden" --author "Henry David Thoreau"
  ingest-book.py --url "https://annas-archive.org/md5/<32hex>"
  ingest-book.py --url "https://www.gutenberg.org/ebooks/205.epub.images" --title Walden --author "Henry David Thoreau" --skip-validation
  ingest-book.py --epub-path /path/to/book.epub --title X --author Y
  ingest-book.py --author "James Clear"                   # bibliography: all books by author
  ingest-book.py --author "James Clear" --limit 5 --dry-run
  ingest-book.py --title X --author Y --whole-book        # do not chapterize
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import lib_common as L


# ---------------------------------------------------------------------------
# Sibling-stage loader — keep ingest from duplicating extractor logic.
# ---------------------------------------------------------------------------

_SIBLING_CACHE: dict[str, object] = {}


def _load_sibling(stem: str):
    if stem in _SIBLING_CACHE:
        return _SIBLING_CACHE[stem]
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(stem.replace("-", "_"), here / f"{stem}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load sibling: {stem}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stem.replace("-", "_")] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(stem.replace("-", "_"), None)
        raise
    _SIBLING_CACHE[stem] = mod
    return mod

ANNAS_BASE = "https://annas-archive.org"
LIBGEN_MIRRORS = (                          # try in order, first reachable wins
    "https://libgen.is",
    "https://libgen.rs",
    "https://libgen.li",
)
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 ULTRON/1.0"
HTTP_TIMEOUT = 30
SOURCE = "book"


class IngestError(Exception):
    """Raised when ingest cannot complete. Caught by main() and by batch callers."""


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


def try_direct_download(url: str, path_suffix_hint: str = "") -> Path | None:
    """Try downloading url as a book file (epub/pdf). Sniffs Content-Type and
    magic bytes when the URL path doesn't end in a known extension.
    `path_suffix_hint` should be the URL PATH suffix only (e.g. ".epub"),
    NOT the full URL — substring matches on the full URL get fooled by
    `?title=book.epub.html` style query strings.

    Re-raises IngestError on hard limits (size cap). Returns None only when
    the response is not a recognized book file."""
    tmp_dir = Path("/tmp") / f"library-book-{L.today()}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    suffix = (path_suffix_hint or "").lower()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            ext: str | None = None
            if "epub" in ctype or suffix == ".epub":
                ext = "epub"
            elif "pdf" in ctype or suffix == ".pdf":
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
                            local.unlink(missing_ok=True)
                            raise IngestError("download exceeded 200MB")
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
                        local.unlink(missing_ok=True)
                        raise IngestError("download exceeded 200MB")
                    out.write(chunk)
            if local.stat().st_size < 1024:
                return None
            print(f"  downloaded {local.stat().st_size:,} bytes ({ctype}) → {local}")
            return local
    except IngestError:
        raise
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


# ---------------------------------------------------------------------------
# LibGen fallback (when annas is unreachable or returns no results)
# ---------------------------------------------------------------------------

LIBGEN_ROW_RE = re.compile(
    r'<tr[^>]*?>(?P<row>.*?)</tr>', re.IGNORECASE | re.DOTALL,
)


def _libgen_first_reachable_mirror() -> str | None:
    """Return the base URL of the first reachable libgen mirror, or None.
    Uses a short HEAD probe so we don't burn 30s on every search."""
    for base in LIBGEN_MIRRORS:
        try:
            req = urllib.request.Request(base, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status < 500:
                    return base
        except Exception:
            continue
    return None


def search_libgen(query: str, lang: str = "english", ext: str = "epub",
                  limit: int = 5) -> list[dict]:
    """Search LibGen for `query`. Returns the same shape as `search_annas`:
    [{md5, url, raw_text, title, author, ext}]. `url` here is the LibGen
    book page (used by resolve_libgen_md5_page); md5 is the canonical key."""
    base = _libgen_first_reachable_mirror()
    if not base:
        sys.stderr.write("  no libgen mirror reachable\n")
        return []
    qs = urllib.parse.urlencode({
        "req": query, "open": "0", "res": "25",
        "view": "simple", "phrase": "1", "column": "def",
    })
    url = f"{base}/search.php?{qs}"
    try:
        html = fetch_text(url)
    except Exception as e:
        sys.stderr.write(f"  libgen search failed: {e}\n")
        return []
    results: list[dict] = []
    for m in LIBGEN_ROW_RE.finditer(html):
        row = m.group("row")
        # 9-column simple view: id, author, title, publisher, year, pages, lang, size, ext, dl-mirrors
        md5_m = re.search(r'md5=([A-Fa-f0-9]{32})', row)
        if not md5_m:
            continue
        md5 = md5_m.group(1).lower()
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 9:
            continue
        def _strip(s: str) -> str:
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()
        author = _strip(cells[1])
        title = _strip(cells[2])
        year = _strip(cells[4])
        row_lang = _strip(cells[6]).lower()
        row_ext = _strip(cells[8]).lower()
        # Filter to our requested ext / lang. ext "epub"==target; allow "pdf" as
        # second-choice when explicitly requested.
        if ext and row_ext and ext.lower() != row_ext:
            continue
        if lang and row_lang and lang.lower() not in row_lang:
            continue
        results.append({
            "md5": md5,
            "url": f"{base}/book/index.php?md5={md5}",
            "raw_text": f"{title} — {author}",
            "title": title,
            "author": author,
            "year": year or None,
            "format": row_ext or None,
            "language": row_lang or None,
            "_backend": "libgen",
        })
        if len(results) >= limit:
            break
    return results


def resolve_libgen_md5_page(url: str, md5: str | None = None) -> dict:
    """Resolve a libgen book page. LibGen exposes the artifact via mirror
    links to library.lol / cdn / etc. The function returns the same shape
    as resolve_md5_page for annas."""
    out = {"url": url, "title": None, "author": None, "year": None,
           "format": None, "language": None, "size": None, "download_urls": []}
    try:
        html = fetch_text(url)
    except Exception as e:
        sys.stderr.write(f"  libgen md5 page fetch failed: {e}\n")
        return out
    if not md5:
        md5_m = re.search(r'md5=([A-Fa-f0-9]{32})', url)
        if md5_m:
            md5 = md5_m.group(1).lower()
    if not md5:
        return out
    title_m = re.search(r'<title>(.+?)</title>', html, re.IGNORECASE | re.DOTALL)
    if title_m:
        out["title"] = re.sub(r"\s+", " ", title_m.group(1)).strip()
    # LibGen pages list mirror links. Add the canonical library.lol mirror and
    # any cdn.* links found in the page.
    out["download_urls"].append(f"https://library.lol/main/{md5}")
    out["download_urls"].append(f"http://libgen.li/ads.php?md5={md5}")
    for href in re.findall(r'href="(https?://[^"]+/main/[A-Fa-f0-9]{32}[^"]*)"', html):
        if href not in out["download_urls"]:
            out["download_urls"].append(href)
    # Format hint from URL or page
    if re.search(r'\.epub', html, re.IGNORECASE):
        out["format"] = "epub"
    elif re.search(r'\.pdf', html, re.IGNORECASE):
        out["format"] = "pdf"
    return out


def resolve_book_page(candidate: dict) -> dict:
    """Backend-agnostic dispatch: route to annas or libgen resolver based on
    where the candidate came from. Annas md5 pages are richer; libgen needs
    its own resolver."""
    if candidate.get("_backend") == "libgen":
        return resolve_libgen_md5_page(candidate["url"], md5=candidate.get("md5"))
    return resolve_md5_page(candidate["url"])


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


DISCOVER_MAX_CANDIDATES = 30
DISCOVER_AUTHOR_MIN = 0.7


def discover_books_by_author(author: str, limit: int = 20) -> list[dict]:
    """Search annas-archive for books by a single author. Falls back to
    LibGen when annas returns empty or unreachable.

    Strategy: search by author name → walk the top results (capped at
    DISCOVER_MAX_CANDIDATES regardless of `limit` so common names don't
    burn 60+ md5-page resolves) → keep candidates whose parsed author
    fuzzy-matches at ≥ DISCOVER_AUTHOR_MIN. Stops once `limit` matches
    accumulate.

    Returns a list of resolved metadata dicts (one per matching book), each
    with at minimum `title`, `author`, `url`, `format`, `language` populated."""
    candidate_cap = min(max(limit + 10, limit * 2), DISCOVER_MAX_CANDIDATES)
    raw_results = search_annas(author, limit=candidate_cap)
    backend = "annas"
    if not raw_results:
        raw_results = search_libgen(author, limit=candidate_cap)
        backend = "libgen"
    matched: list[dict] = []
    seen_titles: set[str] = set()
    for r in raw_results:
        if len(matched) >= limit:
            break
        try:
            if backend == "libgen" or r.get("_backend") == "libgen":
                meta = resolve_libgen_md5_page(r["url"], md5=r.get("md5"))
                # libgen rows already carry title/author/lang — carry forward
                for k in ("title", "author", "format", "language", "year"):
                    if not meta.get(k) and r.get(k):
                        meta[k] = r[k]
            else:
                meta = resolve_md5_page(r["url"])
        except Exception as e:
            sys.stderr.write(f"  resolve {r['url']}: {type(e).__name__}: {e}\n")
            continue
        meta_title = (meta.get("title") or "").strip()
        meta_author = (meta.get("author") or "").strip()
        if not meta_title or not meta_author:
            continue
        if fuzzy_ratio(meta_author, author) < DISCOVER_AUTHOR_MIN:
            continue
        meta_lang = (meta.get("language") or "").lower()
        if meta_lang and meta_lang not in ("en", "english"):
            continue
        title_key = meta_title.lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        matched.append(meta)
    return matched


def ingest_books_by_author(
    author: str,
    limit: int = 20,
    dry_run: bool = False,
    skip_validation: bool = False,
    whole_book: bool = False,
) -> dict:
    """Search annas-archive for all books matching `author`, then ingest each.

    Returns a summary dict {matched, ingested, skipped, failed, items}."""
    print(f"  searching annas-archive for author: {author!r}")
    matched = discover_books_by_author(author, limit=limit)
    print(f"  discovered {len(matched)} candidate books matching author={author!r}")
    for i, m in enumerate(matched, 1):
        print(f"    {i}. {m.get('title')!r} — {m.get('author')} ({m.get('format') or '?'}, {m.get('language') or '?'})")

    items: list[dict] = []
    ingested = 0
    failed = 0
    if not dry_run:
        for m in matched:
            title = m.get("title")
            try:
                ingest_book(
                    title=title,
                    author=author,
                    url=m.get("url"),
                    epub_path=None,
                    isbn=None,
                    year=m.get("year"),
                    skip_validation=skip_validation,
                    whole_book=whole_book,
                )
                ingested += 1
                items.append({"title": title, "status": "ok"})
            except IngestError as e:
                print(f"  ! skipping {title!r}: {e}", file=sys.stderr)
                failed += 1
                items.append({"title": title, "status": "skip", "reason": str(e)})
            except Exception as e:
                print(f"  ! FATAL on {title!r}: {type(e).__name__}: {e}", file=sys.stderr)
                failed += 1
                items.append({"title": title, "status": "error", "reason": f"{type(e).__name__}: {e}"})
    summary = {"matched": len(matched), "ingested": ingested, "failed": failed,
               "dry_run": dry_run, "items": items}
    if dry_run:
        print(f"  --author dry-run: would ingest {summary['matched']} books")
    else:
        print(f"  --author summary: {summary['ingested']} ingested, {summary['failed']} failed (of {summary['matched']} matches)")
        L.log_event(f"ingest-book --author {author!r}: {summary['ingested']}/{summary['matched']} ingested, {summary['failed']} failed")
    return summary


# ---------------------------------------------------------------------------
# Pandoc / pdftotext extraction
# ---------------------------------------------------------------------------

# Extraction (epub_to_markdown / pdf_to_markdown / sanity_check_markdown)
# moved to bin/stage-extract-book.py. Ingest is artifact + metadata stub only;
# stage 02 owns the body. Old helpers removed to prevent drift.


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _normalize_author(name: str) -> str:
    """LibGen lists authors as `Last, First [Middle]`. Annas / native form is
    `First [Middle] Last`. Normalize to "first last" tokens for comparison."""
    s = name.lower().strip()
    if "," in s:
        # "Dalio, Ray" -> "Ray Dalio"
        parts = [p.strip() for p in s.split(",", 1)]
        if len(parts) == 2 and parts[1]:
            s = f"{parts[1]} {parts[0]}"
    # collapse non-letters / non-spaces
    s = re.sub(r"[^a-z\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fuzzy_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None,
                                   _normalize_author(a),
                                   _normalize_author(b)).ratio()


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
    whole_book: bool = False,
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
            url_path_suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
            local = try_direct_download(url, path_suffix_hint=url_path_suffix)
            if local is None and title and author:
                print(f"  direct download did not yield epub/pdf; falling back to annas search")
            elif local is not None:
                meta = {"title": title, "author": author, "year": year, "language": "en",
                        "format": local.suffix.lstrip(".")}
        if local is None and md5_url is None:
            if not (title and author):
                raise IngestError("URL did not resolve and no title+author for fallback search")
            picked_candidate: dict | None = None
            print(f"  searching annas-archive for: {title} | {author}")
            annas_results = search_annas(f"{title} {author}", limit=5)
            if annas_results:
                picked_candidate = annas_results[0]
                print(f"  annas top result: {picked_candidate['url']}")
            else:
                print("  no annas results, trying libgen")
                libgen_results = search_libgen(f"{title} {author}", limit=5)
                if libgen_results:
                    picked_candidate = libgen_results[0]
                    print(f"  libgen top result: {picked_candidate['url']}")
            if not picked_candidate:
                raise IngestError("no search results from annas-archive or libgen")
            md5_url = picked_candidate["url"]
        if md5_url:
            print(f"  resolving book page: {md5_url}")
            # Backend dispatch
            if "libgen" in md5_url:
                meta = resolve_libgen_md5_page(md5_url)
                if not meta.get("title"):
                    meta["title"] = title
                if not meta.get("author"):
                    meta["author"] = author
            else:
                meta = resolve_md5_page(md5_url)
            print(f"  parsed metadata: title={meta.get('title')!r} author={meta.get('author')!r} format={meta.get('format')} lang={meta.get('language')}")
            ok, failures = validate_metadata(meta, title, author) if not skip_validation else (True, [])
            if not ok:
                raise IngestError("validation failed: " + "; ".join(failures))
            ext = meta.get("format") or "epub"
            tmp_dir = Path("/tmp") / f"library-book-{L.today()}"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            local = tmp_dir / f"download.{ext}"
            ok, msg = attempt_download(meta, local)
            if not ok:
                raise IngestError(f"download failed: {msg}")
            print(f"  {msg}")

    final_title = meta.get("title") or title or local.stem
    final_author = meta.get("author") or author or "Unknown"
    final_year = meta.get("year") or year

    # Slug fallback for non-Latin titles/authors that ASCII-fold to empty.
    raw_slug = L.book_slug(final_title, final_author)
    if not raw_slug or raw_slug.startswith("-") or raw_slug == "unknown-":
        digest = hashlib.sha256(f"{final_title}|{final_author}".encode("utf-8")).hexdigest()[:8]
        raw_slug = f"book-{digest}"
    slug = raw_slug

    author_slug = L.author_slug(final_author)
    if not author_slug:
        author_slug = "author-" + hashlib.sha256(final_author.encode("utf-8")).hexdigest()[:6]

    artifact_hash_pre = L.file_sha256(local)

    # New nested layout: raw/books/<author-slug>/<book-slug>/{source.*, _full.md, ch-NN-*.md}
    author_dir = L.RAW / "books" / author_slug
    book_dir = author_dir / slug

    # Collision check — only when the directory is non-empty AND looks like
    # a previous ingest of a DIFFERENT source. Three signals (in order):
    #   1. existing source_url ≠ incoming url
    #   2. existing artifact_sha256 ≠ artifact_hash_pre (for --epub-path mode
    #      where neither side has a source_url)
    #   3. existing title differs significantly from final_title
    if book_dir.exists() and any(book_dir.iterdir()):
        full_path = book_dir / "_full.md"
        existing_fm, _ = L.read_md(full_path) if full_path.exists() else ({}, "")
        existing_url = (existing_fm.get("source_url") or "").strip()
        existing_hash = (existing_fm.get("artifact_sha256")
                         or existing_fm.get("source_hash") or "").strip()
        existing_title = (existing_fm.get("title") or "").strip()
        is_collision = False
        if existing_url and url and existing_url != url:
            is_collision = True
        elif existing_hash and existing_hash != artifact_hash_pre:
            is_collision = True
        elif existing_title and final_title and fuzzy_ratio(existing_title, final_title) < 0.85:
            is_collision = True
        if is_collision:
            disambig = hashlib.sha256(
                (url or str(local) or artifact_hash_pre).encode("utf-8")
            ).hexdigest()[:5]
            slug = f"{raw_slug}-{disambig}"
            book_dir = author_dir / slug
    book_dir.mkdir(parents=True, exist_ok=True)

    artifact_ext = local.suffix.lower().lstrip(".") or "epub"
    raw_artifact_path = book_dir / f"source.{artifact_ext}"
    if local.resolve() != raw_artifact_path.resolve():
        shutil.copy2(local, raw_artifact_path)

    # Write a metadata-only stub _full.md so stage 02 has a place to land its
    # body. NO source_hash here — stage 02 sets that after it extracts.
    raw_path = book_dir / "_full.md"
    extra = {
        "slug": slug,
        "title": final_title,
        "author": final_author,
        "year": final_year,
        "isbn": isbn,
        "language": "en",
        "format": artifact_ext,
        "source_url": url,
        "annas_md5": (meta.get("url") or "").rsplit("/", 1)[-1] if meta.get("url") else None,
        "artifact_sha256": L.file_sha256(raw_artifact_path),
        "whole_book": bool(whole_book),
        "extract_status": "pending",      # stage 02 sets this to 'ok' or 'failed'
    }
    provider_modified_at = f"{final_year:04d}-01-01T00:00:00Z" if isinstance(final_year, int) else None
    stub_body = (
        "## Stub\n\n"
        "_This file is a metadata stub written by `bin/ingest-book.py`. "
        "Run `bin/library-build.sh --stage extract` "
        "(or `bin/stage-extract-book.py`) to populate the body._\n"
    )
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=stub_body,
        provider_modified_at=provider_modified_at,
        extra=extra,
    )
    print(f"  wrote raw/{raw_path.relative_to(L.RAW)} (metadata stub)"
          + (" (whole-book)" if whole_book else ""))

    # Hand off to stage 02 for the actual extraction. This is the canonical
    # extractor — keeps ingest and stage 02 from diverging.
    stage2 = _load_sibling("stage-extract-book")
    rec = stage2.extract_book(book_dir, force=True, dry_run=False)
    stage2.log_record(rec)
    if rec.get("status") not in ("ok", "noop"):
        raise IngestError(
            f"stage-extract-book failed for {slug}: {rec.get('reason') or rec.get('status')}"
        )
    print(f"  stage 02 extract: {rec['status']} "
          f"({rec.get('body_chars', '?')} chars, {rec.get('heading_count', '?')} H1s)")

    L.log_event(f"ingest-book: {slug} ({final_title!r})"
                + (" [whole-book]" if whole_book else ""))
    L.log_ingest("book", slug, "ok", {"author": final_author, "format": extra["format"],
                                       "whole_book": bool(whole_book)})
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
    ap.add_argument("--limit", type=int, default=20,
                    help="for --author bibliography mode: max books to ingest")
    ap.add_argument("--dry-run", action="store_true",
                    help="for --author bibliography mode: discover but do not download/ingest")
    ap.add_argument("--whole-book", action="store_true",
                    help="mark this ingest as whole-book — chapterize stage will skip it")
    args = ap.parse_args()

    bibliography_mode = bool(
        args.author and not args.title and not args.url and not args.epub_path
    )
    try:
        if bibliography_mode:
            summary = ingest_books_by_author(
                args.author,
                limit=args.limit,
                dry_run=args.dry_run,
                skip_validation=args.skip_validation,
                whole_book=args.whole_book,
            )
            if summary["matched"] == 0:
                return 2
            if summary["dry_run"]:
                return 0
            return 1 if summary["failed"] > 0 else 0
        ingest_book(args.title, args.author, args.url, args.epub_path,
                    args.isbn, args.year, skip_validation=args.skip_validation,
                    whole_book=args.whole_book)
    except IngestError as e:
        print(f"  ! {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
