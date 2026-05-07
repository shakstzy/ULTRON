# OnlyFans Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| fan | `wiki/entities/fans/` | A subscriber. Slug is hashed (`fan-<short-hash>`); real handle / billing name lives only in `raw/`. |
| campaign | `wiki/entities/campaigns/` | A content drop / PPV / mass-message push, dated. |
| content-piece | `wiki/entities/content/` | A single piece of content (photo set, video, story). |
| person | `wiki/entities/people/` | Collaborators, photographers, business contacts (NOT subscribers). |
| company | `wiki/entities/companies/` | Platform, payment processors, agency partners. |

## Per-type page format

### fan

```yaml
---
slug: fan-<short-hash>
type: fan
joined_at: <YYYY-MM-DD>
status: <active | churned | banned>
tier: <free | basic | premium | vip>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Engagement summary`, `## Spend pattern`, `## Notes`, `## Backlinks`. NEVER include real handle or billing name in the wiki page; reference `raw/<source>/<id>` if needed.

### campaign

```yaml
---
slug: <kebab>
type: campaign
launched_at: <YYYY-MM-DD>
status: <draft | live | ended>
content_type: <photo-set | video | ppv | mass-dm | story>
gross_revenue_usd: <number>
fan_reach: <number>
---
```

Body sections: `## Goal`, `## Output`, `## Performance`, `## Lessons`, `## Backlinks`.

### content-piece

```yaml
---
slug: <kebab>
type: content-piece
created_at: <YYYY-MM-DD>
format: <photo | video | story | gif>
duration_seconds: <number>          # video only
ppv_eligible: <true | false>
---
```

### person

Standard person frontmatter (see `_shell/docs/entity-stub-format.md`). Do NOT use this type for subscribers.

### company

Standard company frontmatter.

## Vocabulary

- "the platform" — OnlyFans
- "fan" — subscriber (always slug-anonymized in wiki)
- "PPV" — pay-per-view content
- "mass DM" — one-to-many DM blast (PUBLISH-gated)
- "drop" — scheduled content release

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly. Lint agent never modifies this file directly.
