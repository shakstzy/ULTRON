---
workspace: synapse
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Synapse — Workspace Router

You are in workspace `synapse` — Adithya's startup operating context.

## What this workspace is

Synapse is Adithya's startup (domain `synps.xyz`, company name "Synapse"). Tracks fundraising, accelerator/program applications, the Google for Startups Cloud Program (Synapse track), dev-tool vendor relationships, BD partnerships, and Workspace admin for the synps.xyz domain. Founder-only operation as of 2026-05.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice (overrides global)
4. `style.md` — workspace tone
5. `nomenclature.md` — file-system routing

## Voice override

Founder-precise. Numbers verbatim. Speculation tagged. See `identity.md`.

## Hard rules (workspace-specific)

1. Investor / accelerator / partner / vendor references must resolve through `schema.md`'s `person` and `company` types.
2. Sensitive deal data (term sheets, valuations, cap-table specifics) lives only in `raw/` — never in `wiki/`. Wiki summarizes existence and direction, not specifics.
3. Commit messages: `chore(synapse): <stage> <YYYY-MM-DD>`.
4. Workspace-admin alerts for synps.xyz (Google Workspace security, billing, domain) live in raw, surfaced in wiki only when actionable.
5. Do NOT mix synapse content with eclipse content. Eclipse Labs is a separate company (eclipse.builders / eclipse.audio). Synapse is `synps.xyz`. Cross-references via `[[@person]]` global stubs only.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (investor / advisor / partner)? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| What VC firm Y? | `wiki/entities/companies/<y>.md` |
| Status of accelerator program Z? | `wiki/entities/programs/<z>.md` |
| Fundraise pipeline overall | `wiki/synthesis/fundraise.md` |
| Recent comms with someone? | `raw/gmail/adithya-synps/<latest-month>/...` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`. Primary mailbox: `adithya@synps.xyz`. Manual notes via `raw/manual/_inbox/`.
