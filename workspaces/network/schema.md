# Network Schema

Workspace schema. Defines entity types and the per-source raw file formats. The wiki agent reads this when ingesting and synthesizing; the LinkedIn skill writes raw deposits matching the formats below.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A professional contact in scope for this workspace. |

Workspace-local entity pages are optional v1; raw deposits + global stubs cover the common case. Promote via `/promote-entity` when a person earns a workspace-local synthesis page.

## Per-source raw deposit format

### linkedin (one file per person, append-only thread events)

Path: `raw/linkedin/<slug>-linkedin.md`

```yaml
---
source: linkedin
workspace: network
ingested_at: <ISO 8601 UTC>
ingest_version: 1
content_hash: sha256:<hex>
provider_modified_at: <ISO 8601 UTC>      # most recent profile update or thread event
slug: <kebab>
linkedin_public_id: <vanity>              # the LinkedIn /in/<vanity> handle
linkedin_url: https://www.linkedin.com/in/<vanity>/
linkedin_urn: <profileUrn or null>
linkedin_thread_id: <id or null>          # only present when origin = thread_sync
name: <display name>
connection_status: connected|pending|incoming_request|connectable|follow_only|self_profile|null
entity: "[[_global/entities/people/<slug>]]"
first_seen: <ISO 8601 UTC>
last_pulled_at: <ISO 8601 UTC>
last_action_at: <ISO 8601 UTC>
previous_slugs: []
---
```

Body sections:

- `## Profile snapshot` — innerText of LinkedIn `<main>` from the most recent get-profile (overwritten on re-pull).
- `## Threads` — append-only event log, dedup'd on (day, direction, text). Each line `### <ISO ts> — <direction>: <text>`.

## Per-type page format (workspace-local, optional)

### person

```yaml
---
slug: <kebab>
type: person
canonical_name: <name>
relationship: investor|founder|operator|peer|prospect|other
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Active threads`, `## Open questions`, `## Backlinks` (auto-built).

## Vocabulary

- **person**: a human with a LinkedIn profile or other professional identifier (email/phone/handle from contacts).
- **provisional global stub**: a `_global/entities/people/<slug>.md` auto-created on first LinkedIn fetch, with `entity_status: provisional` until promoted. Cleaned up by audit if no further activity within N days (TBD).
- **connection_status**: enum of LinkedIn relationship states from `src/linkedin/connection-state.mjs`.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya weekly. Lint agent never modifies this file directly.
