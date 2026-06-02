# Stage 01 — ingest (library)

## Purpose
Pure capture. Pull a source (book, paper, YouTube, reel, article) into `raw/<source>/<path>.md` carrying the universal envelope. NO LLM. NO wiki writes. Downstream stages do everything else.

## Inputs
- A URL (any of: annas-archive md5, gutenberg epub, arxiv, YouTube, instagram, http article), OR
- A local file path (`--epub-path`, `--pdf-path`), OR
- An author name (`--author "<name>"` for the book bibliography path), OR
- A list/file/stdin for multi-URL paste, OR
- A hub URL for the blog-series crawler.

## Process
1. Dispatch via the matching `bin/ingest-*.py` (article / youtube / paper / book / reel) OR `bin/ingest-batch.py` for the bulk paths.
2. Each ingester writes ONE markdown file per item with the universal envelope per `_shell/stages/ingest/CONTEXT.md`.
3. For books, the file lands at `raw/books/<author-slug>/<book-slug>/_full.md` (folder per book). The source artifact (`source.epub` / `source.pdf`) stays alongside, gitignored.

## Outputs
- `raw/articles/<YYYY-MM>/<slug>.md`
- `raw/books/<author>/<book-slug>/_full.md` + `source.{epub,pdf}` (gitignored)
- `raw/papers/<slug>.md` + `<slug>.pdf` (gitignored)
- `raw/youtube/<channel>/<YYYY-MM>/<slug>.md`
- `raw/reels/<creator>/<YYYY-MM>/<slug>.md`
- `_meta/log.md` + `_meta/ingested.jsonl` appended

## Idempotency
Yes. `lib_common.write_raw` is a no-op when the same path exists with matching `content_hash`. `collision_safe_path` adds a 5-char URL-derived suffix when slugs collide across distinct sources.

## Invocation
```bash
bin/ingest-book.py --title "X" --author "Y"
bin/ingest-book.py --author "James Clear" --limit 5
bin/ingest-book.py --title X --author Y --whole-book   # disables chapterize for this book
bin/ingest-batch.py <urls...> | --urls file | --crawl <hub>
```

## Failure mode
Per-item. Bulk modes catch `IngestError` per URL/book and continue; batch summary records `ok / skip / error` counts. Exit code 1 if any errors.

## Next stage
`stages/02-extract/` reads `raw/books/<author>/<book-slug>/source.{epub,pdf}` and produces `_full.md`. Stage 02 is a no-op if `_full.md` is already present and matches the artifact's hash.
