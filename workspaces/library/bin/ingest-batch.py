#!/usr/bin/env python3
"""
ingest-batch.py — multi-URL paste + blog series crawler for the library workspace.

Two ways to feed it URLs:
  1. URL list (multi-URL paste)
  2. Hub URL → crawler extracts every linked article on the page

Each URL is classified by domain and dispatched to the matching ingest script:
  youtube.com / youtu.be      → ingest-youtube.ingest_video / ingest_channel
  instagram.com               → ingest-reel.ingest_reel
  arxiv.org / *.pdf           → ingest-paper.ingest_paper
  annas-archive.org/md5/*     → ingest-book.ingest_book
  everything else             → ingest-article.ingest_article

NO cloud-llm. NO wiki writes. Pure capture — the wiki layer is built downstream
by `/graphify --wiki workspaces/library`.

Examples:
  # multi-URL paste (positional)
  ingest-batch.py https://paulgraham.com/ds.html https://arxiv.org/abs/1706.03762

  # multi-URL paste from a file (one URL per line; blanks and `#` comments OK)
  ingest-batch.py --urls /path/to/list.txt

  # multi-URL paste from stdin
  cat list.txt | ingest-batch.py --urls -

  # blog crawler: paste a hub page, ingest every linked article on the same domain
  ingest-batch.py --crawl https://paulgraham.com/articles.html
  ingest-batch.py --crawl https://paulgraham.com/articles.html --limit 5 --dry-run

  # opt-in cross-domain crawl + pattern controls
  ingest-batch.py --crawl https://blog.example.com/index --include-pattern '/posts/' --exclude-pattern '/tag/'
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import lib_common as L

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 ULTRON-library/1.0"
HTTP_TIMEOUT = 30
BIN_DIR = Path(__file__).resolve().parent

# Crawler safety bounds
MAX_HUB_BYTES = 10_000_000          # cap a single hub fetch at 10 MB
MAX_HUB_LINKS = 5_000               # parser hard-cap on accumulated <a href>
MAX_URL_LIST_LINES = 100_000        # read_url_list line cap (stdin / file)


# ---------------------------------------------------------------------------
# Sibling ingest module loaders — each ingest-*.py exposes its own ingest_*
# function. We can't `import ingest-article` because of the hyphen, so we load
# via importlib. Lazy: only modules actually needed for the URLs at hand are
# imported (e.g. all-article batches don't touch yt-dlp imports).
# ---------------------------------------------------------------------------

_LOADED: dict[str, object] = {}


def _load(stem: str):
    """Load a sibling ingest-*.py module by file. On exec_module failure,
    pop the half-initialized entry from sys.modules so a later retry sees a
    clean slate (avoids partial-module pollution that breaks subsequent
    batch items)."""
    if stem in _LOADED:
        return _LOADED[stem]
    path = BIN_DIR / f"{stem}.py"
    if not path.exists():
        raise RuntimeError(f"sibling module not found: {path}")
    name = stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not build spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        raise
    _LOADED[stem] = mod
    return mod


# ---------------------------------------------------------------------------
# URL classification
# ---------------------------------------------------------------------------

YT_VIDEO_PATH_RE = re.compile(r"^/(?:watch|shorts/|live/|embed/)")
YT_VIDEO_QUERY_V = re.compile(r"(?:^|&)v=([A-Za-z0-9_-]{11})")
YT_VIDEO_PATH_ID = re.compile(r"^/(?:shorts|live|embed)/([A-Za-z0-9_-]{11})")
YT_BE_PATH_ID = re.compile(r"^/([A-Za-z0-9_-]{11})")
YT_CHANNEL_PATH = re.compile(r"^/(?:@[A-Za-z0-9._-]+|c/[A-Za-z0-9._-]+|channel/[A-Za-z0-9_-]+)")
IG_PATH = re.compile(r"^/(?:share/)?(?:p|reel|reels|tv)/[A-Za-z0-9_-]+")
ANNAS_PATH = re.compile(r"^/md5/[a-f0-9]{32}")


def _host(url: str) -> str:
    """Lowercased host with leading 'www.' stripped, port and userinfo removed.
    Empty string if url has no parseable host."""
    parts = urllib.parse.urlsplit(url)
    h = (parts.hostname or "").lower()
    if h.startswith("www."):
        h = h[4:]
    return h


def _has_pdf_path(url: str) -> bool:
    path = urllib.parse.urlsplit(url).path.lower()
    return path.endswith(".pdf")


def classify(url: str) -> str:
    """Return one of: 'youtube-video', 'youtube-channel', 'reel', 'paper',
    'book', 'article', 'unknown'.

    Host comparisons are case-insensitive (RFC 3986 § 3.2.2). PDF detection
    inspects the URL path, not the full URL — so query strings like
    `?download=1` don't break the match."""
    u = url.strip()
    parts = urllib.parse.urlsplit(u)
    if parts.scheme not in ("http", "https"):
        return "unknown"
    host = _host(u)
    path = parts.path
    query = parts.query or ""

    if host in ("youtube.com", "m.youtube.com"):
        if path == "/watch":
            if YT_VIDEO_QUERY_V.search(query):
                return "youtube-video"
        if YT_VIDEO_PATH_ID.match(path):
            return "youtube-video"
        if YT_CHANNEL_PATH.match(path):
            return "youtube-channel"
    if host == "youtu.be":
        if YT_BE_PATH_ID.match(path):
            return "youtube-video"
    if host == "instagram.com":
        if IG_PATH.match(path):
            return "reel"
    if host == "arxiv.org":
        if path.startswith(("/abs/", "/pdf/")):
            return "paper"
    if host == "doi.org":
        return "paper"
    if host == "annas-archive.org":
        if ANNAS_PATH.match(path):
            return "book"
    if _has_pdf_path(u):
        return "paper"
    return "article"


