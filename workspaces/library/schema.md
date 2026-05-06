# Library Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A human in scope for this workspace. |
<additional types from bootstrap Q3>

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: <enum>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Open questions`, `## Backlinks` (auto-built).

<additional per-type formats from bootstrap>

## Vocabulary

<populated at bootstrap from Q3 + Q8>

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya weekly. Lint agent never modifies this file directly.
