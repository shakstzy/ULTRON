# Format: notion (skeleton)

## File granularity
One markdown file per Notion page. Database items also become per-page files (Notion treats every row as a page).

## Path
`workspaces/<ws>/raw/notion/<workspace-slug>/<YYYY>/<MM>/<page-slug>__<page-id8>.md`

## Frontmatter

```yaml
---
source: notion
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601 page.last_edited_time>

notion_workspace_id: <id>
page_id: <full uuid>
page_title: ...
parent_path: ["Workspace", "Database", "Item"]
properties: {...}                # for database items
---
```

## Body
Notion blocks rendered to markdown via `notion_to_md` or equivalent. Embeds (databases, callouts, toggles) → markdown approximations.

## Pre-filter
- Skip archived pages.
- Skip pages > 5 MB rendered.

## Dedup key
`notion:<page_id>` (UUID is provider-stable).
