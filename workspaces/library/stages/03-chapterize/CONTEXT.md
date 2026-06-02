# Stage 03 — chapterize (library, books)

## Purpose
Split each book's `_full.md` into per-chapter `ch-NN-<slug>.md` files so the curator (`library-next`) can serve one chapter at a time. Deterministic. NO LLM.

## Inputs
- `raw/books/<author>/<book-slug>/_full.md` (output of stage 02)
- Book frontmatter `whole_book: <bool>` (set by `ingest-book.py --whole-book`)

## Process
1. Scan `raw/books/*/*/`.
2. Skip when `whole_book: true` in `_full.md` frontmatter — book is consumed as one unit.
3. Detect chapter boundaries in `_full.md`:
   a. Primary: `^# ` H1 lines (well-structured EPUBs). Requires ≥3.
   b. Fallback A: `^## ` H2 lines (Gutenberg-style EPUBs where the book title is the only H1). Requires ≥3 AND mean chunk size ≥ MIN_H2_DOMINANCE_WORDS so we don't mis-split a chapter's sub-sections.
   c. Fallback B: `^(Chapter|CHAPTER|Part|PART|Book|BOOK)\s+(\d+|[IVXLCDM]+)` regex (body-only PDFs). Requires ≥3.
   d. If zero boundaries OR every slice ended below MIN_CHAPTER_WORDS: mark the book `whole_book: true` so the curator serves it as one bite.
4. For each chapter:
   - Slug: `ch-<NNN>-<title-3-words>` — 3-digit zero-padded so lexicographic sort matches numeric sort up to 999 chapters. Empty title escalates to `section-<NNN>`.
   - Frontmatter: `parent_book: [[<book-slug>]]`, `chapter_number: N`, `chapter_title: <title>`, `bite_size_minutes` = max(1, round(words / 200)).
   - Body: heading + content, trimmed.
   - Includes the universal envelope (source = book, content_hash on chapter body).
5. Write `raw/books/<author>/<book-slug>/ch-NNN-<slug>.md` atomically (lib_common.write_md does tmp+os.replace).
6. Write `chapter-manifest.json` listing current shards. Files matching `ch-*.md` but not in the manifest are MOVED (not deleted) to `<book-dir>/.orphans/` — keeps the active set clean while preserving history for lint review.
7. Record run in `_meta/chapterize-log.jsonl`: `{book_slug, chapters_written, chapter_count, mode: h1|h2|regex|whole_book, orphans_moved, ts}`.

## Idempotency
Yes. A chapter file with matching `content_hash` is a no-op. If `_full.md` changes, chapter set is rewritten (additions overwrite; orphans flagged in lint, never deleted).

## Outputs
- `raw/books/<author>/<book-slug>/ch-NN-<slug>.md` × N
- `_meta/chapterize-log.jsonl` appended

## Invocation
```bash
bin/stage-chapterize-book.py                       # all books
bin/stage-chapterize-book.py --book clear-atomic-habits
bin/stage-chapterize-book.py --force               # regenerate from scratch
bin/stage-chapterize-book.py --dry-run             # report intended splits, no writes
```

## Failure mode
Per-book isolated. Zero-boundary fallback → whole_book shadow (the curator still gets a deliverable). Other parse errors → log + skip + continue.

## Next stage
`stages/04-wiki-build/` reads the per-chapter files plus the book `_full.md` frontmatter and synthesizes wiki entity pages — one per book at `wiki/entities/books/<slug>.md` and (when chapters exist) one per chapter at `wiki/entities/chapters/<book-slug>__ch-NN.md`.
