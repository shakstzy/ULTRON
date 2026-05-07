---
workspace: outerscope
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Outerscope — Workspace Router

You are in workspace `outerscope` — Adithya's Outerscope venture (InclusiveLayer and adjacent product / contract / market work).

## What this workspace is

Adithya's venture studio. Houses non-main-contract work: product docs, contracts, market research, partner materials, anything Outerscope-branded that does not belong in `eclipse` (separate company) or `synapse` / `mosaic` (child ventures with their own workspaces).

Child ventures and contracts spawned from / housed under Outerscope:

- `synapse` — active pre-launch startup with its own `synps.xyz` domain and Google Workspace; tracks fundraising, accelerator programs, dev-tool relationships.
- `mosaic` — active Outerscope-housed project; Drive content + Granola notes under the `MOSAIC` folder upstream.
- `inclusive-layer` — past growth-lead contract from earlier 2025; archive workspace, Drive content under the `INCLUSIVELAYER` folder.

Gmail / Drive / Granola routing across all four is centralized in `_shell/docs/source-routing.md`. Content tagged Mosaic / Synapse / Inclusive Layer upstream flows to those workspaces, not here.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No `identity.md` / `style.md` override — uses global default voice.)

## Voice

Default ULTRON voice. Plain words. Direct, low-decoration prose. Business-deliberate (contracts, partners, product) without being stiff.

## Hard rules (workspace-specific)

1. Person references resolve through `schema.md`'s `person` type and link to global identity stubs in `_global/entities/people/`.
2. Sensitive deal terms (cap table, valuation, equity %) live only in `raw/`. Wiki synthesis surfaces relationships and status, not numbers.
3. Commit messages: `chore(outerscope): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (Outerscope team / partner / counterparty)? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| What's in InclusiveLayer? | `raw/drive/adithya-outerscope/...` |
| Status of contract / MoU Y? | `wiki/synthesis/<y>.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Sole source today: Drive ingest from `adithya@outerscope.xyz` (designated folder: INCLUSIVELAYER).
