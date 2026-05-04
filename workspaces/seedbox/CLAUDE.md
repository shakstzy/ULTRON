---
workspace: seedbox
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Seedbox — Workspace Router

You are in workspace `seedbox` — Adithya's advisory work for Seedbox Labs.

## What this workspace is

Seedbox Labs is a startup where Adithya is an advisor. Founded / operated by Avery Haskell, Lara Daniel (Stein), and Abraham Choi (`seedboxlabs.co`). Adithya signed an advisor agreement with 83(b) filing in late 2025. Workspace tracks the advisory relationship: intro / pitch / advisor admin, ideas-exchange threads, forwards, and any product discussions that flow through email.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Plain words. This is an advisory workspace, less business-deliberate than eclipse, more focused than personal.

## Hard rules (workspace-specific)

1. Seedbox team / external contact references must resolve through `schema.md`'s `person` type.
2. Ideas / product / pitch synthesis lives in `wiki/synthesis/`. Sensitive deal terms (cap table, valuation, equity %) live only in `raw/`.
3. Commit messages: `chore(seedbox): <stage> <YYYY-MM-DD>`.
4. The 83(b) filing thread and advisor agreement are governance-critical. Surface in wiki summary; full text only in raw.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (Seedbox team / referenced contact)? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| What's the latest from Seedbox? | `raw/gmail/adithya-outerscope/<latest-month>/...` |
| Status of advisor agreement / 83(b) | `wiki/synthesis/advisor-admin.md` |
| Ideas / prototyping threads | `wiki/synthesis/ideas-exchange.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`. Sole source: `label:Seedbox` from `adithya@outerscope.xyz`.
