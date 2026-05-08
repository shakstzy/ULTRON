# Library Nomenclature

File-system conventions and the routing manual for this workspace. The wiki agent and lint agent both read this to know where things go.

## File-system conventions

### Raw (capture, written by `bin/ingest-*.py`)

One markdown file per item, with the universal envelope per `_shell/stages/ingest/CONTEXT.md` plus per-source fields. Body holds the actual content (transcript, extracted markdown, etc.).

| Source type | Path |
|---|---|
| Book | `raw/books/<author-slug>/<slug>.md` (alongside `<slug>.epub` or `<slug>.pdf`, gitignored) |
| Paper | `raw/papers/<slug>.md` (alongside `<slug>.pdf`, gitignored) |
| YouTube video | `raw/youtube/<channel-slug>/<YYYY-MM>/<slug>.md` |
| Instagram reel | `raw/reels/<creator-slug>/<YYYY-MM>/<slug>.md` |
| Article | `raw/articles/<YYYY-MM>/<slug>.md` |
| Manual deposit | `raw/manual/_inbox/` (processed at lint, moved to dated subdir) |

### Wiki (synthesis, built downstream by `/graphify --wiki` or future wiki-agent lint stage)

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
- `_meta/ingested.jsonl` structured ingest log (one line per item)

## Universal envelope

Every raw file carries these fields:

```yaml
source: <source-name>            # book, paper, youtube, instagram-reel, article, manual
workspace: library
ingested_at: <ISO 8601 UTC>      # when ULTRON ingested it
ingest_version: 1                # bump when this format changes
content_hash: blake3:<hex>       # change-detection key
provider_modified_at: <ISO 8601> # source's published/last-modified, or null
```

Per-source fields layer on top — see each script's source code for the specifics (slug, title, url, channel, video_id, etc.).

## Routing table — by query type

| Query type | Read first | Then |
|---|---|---|
| "Who is X?" | `wiki/entities/people/<x>.md` (built downstream) | `[[@x]]` if global stub exists |
| "What did X argue / say about Y?" | `wiki/entities/<book\|paper\|article\|youtube-video>/<slug>.md` | Source file in `raw/` for verbatim |
| "What does the corpus say about Z?" | `wiki/concepts/<z>.md` | Each source's wiki entity page |
| "Synthesize across sources on topic T" | `wiki/synthesis/<t>.md` | Concepts + entity backlinks |
| "What's next to learn?" | Run `bin/library-next.py` | (Curator output is the answer) |
| "What have I read?" | Filter `wiki/entities/*` by `read_status: delivered` | Group by source type |
| "What's queued?" | Filter `wiki/entities/*` by `read_status: queued` | Sort by `last_touched` desc |

## Slug generation

- **Books**: `<first-author-last>-<title-3-words>`. Example: "Atomic Habits" by James Clear → `clear-atomic-habits`.
- **YouTube videos**: `<channel-handle>-<title-4-words>-<video-id-5-chars>`. The 5-char suffix prevents collisions on channels with reused titles.
- **Papers**: `<first-author-last>-<title-3-words>-<year>`.
- **Reels**: `<creator-handle>-<YYYY-MM-DD>-<5char>`.
- **Articles**: `<source-domain-stem>-<title-4-words>`.

All slugs are kebab-case ASCII. Truncate at 60 characters. Numeric suffix appended on collision.

## When source naming conflicts

If two raw items collide on slug, append `-2`, `-3`, etc. Lint agent flags collisions weekly.

## When the wiki layer is empty

`bin/library-next.py` will report "wiki not built — run /graphify --wiki workspaces/library" and exit. Run graphify, then re-run the curator.
