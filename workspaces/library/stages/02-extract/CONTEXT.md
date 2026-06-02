# Stage 02 — extract (library, books)

## Purpose
Convert each ingested book's raw artifact (`source.epub` / `source.pdf`) into a standardized markdown body at `_full.md`. Deterministic. NO LLM. Re-runnable.

## Why this is a separate stage
- Extraction is slow (pandoc 30-90s per EPUB, docling 2-5 min per PDF).
- Extraction tooling changes faster than capture — re-run extract when a better converter ships, without touching `source.epub`.
- Chapterize (Stage 03) requires standardized H1 markers, which only the extractor guarantees.

## Inputs
- `raw/books/<author>/<book-slug>/source.epub` OR `source.pdf`
- Optional: existing `_full.md` (used for idempotency check)

## Process
1. Scan `raw/books/<author>/<book-slug>/` directories.
2. For each book dir, if `_full.md` is absent OR its `source_hash` frontmatter ≠ current artifact SHA-256:
   a. EPUB: `pandoc -f epub -t markdown --wrap=none --toc-depth=2`
   b. PDF: `docling --from pdf --to md` (fallback: `pdftotext -layout`)
3. Sanity-check: body ≥ 5000 chars and ≤ 5 MB. Heading structure is NOT enforced here — chapter detection is stage 03's job, which falls back to whole-book on zero boundaries.
4. Normalize: collapse 3+ blank lines, strip pandoc/docling noise (image-tags with empty src, footnote artifacts), preserve heading hierarchy.
5. Write `_full.md` with frontmatter: `source_hash`, `extractor`, `extracted_at`, `heading_count`, `body_chars`.

## Outputs
- `raw/books/<author>/<book-slug>/_full.md` (with frontmatter envelope)
- `_meta/log.md` appended on each write
- `_meta/extract-log.jsonl` per-book record

## Idempotency
Yes — skip when `source_hash` matches AND `extractor_version` matches AND `_full.md` exists. Bumping `EXTRACTOR_VERSION` (when normalization rules change) triggers re-extract on next run. Re-run forced via `--force` or by deleting `_full.md`. Per-book `flock` (via `lib_common.book_lock`) protects against two concurrent runs corrupting the dir.

## Invocation
```bash
bin/stage-extract-book.py                          # all books
bin/stage-extract-book.py --book clear-atomic-habits   # one book
bin/stage-extract-book.py --force                  # re-run all
```

## Failure mode
Per-book isolated. One book's pandoc/docling failure does not abort siblings. Failure recorded in `extract-log.jsonl` with status `failed` + reason.

## Next stage
`stages/03-chapterize/` reads `_full.md`, splits on H1 boundaries, writes `ch-NN-<slug>.md` per chapter. Skipped for books marked `whole_book: true` at ingest time.
