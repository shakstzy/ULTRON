---
workspace: library
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Library — Workspace Router

You are in workspace `library` — Adithya's personal nonfiction learning corpus, curated for replacing scrolling with bite-sized reading.

## What this workspace is

A pull-based learning system. Adithya pastes a YouTube video / channel link, an Instagram reel, an arxiv URL, an article URL, or a book title + author. Ingest scripts download the raw content, validate it, and write a wiki entity page with takeaways in Adithya's voice. When Adithya asks "what's next," the curator (`bin/library-next.py`) reads corpus state and serves one bite sized to fit the moment. The wiki is the substrate, the curator is the product.

Sources today: YouTube videos, YouTube channels (batch), Instagram reels, papers (arxiv / doi via docling), books (Anna's Archive / LibGen with EPUB → markdown via pandoc), web articles (defuddle), manual deposits.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge and operational rules
3. `identity.md` — workspace voice override (internalized + scannable)
4. `style.md` — capitalization, numbers, body section order
5. `nomenclature.md` — file-system routing

## Voice override

See `identity.md`. One-line summary: internalized + scannable, one short author quote per page, never academic. Pages read like Adithya thinking out loud after finishing the source.

## Hard rules (workspace-specific)

1. **Source items resolve via `schema.md`** — `book`, `paper`, `article`, `podcast`, `lecture`, `youtube-video`, `youtube-channel`, `reel` types, slugged per `nomenclature.md`.
2. **Authors / speakers / channel hosts** resolve via `person` type, with `[[@slug]]` global identity links when the person crosses workspaces.
3. **Concepts** that recur across 3+ sources get auto-promoted to `wiki/concepts/<concept-slug>.md` by the wiki agent.
4. **Synthesis pages** (`wiki/synthesis/<topic>.md`) connect ideas across 5+ sources clustered on a topic. Auto-proposed by wiki agent, surfaced by lint, green-lit by Adithya. Soft cap 300 lines.
5. **Original full text** lives in `raw/`. Books and papers are gitignored (full text stays local). Wiki carries takeaways and one ≤ 15 word quote per source.
6. **Skip YouTube Shorts** by default unless Adithya pastes a Shorts URL directly.
7. **Hybrid co-location**: book-specific videos file under the book; standalone videos file under the channel. Resolved at ingest by the wiki agent.
8. **Curator owns `read_status` and `delivered_at`** frontmatter fields. Wiki agent owns everything else.
9. Commit messages: `chore(library): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What's next to learn? | Run `bin/library-next.py [--minutes N]` |
| What did <author> argue about <topic>? | `wiki/entities/<book\|paper\|article>/<slug>.md` |
| What does the corpus say about <concept>? | `wiki/concepts/<concept>.md` |
| Synthesis on <topic>? | `wiki/synthesis/<topic>.md` |
| Who is <author / speaker>? | `wiki/entities/people/<slug>.md` then `[[@slug]]` |
| What's queued vs delivered? | Filter `wiki/entities/*` by `read_status` |
| Raw text of source X | `raw/<source-type>/<slug>/...` |

## Ingest entry points

```bash
bin/ingest-book.py "<title>" --author "<author>"
bin/ingest-book.py --url "https://annas-archive.org/md5/<md5>"

bin/ingest-youtube.py "<video-or-channel-url>"
bin/ingest-youtube.py "<channel-url>" --backfill all
bin/ingest-youtube.py "<channel-url>" --backfill 50

bin/ingest-reel.py "<instagram-url>"
bin/ingest-paper.py "<arxiv-or-doi-or-pdf-url>"
bin/ingest-article.py "<url>"

bin/library-next.py [--minutes N] [--type book|youtube-video|paper|...]
```

## Agents

- `agents/wiki-agent.md` — used by ingest scripts for wiki page synthesis
- `agents/lint-agent.md` — used by lint stage

## Sources

Declared in `config/sources.yaml`. Scheduled jobs in `config/schedule.yaml` (lint daily; no scheduled ingest, all ingest is on-demand).
