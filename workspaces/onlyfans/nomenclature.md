# OnlyFans Nomenclature

This file documents file-system conventions and the routing manual for this workspace. The wiki agent and lint agent both read this to know where things go.

## File-system conventions

- All raw archive files: `raw/<source>/<YYYY-MM>/<thread-slug>.md`
- Thread slug format: `<participant-slug>-<YYYY-MM-DD>` (or `<topic-slug>-<YYYY-MM-DD>` for multi-party).
- Wiki entity pages: `wiki/entities/<type>/<slug>.md` (type matches `schema.md` types).
- Wiki concept pages: `wiki/concepts/<concept-slug>.md`.
- Wiki synthesis pages: `wiki/synthesis/<topic-slug>.md`.
- `_meta/lint-<YYYY-MM-DD>.md` per lint run.

## Routing table — by query type

<populated at bootstrap from Q3 + Q6>

| Query type | Read first |
|---|---|
| "Who is X?" | `wiki/entities/people/<x>.md`, then `[[@x]]` |

## When the wiki agent creates a new page

1. Determine the entity type from `schema.md`.
2. Use the page format from `schema.md`.
3. File path: `wiki/entities/<type>/<slug>.md`.
4. After creation, check whether `_global/entities/<type>/<slug>.md` exists. If yes, ensure the global stub's `## Backlinks` section will pick it up on the next `build-backlinks.py` run. If no, propose adding the entity to global in `_meta/learning-proposals.md` (audit-agent will recommend promotion).

## When the wiki agent updates an existing page

1. Compute content hash of proposed content.
2. Compare to current `last_updated` content hash.
3. If meaningfully different, write. If not, skip and log.
4. Update `last_touched` frontmatter to today.

## When source naming conflicts

If two raw threads collide on slug, append `-2`, `-3`, etc. Lint agent flags collisions weekly.
