# Format: gmail (AUTHORITATIVE)

> The single source of truth for how Gmail becomes raw markdown. Locked
> in the format-lock session. Routing decisions live in `sources.yaml`;
> this file controls everything else. Re-locking requires explicit
> session intent.

## Lock 1 — Path template

```
workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<filename>
```

**`<account-slug>`** — deterministic from the email. Lowercase. Take
local-part + first domain segment. Replace any non-`[a-z0-9]` run with a
single `-`. Strip leading / trailing `-`. ASCII only.

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@synps.xyz` | `adithya-synps` |
| `adithya@eclipse.builders` | `adithya-eclipse` |
| `adithya.shak.kumar@gmail.com` | `adithya-shak-kumar-gmail` |

**`<YYYY>/<MM>`** — year + zero-padded month of the **first message in the
thread**. Stable forever; new replies don't relocate the file.

**`<filename>`** — `<date>__<subject-slug>__<threadid8>.md`.
- `<date>` is `YYYY-MM-DD` of the first message.
- `<subject-slug>` derives from the original subject:
  1. Strip prefixes (case-insensitive, repeat to fixed point):
     `Re:`, `Fwd:`, `Fw:`, `FW:`, `AW:`, `RES:`, `TR:`,
     `[External]`, `[EXT]`, `[CONFIDENTIAL]`, `[SPAM]`, `AUTO:`.
  2. NFKD-normalize → ASCII (drop non-ASCII).
  3. Replace runs of non-`[a-zA-Z0-9]` with `-`. Lowercase. Strip
     leading / trailing `-`.
  4. Truncate to 60 chars; strip trailing `-`. Empty → `no-subject`.
- `<threadid8>` is the first 8 chars of Gmail `thread_id`.

**Idempotency**: path is deterministic from `(account_slug, thread_id,
first-message-date, subject)`. Re-ingesting the same thread overwrites
the same file. The robot never moves files.

## Lock 2 — Universal frontmatter envelope (REQUIRED)

```yaml
source: gmail
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body markdown only (post-frontmatter)
provider_modified_at: <ISO 8601 with TZ>   # internalDate of last message
```

`content_hash` is computed over the body markdown ONLY. Same body bytes ⇒
same hash regardless of ingest time. This is the dedup signal.

## Lock 3 — Gmail-specific frontmatter

```yaml
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
thread_id: 17abc123def4567
message_ids:
  - <CABx@mail.gmail.com>
subject: "Q3 deck review"              # original; prefixes preserved
participants:
  - { name: "Sydney Hayes", email: "sydney@eclipse.audio", roles: [from, to] }
labels: [INBOX, "Eclipse/Investors"]
first_message: 2026-04-15T14:23:00-05:00
last_message: 2026-04-22T09:11:00-05:00
message_count: 7
attachments:
  - id: a3f8d9
    filename: "deck-v3.pdf"
    size_bytes: 1234567
    mime: application/pdf
    message_index: 0                   # 0-based index into messages[]
routed_by:
  - { workspace: eclipse, rule: "label:Eclipse" }
  - { workspace: personal, rule: "<match-all>" }
deleted_upstream: null                 # ISO 8601 if history.list reports messageDeleted
```

Field rules:
- `participants[].roles` ⊆ `{from, to, cc, bcc}`. Same address across
  multiple roles collapses to one entry; roles unioned.
- `labels` mirrors Gmail's `labelIds` exactly.
- `attachments[].id` is the first 8 chars of Gmail's `attachmentId`.
- `attachments[].message_index` is required.
- `routed_by` lists every workspace this thread was routed to and the
  rule that fired. The same list appears in every workspace copy.
- `deleted_upstream` is the ONLY frontmatter field the robot may modify
  post-write (besides `labels` on `labelAdded` / `labelRemoved` events).

## Lock 4 — Body format

```markdown
# <Original subject (prefixes preserved)>

## YYYY-MM-DD HH:MM TZ — <Sender Name> <sender@email>

<plain markdown body>

### Attachment: <filename>
<extracted text or "Binary attachment, content not extracted.">

## YYYY-MM-DD HH:MM TZ — <Next sender>
<next message body>
```

Rules:
1. Messages chronological (`internalDate` ascending).
2. HTML→markdown via `html2text`. Prefer `text/plain` when both parts exist.
3. Quoted-history removal: drop everything from the first `^On <date> .*
   wrote:$` line; trim trailing `>`-prefixed blockquote lines.
4. Signature stripping: cut at first canonical `^-- ?$` delimiter
   (RFC 3676). NO heuristic stripping. If no delimiter, keep everything.
5. Inline images: reference as `[image: <filename>]`; metadata only.
6. PDF attachments < 10 MB: extract text via `pdftotext` (preferred) or
   `markitdown`, append as `### Attachment: <filename>`.
7. Larger / non-text attachments: metadata in frontmatter only; body
   says `Binary attachment, content not extracted.`
