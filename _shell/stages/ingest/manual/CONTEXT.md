# Stage: ingest-manual

## Inputs
- Files dropped in any workspace's manual `_inbox/` directories declared in its `sources.yaml`.
- Workspace subscriptions in `workspaces/*/config/sources.yaml` (`type: manual`, with `watch_path`).
- No credentials. Local filesystem only.
- Cursor: not used (manual sources move files out of `_inbox/`, so the inbox itself is the cursor).

## Process
See `_shell/bin/ingest-manual.py` (already implemented). For each workspace's manual source: list `_inbox/`, slugify, move into the dated output dir, append a ledger row keyed by `manual:<source_id>:<basename>`.

## Output
- Files at `workspaces/<ws>/raw/<source>/<YYYY-MM>/<slug>.<ext>`.
- Ledger updates in `_meta/ingested.jsonl`.

## Status
Implemented. Manual sources are the simplest case and the most reliable v1 path until OAuth-driven sources land.
