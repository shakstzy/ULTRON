# Synapse Schema

Workspace schema for Synapse (Adithya's startup, domain `synps.xyz`). Defines entity types, page formats, and vocabulary the wiki agent uses.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | An investor, accelerator partner, BD contact, vendor rep, or other professional contact for Synapse. |
| company | `wiki/entities/companies/` | A VC firm, accelerator org, BD partner, vendor, customer, or competitor. |
| program | `wiki/entities/programs/` | An accelerator, grant, or program Synapse is applying to or participating in (Y Combinator, Alliance, HF0, NVIDIA Inception, AWS Activate, Orange Fellowship, Google for Startups Cloud, etc.). |
| deal | `wiki/entities/deals/` | A fundraising round, BD partnership, or commercial agreement in flight or closed. |

## Per-type page format

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
role: investor | accelerator-partner | bd-contact | vendor | advisor | other
company: <wikilink to company entity, or null>
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
category: vc | accelerator | bd-partner | vendor | customer | competitor
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Overview`, `## Relationship`, `## Key contacts`, `## Backlinks`.

### program

```yaml
---
slug: <kebab>
type: program
canonical_name: <name>
status: applied | accepted | active | rejected | declined | completed
applied: <YYYY-MM-DD or null>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Overview`, `## Application status`, `## Deliverables / commitments`, `## Backlinks`.

### deal

```yaml
---
slug: <kebab>
type: deal
canonical_name: <short title>
kind: fundraise | bd | commercial | partnership
status: cold | warm | active | won | lost | paused
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Overview`, `## Status`, `## Key contacts`, `## Notes`, `## Backlinks`.

## Vocabulary

- "GCS" = Google for Startups Cloud Program (Synapse track). NOT Google Cloud Storage.
- "synps" = the short-domain handle (the email domain is `synps.xyz`); the company name is "Synapse".
- "Workspace admin" = synps.xyz Google Workspace administrative mail (security, billing, domain config).
- "Pre-seed" / "Seed" = fundraise stages, lowercase in body, capitalized in deal slugs.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya weekly. Lint agent never modifies this file directly.
