#!/usr/bin/env python3
"""
stage-chapterize-book.py — split each book's _full.md into per-chapter files.

Deterministic. No LLM. Idempotent on chapter content_hash. Skips books with
`whole_book: true` in their _full.md frontmatter (those are consumed whole).

Boundary detection priority:
  1. H1 (^# Heading) — what pandoc emits from a well-structured EPUB TOC.
  2. "Chapter N" / "CHAPTER N" / "Part N" — heuristic for PDF/TXT bodies that
     don't have proper headings.
  3. Nothing detected → mark the book as whole_book so curator still has it.

Output paths:
  raw/books/<author>/<book-slug>/ch-NN-<slug>.md

Each chapter file has its own frontmatter (universal envelope + chapter fields).

Usage:
  stage-chapterize-book.py
  stage-chapterize-book.py --book clear-atomic-habits
  stage-chapterize-book.py --force          # rewrite even when content_hash matches
  stage-chapterize-book.py --dry-run        # report intended splits, no writes
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import lib_common as L


SOURCE = "book"
CHAPTERIZER_VERSION = 2          # bumped after H2-dominance + manifest changes
WORDS_PER_MINUTE = 200           # reading speed for bite_size estimate
MIN_CHAPTER_WORDS = 50           # below this is metadata noise, not a chapter
MIN_H2_DOMINANCE_WORDS = 800     # H2 fallback only fires when mean chunk ≥ this
MAX_CHAPTER_TITLE_LEN = 80
MANIFEST_NAME = "chapter-manifest.json"


# ---------------------------------------------------------------------------
# Boundary detection
# ---------------------------------------------------------------------------

H1_RE = re.compile(r"^# (?P<title>.+?)\s*$", re.MULTILINE)
H2_RE = re.compile(r"^## (?P<title>.+?)\s*$", re.MULTILINE)
CHAPTER_REGEX_RE = re.compile(
    r"^(?:Chapter|CHAPTER|Part|PART|Book|BOOK)\s+(?:[IVXLCDM]+|\d+)(?:[.:]\s*(?P<rest>.+?))?\s*$",
    re.MULTILINE,
)

# Pandoc emits attribute clutter on headings: `# Title {#anchor.class}`.
_HEADING_ATTR_RE = re.compile(r"\s*\{[^}]*\}\s*$")


def _clean_title(raw: str) -> str:
    return _HEADING_ATTR_RE.sub("", raw).strip()[:MAX_CHAPTER_TITLE_LEN]


def _bounds_with_dominance(body: str, matches, min_avg_words: int) -> bool:
    """Return True when the average chunk size between match boundaries is
    at least `min_avg_words`. Used to reject H2 fallback that's splitting a
    chapter into sub-sections (mean chunk too small) rather than splitting
    a book into chapters."""
    if len(matches) < 3:
        return False
    n = len(body)
    chunk_sizes: list[int] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else n
        chunk_sizes.append(len(body[start:end].split()))
    if not chunk_sizes:
        return False
    avg = sum(chunk_sizes) / len(chunk_sizes)
    return avg >= min_avg_words


def detect_boundaries(body: str) -> tuple[str, list[tuple[int, str]]]:
    """Return (mode, [(offset, title)...]) listing chapter start positions in body.

    mode priority:
      'h1' (≥3 H1s, any spacing) — the well-structured EPUB case.
      'h2' (≥3 H2s, mean chunk ≥ MIN_H2_DOMINANCE_WORDS) — Gutenberg-style
            EPUBs where the book title is the only H1. The dominance check
            rejects mis-splits in books where H2 is a sub-section level.
      'regex' (≥3 Chapter-N / Part-N lines) — fallback for body-only PDFs.
      'none' (caller falls back to whole-book).
    """
    h1s = list(H1_RE.finditer(body))
    if len(h1s) >= 3:
        return "h1", [(m.start(), _clean_title(m.group("title"))) for m in h1s]
    h2s = list(H2_RE.finditer(body))
    if _bounds_with_dominance(body, h2s, MIN_H2_DOMINANCE_WORDS):
        return "h2", [(m.start(), _clean_title(m.group("title"))) for m in h2s]
    matches = list(CHAPTER_REGEX_RE.finditer(body))
    if len(matches) >= 3:
        return "regex", [(m.start(), _clean_title(m.group(0))) for m in matches]
    return "none", []


def slice_chapters(body: str, boundaries: list[tuple[int, str]]) -> list[dict]:
    """Return [{number, title, body, words}, ...]. Drops zero-content runs."""
    chapters: list[dict] = []
    n = len(body)
    for i, (start, title) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else n
        chunk = body[start:end].strip()
        words = len(chunk.split())
        if words < MIN_CHAPTER_WORDS:
            continue
        chapters.append({
            "number": len(chapters) + 1,    # re-number after dropping short runs
            "title": title,
            "body": chunk,
            "words": words,
        })
    return chapters


# ---------------------------------------------------------------------------
# Slug + frontmatter
# ---------------------------------------------------------------------------

def chapter_slug(number: int, title: str) -> str:
    """3-digit zero-padded number so lexicographic sort matches numeric sort
    up to 999 chapters. Empty title escalates to `section-NNN` so two empty
    titles don't both fold to `ch-NNN-untitled`."""
    title_part = L.title_words_slug(title or "", n_words=3)
    if not title_part:
        title_part = f"section-{number:03d}"
    return f"ch-{number:03d}-{title_part}"


