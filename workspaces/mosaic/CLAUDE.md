---
workspace: mosaic
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Mosaic — Workspace Router

You are in workspace `mosaic` — Mosaic, a project spawned from Outerscope.

## What this workspace is

Mosaic is one of Adithya's Outerscope-spawned ventures. Sister venture to `synapse`. Parent: `outerscope`. Drive folders under `adithya@outerscope.xyz` and Granola meeting notes filed under the Mosaic folder upstream are the current canonical sources. No dedicated Google account yet.

Personal / friends / fitness / music contexts go to their own workspaces, not here.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Plain words. Business-deliberate (partners, product, contracts) without stiffness. Same register as outerscope.

## Hard rules (workspace-specific)

1. Person / company / partner references must resolve through `schema.md`'s `person` and `company` types, link to `[[@slug]]` for global identity.
2. Sensitive deal data (cap table, valuation, equity) lives only in `raw/`. Wiki summarizes existence and direction, not specifics.
3. Commit messages: `chore(mosaic): <stage> <YYYY-MM-DD>`.
4. Do NOT mix Mosaic content with `synapse`, `eclipse`, or `seedbox`. Cross-references via `[[@person]]` global stubs only.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (Mosaic team / partner / counterparty)? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| What's in the Mosaic Drive folder? | `raw/drive/adithya-outerscope/<...>` |
| Granola notes for Mosaic meetings? | `raw/granola/<YYYY-MM>/...` |
| Status of a Mosaic project / topic | `wiki/synthesis/<topic>.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing rules live in `_shell/docs/source-routing.md`. Sources today: Drive (Mosaic-tagged folders under `adithya@outerscope.xyz`), Granola (folder: `MOSAIC` upstream).
