#!/usr/bin/env python3
"""
ingest-youtube.py — capture YouTube video / channel content into raw/.

Pure capture: fetch metadata via yt-dlp, transcript via youtube-summary venv,
write ONE file per video at `raw/youtube/<channel>/<YYYY-MM>/<slug>.md` with
the universal envelope. NO cloud-llm. NO wiki writes. NO co-location magic.
The wiki layer is built downstream by `/graphify --wiki`.

Single video:
  ingest-youtube.py "https://youtu.be/<id>"
  ingest-youtube.py "https://www.youtube.com/shorts/<id>"   # explicit Shorts

Channel (backfill, Shorts filtered by default):
  ingest-youtube.py "https://youtube.com/@andrewhubermanlab" --backfill all
  ingest-youtube.py "https://youtube.com/@channel" --backfill 50
  ingest-youtube.py "https://youtube.com/@channel" --videos id1,id2,id3
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path

import lib_common as L

YT_DLP = "yt-dlp"
YOUTUBE_SUMMARY_PY = Path.home() / ".ultron" / "youtube-summary" / ".venv" / "bin" / "python"
SHORTS_DURATION_THRESHOLD_SECONDS = 60
SOURCE = "youtube"


class IngestError(Exception):
    """Raised on real failures (metadata fetch, etc.). Sibling batch caller
    treats this as a per-item error. ingest_video() returns None for policy
    skips (Shorts filtered, no transcript)."""


VIDEO_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|live/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
CHANNEL_RE = re.compile(
    r"youtube\.com/(?:@([A-Za-z0-9._-]+)|c/([A-Za-z0-9._-]+)|channel/([A-Za-z0-9_-]+))"
)


def classify_url(url: str) -> tuple[str, str | None]:
    m = VIDEO_ID_RE.search(url)
    if m:
        return "video", m.group(1)
    m = CHANNEL_RE.search(url)
    if m:
        return "channel", url
    return "unknown", None


def is_shorts_url(url: str) -> bool:
    return "/shorts/" in url


def yt_metadata(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [YT_DLP, "--skip-download", "--dump-json", "--no-warnings", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


def yt_channel_videos(channel_url: str, limit: int | None = None) -> list[dict]:
    if not channel_url.rstrip("/").endswith("/videos"):
        channel_url = channel_url.rstrip("/") + "/videos"
    cmd = [YT_DLP, "--flat-playlist", "--dump-json", "--no-warnings", channel_url]
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
    if not skip_shorts:
        return videos
    out = []
    for v in videos:
        dur = v.get("duration")
        if dur is not None and dur < SHORTS_DURATION_THRESHOLD_SECONDS:
            continue
        url = v.get("url") or v.get("webpage_url") or ""
        if not isinstance(url, str):
            url = ""
        if "/shorts/" in url:
            continue
        out.append(v)
    return out


def fetch_transcript(video_id: str, languages: str = "en") -> str | None:
    if not YOUTUBE_SUMMARY_PY.exists():
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


def ingest_video(video_id: str, *, allow_shorts_explicit: bool = False) -> Path | None:
    print(f"  [{video_id}] fetching metadata")
    try:
        meta = yt_metadata(video_id)
    except Exception as e:
        raise IngestError(f"metadata fetch failed for {video_id}: {e}") from e

    title = meta.get("title") or video_id
    channel_name = meta.get("channel") or meta.get("uploader") or "unknown"
    channel_url = meta.get("channel_url") or ""
    if "@" in channel_url:
        channel_handle = channel_url.rsplit("/@", 1)[-1].split("/")[0]
    else:
        channel_handle = channel_name
    duration = int(meta.get("duration") or 0)
    upload_date = meta.get("upload_date") or ""
    published_at = (
        f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}T00:00:00Z"
        if upload_date and len(upload_date) == 8
        else None
    )
    is_short = duration > 0 and duration < SHORTS_DURATION_THRESHOLD_SECONDS

    if is_short and not allow_shorts_explicit:
        print(f"  [{video_id}] skipping Shorts (duration={duration}s) — pass --allow-shorts to ingest")
        return None

    print(f"  [{video_id}] fetching transcript")
    transcript = fetch_transcript(video_id)
    if not transcript:
        print(f"  [{video_id}] no transcript available — skipping")
        L.log_ingest("youtube", video_id, "skip", {"reason": "no_transcript"})
        return None

    slug = L.youtube_video_slug(title, channel_handle, video_id=video_id)
    ym = (published_at[:7] if published_at else L.today_year_month())
    raw_path = L.RAW / "youtube" / L.slugify(channel_handle) / ym / f"{slug}.md"
    raw_path = L.collision_safe_path(raw_path, source_url=f"https://www.youtube.com/watch?v={video_id}")
    if raw_path.stem != slug:
        slug = raw_path.stem

    extra = {
        "slug": slug,
        "video_id": video_id,
        "title": title,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "channel": channel_name,
        "channel_handle": f"@{channel_handle}" if channel_handle else None,
        "channel_url": channel_url or None,
        "duration_seconds": duration,
        "is_shorts": is_short,
    }
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=transcript,
        provider_modified_at=published_at,
        extra=extra,
    )
    print(f"  [{video_id}] wrote raw/{raw_path.relative_to(L.RAW)}")
    L.log_event(f"ingest-youtube: {slug} ({title!r})")
    L.log_ingest("youtube", slug, "ok", {"video_id": video_id, "channel": channel_name})
    return raw_path


def ingest_channel(
    channel_url: str,
    *,
    backfill: str = "all",
    parallel: int = 1,
    skip_shorts: bool = True,
) -> dict:
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

    successes = 0
    skips = 0
    failures = 0
    if parallel <= 1:
        for v in videos:
            vid = v.get("id")
            if not vid:
                continue
            try:
                p = ingest_video(vid)
                if p:
                    successes += 1
                else:
                    skips += 1
            except IngestError as e:
                print(f"  [{vid}] {e}", file=sys.stderr)
                failures += 1
            except Exception as e:
                print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                failures += 1
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
            futs = {pool.submit(ingest_video, v["id"]): v["id"]
                    for v in videos if v.get("id")}
            for fut in concurrent.futures.as_completed(futs):
                vid = futs[fut]
                try:
                    p = fut.result()
                    if p:
                        successes += 1
                    else:
                        skips += 1
                except IngestError as e:
                    print(f"  [{vid}] {e}", file=sys.stderr)
                    failures += 1
                except Exception as e:
                    print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                    failures += 1

    summary = {"successes": successes, "skips": skips, "failures": failures, "total": len(videos)}
    print(f"  channel ingest summary: {summary}")
    L.log_event(f"ingest-channel: {channel_url} {summary}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="YouTube video URL or channel URL")
    ap.add_argument("--backfill", default="all",
                    help="for channel ingest: 'all' or integer count (default all)")
    ap.add_argument("--videos", help="comma-separated video IDs to ingest from a channel")
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--allow-shorts", action="store_true",
                    help="ingest a Shorts URL when passed directly")
    ap.add_argument("--include-shorts-in-channel", action="store_true",
                    help="don't filter Shorts when ingesting a channel")
    args = ap.parse_args()

    kind, payload = classify_url(args.url)
    if kind == "video":
        try:
            ingest_video(
                payload,
                allow_shorts_explicit=args.allow_shorts or is_shorts_url(args.url),
            )
        except IngestError as e:
            print(f"  ! {e}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    elif kind == "channel":
        try:
            if args.videos:
                ids = [v.strip() for v in args.videos.split(",") if v.strip()]
                successes, skips, failures = 0, 0, 0
                for vid in ids:
                    try:
                        p = ingest_video(vid, allow_shorts_explicit=args.allow_shorts)
                        if p:
                            successes += 1
                        else:
                            skips += 1
                    except IngestError as e:
                        print(f"  [{vid}] {e}", file=sys.stderr)
                        failures += 1
                    except Exception as e:
                        print(f"  [{vid}] FATAL: {e}", file=sys.stderr)
                        failures += 1
                print(f"  selective ingest: {successes} ok, {skips} skipped, {failures} failed")
            else:
                ingest_channel(
                    args.url,
                    backfill=args.backfill,
                    parallel=args.parallel,
                    skip_shorts=not args.include_shorts_in_channel,
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
