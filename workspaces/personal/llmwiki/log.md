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
- Slug discrepancy flagged: `dad` and `dad-9967` appear in the same family. Same person, two contact entries.
- 762 individuals + 270 groups remain unprocessed. Pace next batches at 20–40 entities per turn.

## [2026-05-09] ingest | iMessage batch 2 (44 individuals + 20 groups)

Took the next slice of top-volume contacts: 44 individuals (Avery Abraham, Mychal Kendricks, Aurat, Saif Ali, Pseuhas, Austin Davis, Binni, Aaliyah, Edwin, Keith, Zach, Sandeep Chinchali, Sydney Huang, Dr Luke, etc.) plus 20 groups (the Berkeley core groups, Klein Ct roommate variants, music-industry groups, Amsterdam, intervention-4-shakti, plus 8 thinner groups consolidated into one misc-small-groups page).

Wrote 43 new individual entity pages, 1 self-thread page (adithya-self), 9 group pages (3 large + 1 misc consolidating 8 small ones), 5 new concept pages (dvro-2026-02-03, adithya-business-portfolio, klein-ct-property, austin-drug-circle, eclipse-labs). Updated relationships-2026-05 synthesis with the new active and Hinge threads. Rewrote index from scratch grouped by category.

Notable items surfaced this batch (worth your attention):
- A Domestic Violence Restraining Order was filed against Adithya in Feb–Mar 2026. Petitioner not named in the visible data. See [[wiki/concepts/dvro-2026-02-03]].
- Multiple concurrent romantic threads in May 2026 (Sanvi, Binni, Rishika), with Aurat in the recent past. See [[wiki/synthesis/relationships-2026-05]].
- a16z Speedrun rejection landed May 4, 2026. Mychal Kendricks delivered the most useful reframing.
- Austin Davis lawsuit (Klein Ct, five months unpaid rent, Notice of Intent to Sue Nov 2025).
- SeedBox cofounder relationship with Avery Abraham; $25k equity; YC track.
- Bufords (Austin bar) shooting referenced — Adithya was on premises late February / early March 2026.
- Second car accident in February 2026.
- An "Asian unc" VC scam attempt at a SF conference bar in April 2026.

Next batches should: pull top-volume by remaining slugs, prioritize family group members surfacing in `gold-kums-powna-ams-family`, ingest non-iMessage sources (granola transcripts have meaningful signal per file ratio), and resolve the saif vs pseuhas slug overlap.
