# Format: imessage (AUTHORITATIVE)

> Locked. Every iMessage file written by `ingest-imessage.py` must conform
> to this spec exactly. The 9 locks below are the contract.

## A. File granularity (LOCK 1)
One markdown file per `(contact, year-month)`. 1:1 chats live under
`individuals/<slug>/`, group chats under `groups/<slug>/`. Months with no
messages produce no file. Re-ingest of a current month rewrites in place.

## B. Path template + _profiles (LOCK 2)
```
workspaces/<ws>/raw/imessage/{individuals|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md
workspaces/<ws>/raw/imessage/_profiles/<slug>.md
```

`_profiles/<slug>.md` is the stable identity stub. Created once on first
sight, never deleted, never relocated. Schema:
```yaml
---
slug: sydney-hayes
contact_type: individual                  # individual | group
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes                # Apple Contacts name at first sight
slug_derivation: contacts_full_name       # contacts_full_name | email_local | phone_e164 | hash_fallback
chat_guid: null                           # set for groups (chat.guid from chat.db)
first_seen: 2024-08-12
aliases: []                               # prior names / handle changes
---
```

## C. Slug derivation (LOCK 3)
Priority order, applied once per contact at first sight, recorded in
`_profiles/<slug>.md`, stable forever:

1. **Apple Contacts full name** via `Contacts.framework` (PyObjC). NFKD to
   ASCII, lowercase, runs of non-`[a-z0-9]` collapsed to `-`, max 40 chars.
2. **Email local-part + domain stem**: `sydney@eclipse.audio` →
   `sydney-eclipse`. Domain stem is first label of the registrable domain.
3. **E.164 phone**: `+15125551234` → `phone-15125551234`.
4. **Hash fallback**: `unknown-<12-hex blake3 of identifier>`. 12 hex (48 bits) keeps birthday-collision risk negligible across the personal contact set; 8 was undersized.

If priorities 1 to 3 yield an empty or dash-only slug after normalization
(emoji-only contact names, all-non-ASCII handles), drop to priority 4.
Group slug: display name kebab-cased if set, else
`group-<8-hex blake3 of chat.guid>`. `chat.guid` is stable identity; member
churn does not change the slug. Contacts permission denied: fall through
2 to 4; never fail.

## D. Frontmatter (LOCK 4)
Universal envelope (REQUIRED) + iMessage-specific keys:
```yaml
---
source: imessage
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>             # of body markdown only
provider_modified_at: <ISO 8601 with TZ>  # latest message date in this month

contact_slug: sydney-hayes
contact_type: individual
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes
chat_guid: null                           # set for groups
month: 2026-04
date_range: [2026-04-02, 2026-04-29]
message_count: 142
my_message_count: 71
their_message_count: 71
attachments:
  - id: a3f8d901c2e7                      # blake3(filename + size + ROWID)[:12]
    filename: IMG_2384.HEIC
    mime: image/heic
    size_bytes: 4321099
    sender: sydney-hayes                  # slug or "me"
    sent_at: 2026-04-04T18:43:00-05:00
    sha256: <64-hex>                      # of binary content
    copied_to_raw: true                   # true | false
    attachment_path: _attachments/a3f8d901c2e7.heic   # null if not copied
    source_missing: false                 # true if iCloud-pruned or migrated
attachment_pruned: false                  # true if any attachment skipped due to copy budget
chat_message_guids_count: 142             # advisory; chat.message.guid set captured for this month
deleted_upstream: null
superseded_by: null
---
```

Field rules: attachments listed even when `copied_to_raw: false` (sha256 + size_bytes preserved for later reconciliation). Reactions live inline in the body, not in `attachments`. Full edit history deferred to v1.5. When `message.text` is null (frequent on macOS 13+), parse the `attributedBody` typedstream blob to recover text; empty body acceptable only when both columns are null. ROWID min/max intentionally NOT stored (ROWIDs reset / have gaps); `chat.message.guid` is stable identity.

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
- **Canonical timezone**: `America/Chicago` for day-bucketing and `HH:MM` rendering. Per-workspace override via `sources.yaml.imessage.timezone`. Never use machine-local TZ; that breaks dedup when the host travels.
- **Mac absolute time**: chat.db `date` columns are nanoseconds since 2001-01-01T00:00:00Z (pre-10.13 was seconds, detect by magnitude). Convert deterministically before bucketing.
- Day headers: `## YYYY-MM-DD (DayOfWeek)` in canonical TZ.
- Message line: `**HH:MM — sender:** <body>`. Sender is Apple Contacts display name, or `me` for outgoing.
- Reactions / tapbacks: `[reaction: <type> to "<original snippet ≤ 60 chars>"]`. Types: `love`, `like`, `dislike`, `laugh`, `emphasize`, `question`. Removed reactions are not rendered (latest state wins).
- Replies: `> **HH:MM — sender (replying to "<snippet>"):** <body>`.
- Attachments inline at sent moment: `[<kind>: <filename>, <size>]` where kind is `image | video | audio | file | app`. Size is human (e.g., `4.1MB`).
- App messages (Apple Cash, polls, GamePigeon, link previews): `[app message: <balloon_bundle_id>]`. Never crash, never drop.
- Edits: `**HH:MM — sender (edited):** <current text>`. Full edit history deferred to v1.5; v1 stores `is_edited: true` per-message metadata only.
- Unsents: `**HH:MM — sender:** [unsent at HH:MM]`. Preserves existence.

## F. Pre-filter (LOCK 6, deterministic, NO LLM)
Universal blocklist before render. Per-contact / per-group allowlists and
allowlist-overrides live in `sources.yaml`, not here.

