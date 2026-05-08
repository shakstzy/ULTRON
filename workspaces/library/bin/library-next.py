#!/usr/bin/env python3
"""
library-next.py — the curator. Picks one bite from the corpus and serves it.

Adithya pings: "what's next to learn?" → this script reads all wiki entity
pages, scores them, and returns one. It also marks the picked entity as
delivered (updates `delivered_at` and increments `delivery_count`).

Usage:
  library-next.py                     # default: 5 minute bite, any source type
  library-next.py --minutes 10        # longer bite
  library-next.py --type book         # only books (or paper, youtube-video, etc.)
  library-next.py --tag finance       # only entities tagged with 'finance'
  library-next.py --dry-run           # don't update delivered_at, just print
  library-next.py --json              # machine-readable output

Scoring:
  read_status:
    queued       → 100
    ingested     → 60     (not yet delivered)
    delivered    → 20     (only if delivered_at > 30 days ago, for spaced recall)
    archived     → 0
  Recency bonus: ingested in last 7 days → +15
  Variety penalty: same type as last delivered → -10
  Size match: |bite_size_minutes - target| → -3 per minute off
  Tag match (if --tag passed): matching tag → +25, else excluded
"""
from __future__ import annotations

import argparse
import datetime
import json
import random
import sys
from pathlib import Path

import lib_common as L

ENTITY_TYPES_WITH_STATUS = {
    "book", "paper", "article", "podcast", "lecture", "youtube-video", "reel",
}

DELIVERED_REVISIT_DAYS = 30


