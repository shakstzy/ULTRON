---
workspace: eclipse
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: route_to_main
---

# Eclipse — Workspace Router

You are in workspace `eclipse` — Eclipse Labs operating context.

## What this workspace is

Eclipse Labs sells consent-verified audio data to AI labs and ML teams. Adithya is co-founder and operates with Sydney (CEO/co-founder), Julian, Kayla, Emmett. Active BD focus on ElevenLabs, OpenAI, Deepgram, Mercor relationships, Fluffle vendor.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice (overrides global)
4. `style.md` — workspace tone
5. `nomenclature.md` — file-system routing

## Voice override

This workspace uses a tighter, more business-deliberate voice than the global default. See `identity.md`. Numbers cited verbatim. Speculation explicitly tagged.

## Hard rules (workspace-specific)

1. Customer / vendor / partner / competitor references must resolve through `schema.md`.
2. `wiki/synthesis/` pages over 200 lines split by quarter (e.g., `q1-2026-bd.md`).
3. Sensitive deal data (term sheets, exclusive intel) lives only in `raw/` — never in `wiki/`. Wiki summarizes the existence and direction, not specifics.
4. Commit messages: `chore(eclipse): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| State of deal with Y | `wiki/synthesis/y-deal.md` (or absent → check `raw/` and propose synthesis) |
| Recent comms with Z | `raw/gmail/<latest-month>/...` for verbatim; `wiki/entities/people/<z>.md` for synthesis |
| Vendor / partner status | `wiki/entities/companies/<vendor>.md` |
| BD pipeline overall | `wiki/synthesis/bd-pipeline.md` |
| Audio QA conventions | `wiki/concepts/audio-qa.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`. Currently: gmail, slack, drive, manual notes (all configured-but-not-yet-running until Adithya provisions credentials and re-enables ingest).
