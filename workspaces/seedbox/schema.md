# Seedbox Schema

Workspace schema for Adithya's advisory work for Seedbox Labs (`seedboxlabs.co`). Defines entity types and page formats.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A Seedbox team member, external contact mentioned in threads, or referenced individual. |
| topic | `wiki/entities/topics/` | A recurring discussion theme (ideas exchanges, product / prototyping discussions, advisor admin). |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
role: seedbox-team | external-contact | other
company: <wikilink to company entity, or null>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Open questions`, `## Backlinks` (auto-built).

### topic

```yaml
---
slug: <kebab>
type: topic
canonical_name: <short title>
status: active | dormant | closed
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Overview`, `## Threads`, `## Decisions / next steps`, `## Backlinks`.

## Vocabulary

- "advisor agreement" = the formal agreement Adithya signed with Seedbox in late 2025.
- "83(b) filing" = the equity-grant tax election Adithya filed as advisor; thread dated 2025-12-18.
- "Seedbox team" = currently Avery Haskell, Lara Daniel (also "Lara Stein" in some sigs), Abraham Choi.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya weekly. Lint agent never modifies this file directly.
