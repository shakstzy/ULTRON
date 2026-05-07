---
workspace: power-kinetics
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Power Kinetics — Workspace Router

You are in workspace `power-kinetics` — Adithya's past growth-lead contract with Power Kinetics.

## What this workspace is

A multi-month contract Adithya took as growth lead earlier in 2025. Drive content lived under `adithya@outerscope.xyz` in the `POWERKINETICS` folder. Now an archive workspace — historical reference, occasional follow-up email, the people who threaded through it.

Past-job archive shape: no active ingest cron, lint-only schedule. New mail / docs trickle in via the gmail label (TBD: confirm label name with Adithya) and the drive folder, both routed through `_shell/docs/source-routing.md`.

Sister to `mosaic`, `synapse`, `seedbox`. Parent context: `outerscope` (the venture studio drive that hosted contract content).

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Plain words. Business-deliberate (contract / counterparty / partner) without stiffness. Past-tense by default; flag any active-tense reference for review.

## Hard rules (workspace-specific)

1. Person / company / counterparty references must resolve through `schema.md`'s `person` and `company` types, link to `[[@slug]]` for global identity.
2. Sensitive deal data (contract terms, billing amounts, equity if any) lives only in `raw/`. Wiki summarizes existence and direction, not specifics.
3. Past-tense default. The contract ended; the wiki tracks history, not in-flight work.
4. Commit messages: `chore(power-kinetics): <stage> <YYYY-MM-DD>`.
5. Do NOT mix Power Kinetics content with `mosaic`, `synapse`, `eclipse`, or `sei`. Cross-references via `[[@person]]` global stubs only.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (Power Kinetics team / counterparty)? | `wiki/entities/people/<x>.md` then `[[@x]]` |
| What was the engagement scope? | `wiki/synthesis/engagement.md` |
| Drive content from the contract? | `raw/drive/adithya-outerscope/POWERKINETICS/...` |
| Granola notes for Power Kinetics meetings? | `raw/granola/<YYYY-MM>/...` (if folder exists upstream) |
| Recent follow-up mail? | `raw/gmail/<account>/<YYYY-MM>/...` (filtered to label TBD) |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: drive (`POWERKINETICS` folder under `adithya@outerscope.xyz`), gmail (label TBD), granola (folder TBD), manual deposits.
