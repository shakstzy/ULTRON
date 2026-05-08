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


# ---------------------------------------------------------------------------
# Sibling ingest module loaders — each ingest-*.py exposes its own ingest_*
# function. We can't `import ingest-article` because of the hyphen, so we load
# via importlib. Lazy: only modules actually needed for the URLs at hand are
# imported (e.g. all-article batches don't touch yt-dlp imports).
# ---------------------------------------------------------------------------

_LOADED: dict[str, object] = {}


def _load(stem: str):
    if stem in _LOADED:
        return _LOADED[stem]
    path = BIN_DIR / f"{stem}.py"
    if not path.exists():
        raise RuntimeError(f"sibling module not found: {path}")
    spec = importlib.util.spec_from_file_location(stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stem.replace("-", "_")] = mod
    spec.loader.exec_module(mod)   # type: ignore[union-attr]
    _LOADED[stem] = mod
    return mod


# ---------------------------------------------------------------------------
# URL classification
# ---------------------------------------------------------------------------

YT_VIDEO_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|live/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
YT_CHANNEL_RE = re.compile(
    r"youtube\.com/(?:@[A-Za-z0-9._-]+|c/[A-Za-z0-9._-]+|channel/[A-Za-z0-9_-]+)"
)
IG_RE = re.compile(r"instagram\.com/(?:share/)?(?:p|reel|reels|tv)/[A-Za-z0-9_-]+")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/")
ANNAS_RE = re.compile(r"annas-archive\.org/md5/[a-f0-9]{32}")


def classify(url: str) -> str:
    """Return one of: 'youtube-video', 'youtube-channel', 'reel', 'paper',
    'book', 'article', 'unknown'."""
    u = url.strip()
    if YT_VIDEO_RE.search(u):
        return "youtube-video"
    if YT_CHANNEL_RE.search(u):
        return "youtube-channel"
    if IG_RE.search(u):
        return "reel"
    if ARXIV_RE.search(u):
        return "paper"
    if ANNAS_RE.search(u):
        return "book"
    if u.lower().endswith(".pdf"):
        return "paper"
    if u.startswith(("http://", "https://")):
        return "article"
    return "unknown"


# ---------------------------------------------------------------------------
# Single-URL dispatcher — translates classify() → the right ingest function
# ---------------------------------------------------------------------------

def ingest_one(url: str) -> tuple[str, str | None]:
    """Ingest one URL. Returns (status, slug_or_none).
    status ∈ {'ok', 'skip', 'error'}."""
    kind = classify(url)
    try:
        if kind == "article":
            mod = _load("ingest-article")
            path = mod.ingest_article(url)
            return ("ok", path.stem if path else None)
        if kind == "youtube-video":
            mod = _load("ingest-youtube")
            m = YT_VIDEO_RE.search(url)
            video_id = m.group(1) if m else None
            if not video_id:
                return ("error", None)
            allow_shorts = "/shorts/" in url
            path = mod.ingest_video(video_id, allow_shorts_explicit=allow_shorts)
            return (("ok", path.stem) if path else ("skip", video_id))
        if kind == "youtube-channel":
            mod = _load("ingest-youtube")
            mod.ingest_channel(url)
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
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        for k, v in attrs:
            if k.lower() == "href" and v:
                self.links.append(v)
                return


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        raw = resp.read()
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
    """Fetch a hub page, extract <a href> links, normalize and filter, return
    a deduped list. By default constrains to the hub's domain — pass
    allow_cross_domain=True to follow external links."""
    print(f"  fetching hub: {hub_url}")
    html = _fetch(hub_url)
    parser = _LinkExtractor()
    parser.feed(html)

    base_host = urllib.parse.urlsplit(hub_url).netloc.lower()
    inc_re = re.compile(include_pattern) if include_pattern else None
    exc_re = re.compile(exclude_pattern) if exclude_pattern else None

    out: list[str] = []
    seen: set[str] = set()
    skipped = {"empty": 0, "scheme": 0, "domain": 0, "self": 0, "include": 0, "exclude": 0, "dup": 0}
    hub_norm = _normalize_link(hub_url, hub_url)
    for href in parser.links:
        norm = _normalize_link(href, hub_url)
        if not norm:
            skipped["empty"] += 1
            continue
        if norm == hub_norm:
            skipped["self"] += 1
            continue
        host = urllib.parse.urlsplit(norm).netloc.lower()
        if not allow_cross_domain and host != base_host:
            skipped["domain"] += 1
            continue
        if inc_re and not inc_re.search(norm):
            skipped["include"] += 1
            continue
        if exc_re and exc_re.search(norm):
            skipped["exclude"] += 1
            continue
        if norm in seen:
            skipped["dup"] += 1
            continue
        seen.add(norm)
        out.append(norm)
        if limit and len(out) >= limit:
            break
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
    positional args. Strips blanks and `#`-prefixed comments."""
    urls: list[str] = []
    if source:
        if source == "-":
            text = sys.stdin.read()
        else:
            text = Path(source).read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    urls.extend(u.strip() for u in positional if u.strip())
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
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
        urls = read_url_list(args.urls_file, args.urls)
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
