---
workspace: network
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: route_to_main
---

# Network — Workspace Router

You are in workspace `network` — Adithya's professional network. Investors, founders, operators, peers, prospects. People he meets through work, not through dating or family. The data here feeds enrichment of the canonical person stubs at `_global/entities/people/`.

## What this workspace is

Stream-style ingest of professional contact data: LinkedIn profile snapshots, message threads, connection events, search results. Optional Gmail / Calendar / Slack future-pulls land here too when they're work-shaped. Anything dating goes to `personal`; anything Eclipse-team-internal goes to `eclipse`. This workspace is the catch-all for "people he wants to track professionally."

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

## Voice override

This workspace uses the global default voice. See `~/ULTRON/CLAUDE.md`.

## Hard rules (workspace-specific)

1. People deposits land in `raw/linkedin/<slug>-linkedin.md` (LinkedIn) — never duplicated into the global stub. The global stub at `_global/entities/people/<slug>.md` is identity + backlinks only.
2. Every raw deposit's frontmatter must include an `entity:` wikilink up to its global stub so graphify resolves the route.
3. Slug is the join key. If LinkedIn returns one slug and Apple Contacts has another for the same person, run `/alias` to merge — never hand-rewrite wikilinks.
4. Auto-created global stubs from LinkedIn `get-profile` are tagged `entity_status: provisional` until promoted. Use `/promote-entity` to elevate them to first-class.
5. Send-direction LinkedIn actions (send-connect, send-dm, accept-invite, withdraw-invite) require `--send` to execute; default is dry-run.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (professionally)? | `_global/entities/people/<x>.md` for identity, `raw/linkedin/<x>-linkedin.md` for snapshot |
| What did X say to me on LinkedIn? | `raw/linkedin/<x>-linkedin.md` `## Threads` section |
| Outstanding LinkedIn connection requests | run `linkedin list-invites --direction sent` |
| Recent inbound LinkedIn invites | run `linkedin list-invites --direction received` |
| Who's in my network from <company>? | obsidian-base over `_global/entities/people/` filtered on `identifiers.linkedin` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage (deferred; LinkedIn ingest is direct-to-raw).
- `agents/lint-agent.md` — used by lint stage (deferred).

## Sources

| Source | Path | Skill |
|---|---|---|
| linkedin | `raw/linkedin/<slug>-linkedin.md` | `linkedin` (run.mjs dispatcher) |
