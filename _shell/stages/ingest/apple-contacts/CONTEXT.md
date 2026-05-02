# Stage: ingest-apple-contacts (SPECIAL — direct to global)

## Why this is different

Apple Contacts is reference data, not a stream. It does NOT land in `workspaces/<ws>/raw/`. Instead, it upserts canonical entity stubs at `_global/entities/people/<slug>.md`.

The actual implementation lives in the **contacts-sync skill** at `_shell/skills/contacts-sync/`. This stage directory exists for shape-consistency with other sources and for documentation; the schedule skill emits a global cron that calls the contacts-sync skill, not a per-(account,source) ingest plist.

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Apple Contacts via AppleScript | `osascript` to `Contacts.app` | Source of truth |
| Per-skill scripts | `_shell/skills/contacts-sync/scripts/sync.py` | Implementation |
| Global cron | `_shell/config/global-schedule.yaml` (`apple_contacts_sync`) | Cadence (nightly 03:00) |

## Process
See the contacts-sync skill. Summary:
1. Query `Contacts.app` via AppleScript.
2. For each contact: derive a stable slug (full name → email local-part → phone → hash); upsert `_global/entities/people/<slug>.md` with frontmatter overwritten and body preserved.
3. Log summary: created / updated / unchanged / conflicts.

## Outputs
- `_global/entities/people/<slug>.md` (one file per contact).
- Log entry in `_logs/apple-contacts-sync.out.log`.

## Idempotency
Yes. Re-running an unchanged Contacts DB produces no writes.

## NOT
- No `workspaces/<ws>/raw/apple-contacts/` files.
- No `ingested.jsonl` rows. Apple Contacts has its own implicit ledger via the slug → file mapping in `_global/entities/people/`.
