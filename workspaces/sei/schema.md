# Sei Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A human in scope (Sei team, ecosystem founder, partner, investor). |
| company | `wiki/entities/companies/` | A company in scope (Sei Labs itself, partner, vendor, investor, competitor L1). |
| portfolio-project | `wiki/entities/portfolio-projects/` | An ecosystem / portfolio / incubation project Adithya engaged with. |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: <sei-team | ecosystem-founder | partner | investor | advisor | other>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Followups`, `## Backlinks`.

### company

```yaml
---
slug: <kebab>
type: company
canonical_name: <name>
relationship: <sei-itself | partner | investor | vendor | competitor | counterparty>
domain: <example.com>
last_touched: <YYYY-MM-DD>
---
```

### portfolio-project

```yaml
---
slug: <kebab>
type: portfolio-project
canonical_name: <name>
status: <active | paused | shipped | dead | acquired>
domain: <example.com>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## What it is`, `## Adithya's involvement`, `## Status`, `## Backlinks`.

## Vocabulary

- "Sei" — Sei Labs / sei.io, a Layer-1 blockchain focused on high-speed trading
- "ecosystem" — the set of teams building on Sei
- "incubation" — early-stage support Adithya provided to ecosystem teams
- "portfolio project" — a specific ecosystem team Adithya engaged with

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly.
