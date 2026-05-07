# Library Style

## Capitalization

- **Source titles in body text and frontmatter `title` field**: Title Case as published (e.g. "The Power Broker", "Attention Is All You Need").
- **Slugs**: lowercase kebab-case ASCII. `clear-atomic-habits`, `huberman-sleep-protocol`, `attention-is-all-you-need-2017`.
- **Concept slugs**: noun phrases, lowercase kebab. `network-effects`, `availability-heuristic`, `compound-interest`.
- **Channel slugs**: handle without `@`, lowercase kebab. `andrewhubermanlab`, `lexfridman`, `huberman-lab` if compound.
- **Author / speaker slugs**: `<first>-<last>`, lowercase. Disambiguate on collision with a domain hint (`james-clear`, `sarah-clear-physiologist`).

## Numbers

- Durations in minutes as integers: `duration_minutes: 47`. Hours format: `2h 14m` in body text only, never in frontmatter.
- Year fields are 4-digit integers: `year: 2018`. Not strings.
- Page numbers and timestamps cited inline with the quote: `(p. 142)`, `(@12:34)`.
- View counts and follower counts not stored. They drift, they lie, they do not change the takeaway.
- Page-length soft caps: book / paper / channel pages ≤ 200 lines. Synthesis pages ≤ 300 lines. Concept pages ≤ 250 lines.

## Frontmatter

- All wiki pages have YAML frontmatter as defined per type in `schema.md`.
- Required fields per type are enforced by the lint agent. Missing required fields are flagged for fix, not auto-deleted.
- `last_touched` is updated by the wiki agent on every meaningful update (computed from content hash diff, not file mtime).
- `read_status` and `delivered_at` are owned by the curator (`library-next`). The wiki agent sets `read_status: ingested` on creation; the curator transitions it forward.
- Lists in frontmatter are YAML lists, never inline arrays: `authors:` on one line, `  - james-clear` on the next.

## Tables

- Used sparingly. Only when comparing 3+ items across the same axes. Never as decoration.
- Max 6 columns. If you need more, switch to bullets nested under each item.
- Header row in Title Case. Body cells in sentence case.

## Body sections

Per-type body sections defined in `schema.md`. The order is fixed:

1. `## TL;DR` — 1-3 sentences. Always first.
2. `## Key takeaways` — 3-7 bullets. The actual content of the bite.
3. `## Quote` — single quote, ≤ 15 words, attributed.
4. `## Why it matters` — 1-2 sentences tying the source to something Adithya already cares about.
5. `## Connections` — wikilinks to related books / videos / papers / concepts.
6. `## Backlinks` — auto-built by `_shell/bin/build-backlinks.py`.

If a section has nothing to say, the section header is omitted entirely. Empty sections are noise.
