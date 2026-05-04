# Synapse Nomenclature

File-system conventions and routing manual for the synapse workspace. The wiki agent and lint agent both read this to know where things go.

## File-system conventions

- Gmail raw: `raw/gmail/adithya-synps/<YYYY>/<MM>/<YYYY-MM-DD>__<subject-slug>__<threadid8>.md` (locked by ingest pipeline; see `_shell/stages/ingest/gmail/format.md`).
- Manual notes: `raw/manual/<YYYY-MM-DD>/<note-slug>.md` (after ingest moves them out of `_inbox/`).
- Wiki entity pages: `wiki/entities/<type>/<slug>.md` (type matches `schema.md` types).
- Wiki concept pages: `wiki/concepts/<concept-slug>.md`.
- Wiki synthesis pages: `wiki/synthesis/<topic-slug>.md`.
- `_meta/lint-<YYYY-MM-DD>.md` per lint run.

## Slug rules

- People: `<first>-<last>` lowercase kebab. Disambiguate with `<first>-<context>` for collisions (`arjun-veera` vs `arjun-synapse`).
- Companies: short canonical name lowercase (`alliance`, `hf0`, `ycombinator`, `companyon`, `redbeard`, `denarii-labs`).
- Programs: short canonical name (`y-combinator`, `alliance`, `hf0`, `nvidia-inception`, `aws-activate`, `orange-fellowship`, `gcs-synapse`).
- Deals: `<kind>-<descriptor>-<YYYY>` (e.g., `fundraise-pre-seed-2026`, `bd-checkbook-2025`).

## Routing table — by query type

| Query type | Read first |
|---|---|
| "Who is X (investor / partner)?" | `wiki/entities/people/<x>.md`, then `[[@x]]` for global |
| "Status of program Y?" | `wiki/entities/programs/<y>.md` |
| "What VC firm Z?" | `wiki/entities/companies/<z>.md` |
| "Where's the fundraise pipeline?" | `wiki/synthesis/fundraise.md` |
| "Recent comms with someone?" | `raw/gmail/adithya-synps/<latest-month>/...` |

## When the wiki agent creates a new page

1. Determine the entity type from `schema.md`.
2. Use the page format from `schema.md`.
3. File path: `wiki/entities/<type>/<slug>.md`.
4. After creation, check whether `_global/entities/<type>/<slug>.md` exists. If yes, ensure the global stub's `## Backlinks` section picks it up on the next `build-backlinks.py` run. If no, propose adding the entity to global in `_meta/learning-proposals.md`.

## When the wiki agent updates an existing page

1. Compute content hash of proposed content.
2. Compare to current `last_updated` content hash.
3. If meaningfully different, write. If not, skip and log.
4. Update `last_touched` frontmatter to today.

## When source naming conflicts

If two raw threads collide on slug, the ingest pipeline already disambiguates via the 8-char thread-id suffix. Wiki entity collisions: append `-2`, `-3`, etc. Lint agent flags collisions weekly.