def estimate_bite_minutes(words: int) -> int:
    return max(1, round(words / WORDS_PER_MINUTE))


def write_chapter(
    book_dir: Path,
    book_slug: str,
    chapter: dict,
    book_fm: dict,
    *,
    force: bool,
) -> tuple[str, str]:
    """Returns (status, slug) where status ∈ {'ok','noop','overwrite'}."""
    slug = chapter_slug(chapter["number"], chapter["title"])
    path = book_dir / f"{slug}.md"
    new_hash = L.content_hash(chapter["body"])
    existed = path.exists()

    if existed and not force:
        existing_fm, _ = L.read_md(path)
        if existing_fm.get("content_hash") == new_hash:
            return "noop", slug

    title_for_fm = chapter["title"] or f"Section {chapter['number']}"
    extra = {
        "slug": slug,
        "title": title_for_fm,
        "parent_book": f"[[{book_slug}]]",
        "book_slug": book_slug,
        "chapter_number": chapter["number"],
        "chapter_title": title_for_fm,
        "chapter_words": chapter["words"],
        "bite_size_minutes": estimate_bite_minutes(chapter["words"]),
        "chapterizer_version": CHAPTERIZER_VERSION,
        "author": book_fm.get("author"),
        "year": book_fm.get("year"),
    }
    L.write_raw(path, source=SOURCE, body=chapter["body"],
                provider_modified_at=book_fm.get("provider_modified_at"),
                extra=extra)
    return ("overwrite" if existed else "ok"), slug


def mark_whole_book(book_dir: Path) -> None:
    """Mutate _full.md frontmatter to set whole_book=True after zero boundaries."""
    full_path = book_dir / "_full.md"
    fm, body = L.read_md(full_path)
    fm["whole_book"] = True
    fm["chapterize_status"] = "fallback-whole-book"
    fm["last_touched"] = L.today()
    L.write_md(full_path, fm, body)


# ---------------------------------------------------------------------------
# Per-book orchestration
# ---------------------------------------------------------------------------

def _load_manifest(book_dir: Path) -> dict:
    p = book_dir / MANIFEST_NAME
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_manifest(book_dir: Path, manifest: dict) -> None:
    p = book_dir / MANIFEST_NAME
    p.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rename_orphans(book_dir: Path, current_slugs: set[str]) -> list[str]:
    """Find ch-*.md files not produced by the current run and move them
    under `.orphans/<slug>.md`. Never deletes. Returns the list of moved slugs."""
    orphan_dir = book_dir / ".orphans"
    moved: list[str] = []
    for f in sorted(book_dir.glob("ch-*.md")):
        if f.stem in current_slugs:
            continue
        orphan_dir.mkdir(exist_ok=True)
        target = orphan_dir / f.name
        # If a previous orphan with the same name exists, suffix with timestamp
        if target.exists():
            ts = L.iso_utc().replace(":", "").replace("-", "")[:14]
            target = orphan_dir / f"{f.stem}.{ts}.md"
        f.rename(target)
        moved.append(f.stem)
    return moved


