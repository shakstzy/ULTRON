# Log

Append-only chronological record. Header format: `## [YYYY-MM-DD] <op> | <title>`.

## [2026-05-09] init | wiki initialized

Created folder structure, schema (CLAUDE.md), index, log, and overview placeholder. No sources ingested yet. Adithya drops files in `raw/` to begin.

## [2026-05-09] ingest | iMessage pilot batch (20 entities)

Pilot run against `workspaces/personal/raw/imessage/` (3,967 monthly shards across 782 individuals and 273 groups). Selected 17 individuals and 3 groups across cohorts (family, UC Berkeley, romantic, renters, music, one Hinge sample) by source-volume + cohort variety.

For each entity, read the most recent monthly shard (capped at 200 lines after frontmatter) and synthesized one entity page citing all known shards. Wrote 20 entity pages, 5 concept pages (family-tension, breakup-aarti-2026-02, uc-berkeley-cohort, austin-rental-tenants, music-collaborators-2026), and 1 synthesis page (relationships-2026-05). Updated index and overview.

Approach decisions logged for next batches:
- Entity-per-person, NOT source-page-per-shard. Source citations live in entity-page frontmatter.
- Slug discrepancy flagged: `sanvi-sister` reads as a romantic interest, not a sibling. Renamed in wiki to `sanvi`.
- Slug discrepancy flagged: `dad` and `dad-9967` appear in the same family. Same person or two handles is open.
- 762 individuals + 270 groups remain unprocessed. Pace next batches at 20–40 entities per turn.
