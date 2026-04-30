# Personal Schema

Workspace schema for personal life. Defines entity types and page formats.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A friend, family member, romantic interest, or non-work contact. |
| song | `wiki/entities/songs/` | A track Adithya is producing, has produced, or has planned. |
| gear | `wiki/entities/gear/` | Music production equipment, instruments, audio interfaces, plugins. |
| venue | `wiki/entities/venues/` | A music spot Adithya plays, attends, or tracks (clubs, festivals, studios). |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: friend | family | romantic | acquaintance | industry-contact | other
context: <one-line: where Adithya knows them from>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Context`, `## Recent threads`, `## Open questions`, `## Backlinks`.

### song

```yaml
---
slug: <kebab>
type: song
canonical_name: <title>
status: idea | in-progress | mixed | mastered | released | shelved
collaborators: [<wikilink to people>]
last_touched: <YYYY-MM-DD>
---
```

Body: `## Concept`, `## Status`, `## Versions`, `## Notes`, `## Backlinks`.

### gear

```yaml
---
slug: <kebab>
type: gear
canonical_name: <name>
category: synth | drum-machine | audio-interface | mic | monitor | plugin | controller | other
acquired: <YYYY-MM-DD or "unknown">
last_touched: <YYYY-MM-DD>
---
```

Body: `## What it is`, `## Use cases`, `## Issues`, `## Backlinks`.

### venue

```yaml
---
slug: <kebab>
type: venue
canonical_name: <name>
city: <city>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Overview`, `## Visits`, `## Backlinks`.

## Vocabulary

- "WIP" = work-in-progress song.
- "demo" = early-stage song, not mixed.
- "industry contact" = music industry person, not a personal friend.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied weekly by Adithya.
