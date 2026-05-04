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
  - id: a3f8d901c2e7                      # blake3(guid + size + attachment.ROWID)[:16]
    filename: IMG_2384.HEIC
    mime: image/heic
    size_bytes: 4321099
    sender: sydney-hayes                  # slug or "me"
    sent_at: 2026-04-04T18:43:00-05:00
    sha256: <64-hex>                      # of source binary at extract time (null if source unavailable)
    description: "Two people grilling on a balcony at sunset"  # gemini output, ≤ 100 chars; null if unsupported kind
    description_model: gemini-3-flash-preview                  # null if no extraction
    extracted_at: 2026-05-04T03:30:00Z
    source_available: true                # source binary readable at extract time
chat_message_guids_count: 142             # advisory; chat.message.guid set captured for this month
deleted_upstream: null
superseded_by: null
---
```

Field rules: attachments described, not copied (§ G). `description` may be null for audio / opaque / bundles; body falls back to filename. Reactions inline in body, not `attachments`. Full edit history deferred to v1.5. When `message.text` is null (frequent macOS 13+), parse `attributedBody` typedstream blob; empty body acceptable only when both columns null. ROWID min/max NOT stored; `chat.message.guid` is stable identity.

## E. Body format (LOCK 5)
```markdown
# Sydney Hayes — April 2026

## 2026-04-02 (Tuesday)

**09:14 — Sydney:** want to grab dinner thursday?
**09:21 — me:** yes book me
**09:22 — Sydney:** [reaction: laugh to "yes book me"]

## 2026-04-04 (Thursday)

**18:43 — Sydney:** [image: Two people grilling on a balcony at sunset]
**18:44 — me:** np
> **18:45 — Sydney (replying to "np"):** thanks
**19:02 — me:** [unsent at 19:03]
**19:05 — me (edited):** outside, table by the window
**19:30 — Sydney:** [app message: com.apple.messages.URLBalloonProvider]
```

Conventions:
- **Canonical timezone**: `America/Chicago`, applied to day-bucketing AND `HH:MM` rendering. Universal (no per-workspace override): bucketing must produce identical paths across workspaces or routing breaks. Round-3 fix (Gemini): the prior "per-workspace override" claim conflicted with single-pass render-then-route in `CONTEXT.md`. Machine-local TZ is forbidden.
- **Mac absolute time**: chat.db `date` columns are nanoseconds since 2001-01-01T00:00:00Z (pre-10.13 was seconds, detect by magnitude). Convert deterministically before bucketing.
- Day headers: `## YYYY-MM-DD (DayOfWeek)` in canonical TZ.
- Message line: `**HH:MM — sender:** <body>`. Sender is Apple Contacts display name, or `me` for outgoing.
- Reactions / tapbacks: `[reaction: <type> to "<original snippet ≤ 60 chars>"]`. Types: `love`, `like`, `dislike`, `laugh`, `emphasize`, `question`. Removed reactions are not rendered (latest state wins).
- Replies: `> **HH:MM — sender (replying to "<snippet>"):** <body>`.
- Attachments inline at sent moment: `[<kind>: <description>]` where kind is `image | video | audio | file | app`. Description is the Gemini-extracted summary from § G (≤ 100 chars). When the kind has no extracted description (audio, opaque payloads, bundles), fall back to `[<kind>: <filename>]`.
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

## G. Attachment description strategy (LOCK 7)
Raw stores **descriptions, not binaries.** Reduces disk, keeps markdown
self-contained, gives wiki queryable content without binary deref.

1. `attachment_id` = first 16 hex of `blake3(attachment.guid OR transfer_name OR filename, size_bytes_or_zero, attachment.ROWID)`. `attachment.guid` is stable identity; ROWID is `attachment` table row, NOT `message.ROWID`.
2. `sha256` of source binary at `~/Library/Messages/Attachments/<...>` if readable; null if missing or source is a bundle directory.
3. Description method by `mime` / `uti`:
   - **Image / Video** (`image/*`, `video/*`): Gemini Flash via CLI `@<path>`, ≤ 100 chars.
   - **Audio** (`audio/*`): no extraction v1 (CLI `@<path>` does not pass audio). `description: null`; body falls back to `[audio: <filename>]`. v1.5 wires audio.
   - **Bundle** (source is a directory): placeholder like `"Logic Pro project bundle"` derived from `uti`.
   - **`*.pluginpayloadattachment`** / opaque mime: `description: null`; body falls back to `[file: <filename>]`.
   - **Text-readable** (`text/*`, `application/pdf`, `application/json`): Gemini Flash 2-sentence summary, ≤ 200 chars.
4. Record `description`, `description_model` (`gemini-3-flash-preview`), `extracted_at`, `source_available`.
5. Idempotency: if a prior frontmatter row matches `sha256` AND `description_model`, REUSE the prior description; never re-extract.
6. Gemini calls are limited to attachment descriptions; routing, hashing, body, dedup remain pure Python.

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
4. Apply 3xxx removals; latest per `(target, sender, type)` by `tapback_date` wins. **Tapback events targeting messages outside the current batch (add OR remove)**: query chat.db for the target's date, compute its month bucket, and mark that bucket for re-render. This applies to both adds (cross-month new tapback) and removes (cross-month deletion of a baked-in tapback). Round-3 fix (Gemini): prior wording only flagged removes, leaving cross-month adds permanently lost.
5. Render with the **tapback row's** `HH:MM`, not the target's. If target is in a different month bucket, mark that bucket for re-render (§ H). If target is unsent / deleted, render under a `[deleted target]` placeholder.
6. Never emit tapbacks as standalone message rows.

## J. Forbidden behaviors (immutable contract)
The robot NEVER:
1. Deletes a raw file based on chat.db deletion. v1 sets `deleted_upstream` only on cursor-resync rediscovery; auto-detection of vanished rows is deferred to v1.5.
2. Modifies `chat.db`. Read-only `sqlite3` URI mode required (`?mode=ro`).
3. Runs LLM / vision calls outside the attachment-description subsystem (§ G). Routing, slug derivation, body rendering, content_hash, dedup, and cursor mutation are pure Python.
4. Edits frontmatter post-write, except `deleted_upstream` and `superseded_by`.
5. Writes outside `workspaces/<ws>/raw/imessage/...`. No `_attachments/` binary store; descriptions live in frontmatter only.
6. Skips § F's universal blocklist, even if a workspace allowlists the handle.

## K. Default for unrouted contacts
**SKIP** (privacy-first; opposite of Gmail). Contacts must be explicitly allowlisted in some workspace's `sources.yaml.imessage` block to land.

## L. Cross-references
Workflow: `CONTEXT.md`. Setup / permissions / caveats: `SETUP.md`. Routing: `route.py`. Universal envelope: `_shell/bin/check-frontmatter.py`.
