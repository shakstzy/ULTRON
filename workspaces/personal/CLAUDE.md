---
workspace: personal
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: route_to_main
---

# Personal — Workspace Router

You are in workspace `personal` — Adithya's personal life that does not have a more specific workspace.

## What this workspace is

Friends, family, home, day-to-day life, social events, travel, personal projects that do not fit elsewhere. Genuine catch-all.

What does NOT belong here:

- Music production, songs, releases, gear, music-industry contacts → `music`
- Workouts, nutrition, sleep, supplements, medical, vitals → `health`
- Dating-app activity, matches, dates → `dating`
- Banking, investments, taxes, recurring bills → `finance`
- Active markets, trading, P&L → `trading`
- Real-estate transactions / investing → `real-estate`
- Rental ops → `property-management`
- Reading / learning corpus → `library`

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No `identity.md` or `style.md` — uses global default voice, slightly more casual register inferred from context.)

## Voice

Default ULTRON voice. Plain words. Don't be stiff. This is the life-stuff workspace, not a B2B context.

## Hard rules (workspace-specific)

1. Friend / contact / family references must resolve through `schema.md`'s `person` type. Disambiguate by context (`<first>-<context>`) when the same first name appears in 2+ contexts.
2. Pets and household items are separate entity types from `person`. Do NOT introduce music / gear / song / venue / workout / supplement entity types here — those live in `music` and `health`.
3. Wiki synthesis pages tend to be longer here (life topics span months) — soft cap 300 lines instead of 200.
4. Commit messages: `chore(personal): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (friend / family / non-domain contact)? | `wiki/entities/people/<x>.md` then `[[@x]]` for global identity |
| Recent comms with someone (general)? | `raw/imessage/<latest>/...` then `raw/gmail/<latest>/...` |
| Travel / trip log? | `wiki/synthesis/travel.md` |
| Home / household? | `wiki/synthesis/home.md` |
| Personal projects that do not fit a domain workspace? | `wiki/synthesis/projects/<name>.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage for this workspace's health check.

## Sources

Declared in `config/sources.yaml`. Defaults: gmail (personal account), iMessage (filtered to personal contacts), manual notes. Ingest deferred until credentials provisioned.
