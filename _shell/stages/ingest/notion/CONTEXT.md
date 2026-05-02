# Stage: ingest-notion

## Status
Skeleton. Not yet wired. To enable:
1. Create a Notion internal integration; install in target workspaces.
2. Drop the integration token at `_credentials/notion-<workspace-slug>.json`.
3. Implement `_shell/bin/ingest-notion.py` (skeleton only today).
4. Define page/database filters in each workspace's `sources.yaml` notion block.

## Planned shape
Per-page markdown files at `workspaces/<ws>/raw/notion/<workspace-slug>/<YYYY>/<MM>/<page-slug>__<page-id8>.md`. Cursor by `last_edited_time`. See the universal envelope in `_shell/stages/ingest/CONTEXT.md`.
