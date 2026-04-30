# Personal Nomenclature

File-system conventions and routing manual for workspace `personal`.

## File-system conventions

- Raw archive: `raw/<source>/<YYYY-MM>/<thread-slug>.md`
- Thread slug: `<participant-slug>-<YYYY-MM-DD>` for 1:1; `<topic-slug>-<YYYY-MM-DD>` for group/topic.
- Wiki entity pages: `wiki/entities/<type>/<slug>.md`.
- Wiki concept pages: `wiki/concepts/<concept-slug>.md`.
- Wiki synthesis pages: `wiki/synthesis/<topic-slug>.md`.
- `_meta/lint-<YYYY-MM-DD>.md` per lint run.

## Routing table — by query type

| Query type | Read first |
|---|---|
| "Who is X?" | `wiki/entities/people/<x>.md`, then `[[@x]]` |
| "What's the status of song Y?" | `wiki/entities/songs/<y>.md` |
| "Do I own Z gear?" | `wiki/entities/gear/<z>.md` |
| "What did <person> say last week?" | `raw/imessage/<latest>/...` then `raw/gmail/<latest>/...` |
| "Where did I last see venue V?" | `wiki/entities/venues/<v>.md` |

## When the wiki agent creates a new page

1. Determine the entity type from `schema.md`. Slug per kebab-case.
2. Use the page format from `schema.md`.
3. File path: `wiki/entities/<type>/<slug>.md`.
4. After creation, check `_global/entities/<type>/<slug>.md`. If yes, ensure backlink picks it up. If no, propose adding to global in `_meta/learning-proposals.md`.

## When the wiki agent updates an existing page

1. Compute content hash; compare; write if meaningfully different.
2. Update `last_touched` frontmatter.

## Disambiguation

When multiple people share a first name, use `<first>-<context>` (e.g., `sarah-friend` vs `sarah-bd-contact`). Lint flags ambiguous slugs.
