#!/usr/bin/env python3
"""
ingest-youtube.py — YouTube video / channel ingest for library.

Single video:
  ingest-youtube.py "https://youtu.be/<id>"
  ingest-youtube.py "https://youtube.com/watch?v=<id>"
  ingest-youtube.py "https://youtube.com/shorts/<id>"   # explicit Shorts ingest

Channel (backfill all videos, skipping Shorts):
  ingest-youtube.py "https://youtube.com/@andrewhubermanlab" --backfill all
  ingest-youtube.py "https://youtube.com/@channel" --backfill 50
  ingest-youtube.py "https://youtube.com/@channel" --videos id1,id2,id3

Pipeline per video:
  1. yt-dlp metadata fetch (title, channel, duration, upload_date)
  2. youtube-summary venv → transcript
  3. Hybrid co-location check vs existing wiki/entities/books/
  4. cloud-llm synthesis → wiki entity page
  5. Write raw + wiki, log
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import lib_common as L

YT_DLP = "yt-dlp"
YOUTUBE_SUMMARY_PY = Path.home() / ".ultron" / "youtube-summary" / ".venv" / "bin" / "python"
SHORTS_DURATION_THRESHOLD_SECONDS = 60
DEFAULT_PARALLEL_WORKERS = 4


# ---------------------------------------------------------------------------
# URL classification
# ---------------------------------------------------------------------------

VIDEO_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|live/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
CHANNEL_RE = re.compile(
    r"youtube\.com/(?:@([A-Za-z0-9._-]+)|c/([A-Za-z0-9._-]+)|channel/([A-Za-z0-9_-]+))"
)


def classify_url(url: str) -> tuple[str, str | None]:
    """Returns ('video', video_id) | ('channel', channel_url) | ('unknown', None)."""
    m = VIDEO_ID_RE.search(url)
    if m:
        return "video", m.group(1)
    m = CHANNEL_RE.search(url)
    if m:
        return "channel", url
    return "unknown", None


def is_shorts_url(url: str) -> bool:
    return "/shorts/" in url


# ---------------------------------------------------------------------------
# yt-dlp metadata
# ---------------------------------------------------------------------------

def yt_metadata(video_id: str) -> dict:
    """Fetch single-video metadata via yt-dlp --dump-json."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [YT_DLP, "--skip-download", "--dump-json", "--no-warnings", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


