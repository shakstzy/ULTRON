#!/usr/bin/env python3
"""
stage-extract-book.py — convert each book's raw artifact (source.epub / source.pdf)
into a standardized _full.md alongside it.

Pure capture pipeline stage. No LLM. No wiki writes. Deterministic. Idempotent
on source-file SHA-256: if _full.md already records the same source_hash, skip.

Path convention (post-refactor):
  raw/books/<author-slug>/<book-slug>/
    ├── source.epub          # gitignored
    ├── _full.md             # this script's output
    └── ch-NN-<slug>.md      # stage 03 output

Usage:
  stage-extract-book.py                       # walk all books
  stage-extract-book.py --book clear-atomic-habits
  stage-extract-book.py --author henry-thoreau
  stage-extract-book.py --force               # re-extract regardless of hash
  stage-extract-book.py --dry-run             # report what would run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import lib_common as L


class ExtractError(Exception):
    """Raised on extraction failure. Caught at the book level; siblings continue."""


SOURCE = "book"
EXTRACTOR_VERSION = 2            # bumped after normalize() regex tightening
MIN_BODY_CHARS = 5_000
ARTIFACT_NAMES = ("source.epub", "source.pdf")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_books(
    author_filter: str | None = None,
    book_filter: str | None = None,
) -> list[Path]:
    """Yield every `raw/books/<author>/<book>/` directory containing an artifact."""
    root = L.RAW / "books"
    if not root.exists():
        return []
    out: list[Path] = []
    for author_dir in sorted(root.iterdir()):
        if not author_dir.is_dir() or author_dir.name.startswith("."):
            continue
        if author_filter and author_dir.name != author_filter:
            continue
        for book_dir in sorted(author_dir.iterdir()):
            if not book_dir.is_dir() or book_dir.name.startswith("."):
                continue
            if book_filter and book_dir.name != book_filter:
                continue
            if any((book_dir / n).exists() for n in ARTIFACT_NAMES):
                out.append(book_dir)
    return out


def artifact_for(book_dir: Path) -> Path | None:
    for n in ARTIFACT_NAMES:
        p = book_dir / n
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def epub_to_markdown(epub_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pandoc", "-f", "epub", "-t", "markdown",
        "--wrap=none", "--toc-depth=2",
        "-o", str(out_path), str(epub_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise ExtractError(f"pandoc failed: {proc.stderr.strip()[:200]}")


def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    docling = shutil.which("docling")
    if docling:
        cmd = [docling, "--from", "pdf", "--to", "md",
               "--output", str(out_path.parent), str(pdf_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if proc.returncode == 0:
            produced = out_path.parent / (pdf_path.stem + ".md")
            if produced.exists() and produced.resolve() != out_path.resolve():
                shutil.move(produced, out_path)
            if out_path.exists():
                return
            sys.stderr.write("  docling exited 0 but no markdown; falling back\n")
        else:
            sys.stderr.write(f"  docling failed (rc={proc.returncode}); falling back to pdftotext\n")
    if shutil.which("pdftotext"):
        cmd = ["pdftotext", "-layout", str(pdf_path), str(out_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if proc.returncode != 0:
            raise ExtractError(f"pdftotext failed: {proc.stderr.strip()[:200]}")
        return
    raise ExtractError("neither docling nor pdftotext available")


def extract_artifact(artifact: Path, out_path: Path) -> str:
    """Returns the extractor name used."""
    suffix = artifact.suffix.lower()
    if suffix == ".epub":
        epub_to_markdown(artifact, out_path)
        return "pandoc:epub"
    if suffix == ".pdf":
        # pdf_to_markdown probes docling, falls back to pdftotext
        if shutil.which("docling"):
            return _do_pdf_extract(artifact, out_path, prefer="docling")
        return _do_pdf_extract(artifact, out_path, prefer="pdftotext")
    raise ExtractError(f"unsupported artifact suffix: {suffix}")


def _do_pdf_extract(artifact: Path, out_path: Path, *, prefer: str) -> str:
    pdf_to_markdown(artifact, out_path)
    return f"{prefer}:pdf"


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

_MULTI_BLANK_RE = re.compile(r"\n{3,}")
_EMPTY_IMG_RE = re.compile(r"!\[\]\(\s*\)\s*")
# Pandoc emits `::: {.attrs}` to open a div and `:::` to close. The wrapper
# bracket lines are noise, but the content between them IS the book body —
# stripping the span eats whole chapters. Drop only the marker lines.
_PANDOC_DIV_OPEN_RE = re.compile(r"^::: ?\{[^}]*\}\s*$", re.MULTILINE)
_PANDOC_DIV_CLOSE_RE = re.compile(r"^:::\s*$", re.MULTILINE)
# Empty anchor wherever it appears: `[]{#id}` (line-leading OR inline).
# Pandoc emits these at H2 headers AND mid-paragraph for chapter cross-refs.
_EMPTY_ANCHOR_INLINE_RE = re.compile(r"\[\]\{#[^}]+\}")
# Trailing attribute on a heading line ONLY: `## Title {#id .class}` → `## Title`.
# Anchoring to end-of-line is essential — inline `[term]{#crossref}` in body
# prose must be left intact (those are real Pandoc cross-references).
_TRAILING_HEADING_ATTR_RE = re.compile(
    r"(?P<head>^#{1,6} .+?)\s*\{[^}]+\}\s*$", re.MULTILINE,
)
# H2-level anchor leading the heading text: `## []{#anchor}Real Title`
_H2_ANCHOR_PREFIX_RE = re.compile(r"^(##+ +)\[\]\{#[^}]+\}", re.MULTILINE)
_HEADING_RE = re.compile(r"^# .*$", re.MULTILINE)


def normalize(md: str) -> str:
    md = _EMPTY_IMG_RE.sub("", md)
    md = _PANDOC_DIV_OPEN_RE.sub("", md)
    md = _PANDOC_DIV_CLOSE_RE.sub("", md)
    md = _H2_ANCHOR_PREFIX_RE.sub(r"\1", md)
    md = _EMPTY_ANCHOR_INLINE_RE.sub("", md)
    # Strip trailing `{...}` attribute clutter from heading lines only.
    md = _TRAILING_HEADING_ATTR_RE.sub(r"\g<head>", md)
    md = _MULTI_BLANK_RE.sub("\n\n", md)
    return md.strip() + "\n"


def sanity_check(md: str) -> tuple[bool, list[str]]:
    """Body length only. Chapter-structure validation is stage 03's job —
    chapterize falls back to whole-book when no boundaries are found."""
    failures: list[str] = []
    if len(md) < MIN_BODY_CHARS:
        failures.append(f"body length {len(md):,} < {MIN_BODY_CHARS:,}")
    if len(md) > 5_000_000:
        failures.append(f"body length {len(md):,} suspiciously large")
    return (not failures), failures


# ---------------------------------------------------------------------------
# Orchestration per book
# ---------------------------------------------------------------------------

def load_existing(out_path: Path) -> tuple[dict, str]:
    if not out_path.exists():
        return {}, ""
    return L.read_md(out_path)


def extract_book(book_dir: Path, *, force: bool, dry_run: bool) -> dict:
    """Returns a result record dict. Idempotent on (source_hash,
    extractor_version): if both match, noop. A bump to EXTRACTOR_VERSION
    forces re-extract on next run even when the artifact hash is unchanged.
    Per-book flock guards against two concurrent runs corrupting the dir."""
    artifact = artifact_for(book_dir)
    if not artifact:
        return {"book": book_dir.name, "status": "skip", "reason": "no artifact"}
    artifact_hash = L.file_sha256(artifact)
    out_path = book_dir / "_full.md"
    existing_fm, _ = load_existing(out_path)

    same_hash = existing_fm.get("source_hash") == artifact_hash
    same_version = int(existing_fm.get("extractor_version") or 0) == EXTRACTOR_VERSION
    if not force and same_hash and same_version and out_path.exists():
        return {"book": book_dir.name, "status": "noop", "source_hash": artifact_hash}

    if dry_run:
        return {"book": book_dir.name, "status": "would-extract",
                "artifact": artifact.name, "source_hash": artifact_hash,
                "version_bump": not same_version}

    try:
        with L.book_lock(book_dir):
            return _do_extract(book_dir, artifact, artifact_hash, existing_fm, out_path)
    except BlockingIOError:
        return {"book": book_dir.name, "status": "locked",
                "reason": "another extract run holds the book lock"}


def _do_extract(book_dir: Path, artifact: Path, artifact_hash: str,
                existing_fm: dict, out_path: Path) -> dict:
    print(f"  extracting {artifact.relative_to(L.RAW)}")
    # Per-process tmpfile name so concurrent fallback attempts don't trample
    body_path = book_dir / f"_full.body.{os.getpid()}.md"
    try:
        extractor = extract_artifact(artifact, body_path)
    except ExtractError as e:
        body_path.unlink(missing_ok=True)
        return {"book": book_dir.name, "status": "failed", "reason": str(e)}

    body = body_path.read_text(encoding="utf-8", errors="replace")
    body_path.unlink(missing_ok=True)
    body = normalize(body)

    ok, failures = sanity_check(body)
    if not ok:
        return {"book": book_dir.name, "status": "failed",
                "reason": "sanity check: " + "; ".join(failures)}

    # Preserve whole_book flag from existing frontmatter (set by ingest --whole-book)
    whole_book = bool(existing_fm.get("whole_book"))
    extra = {
        "source_hash": artifact_hash,
        "extractor": extractor,
        "extractor_version": EXTRACTOR_VERSION,
        "extracted_at": L.iso_utc(),
        "heading_count": len(_HEADING_RE.findall(body)),
        "body_chars": len(body),
        "whole_book": whole_book,
        "extract_status": "ok",                    # flip ingest's 'pending' stub
    }
    # Carry forward book-level metadata set by ingest if present (title, author, etc.).
    for k in ("slug", "title", "author", "year", "isbn", "language", "format",
              "source_url", "annas_md5", "artifact_sha256"):
        if k in existing_fm and k not in extra:
            extra[k] = existing_fm[k]

    L.write_raw(out_path, source=SOURCE, body=body,
                provider_modified_at=existing_fm.get("provider_modified_at"),
                extra=extra)
    print(f"  wrote raw/{out_path.relative_to(L.RAW)} ({extra['body_chars']:,} chars, {extra['heading_count']} H1s)")
    return {"book": book_dir.name, "status": "ok", "extractor": extractor,
            "source_hash": artifact_hash, "body_chars": extra["body_chars"],
            "heading_count": extra["heading_count"]}


def log_record(rec: dict) -> None:
    L.META.mkdir(parents=True, exist_ok=True)
    rec = dict(rec)
    rec["ts"] = L.iso_utc()
    with open(L.META / "extract-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="filter to a single author slug")
    ap.add_argument("--book", help="filter to a single book slug")
    ap.add_argument("--force", action="store_true", help="re-extract even when source_hash matches")
    ap.add_argument("--dry-run", action="store_true", help="report what would run, no writes")
    args = ap.parse_args()

    books = find_books(author_filter=args.author, book_filter=args.book)
    if not books:
        print("  no books found", file=sys.stderr)
        return 2

    summary = {"total": len(books), "ok": 0, "noop": 0, "skip": 0, "failed": 0,
               "would-extract": 0}
    for i, book_dir in enumerate(books, 1):
        rel = book_dir.relative_to(L.RAW)
        print(f"[{i}/{len(books)}] {rel}")
        rec = extract_book(book_dir, force=args.force, dry_run=args.dry_run)
        summary[rec["status"]] = summary.get(rec["status"], 0) + 1
        log_record(rec)
        if rec["status"] == "failed":
            sys.stderr.write(f"  ! {rec['book']}: {rec['reason']}\n")

    print(f"  extract summary: {summary}")
    if not args.dry_run:
        L.log_event(f"stage-extract-book: {summary}")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
