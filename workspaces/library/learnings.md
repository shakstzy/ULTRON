# Library Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines. Updated only by accepting entries from `_meta/learning-proposals.md`.

## Voice and tone

See `identity.md`. One-line summary: internalized + scannable, one short author quote per page, never academic.

## Architecture (load-bearing)

- **Ingest is capture-only.** `bin/ingest-*.py` scripts download content and write `raw/<source>/<path>.md` with the universal envelope. They do NOT call cloud-llm. They do NOT write to `wiki/`. This is per `_shell/stages/ingest/CONTEXT.md`.
- **Wiki built downstream.** `/graphify --wiki workspaces/library` (or a future `_shell/stages/lint/library-wiki/` stage) reads `raw/` and produces `wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/`.
- **Curator reads wiki.** `bin/library-next.py` scans `wiki/entities/*` for pages with `read_status` frontmatter, scores them, returns one bite. When `wiki/` is empty, it tells the user to run `/graphify --wiki` first.

## Operational rules

- **Pull-based consumption.** Adithya asks "what's next," `library-next` returns one bite. No pushed digests. No scheduled notifications.
- **Skip YouTube Shorts by default.** When ingesting a channel or playlist, filter out videos < 60 seconds. If Adithya pastes a Shorts URL directly, ingest it.
- **Channel ingest semantics.** "Ingest everything" = full backfill of the channel's `/videos` tab (Shorts excluded). "Only X" or `--videos id1,id2` = selective. No subscribe-forward by default.
- **Co-location is a wiki concern, not a capture concern.** All YouTube videos land at `raw/youtube/<channel>/<YYYY-MM>/<slug>.md` regardless of book relevance. Whether a video is "primarily about" a book in the corpus is decided by the wiki agent at synthesis time, not at ingest.
- **Book validation chain (Anna's Archive).** Title fuzzy match ≥ 0.85, author fuzzy match ≥ 0.7, language=en, format=epub preferred. On failure, stop and surface the metadata so Adithya can re-run with a specific MD5 URL.
- **Copyright posture.** Full EPUB and PDF stay in `raw/` (gitignored). Wiki pages will contain takeaways + one ≤ 15 word quote per page. Per ULTRON global copyright rules.
- **Concept promotion threshold.** Wiki agent (downstream) promotes a concept when it appears in 3+ source wiki pages.
- **Synthesis trigger.** Wiki agent proposes a `wiki/synthesis/<topic>.md` when 5+ sources cluster on the same topic. Lint agent surfaces; Adithya green-lights.
- **Entity reuse.** Authors / channel hosts in 1 source stay workspace-local. Promotion to `_global/entities/people/` via `promote-entity` skill when the person crosses workspaces.
- **No deletes.** The wiki agent never deletes a wiki page. Stale pages get `status: archived`.
- **Lint never modifies content.** Lint reports invariant violations. Schema and learning changes propose into `_meta/schema-proposals.md` and `_meta/learning-proposals.md`.

## Curator behavior (`library-next`)

The curator picks one bite per call. Ranking:

1. **Read status priority** (highest first): `queued` > `ingested` (not yet delivered) > `delivered` (older than 30 days, can re-surface for spaced recall).
2. **Variety**: avoid same source type twice in a row (track via `delivered_at` on the most recent delivery).
3. **Recency bonus**: ingested in the last 7 days gets a small score bump.
4. **Size match**: when Adithya specifies a time budget, prefer entities with `bite_size_minutes` in range. Default budget = 5 minutes.

When `wiki/entities/` is empty (no graphify run yet), the curator tells the user to run `/graphify --wiki workspaces/library` and exits.

## Past patterns

(empty — populated as the wiki agent learns from history)

## Mental models

(empty — populated as patterns emerge)
