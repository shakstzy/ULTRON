# Library Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines. Updated only by accepting entries from `_meta/learning-proposals.md`.

## Voice and tone

See `identity.md`. One-line summary: internalized + scannable, one short author quote per page, never academic.

## Operational rules

- **Pull-based consumption.** Adithya asks "what's next," `library-next` returns one bite. No pushed digests. No scheduled notifications. The wiki is the substrate, the curator is the product.
- **Skip YouTube Shorts by default.** When ingesting a channel or playlist, filter out videos < 60 seconds. If Adithya pastes a Shorts URL directly, ingest it.
- **Channel ingest semantics.** "Ingest everything" = full backfill of the channel's `/videos` tab (excluding Shorts). "Only X" or a specific video URL = selective. No subscribe-forward by default. When Adithya wants new uploads, he re-pings.
- **Hybrid co-location for book-specific videos.** When a YouTube video is primarily about a single book already in the corpus, file under `raw/books/<author>/<title>/related-videos/<video-slug>/`. Otherwise file under `raw/youtube/<channel>/<YYYY-MM>/<video-slug>/`. Wiki page links both ways regardless. Resolution happens at ingest time via an LLM check on title + description + transcript opener.
- **Book validation chain (Anna's Archive).** Title fuzzy match ≥ 0.85, author fuzzy match ≥ 0.7, language=en, format=epub preferred (pdf fallback). After download, sanity check: file opens, has chapters, total length within plausible range for a book. On any validation failure, stop and surface top-3 candidates.
- **Copyright posture.** Full EPUB and PDF stay in `raw/` (gitignored). Wiki pages contain takeaways + one ≤ 15 word quote per page. Never reproduce paragraphs. Per ULTRON global copyright rules.
- **Concept promotion threshold.** When a concept appears in 3+ source wiki pages, the wiki agent promotes it to `wiki/concepts/<concept-slug>.md`. Concept pages reference the sources where it appeared.
- **Synthesis trigger.** When 5+ sources cluster on the same topic, the wiki agent proposes a `wiki/synthesis/<topic-slug>.md`. Lint agent surfaces the proposal weekly; Adithya green-lights manually.
- **Entity reuse.** Authors and channel hosts living in 1 source stay workspace-local. When the same person appears in 2+ workspaces (e.g. someone Adithya knows personally is also a paper author), promote to `_global/entities/people/` via the `promote-entity` skill.
- **No deletes.** The wiki agent never deletes a wiki page. Stale pages get `status: archived` in frontmatter.
- **Lint never modifies content.** Lint reports invariant violations. Schema and learning changes propose into `_meta/schema-proposals.md` and `_meta/learning-proposals.md`.

## Curator behavior (`library-next`)

The curator picks one bite per call. Ranking:

1. **Read status priority** (highest first): `queued` > `ingested` (not yet delivered) > `delivered` (older than 30 days, can re-surface for spaced recall).
2. **Variety**: avoid same source type twice in a row (track via `delivered_at` on the most recent delivery).
3. **Recency bonus**: ingested in the last 7 days gets a small score bump (Adithya tends to want fresh stuff).
4. **Size match**: when Adithya specifies a time budget, prefer entities with `bite_size_minutes` in range. Default budget = 5 minutes.

Output shape: TL;DR + 3-5 takeaway bullets + the quote (if present) + a wikilink to the full page. Mark `delivered_at = today` on the picked entity.

## Past patterns

(empty — populated as the wiki agent learns from history)

## Mental models

(empty — populated as patterns emerge)
