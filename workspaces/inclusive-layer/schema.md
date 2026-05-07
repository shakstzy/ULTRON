# Inclusive Layer Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A human in scope for this engagement (team, counterparty, partner). |
| company | `wiki/entities/companies/` | A company in scope (the client itself, partner, vendor, counterparty). |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: <client-team | counterparty | partner | advisor | other>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Contributions`, `## Followups`, `## Backlinks`.

### company

```yaml
---
slug: <kebab>
type: company
canonical_name: <name>
relationship: <client | partner | counterparty | vendor | competitor>
domain: <example.com>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Engagement notes`, `## Backlinks`.

## Vocabulary

- "the engagement" — the contract itself
- "the client" — Inclusive Layer
- "the drive folder" — `INCLUSIVELAYER` under `adithya@outerscope.xyz`

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly.