8. **No LLM calls.** All conversion is deterministic.

## Lock 5 — Pre-filter (deterministic, NO LLM)

Skip the entire thread if any of:

- **Size** > 25 MB (sum of attachment + body bytes across all messages).
- **First-message subject** matches
  `/^(out of office|automatic reply|undeliverable|delivery (status )?notification)/i`.
- **All senders blocklisted** — every message's `From:` matches the
  universal blocklist (case-insensitive):
  - `noreply@*`, `no-reply@*`, `*-noreply@*`, `donotreply@*`
  - `mailer-daemon@*`, `postmaster@*`
  - `calendar-notification@google.com`, `*@calendar.google.com`
  - `*@bounces.amazonses.com`, `*@accounts.google.com`
- **Labels** — every label on the thread is in `{SPAM, TRASH}`.
- **MIME outside allowlist**: thread-skip only if EVERY attachment is
  outside `{text/plain, text/html, application/pdf, image/*,
  multipart/*}`. Mixed threads with one bad attachment get a
  per-attachment warning, not a thread skip.
- **Calendar-invite-only**: thread has attachments and every attachment
  is `.ics` (text/calendar).

This blocklist is universal. Per-account exclusions belong in
`sources.yaml`'s `api_query.exclude`.

## Lock 6 — Dedup

Key: `gmail:<thread_id>`. Per-workspace ledger at
`workspaces/<ws>/_meta/ingested.jsonl`, one JSON line per ingest:

```json
{"source":"gmail","key":"gmail:17abc...","content_hash":"blake3:...","raw_path":"raw/gmail/...","ingested_at":"...","run_id":"..."}
```

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | — | write file, append ledger row |
| present | matches | no-op (silent skip, log line) |
| present | mismatches | overwrite file, append a NEW ledger row (ledger is append-only) |

## Lock 7 — Cursor + robot CLI

**Cursor file**: `_shell/cursors/gmail/<account-slug>.txt`. Stores the
last seen Gmail `historyId` (decimal integer, written as text).

**First run** (cursor missing or empty):
1. `users.messages.list(q=<union>)` bounded by
   `GMAIL_INITIAL_LOOKBACK_DAYS` env var (default 365) via an `after:`
   clause.
2. Dedupe results to threads; fetch each via
   `users.threads.get(format='full')`.
3. After successful processing, persist `historyId` from
   `users.getProfile()`.

**Subsequent runs** (cursor present):
1. `users.history.list(startHistoryId=<cursor>,
   historyTypes=[messageAdded, messageDeleted, labelAdded,
   labelRemoved])`.
2. Per event:
   - `messageAdded` — fetch thread, normal pipeline.
   - `messageDeleted` — locate existing raw file by `thread_id`, set
     `deleted_upstream` in frontmatter, rewrite. Don't delete the file.
   - `labelAdded` / `labelRemoved` — re-evaluate routing. Update
     `labels` on existing copies; new matches → write to new
     workspaces. Existing copies stay even if no longer matching.
3. Advance cursor to `users.getProfile().historyId` ONLY after the
   write phase succeeds. Mid-batch failure leaves the cursor at its
   previous value; the next run replays.

**Robot CLI**:

```
ingest-gmail.py
  --account <email>           required; e.g. adithya@outerscope.xyz
  [--workspaces <a,b,c>]      subset; default = every subscribing workspace
  [--dry-run]                 fetch + render but write nothing; cursor untouched
  [--show]                    in dry-run, print full content to stdout
  [--max-items <int>]         hard cap on threads processed
  [--reset-cursor]            delete cursor; rebuild from lookback window
  [--run-id <id>]             tag for ledger / log lines
```

**flock** at `/tmp/com.adithya.ultron.ingest-gmail-<account-slug>.lock`.
Concurrent invocation for the same account exits 0 silently.

## Forbidden behaviors (immutable contract)

The robot **NEVER**:
1. Deletes a raw file based on Gmail-side deletion. `messageDeleted`
   events set `deleted_upstream`; the file persists.
2. Moves files between paths. Path is fixed at write time. Mid-thread
   subject changes don't relocate the file.
3. Runs LLM / vision calls during ingest. PDF text via `pdftotext` /
   `markitdown` is fine; everything else is metadata-only.
4. Edits frontmatter post-write, except `deleted_upstream` and `labels`
   (the latter only on `labelAdded` / `labelRemoved`).
5. Writes outside `workspaces/<ws>/raw/gmail/<account-slug>/...`.
   Ledger / log appends happen in the dispatcher, not the rendering loop.
6. Skips the universal blocklist (Lock 5), even if a workspace's
   `api_query.include` would otherwise pull a blocklisted sender.

## Cross-references

- Workflow contract: `CONTEXT.md` (this directory).
- sources.yaml schema: `sources-schema.md`.
- Operator runbook: `_shell/docs/runbook-gmail.md`.
- Credentials inventory: `_credentials/INVENTORY.md`.
