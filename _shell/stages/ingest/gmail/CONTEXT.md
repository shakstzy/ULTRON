# Stage: ingest-gmail

> **Authoritative data spec**: `_shell/stages/ingest/gmail/format.md`.
> **sources.yaml schema** (locked in §3): `sources-schema.md`.
> **Operator runbook** (written in §9): `_shell/docs/runbook-gmail.md`.
> **Credential layout** (written in §9): `_shell/docs/credentials-gmail.md`.

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace gmail subscriptions | `workspaces/*/config/sources.yaml` (gmail block) | Build per-mailbox union query + per-workspace routing |
| Format spec | `_shell/stages/ingest/gmail/format.md` | Output shape (paths, frontmatter, body, pre-filter, dedup) |
| Cursor | `_shell/cursors/gmail/<mailbox-slug>.txt` | Last `historyId` per upstream mailbox |
| OAuth credentials | `_credentials/gmail-<mailbox-slug>.json` | Authorized-user JSON. 1:1 with upstream mailbox. |
| Dedup ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `gmail:<thread_id>` |

## Process
1. **Discover subscriptions.** Scan every `workspaces/*/config/sources.yaml`,
   collect entries inside the `sources.gmail.accounts` list. Group by
   upstream mailbox (the `account` email). One mailbox may serve several
   workspaces with different rules.
2. **For each mailbox** (one robot run = one upstream mailbox; cron compiles
   1 plist per mailbox):
   a. Acquire `flock` on `/tmp/com.adithya.ultron.ingest-gmail-<mailbox-slug>.lock`.
      If another instance is running, exit 0 silently (cron-friendly).
   b. Load credentials from `_credentials/gmail-<mailbox-slug>.json` and
      build the Gmail API client.
   c. Read cursor at `_shell/cursors/gmail/<mailbox-slug>.txt`.
      - **First run** (no cursor): use `messages.list(q=<union>)` over a
        `lookback_days_initial` window (default `GMAIL_INITIAL_LOOKBACK_DAYS`).
        After processing, persist the `historyId` from
        `users.getProfile`.
      - **Subsequent runs**: `users.history.list(startHistoryId=<cursor>)`
        with `historyTypes=[messageAdded, messageDeleted, labelAdded, labelRemoved]`.
        Process each event:
        | Event | Action |
        |---|---|
        | `messageAdded` | Fetch thread, run normal pipeline. |
        | `messageDeleted` | If we have the file, set `deleted_upstream` and rewrite. Don't delete. |
        | `labelAdded` / `labelRemoved` | Re-evaluate routing. If a new label means a previously-non-matching workspace now matches, write to that workspace too. Existing copies stay. |
   d. Build the **union query** (Gmail `q=` syntax — see §3 schema): the
      OR of every subscribing workspace's `api_query.include`, AND'd with
      the union of `api_query.exclude`, AND'd with the universal
      blocklist (see `format.md` § F).
   e. **For each thread** returned (or each thread implicated by a history
      event):
      - Apply the deterministic pre-filter (`format.md` § F).
      - Render thread → markdown per `format.md` § E.
      - Compute `content_hash` (blake3 of body markdown).
      - Call `route(thread, workspaces_config) -> (destinations, matched_rules)`
        from `_shell/stages/ingest/gmail/route.py`.
      - For each destination workspace:
        * Check the ledger; skip if same `(key, content_hash)` already present.
        * Write the file at the deterministic path (`format.md` § B).
        * Append the ledger row (`format.md` § G).
   f. **Advance cursor** to the latest `historyId` seen. Persist only AFTER
      successful write phase. If a write phase fails mid-batch, cursor stays
      at the previous value — the next run picks up the same range.
3. **Append a one-line summary** to each affected workspace's
   `_meta/log.md` (per-mailbox, per-run, with counts).
4. **Run deterministic post-run validation** (`_shell/bin/validate-gmail-run.py`,
   written in §5). Verifies:
   - Every newly-written file passes `check-frontmatter.py`.
   - Every newly-written file's path matches the deterministic template
     (`format.md` § B).
   - Every newly-written file's `content_hash` re-computes to the same value.
   - Every newly-written file has a corresponding ledger row in its
     destination workspace.
   - Cursor advanced strictly forward (or stayed at its previous value if
     the run was a no-op).
   No LLM calls; pure Python checks. Failures are written to
   `_logs/gmail-<mailbox-slug>-<run-id>.validation.log` and the run exits
   non-zero.

## Outputs
| Artifact | Location |
|---|---|
| Gmail thread files | `workspaces/<ws>/raw/gmail/<mailbox-slug>/<YYYY>/<MM>/<file>.md` |
| Cursor | `_shell/cursors/gmail/<mailbox-slug>.txt` |
| Ledger updates | `workspaces/<ws>/_meta/ingested.jsonl` |
| Log entries | `workspaces/<ws>/_meta/log.md` (one line per run, per workspace) |
| Per-run log | `_logs/gmail-<mailbox-slug>-<run-id>.log` |
| Per-run validation log | `_logs/gmail-<mailbox-slug>-<run-id>.validation.log` (only if validation findings) |

## Deferred / out of scope (this phase)

- LLM-based attachment summarization or vision calls.
- Backfill operations beyond `lookback_days_initial`.
- Cross-source dedup (e.g. dropping a Gmail thread because its content also
  exists in iMessage).
- Multi-account batching in a single robot invocation (one mailbox per run;
  the dispatcher loops via `--account-list` if needed).
