# Eclipse Schema

Workspace schema for Eclipse Labs. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A human Adithya or the team interacts with. |
| company | `wiki/entities/companies/` | A buyer, vendor, partner, or competitor. |
| project | `wiki/entities/projects/` | A specific engagement, dataset, or BD initiative. |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
role: <current role>
company: <wikilink to company entity>
relationship: customer | prospect | vendor | partner | team | competitor-contact | other
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
relationship: customer | prospect | vendor | partner | competitor
deal_stage: prospect | discovery | proposal | active | closed-won | closed-lost | n/a
last_touched: <YYYY-MM-DD>
---
```

Body: `## Overview`, `## Decision-makers`, `## Active deal status`, `## Past interactions`, `## Backlinks`.

### project

```yaml
---
slug: <kebab>
type: project
canonical_name: <name>
status: planning | active | paused | shipped | archived
owner: <wikilink to person>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Goal`, `## Key deliverables`, `## Status`, `## Threads`, `## Backlinks`.

## Vocabulary

- "deal" = an active commercial conversation with a prospect / customer.
- "lead" = an unqualified prospect; pre-discovery.
- "intro" = a warm referral.
- "vendor" = an upstream supplier (data, tooling).
- "partner" = a co-go-to-market relationship.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied weekly by Adithya. Lint agent never modifies this file directly.
