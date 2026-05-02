# Stage: ingest-apple-health

## Inputs
- Apple Health XML/CSV exports dropped at `workspaces/<ws>/raw/apple-health/_inbox/`.
- Workspace subscriptions in `workspaces/<ws>/config/sources.yaml`.

## Process
1. Watch `_inbox/` for `.xml`, `.zip`, `.csv` files.
2. For each new file: parse, split per metric type, write per-metric per-month files.
3. Move source out of `_inbox/` to dated subdir.
4. Append to ledgers.

## Status
Skeleton. Use `_shell/bin/ingest-manual.py` flow today (drop XML in `_inbox/`, get archived). Real parsing of Apple Health XML deferred until Adithya wires the dedicated robot.
