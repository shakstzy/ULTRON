# LLM Wiki — Schema

A persistent, compounding personal knowledge base. You (the LLM) read raw sources, integrate them into the wiki, and maintain it over time. Adithya curates sources and asks questions. You do all the writing.

## Layout

- `raw/` — source documents (articles, PDFs, notes, transcripts, screenshots). Immutable. Never edit, never delete.
- `wiki/` — all generated pages. You own this layer end-to-end.
- `index.md` — catalog of every wiki page with a one-line summary. Read first on any query.
- `log.md` — append-only chronological record of every ingest, query, and lint pass.

## Wiki page types

- `wiki/entities/people/<slug>.md` — one page per person.
- `wiki/entities/places/<slug>.md` — one page per location.
- `wiki/concepts/<slug>.md` — one page per recurring idea, theme, framework.
- `wiki/sources/<slug>.md` — one page per ingested raw source (your summary + key quotes).
- `wiki/synthesis/<topic>.md` — cross-source synthesis pages.
- `wiki/overview.md` — top-level orientation. Always keep current.

Slugs are kebab-case. Paths are stable; if you must rename, fix every backlink in the same pass.

## Page format

Every wiki page starts with frontmatter:

```yaml
---
title: <human-readable title>
type: entity | concept | source | synthesis | overview
last_updated: <YYYY-MM-DD>
sources: [<wikilinks to source pages>]
tags: [<short list>]
---
```

Body uses Obsidian-flavored markdown. Wikilinks: `[[wiki/concepts/foo]]`. Always link entities and concepts on first mention.

## Operations

### Ingest

Adithya drops a file in `raw/` (or you fetch one with his approval). You:

1. Read the source.
2. Discuss takeaways with Adithya in chat. Surface anything surprising, contradicting prior pages, or worth a follow-up.
3. Write `wiki/sources/<slug>.md` with a tight summary, key quotes, and a citation back to the raw file.
4. Update or create the entity, concept, and synthesis pages it touches. A single source typically touches 5–15 pages.
5. Update `index.md`.
6. Append a log entry.

If a new claim contradicts an existing page, do not silently overwrite. Note both, flag the conflict in the page, and surface it to Adithya.

### Query

Adithya asks a question.

1. Read `index.md` to find candidate pages.
2. Read the candidates.
3. Answer with citations to wiki pages (and through them, to raw sources).
4. If the answer is a novel synthesis worth keeping, file it as `wiki/synthesis/<topic>.md` and append a log entry. Don't file trivial Q&A.

### Lint

On request, run a health check:

- Contradictions across pages.
- Stale claims newer sources have superseded.
- Orphan pages with no inbound links.
- Concepts mentioned but lacking their own page.
- Cross-references missing on either side.
- Suggested follow-up questions or sources Adithya might want.

Write findings to `wiki/synthesis/lint-<YYYY-MM-DD>.md`. Append a log entry. Lint never deletes.

## Index conventions

`index.md` lists every wiki page, grouped by type. Each line:

`- [[<path>]] — <one-line summary>`

Update on every page create or substantive edit. Don't let it drift.

## Log conventions

Append-only. Every entry starts:

`## [<YYYY-MM-DD>] <ingest|query|lint|note> | <short title>`

Body: 1–3 lines. What you did, what changed. The header format is greppable: `grep "^## \[" log.md | tail -10`.

## Style

Plain prose. No hedging. Quote source language where framing matters; paraphrase where it does not. No corporate-speak. Write analysis pages in second person to Adithya where natural.

## Out of scope

This is a single-user, file-only system. No CLI, no scheduler, no embeddings, no automation. If a tool ever helps (search, dataview, plugin), add it then; do not pre-build.
