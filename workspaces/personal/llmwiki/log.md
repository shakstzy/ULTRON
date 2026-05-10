# Log

Append-only chronological record. Header format: `## [YYYY-MM-DD] <op> | <title>`.

## [2026-05-09] init | wiki initialized

Created folder structure, schema (CLAUDE.md), index, log, and overview placeholder. No sources ingested yet. Adithya drops files in `raw/` to begin.

## [2026-05-09] ingest | iMessage pilot batch (20 entities)

Pilot run against `workspaces/personal/raw/imessage/` (3,967 monthly shards across 782 individuals and 273 groups). Selected 17 individuals and 3 groups across cohorts (family, UC Berkeley, romantic, renters, music, one Hinge sample) by source-volume + cohort variety.

For each entity, read the most recent monthly shard (capped at 200 lines after frontmatter) and synthesized one entity page citing all known shards. Wrote 20 entity pages, 5 concept pages, and 1 synthesis page.

## [2026-05-09] ingest | iMessage batch 2 (44 individuals + 20 groups)

Took the next slice of top-volume contacts. Wrote 43 new individual entity pages, 1 self-thread page, 9 group pages (3 large + 1 misc consolidating 8), 5 new concept pages, updated relationships-2026-05 synthesis.

Notable: Domestic Violence Restraining Order filed against Adithya Feb–Mar 2026 (petitioner not named in visible data); a16z Speedrun rejection May 4; Austin Davis lawsuit; SeedBox $25k equity; Bufords Austin shooting February 2026.

## [2026-05-09] ingest | iMessage batch 3 (28 individuals)

Tier 46–90 of remaining individuals by volume. Wrote 11 substantive new pages (Larry the lawyer, Jaeden / Selfpause podcast deal, David Bloom at The House Fund, Jeff at Sei + Forge accelerator pitch, Will Avery / gmtrade.xyz, Wes Cyphers AI voice work, Noah-renter Klein Ct rent collection era, Filip LA party friend, Lorenzo airport-driver, Jim Edmunds AI vox repo, Sai Om uncle at Antimetal). Surfaced **Forge** Berkeley accelerator project and **Outerscope** as Adithya's company name.

## [2026-05-09] ingest | iMessage swarm — batch 4 (parallel: ~970 entities, 7 workers)

Architectural shift. Per Adithya request, parallelized via Ruflo install + map-reduce pattern. 7 background subagents launched in one message, each handling a non-overlapping cohort. Wall time start-to-last-completion: ~24 minutes.

Worker breakdown:
- W1 Berkeley (Sonnet, 95): 10 tier-1, 35 tier-2, 41 tier-3 skipped, 9 already existed.
- W2 Renter+Crypto (Sonnet, 71): 4 tier-1, 17 tier-2, 35 tier-3, 14 already existed.
- W3 LA/Music (Sonnet, 168): 8 tier-1, 133 tier-2, 20 tier-3, 7 already existed. **Quality concern**: tier-1/tier-2 ratio looks generous; spot-check needed.
- W4 Misc-A (Sonnet, 135 A–L): 36 tier-1, 58 tier-2, 24 tier-3, 17 already existed.
- W5 Misc-B (Sonnet, 134 M–Z): 4 tier-1, 30 tier-2, 85 tier-3, 5 already existed. Conservative classifier.
- W6 Hinge (Haiku, 179): 175 pages produced template-fill garbage. **Deleted all 175 and re-spawned with Sonnet (W6-REDO) in flight.**
- W7 Groups (Sonnet, 273): 24 tier-1, 89 tier-2, 135 tier-3 (consolidated into `misc-small-groups-2.md`), 25 already existed. **426 facts.**

Total facts written across W1–W7: 1,415 (`/tmp/imw/facts_w*.jsonl`, merged to `/tmp/imw/all_facts.jsonl`).

Page count after batch 4 (and before W6-REDO completes): 509 people + 118 groups = 627.