def yt_channel_videos(channel_url: str, limit: int | None = None) -> list[dict]:
    """Enumerate videos from a channel via flat playlist. Returns list of metadata dicts.

    We use --flat-playlist for speed (no per-video metadata fetch yet) — duration
    is included in flat output so we can filter Shorts upstream.
    """
    if not channel_url.rstrip("/").endswith("/videos"):
        channel_url = channel_url.rstrip("/") + "/videos"
    cmd = [
        YT_DLP, "--flat-playlist", "--dump-json", "--no-warnings",
        channel_url,
    ]
    if limit:
        cmd.extend(["--playlist-end", str(limit)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp channel listing failed: {proc.stderr.strip()[:200]}")
    videos = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return videos


def filter_shorts(videos: list[dict], skip_shorts: bool = True) -> list[dict]:
    """Filter out Shorts (duration < 60s). Live streams without duration are kept."""
    if not skip_shorts:
        return videos
    out = []
    for v in videos:
        dur = v.get("duration")
        if dur is not None and dur < SHORTS_DURATION_THRESHOLD_SECONDS:
            continue
        # Some flat results have url like .../shorts/<id> — exclude those too.
        # yt-dlp can return explicit null for url/webpage_url, so coerce to str.
        url = v.get("url") or v.get("webpage_url") or ""
        if not isinstance(url, str):
            url = ""
        if "/shorts/" in url:
            continue
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# Transcript fetch
# ---------------------------------------------------------------------------

def fetch_transcript(video_id: str, languages: str = "en") -> str | None:
    """Fetch transcript via the youtube-summary venv. Returns None on no transcript."""
    if not YOUTUBE_SUMMARY_PY.exists():
        # Fall back to module from system Python if available
        cmd = [sys.executable, "-m", "youtube_transcript_api", video_id, "--languages", languages, "--format", "text"]
    else:
        cmd = [str(YOUTUBE_SUMMARY_PY), "-m", "youtube_transcript_api", video_id, "--languages", languages, "--format", "text"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        sys.stderr.write(f"  transcript unavailable for {video_id}: {proc.stderr.strip()[:200]}\n")
        return None
    text = proc.stdout.strip()
    if not text or len(text) < 100:
        return None
    return text


# ---------------------------------------------------------------------------
# Hybrid co-location: book-specific?
# ---------------------------------------------------------------------------

def find_co_located_book(title: str, transcript: str) -> dict | None:
    """Heuristic: a video is 'primarily about' a book in the corpus if the book
    title or author appears multiple times in the video title or transcript.

    Returns the book frontmatter dict if matched, else None.
    """
    books_dir = L.WIKI / "entities" / "books"
    if not books_dir.exists():
        return None
    haystack = (title + " " + (transcript or "")).lower()
    best = None
    best_score = 0
    for book_md in books_dir.glob("*.md"):
        fm, _ = L.read_md(book_md)
        if not fm or fm.get("type") != "book":
            continue
        bt = (fm.get("title") or "").lower()
        if not bt or len(bt) < 4:
            continue
        title_hits = haystack.count(bt)
        # Author hits
        authors = fm.get("authors") or []
        author_hits = 0
        for a in authors:
            # Slug → "james-clear" → match "james clear" or "clear" in haystack
            parts = a.replace("-", " ")
            author_hits += haystack.count(parts)
        # Threshold: title appears in video title (1+) AND transcript references book or author 2+ total
        in_video_title = bt in title.lower()
        score = (title_hits * 3) + author_hits + (5 if in_video_title else 0)
        if score >= 5 and score > best_score:
            best = fm
            best_score = score
    return best


# ---------------------------------------------------------------------------
# Single video ingest
# ---------------------------------------------------------------------------

def ingest_video(video_id: str, *, allow_shorts_explicit: bool = False, overwrite: bool = False) -> Path | None:
    print(f"  [{video_id}] fetching metadata")
    try:
        meta = yt_metadata(video_id)
    except Exception as e:
        print(f"  [{video_id}] metadata fetch failed: {e}", file=sys.stderr)
        return None

    title = meta.get("title") or video_id
    channel = meta.get("channel") or meta.get("uploader") or "unknown"
    channel_handle = (meta.get("channel_url") or "").rsplit("/@", 1)[-1] if "@" in (meta.get("channel_url") or "") else channel
    channel_handle = channel_handle.split("/")[0]
    duration = int(meta.get("duration") or 0)
    upload_date = meta.get("upload_date") or ""  # YYYYMMDD
    if upload_date and len(upload_date) == 8:
        published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        published_at = L.today()

    # Shorts gate
    if duration > 0 and duration < SHORTS_DURATION_THRESHOLD_SECONDS and not allow_shorts_explicit:
        print(f"  [{video_id}] skipping Shorts (duration={duration}s) — pass --allow-shorts to ingest")
        return None

    # Transcript
    print(f"  [{video_id}] fetching transcript")
    transcript = fetch_transcript(video_id)
    if not transcript:
        print(f"  [{video_id}] no transcript available — skipping")
        L.log_ingest("youtube-video", video_id, "skip", {"reason": "no_transcript"})
        return None

    # Hybrid co-location
    co_book = find_co_located_book(title, transcript)
    if co_book:
        author_part = (co_book.get("authors") or ["unknown"])[0].split("-")[-1]
        title_short = co_book.get("slug")
        print(f"  [{video_id}] co-located under book: {title_short}")

    slug = L.youtube_video_slug(title, channel_handle, video_id=video_id)

    # Raw path
    if co_book:
        # raw/books/<author>/<title>/related-videos/<slug>/
        first_author = (co_book.get("authors") or ["unknown"])[0]
        raw_dir = L.RAW / "books" / first_author / co_book["slug"] / "related-videos" / slug
    else:
        ym = published_at[:7] if len(published_at) >= 7 else L.today_year_month()
        raw_dir = L.RAW / "youtube" / L.slugify(channel_handle) / ym / slug

    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    raw_meta = {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "channel_handle": channel_handle,
        "duration_seconds": duration,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "published_at": published_at,
        "ingested_at": L.today(),
        "co_located_book": co_book.get("slug") if co_book else None,
    }
    L.write_md(raw_dir / "metadata.md", raw_meta, "")

    # Synthesize
    print(f"  [{video_id}] synthesizing")
    syn = L.synthesize(
        metadata={
            "title": title, "channel": channel, "duration_minutes": duration // 60,
            "type": "youtube-video", "published_at": published_at,
        },
        content=transcript,
        max_content_chars=80_000,
    )

    # Person stub (channel host as author placeholder)
    host_slug = L.ensure_person_stub(channel, role="channel-host", domain=None)

    # Wiki page frontmatter
    base_fm = {
        "type": "youtube-video",
        "title": title,
        "video_id": video_id,
        "url": raw_meta["url"],
        "channel": L.slugify(channel_handle),
        "channel_handle": f"@{channel_handle}",
        "authors": [host_slug],
        "duration_minutes": duration // 60,
        "published_at": published_at,
        "tags": [],
        "mentioned_concepts": [],
        "mentioned_books": [co_book["slug"]] if co_book else [],
    }
    page = L.write_entity_page("youtube-video", slug, base_fm, syn, overwrite=overwrite)
    print(f"  [{video_id}] wrote {page.relative_to(L.WORKSPACE)}")
    L.log_event(f"ingest-youtube-video: {slug} ({title!r})")
    L.log_ingest("youtube-video", slug, "ok", {"video_id": video_id, "channel": channel})
    return page


# ---------------------------------------------------------------------------
# Channel ingest
# ---------------------------------------------------------------------------

def ingest_channel(
    channel_url: str,
    *,
    backfill: str = "all",
    parallel: int = DEFAULT_PARALLEL_WORKERS,
    skip_shorts: bool = True,
    overwrite: bool = False,
) -> dict:
    """Ingest all (or N) videos from a channel. Returns summary dict."""
    print(f"  enumerating videos from {channel_url}")
    if backfill == "all":
        videos = yt_channel_videos(channel_url)
    else:
        try:
            limit = int(backfill)
        except ValueError:
            raise ValueError(f"invalid --backfill {backfill!r}; use 'all' or an integer")
        videos = yt_channel_videos(channel_url, limit=limit)
    print(f"  found {len(videos)} videos (pre-filter)")
    videos = filter_shorts(videos, skip_shorts=skip_shorts)
    print(f"  {len(videos)} videos after Shorts filter (skip_shorts={skip_shorts})")

    # Write channel meta
    channel_handle = "unknown"
    if videos and videos[0].get("uploader_id"):
        channel_handle = videos[0]["uploader_id"]
    elif "@" in channel_url:
        channel_handle = channel_url.rsplit("/@", 1)[-1].split("/")[0]
    channel_meta = {
        "channel_handle": channel_handle,
        "url": channel_url,
        "video_count_in_run": len(videos),
        "ingested_at": L.today(),
    }
    channel_dir = L.RAW / "youtube" / L.slugify(channel_handle)
    channel_dir.mkdir(parents=True, exist_ok=True)
    L.write_md(channel_dir / "_meta.md", channel_meta, "")

    # Sequential default for safety; parallel via --parallel N — cloud-llm
    # internally serializes anyway because gemini's oauth_creds.json clobbers
    # cross-thread. Per-account HOME pool is in describe-attachments.py;
    # we can copy that pattern later if quota ever bites.
    successes = 0
    failures = 0
    results: list[Path | None] = []
    if parallel <= 1:
        for v in videos:
            vid = v.get("id")
            if not vid:
                continue
            try:
                p = ingest_video(vid, overwrite=overwrite)
                if p:
                    successes += 1
                    results.append(p)
                else:
                    failures += 1
            except Exception as e:
                print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                failures += 1
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
            futs = {pool.submit(ingest_video, v["id"], overwrite=overwrite): v["id"]
                    for v in videos if v.get("id")}
            for fut in concurrent.futures.as_completed(futs):
                vid = futs[fut]
                try:
                    p = fut.result()
                    if p:
                        successes += 1
                        results.append(p)
                    else:
                        failures += 1
                except Exception as e:
                    print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                    failures += 1

    summary = {"successes": successes, "failures": failures, "total": len(videos)}
    print(f"  channel ingest summary: {summary}")
    L.log_event(f"ingest-channel: {channel_handle} {summary}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="YouTube video URL or channel URL")
    ap.add_argument("--backfill", default="all",
                    help="for channel ingest: 'all' or integer count (default all)")
    ap.add_argument("--videos", help="comma-separated video IDs to ingest from a channel")
    ap.add_argument("--parallel", type=int, default=1,
                    help="parallel workers for channel ingest (default 1; bump cautiously)")
    ap.add_argument("--allow-shorts", action="store_true",
                    help="ingest a Shorts URL when passed directly")
    ap.add_argument("--include-shorts-in-channel", action="store_true",
                    help="don't filter Shorts when ingesting a channel")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    kind, payload = classify_url(args.url)
    if kind == "video":
        try:
            ingest_video(payload, allow_shorts_explicit=args.allow_shorts or is_shorts_url(args.url),
                         overwrite=args.overwrite)
        except Exception as e:
            print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    elif kind == "channel":
        try:
            if args.videos:
                # Selective ingest: ignore --backfill, just hit the listed video IDs.
                ids = [v.strip() for v in args.videos.split(",") if v.strip()]
                successes = 0
                failures = 0
                for vid in ids:
                    try:
                        p = ingest_video(vid, allow_shorts_explicit=args.allow_shorts,
                                         overwrite=args.overwrite)
                        if p:
                            successes += 1
                        else:
                            failures += 1
                    except Exception as e:
                        print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                        failures += 1
                print(f"  selective ingest: {successes} ok, {failures} failed")
            else:
                ingest_channel(
                    args.url,
                    backfill=args.backfill,
                    parallel=args.parallel,
                    skip_shorts=not args.include_shorts_in_channel,
                    overwrite=args.overwrite,
                )
        except Exception as e:
            print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    else:
        print(f"unknown URL shape: {args.url}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
