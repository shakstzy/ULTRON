# Stage: ingest-drive

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace drive subscriptions | `workspaces/*/config/sources.yaml` (drive block) | Per-account folder lists + routing |
| Format spec | `_shell/stages/ingest/drive/format.md` | Output shape |
| Cursor | `_shell/cursors/drive/<account-slug>.txt` | Last `pageToken` or modified-time watermark |
| Credentials | `_credentials/drive-<account-slug>.json` | OAuth |
| Dedup ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `drive:<file_id>` |

## Process
1. Discover Drive subscriptions across workspaces; group by account.
2. For each account: build the union folder list and mime-type allowlist; query `files.list` with `modifiedTime > cursor`.
3. For each new/changed file:
   a. Pre-filter per `format.md` (size cap, mime allowlist, ownership rules).
   b. Export Google Docs as markdown via `files.export` (mimeType `text/markdown` or `text/plain`); pass-through PDFs as PDF (extraction deferred to wiki promotion); image files referenced by metadata only.
   c. Compute content_hash.
   d. Call `route(file_meta, workspaces_config)`.
   e. Write to each destination workspace's `raw/drive/<account-slug>/<YYYY>/<MM>/<slug>__<file_id8>.<ext>`.
   f. Append to ledgers.
4. Advance cursor to the latest `modifiedTime`.

## Outputs
Drive files at deterministic paths; updated cursor + ledgers + log.

## Self-review
Same shape as gmail — verify envelope, cursor, ledger consistency, route outputs.

## Status
Skeleton. Full implementation deferred. The robot at `_shell/bin/ingest-drive.py` exits cleanly with "no credentials, skipping" until OAuth is wired.
