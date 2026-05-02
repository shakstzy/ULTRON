# Stage: ingest-imessage

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace imessage subscriptions | `workspaces/*/config/sources.yaml` (imessage block) | Contact / group allowlist + routing |
| Format spec | `_shell/stages/ingest/imessage/format.md` | Output shape |
| Cursor | `_shell/cursors/imessage/local.txt` | Latest `chat.db` ROWID processed |
| Source DB | `~/Library/Messages/chat.db` | Local SQLite |
| Global routing config | `_shell/config/imessage-routing.yaml` | Skip lists, conflict policy, unrouted default |
| Dedup ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup |

## Permissions
Reading `chat.db` requires Full Disk Access for the process running the ingest. Grant in System Settings > Privacy & Security > Full Disk Access. Add `/bin/bash` (or whatever launchd spawns) for unattended runs. The robot MUST exit cleanly with an actionable message if it cannot read the DB.

## Process
1. Open `chat.db` read-only via Python `sqlite3`.
2. Read cursor: latest ROWID processed last run. First run uses ROWID = 0 (full backfill).
3. SELECT messages with `ROWID > cursor`. Join `chat`, `handle`, `attachment`, `chat_message_join`, `message_attachment_join` for context.
4. Group rows by (`contact_slug`, `YYYY-MM`):
   - Contact slug is derived once per handle and persisted to `workspaces/<ws>/raw/imessage/_profiles/<slug>.md` (the `_profile.md` companion is created on first sight).
5. For each (contact, month) batch:
   a. Apply pre-filter per `format.md` (skip handles, skip groups).
   b. Render markdown per `format.md`.
   c. Compute content_hash.
   d. Call `route(item, workspaces_config)`.
   e. Write to each destination `workspaces/<ws>/raw/imessage/{individuals|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md`.
   f. Append to ledgers.
6. Advance cursor to the max ROWID seen.

## Output structure
```
raw/imessage/
├── _profiles/
│   ├── sydney-hayes.md          # slug derivation history + identifiers (stable forever)
│   └── ...
├── individuals/
│   ├── sydney-hayes/2026/2026-04__sydney-hayes.md
│   └── ...
└── groups/
    ├── eclipse-founders/2026/2026-04__eclipse-founders.md
    └── ...
```

## Idempotency
Re-running with the same cursor produces no writes. Re-running after the cursor advanced overwrites month files with longer transcripts (deterministic path).

## Status
Skeleton. The robot at `_shell/bin/ingest-imessage.py` is foundation-only — it parses arguments and exits cleanly with "not yet wired" until Adithya enables it. See `format.md` for the full spec.