def chapterize_book(book_dir: Path, *, force: bool, dry_run: bool) -> dict:
    full_path = book_dir / "_full.md"
    if not full_path.exists():
        return {"book": book_dir.name, "status": "skip", "reason": "no _full.md"}

    fm, body = L.read_md(full_path)
    book_slug = fm.get("slug") or book_dir.name

    if fm.get("whole_book"):
        return {"book": book_dir.name, "status": "skip",
                "reason": "whole_book=true",
                "book_slug": book_slug}

    mode, boundaries = detect_boundaries(body)
    chapters = slice_chapters(body, boundaries) if boundaries else []

    # Three fallback paths to whole-book:
    #   1. No boundaries detected at all
    #   2. Every slice ended up below MIN_CHAPTER_WORDS
    if not boundaries or not chapters:
        if dry_run:
            return {"book": book_dir.name,
                    "status": "would-fallback-whole-book",
                    "book_slug": book_slug, "mode": mode,
                    "reason": ("zero-boundaries" if not boundaries
                               else "all-slices-too-short")}
        mark_whole_book(book_dir)
        return {"book": book_dir.name, "status": "fallback-whole-book",
                "book_slug": book_slug, "mode": mode,
                "reason": ("zero-boundaries" if not boundaries
                           else "all-slices-too-short")}

    if dry_run:
        return {"book": book_dir.name, "status": "would-chapterize",
                "book_slug": book_slug, "mode": mode,
                "chapters_planned": len(chapters)}

    # Real run — guard with per-book lock
    try:
        with L.book_lock(book_dir):
            return _do_chapterize(book_dir, book_slug, chapters, fm, mode, force)
    except BlockingIOError:
        return {"book": book_dir.name, "status": "locked",
                "book_slug": book_slug,
                "reason": "another chapterize/extract run holds the book lock"}


def _do_chapterize(book_dir: Path, book_slug: str, chapters: list[dict],
                   fm: dict, mode: str, force: bool) -> dict:
    written = 0
    noop = 0
    current_slugs: set[str] = set()
    for c in chapters:
        status, slug = write_chapter(book_dir, book_slug, c, fm, force=force)
        current_slugs.add(slug)
        if status == "noop":
            noop += 1
        else:
            written += 1

    orphans = _rename_orphans(book_dir, current_slugs)
    _write_manifest(book_dir, {
        "book_slug": book_slug,
        "mode": mode,
        "chapter_count": len(chapters),
        "source_hash": fm.get("source_hash"),
        "chapterizer_version": CHAPTERIZER_VERSION,
        "chapter_slugs": sorted(current_slugs),
        "orphans_moved": orphans,
        "updated_at": L.iso_utc(),
    })

    return {"book": book_dir.name, "status": "ok",
            "book_slug": book_slug, "mode": mode,
            "chapters_written": written, "chapters_unchanged": noop,
            "chapters_total": len(chapters),
            "orphans_moved": orphans}


def log_record(rec: dict) -> None:
    L.META.mkdir(parents=True, exist_ok=True)
    rec = dict(rec)
    rec["ts"] = L.iso_utc()
    with open(L.META / "chapterize-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_books(author_filter: str | None, book_filter: str | None) -> list[Path]:
    root = L.RAW / "books"
    if not root.exists():
        return []
    out: list[Path] = []
    for author_dir in sorted(root.iterdir()):
        if not author_dir.is_dir():
            continue
        if author_dir.name.startswith("."):
            continue
        if author_filter and author_dir.name != author_filter:
            continue
        for book_dir in sorted(author_dir.iterdir()):
            if not book_dir.is_dir():
                continue
            if book_dir.name.startswith("."):
                continue
            if book_filter and book_dir.name != book_filter:
                continue
            if (book_dir / "_full.md").exists():
                out.append(book_dir)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author")
    ap.add_argument("--book")
    ap.add_argument("--force", action="store_true",
                    help="rewrite chapter files even when content_hash matches")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    books = find_books(args.author, args.book)
    if not books:
        print("  no books with _full.md found — run stage-extract-book.py first",
              file=sys.stderr)
        return 2

    summary: dict[str, int] = {"total": len(books)}
    for i, book_dir in enumerate(books, 1):
        rel = book_dir.relative_to(L.RAW)
        print(f"[{i}/{len(books)}] {rel}")
        rec = chapterize_book(book_dir, force=args.force, dry_run=args.dry_run)
        summary[rec["status"]] = summary.get(rec["status"], 0) + 1
        log_record(rec)
        if rec["status"] == "ok":
            extra = f", {len(rec['orphans_moved'])} orphans" if rec.get("orphans_moved") else ""
            print(f"  {rec['mode']}: {rec['chapters_written']} written, "
                  f"{rec['chapters_unchanged']} noop (total {rec['chapters_total']}{extra})")
        elif rec["status"].startswith("fallback") or rec["status"].startswith("would-fallback"):
            print(f"  fallback to whole-book: mode={rec.get('mode')} reason={rec.get('reason')}")
        elif rec["status"] == "locked":
            print(f"  locked: {rec.get('reason')}")
        elif rec["status"] == "skip":
            print(f"  skip: {rec.get('reason')}")
    fallbacks = summary.get("fallback-whole-book", 0) + summary.get("would-fallback-whole-book", 0)
    print(f"  chapterize summary: {summary}" + (f"  ({fallbacks} fell back to whole-book)" if fallbacks else ""))
    if not args.dry_run:
        L.log_event(f"stage-chapterize-book: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