def extract_yt_video_id(url: str) -> str | None:
    """Pull the 11-char video id out of any of the YouTube URL shapes."""
    parts = urllib.parse.urlsplit(url)
    host = _host(url)
    path = parts.path
    if host in ("youtube.com", "m.youtube.com"):
        if path == "/watch":
            m = YT_VIDEO_QUERY_V.search(parts.query or "")
            if m:
                return m.group(1)
        m = YT_VIDEO_PATH_ID.match(path)
        if m:
            return m.group(1)
    if host == "youtu.be":
        m = YT_BE_PATH_ID.match(path)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Single-URL dispatcher — translates classify() → the right ingest function
# ---------------------------------------------------------------------------

def ingest_one(url: str) -> tuple[str, str | None]:
    """Ingest one URL. Returns (status, slug_or_none).

    status ∈ {'ok', 'skip', 'error'}:
      - 'ok'    — file written (or no-op idempotent re-write)
      - 'skip'  — sibling chose not to ingest by policy (Shorts filtered, no
                  transcript). NOT a failure.
      - 'error' — sibling raised — counted toward batch exit code 1.
    """
    kind = classify(url)
    try:
        if kind == "article":
            mod = _load("ingest-article")
            path = mod.ingest_article(url)
            return ("ok", path.stem if path else None)
        if kind == "youtube-video":
            mod = _load("ingest-youtube")
            video_id = extract_yt_video_id(url)
            if not video_id:
                sys.stderr.write(f"  ! youtube-video {url}: no parseable video id\n")
                return ("error", None)
            allow_shorts = urllib.parse.urlsplit(url).path.lower().startswith("/shorts/")
            path = mod.ingest_video(video_id, allow_shorts_explicit=allow_shorts)
            return (("ok", path.stem) if path else ("skip", video_id))
        if kind == "youtube-channel":
            mod = _load("ingest-youtube")
            sub = mod.ingest_channel(url) or {}
            sub_failures = int(sub.get("failures", 0))
            sub_successes = int(sub.get("successes", 0))
            if sub_failures > 0:
                return ("error", None)
            if sub_successes == 0:
                return ("skip", None)
            return ("ok", None)
        if kind == "reel":
            mod = _load("ingest-reel")
            path = mod.ingest_reel(url)
            return ("ok", path.stem if path else None)
        if kind == "paper":
            mod = _load("ingest-paper")
            path = mod.ingest_paper(url, None)
            return ("ok", path.stem if path else None)
        if kind == "book":
            mod = _load("ingest-book")
            path = mod.ingest_book(None, None, url, None)
            return ("ok", path.stem if path else None)
        return ("error", None)
    except Exception as e:
        cls = type(e).__name__
        sys.stderr.write(f"  ! {kind} {url} → {cls}: {e}\n")
        return ("error", None)


