# Music Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| song | `wiki/entities/songs/` | A song in flight or finished. Slug is working-title kebab. |
| release | `wiki/entities/releases/` | A DistroKid (or other) release; one or more songs + platforms + status. |
| gear | `wiki/entities/gear/` | Hardware / instrument / synth / interface / monitor. |
| sample-pack | `wiki/entities/sample-packs/` | A sample / loop pack. |
| venue | `wiki/entities/venues/` | A music venue Adithya has played or is playing. |
| person | `wiki/entities/people/` | Collaborator, engineer, label-contact, manager, booking-agent, fan-contact. |
| company | `wiki/entities/companies/` | Label, distributor, venue-owner, software vendor. |

## Per-type page format

### song

```yaml
---
slug: <working-title-kebab>
type: song
working_title: <string>
release_title: <string>            # null until released; alias when set
status: <idea | tracking | mixing | mastering | released | shelved>
bpm: <number>
key: <key-string>                  # e.g. "Cm", "F#"
daw: <ableton | logic | flstudio | other>
created_at: <YYYY-MM-DD>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Concept`, `## Production notes`, `## Collabs`, `## Releases`, `## Backlinks`.

### release

```yaml
---
slug: <kebab>
type: release
distributor: <distrokid | self | label-name>
release_date: <YYYY-MM-DD>
status: <queued | live | taken-down>
songs: [<song-slug>...]
platforms: [spotify, apple, soundcloud, youtube, ...]
---
```

Body sections: `## Metadata`, `## Performance`, `## Notes`, `## Backlinks`.

### gear

```yaml
---
slug: <make>-<model-kebab>          # e.g. teenage-engineering-op-1
type: gear
category: <synth | drum-machine | interface | monitor | mic | controller | other>
acquired_at: <YYYY-MM-DD>
status: <active | sold | broken | loaned-out>
---
```

### sample-pack

```yaml
---
slug: <vendor>-<name-kebab>
type: sample-pack
vendor: <name>
acquired_at: <YYYY-MM-DD>
genre_tags: [...]
---
```

### venue

```yaml
---
slug: <venue-name-kebab>
type: venue
city: <city>
state: <state>
last_played: <YYYY-MM-DD>
---
```

### person

Standard person frontmatter plus `role: <collaborator | engineer | label-contact | manager | booking-agent | fan-contact | other>`.

### company

Standard company frontmatter plus `relationship: <label | distributor | venue-owner | software-vendor | other>`.

## Vocabulary

- "track" — synonym for song
- "release" — DistroKid upload going to streaming services (PUBLISH-gated)
- "drop" — informal release announcement
- "the kit" — Adithya's current studio setup (gear inventory)

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent.
