---
workspace: sei
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Sei — Workspace Router

You are in workspace `sei` — Adithya's past full-time role at Sei (Sei Labs / sei.io) as incubation growth lead.

## What this workspace is

A full-time role Adithya held at Sei. Tracks the people, ecosystem projects, partnerships, and incubation activity from that period. Now an archive workspace — historical reference, occasional follow-up email, ongoing relationships with people who threaded through it.

Sei is a publicly known Layer-1 blockchain focused on high-speed trading. Adithya's role was incubation growth lead, working with portfolio / ecosystem projects on go-to-market.

Past-job archive shape: no active ingest cron, lint-only schedule. New mail trickles in via gmail labels (TBD: confirm label names). Independent of `outerscope` — this was a separate company, not housed under Adithya's venture studio.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Plain words. Business-deliberate (incubation, ecosystem, portfolio) without stiffness. Past-tense by default; flag any active-tense reference for review.

## Hard rules (workspace-specific)

1. Person / company / portfolio-project references must resolve through `schema.md` types, link to `[[@slug]]` for global identity.
2. Sensitive comp / equity / contract terms live only in `raw/`. Wiki summarizes existence and direction, not specifics.
3. Past-tense default. Adithya is no longer at Sei; the wiki tracks history.
4. Commit messages: `chore(sei): <stage> <YYYY-MM-DD>`.
5. Do NOT mix Sei content with `inclusive-layer`, `eclipse`, `mosaic`, `synapse`, or `seedbox`. Cross-references via `[[@person]]` global stubs only.
6. If the Sei team had its own Slack / Drive / Workspace and credentials are no longer valid, those rows in `_shell/docs/source-routing.md` should be marked archived (read-only / no-fetch).

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (Sei team / ecosystem founder / partner)? | `wiki/entities/people/<x>.md` then `[[@x]]` |
| What did portfolio company Y do? | `wiki/entities/portfolio-projects/<y>.md` |
| What was my role / scope? | `wiki/synthesis/role.md` |
| Past Granola notes? | `raw/granola/<YYYY-MM>/...` (if folder exists upstream) |
| Recent follow-up mail from Sei contacts? | `raw/gmail/<account>/<YYYY-MM>/...` (filtered to label TBD) |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: gmail (label TBD), granola (folder TBD), manual. Drive and Slack from Sei's own workspace TBD — credentials may or may not still be valid.
