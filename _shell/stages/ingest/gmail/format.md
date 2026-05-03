# Format: gmail (AUTHORITATIVE)

> This document is the data spec for Gmail ingest. Every Gmail file written
> by `_shell/bin/ingest-gmail.py` must conform to this spec exactly. Locked
> in Phase 3 RESET §2.

## A. File granularity

One markdown file per email **thread** (Gmail's `thread_id`). Not per message.

A thread can grow when new replies arrive; the file is regenerated in place
with the longer body. The file path never changes.

## B. Path template

```
workspaces/<ws>/raw/gmail/<mailbox-slug>/<YYYY>/<MM>/<filename>
```

### `<ws>`
Workspace slug. The robot writes one copy per destination workspace returned
by `route.py`; the same thread can appear in multiple workspaces with
identical content (each copy is a hardlink-equivalent independent file).

### `<mailbox-slug>`
Deterministic from the email address:

1. Lowercase the address.
2. Take the local-part + first domain segment.
3. Replace any non-`[a-z0-9-]` character with `-`.
4. Strip leading/trailing `-`.

Examples:

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@synps.xyz` | `adithya-synps` |
| `adithya@eclipse.builders` | `adithya-eclipse` |
| `adithya.shak.kumar@gmail.com` | `adithya-shak-kumar-gmail` |

### `<YYYY>/<MM>`
Year and zero-padded month of the **first message in the thread**. Stable
across re-ingest even when new replies arrive.

### `<filename>`
```
<date>__<subject-slug>__<threadid8>.md
```

- **`<date>`** — `YYYY-MM-DD` of the first message in the thread.
- **`<subject-slug>`** — derived from the original subject:
  1. Strip prefixes (case-insensitive, repeat until stable):
     `Re:`, `Fwd:`, `Fw:`, `FW:`, `AW:`, `[External]`, `[EXT]`,
     `[CONFIDENTIAL]`, `[SPAM]`, `AUTO:`.
  2. Normalize Unicode → ASCII (NFKD + ascii encode, ignore non-ASCII).
  3. Replace runs of non-`[a-zA-Z0-9]` with `-`.
  4. Lowercase, strip leading/trailing `-`.
  5. Truncate to 60 chars, strip trailing `-`.
  6. Empty result → `no-subject`.
- **`<threadid8>`** — first 8 chars of the Gmail `thread_id`. Provides
  uniqueness when two threads have the same date + subject.

### Idempotency rule
The path is **completely deterministic** from `(mailbox_slug, thread_id,
first-message-date, subject)`. Re-ingesting the same thread always overwrites
the same file. New replies extending a thread regenerate the same file with
the longer body. The robot never moves a file once written.

## C. Universal frontmatter envelope (REQUIRED on every Gmail file)

```yaml
source: gmail
workspace: <ws-slug>            # which workspace's raw/ this copy lives in
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>   # of body markdown only (post-fm)
provider_modified_at: <ISO 8601 with TZ>   # internalDate of last message
```

`content_hash` is computed over the body markdown ONLY (everything below the
closing `---` of the frontmatter). Same body bytes ⇒ same hash, regardless of
ingest time. This is the dedup signal.

## D. Gmail-specific frontmatter (layered on top)

```yaml
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
thread_id: 17abc123def4567
message_ids:
  - <CABx@mail.gmail.com>
  - <CABy@mail.gmail.com>
subject: "Q3 deck review"           # original, prefixes preserved
participants:
  - { name: "Sydney Hayes", email: "sydney@eclipse.audio", roles: [from, to] }
  - { name: "Adithya", email: "adithya@outerscope.xyz", roles: [from, to, cc] }
labels: [INBOX, "Eclipse/Investors"]
first_message: 2026-04-15T14:23:00-05:00
last_message: 2026-04-22T09:11:00-05:00
message_count: 7

# Attachments — metadata only at ingest time.
attachments:
  - id: a3f8d9
    filename: "deck-v3.pdf"
    size_bytes: 1234567
    mime: application/pdf
    message_index: 0           # 0-based index into messages[] (which message this attachment came from)

# Routing provenance — populated by route.py
routed_by:
  - "eclipse:label:Eclipse"            # workspace:rule-id-or-fingerprint
  - "personal:rules.match[0]"

# Lifecycle (set when applicable, otherwise null/omitted)
deleted_upstream: null               # ISO 8601 if Gmail history.list reports messageDeleted
superseded_by: null                  # full path if a follow-up thread merges into this one
```

Field rules:

- `participants[].roles` is a list. Allowed values: `from`, `to`, `cc`, `bcc`.
- Same email appearing in multiple roles across messages collapses to one
  entry with the union of roles.
- `labels` mirrors Gmail's `labelIds` exactly (system labels stay uppercase;
  user labels keep their case).
- `attachments[].id` is the first 8 chars of Gmail's `attachmentId`.
- `attachments[].message_index` is required and points at the 0-based
  message in `messages[]` (NOT a Gmail UID).
- `routed_by` is a list of strings; each entry is `<destination-workspace>:<rule-marker>`
  where `<rule-marker>` describes which rule fired. Helpful for debugging
  fork routing.
- `deleted_upstream` is the ONLY frontmatter field the robot is allowed to
  modify after the initial write (see §H).

## E. Body format

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

1. **Order**: messages in chronological order (`internalDate` ascending).
2. **HTML→markdown**: stripped via `html2text` first; if no `text/html`
   either, fall back to the `text/plain` part. Prefer `text/plain` when
   both exist.
3. **Quoted history removal**: drop everything from the first
   `^On <date> .* wrote:$` line in a reply (and trailing `>`-prefixed
   blockquote lines). Prior messages already appear above; don't duplicate.
4. **Signature stripping**: cut at the first `^-- ?$` delimiter. If absent,
   strip a trailing block (>10 consecutive lines) matching legal-disclaimer
   patterns (`This email and any attachments...`, `CONFIDENTIALITY NOTICE`,
   `IRS Circular 230`, etc.). Conservative — leave noise rather than strip
   signal.
5. **Inline images**: reference as `[image: <filename>]` inline; do NOT
   extract image content. Metadata flows to the `attachments` frontmatter
   field.
6. **PDF attachments < 10 MB**: extract text via `pdftotext` (preferred) or
   `markitdown`. Append as `### Attachment: <filename>` section after the
   message body.
7. **Larger / non-text attachments**: metadata only; body says
   `Binary attachment, content not extracted.`
8. **No LLM calls** at any step. PDF text extraction is deterministic
   (pdftotext / markitdown). Vision extraction is explicitly out of scope.

## F. Pre-filter (deterministic, NO LLM)

Skip the entire thread if **any** of:

- **Size**: total thread size > 25 MB (sum of attachment sizes + body bytes
  across all messages).
- **Subject** matches `/^(out of office|automatic reply|undeliverable|delivery (status )?notification)\b/i` on the FIRST message.
- **Senders all blocklisted**: every message in the thread has a `From:`
  whose address matches the universal blocklist (case-insensitive):
  - `noreply@*`, `no-reply@*`, `*-noreply@*`, `donotreply@*`
  - `mailer-daemon@*`
  - `postmaster@*`
  - `calendar-notification@google.com`, `*@calendar.google.com`
  - `*@bounces.amazonses.com`, `*@accounts.google.com`
- **Labels** `SPAM` or `TRASH` present on any message. (`DRAFT` is
  preserved.)
- **MIME outside allowlist**: every part outside
  `{text/plain, text/html, application/pdf, image/*, multipart/*}` causes
  a per-message warning, but only triggers a thread-level skip if EVERY
  attachment is outside the allowlist.
- **Calendar-invite-only**: every attachment is a `.ics` (text/calendar)
  file → skip.

This blocklist is universal across mailboxes. Per-mailbox or per-workspace
exclusions belong in `sources.yaml`'s `api_query.exclude` block, not here.

## G. Dedup key

`gmail:<thread_id>`

Per-workspace ledger at `workspaces/<ws>/_meta/ingested.jsonl`, one JSON line
per ingest:

```json
{"source":"gmail","key":"gmail:17abc...","content_hash":"blake3:...","raw_path":"raw/gmail/adithya-outerscope/2026/04/...","ingested_at":"...","run_id":"..."}
```

Re-ingest behavior:

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | n/a | write file, append ledger row |
| present | matches | no-op (skip silently, log line) |
| present | mismatches | overwrite file, append NEW ledger row (don't mutate old rows; ledger is append-only audit trail) |

## H. Forbidden behaviors (immutable contract)

The robot **NEVER**:

1. **Deletes a raw file** based on Gmail-side deletion. When
   `users.history.list` reports `messageDeleted` for a thread we have on
   disk, the robot opens the existing file, sets
   `deleted_upstream: <ISO 8601>` in the frontmatter, and rewrites. The
   file persists.
2. **Moves files between paths.** Path is deterministic from immutable
   thread metadata (`mailbox_slug`, `thread_id`, first-message-date,
   subject). If subject changes (Gmail allows mid-thread subject edits),
   the path stays at its original value.
3. **Runs LLM / vision calls during ingest.** All conversion is
   deterministic. PDF text extraction uses `pdftotext` or `markitdown`.
   Vision-based attachment extraction is out of scope for this phase.
4. **Edits frontmatter after the initial write**, except for
   `deleted_upstream` marking (above) and `superseded_by` linking. Every
   other re-ingest produces an entirely fresh file.
5. **Writes outside `workspaces/<ws>/raw/gmail/<mailbox-slug>/...`.** No
   side files. No `_meta/` writes from inside the rendering loop —
   ledger / log appends happen in the dispatcher's outer loop only.
6. **Skips the universal blocklist** under any circumstance, even if a
   workspace's `api_query.include` would otherwise pull a blocklisted
   sender.

## I. Cross-references

- Workflow contract: `_shell/stages/ingest/gmail/CONTEXT.md`.
- sources.yaml schema: `_shell/stages/ingest/gmail/sources-schema.md`
  (locked in §3).
- Operator runbook: `_shell/docs/runbook-gmail.md` (written in §9).
- Credential layout: `_shell/docs/credentials-gmail.md` (written in §9).