# ---------------------------------------------------------------------------
# Blog crawler — extract <a href> from a hub URL
# ---------------------------------------------------------------------------

class _LinkExtractor(HTMLParser):
    """Streaming <a href> extractor. Caller passes a per-link `accept`
    callback that decides whether to keep the link; parsing stops once the
    callback signals enough links have been collected. This keeps memory
    bounded for pathological pages with millions of links."""

    def __init__(self, accept):
        super().__init__(convert_charrefs=True)
        self._accept = accept
        self._stop = False

    def handle_starttag(self, tag, attrs):
        if self._stop or tag.lower() != "a":
            return
        for k, v in attrs:
            if k.lower() == "href" and v:
                if self._accept(v) is False:
                    self._stop = True
                return


def _fetch(url: str, max_bytes: int = MAX_HUB_BYTES) -> str:
    """Stream up to `max_bytes` from `url`. Raises IngestError-like
    RuntimeError on overflow so the crawl halts loudly instead of silently
    truncating."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    chunks: list[bytes] = []
    written = 0
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                raise RuntimeError(f"hub fetch exceeded {max_bytes} bytes; aborting")
            chunks.append(chunk)
    raw = b"".join(chunks)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def _normalize_link(href: str, base_url: str) -> str | None:
    href = (href or "").strip()
    if not href:
        return None
    lower = href.lower()
    if lower.startswith(("javascript:", "mailto:", "tel:", "#")):
        return None
    abs_url = urllib.parse.urljoin(base_url, href)
    parts = urllib.parse.urlsplit(abs_url)
    if parts.scheme not in ("http", "https"):
        return None
    parts = parts._replace(fragment="")
    return urllib.parse.urlunsplit(parts)


def crawl_hub(
    hub_url: str,
    *,
    allow_cross_domain: bool = False,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    limit: int | None = None,
) -> list[str]:
    """Fetch a hub page (capped at MAX_HUB_BYTES), extract <a href> links,
    normalize and filter inline, return a deduped list. By default
    constrains to the hub's host (with leading 'www.' stripped) — pass
    allow_cross_domain=True to follow external links.

    Filtering is done in the streaming HTMLParser callback so memory stays
    bounded even on link-bomb pages: at most MAX_HUB_LINKS accepted entries
    plus an O(1) seen-set live in memory.
    """
    print(f"  fetching hub: {hub_url}")
    html = _fetch(hub_url)

    base_host = _host(hub_url)
    inc_re = re.compile(include_pattern) if include_pattern else None
    exc_re = re.compile(exclude_pattern) if exclude_pattern else None
    hard_cap = limit if (limit and limit > 0) else MAX_HUB_LINKS

    out: list[str] = []
    seen: set[str] = set()
    skipped = {"empty": 0, "domain": 0, "self": 0, "include": 0, "exclude": 0, "dup": 0}
    hub_norm = _normalize_link(hub_url, hub_url)

    def accept(href: str) -> bool:
        """Return False to halt parsing once we have enough links."""
        if len(out) >= hard_cap:
            return False
        norm = _normalize_link(href, hub_url)
        if not norm:
            skipped["empty"] += 1
            return True
        if norm == hub_norm:
            skipped["self"] += 1
            return True
        if not allow_cross_domain and _host(norm) != base_host:
            skipped["domain"] += 1
            return True
        if inc_re and not inc_re.search(norm):
            skipped["include"] += 1
            return True
        if exc_re and exc_re.search(norm):
            skipped["exclude"] += 1
            return True
        if norm in seen:
            skipped["dup"] += 1
            return True
        seen.add(norm)
        out.append(norm)
        return len(out) < hard_cap

    parser = _LinkExtractor(accept)
    parser.feed(html)
    print(f"  extracted {len(out)} links ({skipped})")
    return out


# ---------------------------------------------------------------------------
# Multi-URL ingest with summary
# ---------------------------------------------------------------------------

def ingest_urls(urls: list[str], *, dry_run: bool = False) -> dict:
    summary = {"total": len(urls), "ok": 0, "skip": 0, "error": 0, "by_kind": {}}
    if dry_run:
        print(f"  dry-run: would ingest {len(urls)} URLs:")
        for u in urls:
            kind = classify(u)
            summary["by_kind"][kind] = summary["by_kind"].get(kind, 0) + 1
            print(f"    {kind:<16} {u}")
        return summary
    for i, url in enumerate(urls, 1):
        kind = classify(url)
        summary["by_kind"][kind] = summary["by_kind"].get(kind, 0) + 1
        print(f"[{i}/{len(urls)}] {kind:<16} {url}")
        status, _ = ingest_one(url)
        summary[status] = summary.get(status, 0) + 1
    print(f"  batch summary: {summary}")
    L.log_event(f"ingest-batch: {summary}")
    return summary


# ---------------------------------------------------------------------------
# URL list reading (file / stdin / args)
# ---------------------------------------------------------------------------

def read_url_list(source: str, positional: list[str]) -> list[str]:
    """Load URLs from --urls source ('-' = stdin, else file path) plus any
    positional args. Strips blanks and `#`-prefixed comments. Streams
    line-by-line so a large file/pipe doesn't sit in memory; capped at
    MAX_URL_LIST_LINES."""
    out: list[str] = []
    seen: set[str] = set()

    def add(line: str):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        if line in seen:
            return
        seen.add(line)
        out.append(line)

    if source:
        stream = sys.stdin if source == "-" else open(source, "r", encoding="utf-8")
        try:
            for i, line in enumerate(stream):
                if i >= MAX_URL_LIST_LINES:
                    sys.stderr.write(f"  ! url list truncated at {MAX_URL_LIST_LINES} lines\n")
                    break
                add(line)
        finally:
            if source != "-":
                stream.close()
    for u in positional:
        add(u)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*", help="positional list of URLs to ingest")
    ap.add_argument("--urls", dest="urls_file",
                    help="file with URLs, one per line ('-' = stdin)")
    ap.add_argument("--crawl", dest="crawl_url",
                    help="hub URL: extract every linked article on the page, then ingest each")
    ap.add_argument("--allow-cross-domain", action="store_true",
                    help="for --crawl: don't constrain to the hub's domain")
    ap.add_argument("--include-pattern", help="regex; only URLs matching it are kept")
    ap.add_argument("--exclude-pattern", help="regex; URLs matching it are dropped")
    ap.add_argument("--limit", type=int, help="cap how many URLs to ingest")
    ap.add_argument("--dry-run", action="store_true",
                    help="classify and print what would be ingested without writing")
    args = ap.parse_args()

    if args.crawl_url and (args.urls or args.urls_file):
        print("--crawl is mutually exclusive with --urls / positional URLs", file=sys.stderr)
        return 2
    if not args.crawl_url and not args.urls and not args.urls_file:
        ap.print_help()
        return 2

    if args.crawl_url:
        try:
            urls = crawl_hub(
                args.crawl_url,
                allow_cross_domain=args.allow_cross_domain,
                include_pattern=args.include_pattern,
                exclude_pattern=args.exclude_pattern,
                limit=args.limit,
            )
        except Exception as e:
            print(f"  FATAL crawl: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
        if not urls:
            print("  no links extracted; nothing to ingest", file=sys.stderr)
            return 2
    else:
        try:
            urls = read_url_list(args.urls_file, args.urls)
        except FileNotFoundError as e:
            print(f"  url list not found: {e}", file=sys.stderr)
            return 2
        except OSError as e:
            print(f"  could not read url list: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
        if args.include_pattern:
            inc = re.compile(args.include_pattern)
            urls = [u for u in urls if inc.search(u)]
        if args.exclude_pattern:
            exc = re.compile(args.exclude_pattern)
            urls = [u for u in urls if not exc.search(u)]
        if args.limit:
            urls = urls[: args.limit]
        if not urls:
            print("  no URLs to ingest", file=sys.stderr)
            return 2

    summary = ingest_urls(urls, dry_run=args.dry_run)
    return 0 if summary.get("error", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