def days_since(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        d = datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
    return (datetime.date.today() - d).days


def collect_candidates() -> list[tuple[Path, dict, str]]:
    """Yield (page_path, frontmatter, body) for every entity in the wiki with read_status."""
    out: list[tuple[Path, dict, str]] = []
    entities_root = L.WIKI / "entities"
    if not entities_root.exists():
        return out
    for type_dir in entities_root.iterdir():
        if not type_dir.is_dir():
            continue
        # type_dir name is plural folder name; map back to entity type
        entity_type = type_dir.name.rstrip("s")
        if type_dir.name == "people":
            continue   # people aren't bite candidates
        if type_dir.name == "youtube-channels":
            continue   # channels aggregate; not bites
        if type_dir.name not in ("books", "papers", "articles", "podcasts",
                                 "lectures", "youtube-videos", "reels"):
            continue
        for page in type_dir.glob("*.md"):
            fm, body = L.read_md(page)
            if not fm:
                continue
            if fm.get("read_status") == "archived":
                continue
            out.append((page, fm, body))
    return out


def get_last_delivered_type() -> str | None:
    """Return the type of the most recently delivered entity, or None."""
    most_recent_date: datetime.date | None = None
    most_recent_type: str | None = None
    for page, fm, _ in collect_candidates():
        d = fm.get("delivered_at")
        if not d:
            continue
        try:
            dd = datetime.date.fromisoformat(d)
        except (ValueError, TypeError):
            continue
        if most_recent_date is None or dd > most_recent_date:
            most_recent_date = dd
            most_recent_type = fm.get("type")
    return most_recent_type


def score(
    fm: dict,
    *,
    target_minutes: int,
    type_filter: str | None,
    tag_filter: str | None,
    last_delivered_type: str | None,
) -> tuple[float, list[str]]:
    """Compute score and reason list. Returns (-inf, [...]) for excluded candidates."""
    reasons: list[str] = []
    rs = fm.get("read_status") or "ingested"
    if type_filter and fm.get("type") != type_filter:
        return float("-inf"), [f"type filter excludes {fm.get('type')}"]
    if tag_filter:
        tags = fm.get("tags") or []
        if tag_filter not in tags:
            return float("-inf"), [f"tag filter excludes (tags={tags})"]
        reasons.append(f"+25 tag match")

    base = {"queued": 100, "ingested": 60, "delivered": 20}.get(rs, 0)
    if rs == "delivered":
        d = days_since(fm.get("delivered_at"))
        if d is None or d < DELIVERED_REVISIT_DAYS:
            return float("-inf"), [f"recently delivered ({d} days ago)"]
        reasons.append(f"+20 spaced recall ({d}d since)")
    else:
        reasons.append(f"+{base} {rs}")

    s = float(base)

    # Recency bonus on ingested_at
    ing_days = days_since(fm.get("ingested_at"))
    if ing_days is not None and ing_days <= 7:
        s += 15
        reasons.append("+15 recent ingest")

    # Variety penalty
    if last_delivered_type and fm.get("type") == last_delivered_type:
        s -= 10
        reasons.append("-10 same type as last")

    # Size match
    bsm = int(fm.get("bite_size_minutes") or 5)
    diff = abs(bsm - target_minutes)
    if diff > 0:
        penalty = min(diff * 3, 30)
        s -= penalty
        reasons.append(f"-{penalty} size off by {diff}min")
    else:
        reasons.append("+0 size match")

    if tag_filter:
        s += 25

    # Tiny random tiebreaker (deterministic across same bucket but not always
    # picking the alphabetically-first entity)
    s += random.uniform(0, 0.5)

    return s, reasons


def render_bite(fm: dict, body: str, page_path: Path) -> str:
    """Render the curator's output: one bite for Adithya."""
    lines: list[str] = []
    title = fm.get("title") or fm.get("slug")
    typ = fm.get("type")
    bsm = fm.get("bite_size_minutes") or 5
    lines.append(f"# {title}")
    lines.append(f"_{typ} · {bsm} min bite_\n")

    # Pull TL;DR + Key takeaways + Quote sections from body
    in_section = None
    section_text: dict[str, list[str]] = {}
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            in_section = s[3:].strip().lower()
            section_text.setdefault(in_section, [])
        elif in_section is not None:
            section_text[in_section].append(ln)

    for sect_key in ("tl;dr", "tldr"):
        if sect_key in section_text:
            lines.append("## TL;DR")
            lines.append("\n".join(section_text[sect_key]).strip())
            lines.append("")
            break

    if "key takeaways" in section_text:
        lines.append("## Key takeaways")
        lines.append("\n".join(section_text["key takeaways"]).strip())
        lines.append("")

    if "quote" in section_text:
        q = "\n".join(section_text["quote"]).strip()
        if q:
            lines.append("## Quote")
            lines.append(q)
            lines.append("")

    if "why it matters" in section_text:
        lines.append("## Why it matters")
        lines.append("\n".join(section_text["why it matters"]).strip())
        lines.append("")

    rel = page_path.relative_to(L.WORKSPACE)
    lines.append(f"_full page: `{rel}`_")
    return "\n".join(lines).rstrip() + "\n"


def mark_delivered(page_path: Path) -> None:
    fm, body = L.read_md(page_path)
    fm["read_status"] = "delivered"
    fm["delivered_at"] = L.today()
    fm["delivery_count"] = int(fm.get("delivery_count") or 0) + 1
    fm["last_touched"] = L.today()
    L.write_md(page_path, fm, body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=5,
                    help="target bite size in minutes (default 5)")
    ap.add_argument("--type", dest="type_filter",
                    help="filter to a single entity type (book / paper / youtube-video / etc.)")
    ap.add_argument("--tag", dest="tag_filter",
                    help="filter to entities with this tag")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the pick without updating delivered_at")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output")
    ap.add_argument("--top", type=int, default=1,
                    help="show top N candidates (default 1)")
    ap.add_argument("--debug-scores", action="store_true",
                    help="print all scored candidates with reasons")
    args = ap.parse_args()

    candidates = collect_candidates()
    if not candidates:
        # Distinguish "no ingest yet" from "ingest done, wiki not built"
        raw_root = L.WORKSPACE / "raw"
        any_raw = any(p.suffix == ".md" and p.name != ".gitkeep"
                      for p in raw_root.rglob("*.md")) if raw_root.exists() else False
        if any_raw:
            msg = ("wiki not built — run `/graphify --wiki workspaces/library` "
                   "to generate wiki entity pages from raw/, then re-run library-next")
        else:
            msg = "library is empty — run a `bin/ingest-*.py` first, then `/graphify --wiki workspaces/library`"
        print(msg if not args.json else json.dumps({"error": msg}), file=sys.stderr)
        return 2

    last_type = get_last_delivered_type()
    scored = []
    for page, fm, body in candidates:
        s, reasons = score(
            fm,
            target_minutes=args.minutes,
            type_filter=args.type_filter,
            tag_filter=args.tag_filter,
            last_delivered_type=last_type,
        )
        scored.append((s, page, fm, body, reasons))

    scored.sort(key=lambda r: r[0], reverse=True)
    eligible = [r for r in scored if r[0] != float("-inf")]

    if args.debug_scores:
        for s, page, fm, _, reasons in scored:
            slug = fm.get("slug")
            mark = "EXCLUDED" if s == float("-inf") else f"{s:6.1f}"
            print(f"  {mark}  {fm.get('type'):<15} {slug}  {' '.join(reasons)}")
        return 0

    if not eligible:
        msg = "no eligible candidates after filters"
        print(msg if not args.json else json.dumps({"error": msg}), file=sys.stderr)
        return 2

    picks = eligible[: args.top]

    if args.json:
        out = []
        for s, page, fm, body, reasons in picks:
            out.append({
                "score": s,
                "reasons": reasons,
                "slug": fm.get("slug"),
                "type": fm.get("type"),
                "title": fm.get("title"),
                "page": str(page.relative_to(L.WORKSPACE)),
                "bite_size_minutes": fm.get("bite_size_minutes"),
            })
        print(json.dumps({"picks": out}, indent=2, default=str))
    else:
        for i, (s, page, fm, body, reasons) in enumerate(picks):
            if i > 0:
                print("\n---\n")
            print(render_bite(fm, body, page))

    if not args.dry_run and len(picks) >= 1:
        # Mark only the top pick as delivered
        _, page, fm, _, _ = picks[0]
        mark_delivered(page)
        L.log_event(f"library-next: served {fm.get('slug')} (score {picks[0][0]:.1f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
