# Eclipse Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines. Updated only by accepting entries from `_meta/learning-proposals.md`.

## Voice and tone (overrides global)

- Numbers cited verbatim from source. Never round revenue, headcount, or pipeline figures unless explicitly stated as estimates.
- Sydney speaks in concise Slack-style sentences. When summarizing her positions, preserve directness.
- Vendor / partner / competitor language must resolve to schema types — no fuzzy "they."

## Operational rules

- Sensitive deal info (term sheets, pricing, exclusive intel) NEVER summarized in `wiki/`. It stays in `raw/` only. Wiki may note "term sheet exists; see `raw/drive/<...>`" without specifics.
- Quarterly synthesis pages auto-rotate: `q1-2026-*.md`, `q2-2026-*.md`. New quarter triggers a fresh page; previous page becomes append-only reference.

## Past patterns

- We have gotten burned twice by aliasing two contacts at the same prospect company under one entity. Always disambiguate: `<first>-<company-slug>` if there is any ambiguity.
- Mercor and Fluffle relationships have separate concept pages because the operational flow differs. Don't merge.

## Mental models

- "Deal stage" enum is the source of truth for pipeline reporting. Lint agent flags stage transitions that skip a step.
- Audio QA workflow has a vendor (Fluffle), an alignment process, and a delivery cadence. All three live in `wiki/concepts/audio-qa.md`.
