---
workspace: personal
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: route_to_main
---

# Personal — Workspace Router

You are in workspace `personal` — Adithya's personal life, outside of work.

## What this workspace is

Music production, fitness lifestyle, dating, home, friends, music industry contacts, gear, songs in flight, venues, ongoing personal projects. The catch-all for the parts of Adithya's life that don't fit a more specific workspace.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No `identity.md` or `style.md` — uses global default voice, slightly more casual register inferred from context.)

## Voice

Default ULTRON voice. Plain words. Don't be stiff. This is the life-stuff workspace, not a B2B context.

## Hard rules (workspace-specific)

1. Friend / contact / family references must resolve through `schema.md`'s `person` type. Disambiguate by context (`<first>-<context>`) when the same first name appears in 2+ contexts.
2. Music gear, songs, venues, pets are separate entity types from `person`.
3. Wiki synthesis pages tend to be longer here (life topics span months) — soft cap 300 lines instead of 200.
4. Commit messages: `chore(personal): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (friend / family / contact)? | `wiki/entities/people/<x>.md` |
| Status of song / project Y? | `wiki/entities/songs/<y>.md` |
| What gear do I have? | `wiki/entities/gear/` (inventory) |
| Where did I see Z play? | `wiki/entities/venues/<z>.md` |
| Recent comms with someone? | `raw/imessage/<latest>/...` then `raw/gmail/<latest>/...` |
| "Ship / drop / release / upload <track> to distrokid" | `_shell/skills/distrokid/SKILL.md` (impl in `~/QUANTUM/workspaces/distrokid/`) |
| "Remove / takedown <track> from stores" | `_shell/skills/distrokid/SKILL.md` (HITL flow) |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`. Defaults: gmail (personal account), iMessage (filtered to personal contacts), manual notes. Ingest deferred until credentials provisioned.
