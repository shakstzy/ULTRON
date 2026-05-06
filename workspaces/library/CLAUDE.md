---
workspace: library
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Library — Workspace Router

You are in workspace `library` — Adithya's personal learning corpus.

## What this workspace is

Books, papers, articles, podcasts, lectures, courses, and the notes / takeaways Adithya keeps from them. Source-agnostic: scraped articles via defuddle, EPUB / PDF books converted via pandoc, paper PDFs via docling, YouTube / podcast transcripts via the future ULTRON-local copy of `youtube-summary`.

This workspace does not generate content; it absorbs and indexes it. Synthesis pages connect ideas across sources.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Factual. Quote sources verbatim with attribution. Distinguish "the author claims" from "I think." Cite page / timestamp when available.

## Hard rules (workspace-specific)

1. Source items resolve via `schema.md`'s `book`, `paper`, `article`, `podcast`, `lecture` types, slugged by `<author-kebab>-<title-kebab>` (truncated).
2. Authors / speakers resolve via `person` type, with `[[@slug]]` global identity links.
3. Concepts that recur across 3+ sources get promoted to `wiki/concepts/<concept-slug>.md`.
4. Synthesis pages (`wiki/synthesis/<topic>.md`) connect ideas across sources. Soft cap 300 lines.
5. Original full text lives in `raw/`. Wiki carries notes, takeaways, quotes — not full-text reproductions of copyrighted material.
6. Commit messages: `chore(library): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What did <author> argue about <topic>? | `wiki/entities/<book\|paper\|article>/<slug>.md` |
| Who is <author>? | `wiki/entities/people/<author>.md` then `[[@author]]` |
| What does the corpus say about <concept>? | `wiki/concepts/<concept>.md` |
| Synthesis on <topic>? | `wiki/synthesis/<topic>.md` |
| Raw text of source X | `raw/<source-type>/<slug>/...` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: manual deposits in `raw/manual/_inbox/`, defuddle-extracted articles, future YouTube transcript ingest.
