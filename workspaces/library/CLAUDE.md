---
workspace: library
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Library — Workspace Router

You are in workspace `library` — Adithya's personal nonfiction learning corpus, curated for replacing scrolling with bite-sized reading.

## What this workspace is

A pull-based learning system. Adithya pastes a YouTube video / channel link, an Instagram reel, an arxiv URL, an article URL, or a book title + author. Ingest scripts in `bin/` perform pure capture: they download the content and write a single markdown file per item to `raw/<source>/<path>.md` carrying the universal envelope per `_shell/stages/ingest/CONTEXT.md`. NO LLM calls during ingest. NO wiki writes during ingest.

The wiki layer (`wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/`) is built downstream by `/graphify --wiki workspaces/library` over the populated `raw/`. The curator (`bin/library-next.py`) reads the wiki and serves one bite per call.

Sources today: YouTube videos and channels, Instagram reels, papers (arxiv + direct PDF via docling), books (Anna's Archive / direct EPUB via pandoc), web articles (defuddle), manual deposits.

## Reading order on entry

1. `schema.md` — entity types, page formats (wiki-side; raw uses universal envelope)
2. `learnings.md` — workspace meta-knowledge and operational rules
3. `identity.md` — workspace voice override (internalized + scannable)
4. `style.md` — capitalization, numbers, body section order
5. `nomenclature.md` — file-system routing

## Voice override

See `identity.md`. One-line summary: internalized + scannable, one short author quote per page, never academic. The wiki agent (run downstream by `/graphify --wiki` or a future lint stage) is the one that produces these pages, not the ingest scripts.

## Hard rules (workspace-specific)

1. **Ingest is capture-only.** Bin scripts download content into `raw/<source>/<path>.md` with the universal envelope. They do NOT call cloud-llm. They do NOT touch `wiki/`.
2. **Universal envelope** on every raw file: `source`, `workspace`, `ingested_at`, `ingest_version`, `content_hash`, `provider_modified_at`. Per-source fields layer on top.
3. **Wiki built downstream.** `/graphify --wiki workspaces/library` (or a future `_shell/stages/lint/library-wiki/` stage) generates `wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/` from raw.
4. **Original full text** lives in `raw/`. Books and papers are gitignored (full content stays local). Wiki carries takeaways and one ≤ 15 word quote per source.
5. **Skip YouTube Shorts** by default unless Adithya pastes a Shorts URL directly.
6. **Curator owns `read_status` and `delivered_at`** in wiki frontmatter. Wiki agent owns everything else there.
7. Commit messages: `chore(library): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Add a source | Run the matching `bin/ingest-*.py` (writes raw only) |
| Build the wiki | `/graphify --wiki workspaces/library` |
| What's next to learn? | `bin/library-next.py [--minutes N]` (requires populated wiki) |
| What did <author> argue about <topic>? | `wiki/entities/<book\|paper\|article>/<slug>.md` |
| What does the corpus say about <concept>? | `wiki/concepts/<concept>.md` |
| Synthesis on <topic>? | `wiki/synthesis/<topic>.md` |
| Raw text of source X | `raw/<source>/<slug>.md` |

## Ingest entry points

```bash
# Single-source ingest (capture-only, writes to raw/)
bin/ingest-book.py --title "<title>" --author "<author>"
bin/ingest-book.py --url "https://annas-archive.org/md5/<md5>"
bin/ingest-book.py --epub-path /path/to/book.epub --title X --author Y

bin/ingest-youtube.py "<video-or-channel-url>"
bin/ingest-youtube.py "<channel-url>" --backfill all
bin/ingest-youtube.py "<channel-url>" --backfill 50
bin/ingest-youtube.py "<channel-url>" --videos id1,id2,id3

bin/ingest-reel.py "<instagram-url>"
bin/ingest-paper.py "<arxiv-or-doi-or-pdf-url>"
bin/ingest-article.py "<url>"

# Bulk ingest
bin/ingest-book.py --author "James Clear"                 # all books by author from annas-archive
bin/ingest-book.py --author "James Clear" --limit 5 --dry-run

bin/ingest-batch.py url1 url2 url3                        # multi-URL paste (positional)
bin/ingest-batch.py --urls list.txt                       # one URL per line, # comments OK
cat list.txt | bin/ingest-batch.py --urls -               # stdin
bin/ingest-batch.py --crawl https://paulgraham.com/articles.html
bin/ingest-batch.py --crawl <hub> --limit 5 --dry-run     # preview before downloading
bin/ingest-batch.py --crawl <hub> --include-pattern '/posts/' --exclude-pattern '/tag/'

# After ingest, build the wiki:
/graphify --wiki workspaces/library

# Then ask for next bite:
bin/library-next.py [--minutes N] [--type book|youtube-video|paper|...]
```

## Agents

- `agents/wiki-agent.md` — runs DOWNSTREAM of ingest (lint stage or graphify), not from `bin/ingest-*.py`. Synthesizes wiki entity pages from `raw/` per the schema.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Scheduled jobs in `config/schedule.yaml` (lint daily; no scheduled ingest, all ingest is on-demand).
