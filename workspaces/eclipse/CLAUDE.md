# <Workspace Name> — Workspace Router

You are in workspace `<workspace-slug>` — <one-line domain description, populated at bootstrap>.

## What this workspace is

<2-3 sentences. The bootstrap agent fills this from Q1.>

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice (overrides global; only if present)
4. `style.md` — workspace tone (only if present)
5. `nomenclature.md` — file-system routing

## Voice override

<If Q4 = a, write: "This workspace uses the global default voice. See ~/ULTRON/CLAUDE.md.">
<If Q4 = b, write: "See identity.md for the voice override.">

## Hard rules (workspace-specific)

<Populated at bootstrap from Q3 + Q4 + Q8.>

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X? | `wiki/entities/people/<x>.md` → `[[@x]]` for global identity |
| <other workspace-specific queries from Q3> | <path> |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`.
