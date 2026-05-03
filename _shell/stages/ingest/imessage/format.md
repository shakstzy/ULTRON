# Format: imessage (AUTHORITATIVE)

> Locked. Every iMessage file written by `ingest-imessage.py` must conform to
> this spec exactly. The 9 locks below are the contract.

## A. File granularity (LOCK 1)
One markdown file per `(contact, year-month)`. 1:1 chats live under
`individuals/<slug>/`, group chats under `groups/<slug>/`. Months with no
messages produce no file. Re-ingest of a current month rewrites that file
in place.

## B. Path template + _profiles (LOCK 2)
```
workspaces/<ws>/raw/imessage/{individuals|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md
workspaces/<ws>/raw/imessage/_profiles/<slug>.md
```

`_profiles/<slug>.md` is the stable identity stub for the contact or group.
Created once on first sight, never deleted, never relocated. New handles
append to its `contact_handles` list. Schema:

```yaml
---
slug: sydney-hayes
contact_type: individual                       # individual | group
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes                     # Apple Contacts name at first sight
slug_derivation: contacts_full_name            # contacts_full_name | email_local | phone_e164 | hash_fallback
chat_guid: null                                # set for groups (chat.guid from chat.db)
first_seen: 2024-08-12
aliases: []                                    # prior names / handle changes
---
```

## C. Slug derivation (LOCK 3)
Priority order, applied once per contact at first sight, recorded in
`_profiles/<slug>.md`, stable forever:

1. **Apple Contacts full name** via `Contacts.framework` (PyObjC). NFKD to
   ASCII, lowercase, runs of non-`[a-z0-9]` collapsed to `-`, max 40 chars.
2. **Email local-part + domain stem**: `sydney@eclipse.audio` becomes
   `sydney-eclipse`. Domain stem is the first label of the registrable
   domain.
3. **E.164 phone**: `+15125551234` becomes `phone-15125551234`.
4. **Hash fallback**: `unknown-<8-hex blake3 of identifier>`.

Group slug: group display name if set (kebab-case), else
`group-<8-hex blake3 of chat.guid>`. `chat.guid` is the stable identity for
groups; member churn does not change the slug.

If Apple Contacts permission is denied, fall back through priorities 2 to 4.
Do not fail.

## D. Frontmatter (LOCK 4)

Universal envelope (REQUIRED):
```yaml
source: imessage
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>                  # of body markdown only
provider_modified_at: <ISO 8601 with TZ>       # latest message date in this month
```

iMessage-specific:
```yaml
contact_slug: sydney-hayes
contact_type: individual                       # individual | group
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes
chat_guid: null                                # set for groups
month: 2026-04
date_range: [2026-04-02, 2026-04-29]
message_count: 142
my_message_count: 71
their_message_count: 71
attachments:
  - id: a3f8d901c2e7                           # blake3(filename + size + ROWID)[:12]
    filename: IMG_2384.HEIC
    mime: image/heic
    size_bytes: 4321099
    sender: sydney-hayes                       # slug or "me"
    sent_at: 2026-04-04T18:43:00-05:00
    sha256: <64-hex>                           # of binary content
    copied_to_raw: true                        # true | false
    attachment_path: _attachments/a3f8d901c2e7.heic   # relative; null if not copied
    source_missing: false                      # true if iCloud-pruned or migrated
attachment_pruned: false                       # true if any attachment skipped due to copy budget
chat_db_message_ids: { min: 12483, max: 13901 }
deleted_upstream: null                         # ISO 8601 if message rows vanish
superseded_by: null
```

Field rules:
- `chat_db_message_ids` lets the renderer rebuild only this month deterministically.
- Attachments are listed even when `copied_to_raw: false`. Hash and size are always captured so a future copy pass can verify identity.
- Reactions are NOT listed in `attachments`. They live inline in the body.
- Edit history beyond the current text is deferred to v1.5 (see SETUP.md).

## E. Body format (LOCK 5)

```markdown
# Sydney Hayes — April 2026

## 2026-04-02 (Tuesday)

**09:14 — Sydney:** want to grab dinner thursday?
**09:21 — me:** yes book me
**09:22 — Sydney:** [reaction: laugh to "yes book me"]

## 2026-04-04 (Thursday)

**18:43 — Sydney:** [image: IMG_2384.HEIC, 4.1MB]
**18:44 — me:** np
> **18:45 — Sydney (replying to "np"):** thanks
**19:02 — me:** [unsent at 19:03]
**19:05 — me (edited):** outside, table by the window
**19:30 — Sydney:** [app message: com.apple.messages.URLBalloonProvider]
```

Conventions:
- Day headers: `## YYYY-MM-DD (DayOfWeek)`. Local TZ of message timestamps.
- Message line: `**HH:MM — sender:** <body>`. Sender is Apple Contacts
  display name, or `me` for outgoing.
- Reactions / tapbacks: `[reaction: <type> to "<original snippet ≤ 60 chars>"]`.
  Types: `love`, `like`, `dislike`, `laugh`, `emphasize`, `question`.
  Removed reactions are not rendered (latest state wins).
- Replies: `> **HH:MM — sender (replying to "<snippet>"):** <body>`.
- Attachments inline at sent moment: `[<kind>: <filename>, <size>]` where
  kind is `image | video | audio | file | app`. Size is human (e.g., `4.1MB`).
- App messages (Apple Cash, polls, GamePigeon, link previews):
  `[app message: <balloon_bundle_id>]`. Never crash, never drop.