Notable findings surfaced this batch (worth your attention):
- **dimpal-aarti** (Feb 2026): hostile thread accusing Adithya of harassment over pursuing someone. Possible angle on the [[wiki/concepts/dvro-2026-02-03]] thread.
- **trevor**: confirmed production credit on Iann Dior's "Gucci Bag." Real chart placement.
- **ankur-uncle**: Emergent Ventures (Tyler Cowen). Mom intro. Jan 2026 video call. Professional-family crossover.
- **jaeden / Selfpause**: 150K-user meditation app, 455 hours of audio under licensing discussion at $25/hr ($11,375 if it clears).
- **Forge**: Berkeley student accelerator project Adithya is building. Real pitch deck, sponsor tiers, V2 plan red-teamed. Pitched to Jeff at Sei.
- **Outerscope**: Adithya's company name. First explicit reference.
- **group-amadeus-angel-dad**: tenants delivered formal rent-withholding notice for habitability violations. Mirror of [[wiki/entities/people/austin-davis]] but other side.
- **group-abraham-pseuhas-xanos**: ketamine sourcing intro via Signal at $1000/oz.
- **mychal-kendricks**: described in pitch context as "ex-SpaceX/PayPal/Seedbox advisor" — flag, not corroborated elsewhere in corpus.
- **W3 surfaced**: jt-huskins-crypto stayed engaged through his own father's stage-4 cancer diagnosis; jean-parker sent his Dropbox loop archive for a Laroi/Beazy session; rhea positioned Caitlin as Adithya's primary A&R.
- **W5 surfaced**: vina-nyc actually met IRL at Tompkins Square; riya-nyc's 43-msg post-breakup thread; preethi-launchx says Adithya stood her up.

## [2026-05-09] ingest | W6-REDO Hinge cohort (Sonnet)

Re-ran the 175 Hinge slugs through Sonnet (the Haiku-driven W6 had generated template-fill pages). Wall time ~19 minutes. Final tier distribution: 17 TIER 1, 77 TIER 2, 81 TIER 3 (skipped). Total Hinge cohort coverage: 5 pre-existing + 17 + 77 = ~99 pages, plus 81 entries surfaced as TIER 3 in the worker output.

New high-signal threads surfaced this redo:
- **emmy-hinge-sd**: only confirmed in-person hookup in the Hinge cohort (April 2026, SF Airbnb).
- **sreya-hinge-austin**: emotionally raw thread tied to the **March 1, 2026 6th Street shooting at Bufords**. Both Adithya and Sreya knew the victim **Savitha** independently (high-school connection on his side). New concept page `sixth-street-shooting-2026-03-01.md` created.
- **trisha-hinge-alabama**: most romantically open exchange. Tamil family imagined-future content.
- **anjali-hinge-austin**: Tamil-language texting; persistent on her side, missed windows on his.
- **gayathri-hinge-dallas**: Adithya showed up at her Dallas place at 3am to apologize for "what I had done last summer." Pattern echo of the DVRO "rocks at the window" admission.
- **sriya-hinge-austin**, **presley-hinge-austin**: confirmed prior physical contact; could be relevant to the DVRO petitioner question.
- **sabrina-hinge-austin**: explicit named-pattern callout — "this is the 5th time you asking me to hang out really late and it just doesnt seem respectful."

## [2026-05-09] synthesis | post-swarm pass

Updated:
- `overview.md` (full rewrite covering career / family / romantic / property / friends / timeline).
- `index.md` (cohort-organized navigation hub instead of flat 800-page list).
- `wiki/synthesis/relationships-2026-05.md` (expanded with W6-REDO findings, DVRO petitioner candidate revisit).
- `wiki/concepts/dvro-2026-02-03.md` (added Dimpal-Aarti angle).
- `wiki/concepts/adithya-business-portfolio.md` (full rewrite; Outerscope, Forge, Selfpause/Jaeden, Ankur-uncle, network mentors).
- `wiki/concepts/music-collaborators-2026.md` (full rewrite; Iann Dior credit, Prescription / Rhea / Caitlin, ~12 active producer pipelines).
- `wiki/concepts/austin-rental-tenants.md` (added habitability complaints, Sidhant near-sign, prospect pipeline).
- `wiki/concepts/austin-drug-circle.md` (extended with new substances/sources; ketamine, psilocybin trip groups, alcohol).
- `wiki/concepts/klein-ct-property.md` (extended timeline, prior tenant cohort, LA property, habitability complaint).
- New: `wiki/concepts/sixth-street-shooting-2026-03-01.md`.

Lint cleanup: deleted empty `austin-davis-renter-showing.md` duplicate; deleted `noah-bailie-2.md` duplicate (folded into noah-bailie). Fixed broken wikilinks: austin-davis-renter-showing → austin-davis (auto-replaced across all pages); johnny-lee placeholder applied (no source page yet).

Final page counts: ~770 people pages + 118 group pages = **~888 total entity pages**, up from 86 at the start of today's session.

Outstanding: full Quality Review pass with finer dedup (some Hinge-city same-name slugs may be the same person across moves — e.g., possible Aaliyah variants); ingest of non-iMessage sources (gmail, granola, whatsapp, discord, reddit, manual).
