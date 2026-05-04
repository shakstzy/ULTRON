# Seedbox Nomenclature

File-system conventions and routing manual for the seedbox workspace.

## File-system conventions

- Gmail raw: `raw/gmail/adithya-outerscope/<YYYY>/<MM>/<YYYY-MM-DD>__<subject-slug>__<threadid8>.md` (locked by ingest pipeline; see `_shell/stages/ingest/gmail/format.md`).
- Wiki entity pages: `wiki/entities/<type>/<slug>.md` (type matches `schema.md` types).
- Wiki synthesis pages: `wiki/synthesis/<topic-slug>.md`.
- `_meta/lint-<YYYY-MM-DD>.md` per lint run.

## Slug rules

- People: `<first>-<last>` lowercase kebab. Disambiguate with `<first>-<context>` for collisions.
- Topics: short canonical name (`advisor-admin`, `ideas-exchange`, `prototyping-2026`).

## Routing table — by query type

| Query type | Read first |
|---|---|
| "Who is X (Seedbox team or external contact)?" | `wiki/entities/people/<x>.md`, then `[[@x]]` for global |
| "What's the latest from Seedbox?" | `raw/gmail/adithya-outerscope/<latest-month>/...` |
| "Status of advisor agreement / 83(b)?" | `wiki/synthesis/advisor-admin.md` |
| "Ideas / prototyping threads?" | `wiki/synthesis/ideas-exchange.md` |

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

If two raw threads collide on slug, the ingest pipeline disambiguates via the 8-char thread-id suffix. Wiki entity collisions: append `-2`, `-3`. Lint agent flags collisions weekly.