Skip messages where the handle matches:
- `+1800*`, `+1888*`, `+1877*`, `+1866*`, `+1855*`, `+1844*`, `+1833*` (toll-free)
- 5-digit short codes (`24365`, `33728`, `262966`) typically OTP / 2FA
- `verify@*`, `noreply@*`, `no-reply@*`, `donotreply@*`

Skip app messages where `balloon_bundle_id` is `com.apple.messages.URLBalloonProvider` **with no text body** (standalone link previews; the preview captured once inline on the original message is preserved).

## G. Attachment copy strategy (LOCK 7)
For each attachment in a month being rendered:

1. Compute `attachment_id` = first 16 hex chars of `blake3(attachment.guid OR transfer_name OR filename, size_bytes_or_zero, attachment.ROWID)`. `attachment.guid` is the stable identity when present; ROWID is the chat.db `attachment` table row, NOT `message.ROWID`. `filename` and `size_bytes` may both be null while Messages is mid-download; record `state: downloading` in metadata and retry next run.
2. Track running per-month copy total in bytes.
3. If `running_total + size_bytes ≤ 100 MB`: copy from `~/Library/Messages/Attachments/<...>` to `raw/imessage/<individuals|groups>/<slug>/<YYYY>/_attachments/<attachment_id>.<ext>`. Set `copied_to_raw: true`, `attachment_path: _attachments/<id>.<ext>`.
4. If `running_total + size_bytes > 100 MB` (strict): skip copy. Set `copied_to_raw: false`, `attachment_path: null`. Capture `sha256` and `size_bytes` IF source readable; both may be null when source is missing. Set `attachment_pruned: true` on the month-file frontmatter.
5. If source binary missing (iCloud pruned, migration loss): `copied_to_raw: false`, `attachment_path: null`, `source_missing: true`, `sha256: null`. Log warning. Do not fail.
6. Collision guard: if `_attachments/<id>.<ext>` exists with a different sha256, log warning and skip the copy. Never overwrite.

## H. Cursor + dedup (LOCK 8)
Cursor at `_shell/cursors/imessage/<account>.txt`. Account is `local` for
chat.db. Stores TWO values, one per line:
```
last_rowid: <int>
last_message_date: <ISO 8601>
```

Sanity check on every run, in order:
1. `SELECT date FROM message WHERE ROWID = <last_rowid>`.
2. If row exists AND date matches `last_message_date` (within 60s): ROWID path. Fast.
3. If row missing OR date mismatch: ROWID was reset / reused (migration, rebuild). Fall back to date path (`SELECT ... WHERE date > last_message_date`). Log warning.
4. After successful run, advance both values atomically (fsync temp + parent dir before rename).

Incremental scan also captures **mutations to past months**, not just new rows: tapback rows whose `associated_message_guid` targets a message older than the cursor, edited rows with `date_edited > last_message_date`, and unsent rows. Mark every `(contact_slug, YYYY-MM)` bucket touched by such mutations for re-render this run; otherwise past months go stale.

Dedup ledger: `workspaces/<ws>/_meta/ingested.jsonl`. Key:
`imessage:<contact_type>:<contact_slug>:<YYYY-MM>` where `contact_type ∈ {individual, group}`. The contact_type prefix prevents individual / group slug collisions.

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | n/a | write file, append ledger row |
| present | matches | no-op (silent skip) |
| present | mismatches | overwrite file, append a NEW ledger row |

## I. Tapback resolution
Tapbacks are separate `message` rows where `associated_message_type` is in
`2000..2005` (add: love, like, dislike, laugh, emphasize, question) or
`3000..3005` (remove). `associated_message_guid` points at the target.

The renderer must:
1. Filter all tapback rows out of the main message stream.
2. Strip prefix from `associated_message_guid`: `p:0/`, `bp:`, `p:<n>/`. Target's own `message.guid` does not carry this prefix.
3. Build map `stripped_target_guid -> list[(type, sender, tapback_date, removed?)]`.
4. Apply 3xxx removals; latest per `(target, sender, type)` by `tapback_date` wins. **Removal-without-prior-add in the current batch**: query chat.db for the target's date, mark its month bucket for re-render (the prior add is baked into the existing markdown).
5. Render with the **tapback row's** `HH:MM`, not the target's. If target is in a different month bucket, mark that bucket for re-render (§ H). If target is unsent / deleted, render under a `[deleted target]` placeholder.
6. Never emit tapbacks as standalone message rows.

## J. Forbidden behaviors (immutable contract)
The robot NEVER:
1. Deletes a raw file based on chat.db deletion. v1 sets `deleted_upstream` only on cursor-resync rediscovery; auto-detection of vanished rows is deferred to v1.5.
2. Modifies `chat.db`. Read-only `sqlite3` URI mode required (`?mode=ro`).
3. Runs LLM or vision calls during ingest. Pure Python only.
4. Edits frontmatter post-write, except `deleted_upstream` and `superseded_by`.
5. Writes outside `workspaces/<ws>/raw/imessage/...` and the `_attachments/` path under it.
6. Overwrites an existing `_attachments/<id>.<ext>` whose sha256 differs.
7. Skips § F's universal blocklist, even if a workspace allowlists the handle.

## K. Default for unrouted contacts
**SKIP** (privacy-first; opposite of Gmail). Contacts must be explicitly allowlisted in some workspace's `sources.yaml.imessage` block to land.

## L. Cross-references
Workflow: `CONTEXT.md`. Setup / permissions / caveats: `SETUP.md`. Routing: `route.py`. Universal envelope: `_shell/bin/check-frontmatter.py`.
