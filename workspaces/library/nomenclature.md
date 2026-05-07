# Library Nomenclature

File-system conventions and the routing manual for this workspace. The wiki agent and lint agent both read this to know where things go.

## File-system conventions

### Raw

| Source type | Path |
|---|---|
| Book | `raw/books/<author-slug>/<title-slug>/{book.epub, book.md, metadata.md}` |
| Book-specific YouTube video | `raw/books/<author-slug>/<title-slug>/related-videos/<video-slug>/{transcript.md, metadata.md}` |
| Standalone YouTube video | `raw/youtube/<channel-slug>/<YYYY-MM>/<video-slug>/{transcript.md, metadata.md}` |
| YouTube channel metadata | `raw/youtube/<channel-slug>/_meta.md` |
| Instagram reel | `raw/reels/<creator-slug>/<YYYY-MM>/<reel-slug>.md` |
| Paper (arxiv / doi) | `raw/papers/<first-author>-<short-title>-<year>/{paper.pdf, paper.md, metadata.md}` |
| Article | `raw/articles/<YYYY-MM>/<source-slug>-<title-slug>.md` |
| Manual deposit | `raw/manual/_inbox/` (processed at lint, moved to dated subdir) |

### Wiki

| Page type | Path |
|---|---|
| Book entity | `wiki/entities/books/<slug>.md` |
| YouTube video entity | `wiki/entities/youtube-videos/<slug>.md` |
| YouTube channel entity | `wiki/entities/youtube-channels/<slug>.md` |
| Reel entity | `wiki/entities/reels/<slug>.md` |
| Paper entity | `wiki/entities/papers/<slug>.md` |
| Article entity | `wiki/entities/articles/<slug>.md` |
| Person entity | `wiki/entities/people/<slug>.md` |
| Concept | `wiki/concepts/<slug>.md` |
| Synthesis | `wiki/synthesis/<slug>.md` |

### Meta

- `_meta/lint-<YYYY-MM-DD>.md` per lint run
- `_meta/log.md` append-only event log
- `_meta/learning-proposals.md` proposed updates to `learnings.md`
- `_meta/schema-proposals.md` proposed updates to `schema.md`
- `_meta/backfill-log.md` entities encountered without sufficient raw history

## Routing table — by query type

| Query type | Read first | Then |
|---|---|---|
| "Who is X?" | `wiki/entities/people/<x>.md` | `[[@x]]` if global stub exists |
| "What did X argue / say about Y?" | `wiki/entities/<book\|paper\|article\|youtube-video>/<slug>.md` | Source file in `raw/` for verbatim |
| "What does the corpus say about Z?" | `wiki/concepts/<z>.md` | Each source's wiki entity page from the concept's `sources:` list |
| "Synthesize across sources on topic T" | `wiki/synthesis/<t>.md` | If absent, scan concepts + entity backlinks |
| "What's next to learn?" | Run `bin/library-next.py` | (Curator output is the answer) |
| "What have I read?" | Filter `wiki/entities/*` by `read_status: delivered` | Group by source type |
| "What's queued?" | Filter `wiki/entities/*` by `read_status: queued` | Sort by `last_touched` desc |

## When the wiki agent creates a new page

1. Determine the entity type from `schema.md`.
2. Compute slug per the conventions above.
3. Use the per-type page format from `schema.md`.
4. File path: `wiki/entities/<type>/<slug>.md`.
5. After creation, check whether `_global/entities/<type>/<slug>.md` exists. If yes, ensure the global stub's `## Backlinks` section will pick it up on the next `build-backlinks.py` run. If no, propose adding to global in `_meta/learning-proposals.md` only when cross-workspace relevance is plausible.

## When the wiki agent updates an existing page

1. Compute content hash of proposed content.
2. Compare to current `last_touched` content hash.
3. If meaningfully different, write. If not, skip and log.
4. Update `last_touched` to today.

## When source naming conflicts

If two raw items collide on slug, append `-2`, `-3`, etc. Lint agent flags collisions weekly.

## Slug generation

- **Books**: `<first-author-last-name>-<title-truncated-3-words>`. Truncate at 3 meaningful words. Example: "The 7 Habits of Highly Effective People" by Stephen Covey → `covey-seven-habits`. Numbers spelled out when leading.
- **YouTube videos**: `<channel-handle>-<title-truncated-4-words>`. Drop emoji and punctuation. Example: "Andrew Huberman: Optimize Your Sleep" → `andrewhuberman-optimize-your-sleep`.
- **Papers**: `<first-author-last>-<title-truncated-3-words>-<year>`. Example: Vaswani et al "Attention Is All You Need" 2017 → `vaswani-attention-is-all-2017`.
- **Reels**: `<creator-handle>-<YYYY-MM-DD>-<5-char-id>`. Multiple reels per day from one creator collide otherwise.
- **Articles**: `<source-domain>-<title-truncated-4-words>`. Example: paulgraham.com "Do Things That Don't Scale" → `paulgraham-do-things-that-dont`.

All slugs are kebab-case ASCII. Truncate at 60 characters. If truncation creates collision, append numeric suffix.
