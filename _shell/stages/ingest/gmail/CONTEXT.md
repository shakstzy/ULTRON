# Stage: ingest-gmail

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace gmail subscriptions | `workspaces/*/config/sources.yaml` (gmail block) | Build per-account union query + per-workspace routing |
| Format spec | `_shell/stages/ingest/gmail/format.md` | Output shape |
| Cursor | `_shell/cursors/gmail/<account-slug>.txt` | Last `historyId` (or last-fetched ISO date for first run) |
| OAuth credentials | `_credentials/gmail-<account-slug>.json` | Authorized-user JSON with refresh_token |
| Dedup ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `gmail:<thread_id>` |

## Process
1. Discover Gmail subscriptions: scan every workspace's `sources.yaml`, collect entries that include the gmail block. Group by `account` (a single account may serve multiple workspaces with different rules).
2. For each `(account, accounts in subscriptions)`:
   a. Load creds; build the Gmail API client.
   b. Read `_shell/cursors/gmail/<account-slug>.txt`. First run: empty cursor → use `lookback_days_initial` window from any workspace's config; subsequent runs: incremental via `historyId`.
   c. Build the union query — UNION of all subscribing workspaces' `include` rules, INTERSECT with their `exclude` rules. (Conservative: a thread fetched by union may still be filtered out per workspace by `route.py`.)
   d. Page through `users.threads.list` until exhausted.
   e. For each new thread:
      - Apply deterministic skip rules (see `format.md` § Pre-filter).
      - Render thread to markdown per `format.md`.
      - Compute `content_hash`.
      - Call `route(thread, workspaces_config)` → list of destination workspace slugs.
      - For each destination: write `workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<file>.md` and append to `_meta/ingested.jsonl`.
   f. Advance cursor to the latest `historyId` returned.
3. Append a one-line summary to each affected workspace's `_meta/log.md`.
4. Run self-review (~200 tokens) and write `_shell/runs/<run-id>/self-review.md`.

## Outputs
| Artifact | Location |
|---|---|
| Gmail thread files | `workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<file>.md` |
| Cursor | `_shell/cursors/gmail/<account-slug>.txt` |
| Ledger updates | `workspaces/<ws>/_meta/ingested.jsonl` |
| Log entries | `workspaces/<ws>/_meta/log.md` |
| Run self-review | `_shell/runs/<run-id>/self-review.md` |

## Self-review
- Every new file has the universal envelope.
- Cursor advanced past the latest `historyId`.
- Every file has a corresponding ledger row in every destination workspace.
- `route.py` returned a non-empty destination set OR fell back to the unrouted default; flag any item where every workspace's rules matched but routing returned `[]`.
- No file outside `workspaces/<ws>/raw/gmail/...` was written.
