# Stage: ingest-drive

> **Authoritative data spec**: `format.md` (paths, frontmatter, body,
> pre-filter, reconciliation, cursor, CLI, forbidden behaviors).
> **Operator runbook**: `SETUP.md` (OAuth scope verification, folder ID
> retrieval, sources.yaml configuration, activation procedure).
> **Routing**: `route.py` (per-workspace folder claim mapping).
> **Config validator**: `_shell/bin/validate-drive-config.py`.

## Inputs

| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (drive block) | Per-account designated folder list + per-workspace routing |
| Cursor | `_shell/cursors/drive/<account-slug>.txt` | Last `changes.list` page token per upstream account |
| Credentials | `_credentials/gmail-<account-slug>.json` | OAuth refresh token; same file as Gmail (shared client, drive scope already present) |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup keyed by `drive:<file_id>` |
| Lookback | (none) | Designated folders are absolute scope; first-run = full enumerate |

## Process

One robot run = one upstream account. Multi-account scheduling is the
launchd / cron layer's job: one plist per `account-slug`. Multi-workspace
fan-out happens inside the run.

1. **flock** `/tmp/com.adithya.ultron.ingest-drive-<account-slug>.lock`.
   Concurrent run for the same account → exit 0 silently.
2. **Auth** from `_credentials/gmail-<account-slug>.json`; build Drive v3
   API client. On `invalid_grant`: fast-fail with recovery message
   referencing `SETUP.md`.
3. **Resolve subscriptions**:
   - Walk every `workspaces/*/config/sources.yaml` drive block.
   - Filter to entries where `accounts[].account == --account`.
   - Build the union list of designated folders this run owns.
4. **Mode dispatch**:
   - `--mode reconcile` (or first-run with empty cursor) → run the full
     reconciliation algorithm (`format.md` Lock 6) for every
     `(designated_folder, claiming_workspaces)` pair.
   - `--mode incremental` (default, cursor present) → drive the
     `changes.list` event stream (`format.md` Lock 7).
5. **For each fetched file**:
   - Apply pre-filter (`format.md` Lock 5). Skipped → no file written.
   - Resolve target file via shortcut chain if applicable (Lock 5).
   - Render body per file type (`format.md` Lock 4).
   - Compute `content_hash` (blake3 of body bytes).
   - `route(file_meta, workspaces_config) → list[{workspace, rule}]` from
     `route.py` (folder-claim map).
   - Per destination: skip if `(key, content_hash)` already in ledger;
     else write file at deterministic path (`format.md` Lock 1) and
     append ledger row.
6. **Reconciliation deletes**:
   - Files leaving a designated folder, entering Drive trash, or
     hard-deleted upstream → hard-delete from raw (`format.md` Lock 6).
   - Deletes happen AFTER all reads + new ingests succeed in the run.
7. **Advance cursor** to the new `changes.list` page token only after the
   write phase succeeds. Mid-run failure → cursor stays; next run replays.
8. **Per-workspace summary** appended to
   `workspaces/<ws>/_meta/log.md`.
9. **Self-review** writes anomalies to
   `_shell/runs/<RUN_ID>/self-review.md`: 429 deferrals, ACL-hidden files,
   shortcut chain breaks, route misses, extraction failures, cursor
   expiries.

## Outputs

| Artifact | Location |
|---|---|
| File records | `workspaces/<ws>/raw/drive/<account-slug>/<folder-path>/<file-slug>__<file-id-short>.<ext>` |
| Cursor | `_shell/cursors/drive/<account-slug>.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Per-run log | `_logs/drive-<account-slug>-<run-id>.log` |
| Error log | `_logs/drive-errors-<date>.log` |
| Self-review | `_shell/runs/<RUN_ID>/self-review.md` |

## Out of scope (this stage)

LLM / vision text extraction (no OCR for scanned PDFs in v1); attachment
binary copies; multi-tab Sheets export; Drawings / Forms / Sites /
Apps Script ingestion; comment / suggestion ingestion; per-tab routing for
Sheets; cross-source dedup (Drive ↔ Gmail attachments); routing-time
folder allowlist (each folder is either claimed or not in v1, no globs).

## Status

Skeleton. `_shell/bin/ingest-drive.py` has `IMPLEMENTATION_READY = False`.
Activation procedure in `SETUP.md` § 7. Until activated, the robot exits 0
with an actionable stderr message.
