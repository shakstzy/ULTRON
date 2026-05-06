---
workspace: music
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Music — Workspace Router

You are in workspace `music` — Adithya's music production, releases, and music-industry context.

## What this workspace is

Songs in flight, finished tracks, releases via DistroKid, gear inventory, sample / sound libraries, collaborators, labels, venues, music-industry contacts, performance history. Splits out from `personal` to give music its own first-class wiki.

When asked to "release / drop / upload / takedown a track," route through the `distrokid` skill (to be ported from QUANTUM into ULTRON-local form, not symlinked).

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Casual register, music-fluent. Specific about gear (model numbers), DAW versions, BPM / key when relevant. Honest about half-finished work.

## Hard rules (workspace-specific)

1. Songs resolve via `schema.md`'s `song` type, slugged by working-title kebab. Final release titles map back to working-title slugs via aliases.
2. Gear / instruments / synths resolve via `gear` type. Sample packs via `sample-pack` type.
3. Collaborators / labels / engineers resolve via `person` and `company`.
4. Venues resolve via `venue` type.
5. Releases (DistroKid uploads) resolve via `release` type, linking song(s) + platforms + status (queued / live / taken-down).
6. Streaming numbers and royalty data live in `raw/distrokid/<YYYY-MM>/`. Wiki summarizes monthly.
7. Commit messages: `chore(music): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What's the status of song / track X? | `wiki/entities/songs/<x>.md` |
| What gear do I have? | `wiki/entities/gear/` |
| Who is producer / collab / label X? | `wiki/entities/people/<x>.md` then `[[@x]]` |
| Where did I play / will I play? | `wiki/entities/venues/<x>.md` |
| Latest releases | `wiki/synthesis/releases.md` |
| "Ship / drop / release / upload <track> to DistroKid" | `_shell/skills/distrokid/SKILL.md` (ULTRON-local; ported from QUANTUM) |
| "Remove / takedown <track> from stores" | `_shell/skills/distrokid/SKILL.md` (HITL flow) |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: manual deposits in `raw/manual/_inbox/`, gmail (music-labeled threads from primary mailbox), DistroKid CSV exports under `raw/distrokid/`, future iMessage filter for music-industry contacts.