- Edits: `**HH:MM — sender (edited):** <current text>`. Full edit history
  deferred to v1.5; v1 stores `is_edited: true` per-attachment-or-message
  metadata only.
- Unsents: `**HH:MM — sender:** [unsent at HH:MM]`. Preserves existence.

## F. Pre-filter (LOCK 6, deterministic, NO LLM)
Universal blocklist applied before render. Per-contact allowlists are a
routing concern, not a format concern.

Skip messages where the handle matches:
- `+1800*`, `+1888*`, `+1877*`, `+1866*`, `+1855*`, `+1844*`, `+1833*` (toll-free)
- 5-digit short codes (e.g., `24365`, `33728`, `262966`) typically used for OTP / 2FA
- `verify@*`, `noreply@*`, `no-reply@*`, `donotreply@*`

Skip app messages where `balloon_bundle_id` is in:
- `com.apple.messages.URLBalloonProvider` **with no text body** (link
  previews captured once inline; standalone preview rows are dropped).

Group-chat skip lists (e.g., "Pickup Soccer") live in `sources.yaml`, not
here. Format-level pre-filter is universal blocklist only.

## G. Attachment copy strategy (LOCK 7)
For each attachment in a month being rendered:

1. Compute `attachment_id` = first 12 hex chars of
   `blake3(filename + size_bytes + ROWID)`.
2. Track running per-month copy total.
3. If running total + attachment size < 100 MB:
   - Copy from `~/Library/Messages/Attachments/<...>` to
     `raw/imessage/<individuals|groups>/<slug>/<YYYY>/_attachments/<attachment_id>.<ext>`.
   - Set `copied_to_raw: true`, `attachment_path: _attachments/<id>.<ext>`.
4. If running total >= 100 MB:
   - Skip copy. Set `copied_to_raw: false`, `attachment_path: null`.
   - Capture `sha256` and `size_bytes` for later reconciliation.
   - Set `attachment_pruned: true` on the month-file frontmatter.
5. If source binary is missing (iCloud pruned, migration loss):
   - Set `copied_to_raw: false`, `attachment_path: null`, `source_missing: true`.
   - Log warning. Do not fail the run.
6. Collision guard: if `_attachments/<id>.<ext>` already exists with a
   different `sha256`, log warning and skip the copy. Never overwrite.

## H. Cursor + dedup (LOCK 8)
Cursor at `_shell/cursors/imessage/<account>.txt`. Account is `local` for
chat.db (only source today). Cursor stores TWO values, one per line:
```
last_rowid: <int>
last_message_date: <ISO 8601>
```

Sanity check on every run, in order:
1. `SELECT date FROM message WHERE ROWID = <last_rowid>`.
2. If row exists AND date matches `last_message_date`: use ROWID path
   (`SELECT ... WHERE ROWID > last_rowid`). Fast path.
3. If row missing OR date mismatch: ROWID was reset by Messages reset,
   migration, or rebuild. Fall back to date path
   (`SELECT ... WHERE date > last_message_date`). Log a warning.
4. After successful run, advance both values atomically.

Dedup ledger: `workspaces/<ws>/_meta/ingested.jsonl`. One row per write:
```json
{"source":"imessage","key":"imessage:<contact_slug>:<YYYY-MM>","content_hash":"blake3:...","raw_path":"raw/imessage/...","ingested_at":"...","run_id":"..."}
```

Dedup key: `imessage:<contact_slug>:<YYYY-MM>`. Per-month, not per-message.

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | n/a | write file, append ledger row |
| present | matches | no-op (silent skip) |
| present | mismatches | overwrite file, append a NEW ledger row |

## I. Tapback resolution (deterministic logic)
Tapbacks are separate `message` rows where `associated_message_type` is in
`2000..2005` (add: love, like, dislike, laugh, emphasize, question) or
`3000..3005` (remove). `associated_message_guid` points at the target message.

The renderer must:
1. Filter all tapback rows out of the main message stream.
2. Build a map `target_guid -> list[(type, sender, removed?)]`.
3. Apply 3xxx removals (latest tapback per (target, sender, type) wins).
4. Attach surviving tapbacks inline on the line below their target message
   per § E.
5. Never emit tapbacks as standalone message rows.

## J. Forbidden behaviors (immutable contract)
The robot NEVER:
1. Deletes a raw file based on chat.db deletion. Vanished message rows set
   `deleted_upstream` on the existing month file; the file persists.
2. Modifies `chat.db`. Read-only `sqlite3` URI mode required (`?mode=ro`).
3. Runs LLM or vision calls during ingest. Pure Python only.
4. Edits frontmatter post-write, except `deleted_upstream` and
   `superseded_by`.
5. Writes outside `workspaces/<ws>/raw/imessage/...` and the deterministic
   `_attachments/` path under it.
6. Overwrites an existing `_attachments/<id>.<ext>` whose sha256 differs.
7. Skips § F's universal blocklist, even if a workspace allowlists the
   handle in `sources.yaml`.

## K. Default for unrouted contacts
**SKIP** (privacy-first; opposite of Gmail). A contact must be explicitly
allowlisted in some workspace's `sources.yaml.imessage` block to land.

## L. Cross-references
- Workflow: `CONTEXT.md`.
- Setup / permissions / caveats: `SETUP.md`.
- Routing: `route.py` (allowlist, default skip).
- Universal envelope check: `_shell/bin/check-frontmatter.py`.
