# Mosaic Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A human in scope for this workspace (team, partner, counterparty). |
| company | `wiki/entities/companies/` | A company in scope (partner, vendor, customer, competitor). |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: <team | partner | counterparty | advisor | other>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Open questions`, `## Backlinks` (auto-built).

### company

```yaml
---
slug: <kebab>
type: company
canonical_name: <name>
relationship: <partner | vendor | customer | competitor | other>
domain: <example.com>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Backlinks`.

## Vocabulary

- "the project" — Mosaic itself
- "the parent" — Outerscope
- "sister project" — Synapse
- "drive folder" — `MOSAIC` upstream under `adithya@outerscope.xyz`

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya weekly. Lint agent never modifies this file directly.
