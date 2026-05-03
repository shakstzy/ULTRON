# Format: gmail (AUTHORITATIVE)

> Locked in Phase 3 RESET §2. Every Gmail file written by `ingest-gmail.py`
> must conform to this spec exactly.

## A. File granularity
One markdown file per email **thread** (Gmail `thread_id`). New replies grow the file in place; the path never changes.

## B. Path template
```
workspaces/<ws>/raw/gmail/<mailbox-slug>/<YYYY>/<MM>/<filename>
```

**`<ws>`** — workspace slug. Same thread can appear in multiple workspaces; each is an independent copy.

**`<mailbox-slug>`** — deterministic from the email: lowercase, take local-part + first domain segment, replace any non-`[a-z0-9-]` with `-`, strip leading/trailing `-`. Examples:

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@synps.xyz` | `adithya-synps` |
| `adithya@eclipse.builders` | `adithya-eclipse` |
| `adithya.shak.kumar@gmail.com` | `adithya-shak-kumar-gmail` |

**`<YYYY>/<MM>`** — year + zero-padded month of the **first message in the thread**. Stable across re-ingest.

**`<filename>`** — `<date>__<subject-slug>__<threadid8>.md` where:
- `<date>` is `YYYY-MM-DD` of the first message.
- `<subject-slug>` derives from the original subject:
  1. Strip prefixes (case-insensitive, repeat to fixed point): `Re:`, `Fwd:`, `Fw:`, `FW:`, `AW:`, `[External]`, `[EXT]`, `[CONFIDENTIAL]`, `[SPAM]`, `AUTO:`.
  2. NFKD-normalize → ASCII (ignore non-ASCII).
  3. Replace runs of non-`[a-zA-Z0-9]` with `-`. Lowercase. Strip leading/trailing `-`.
  4. Truncate to 60 chars; strip trailing `-`. Empty → `no-subject`.
- `<threadid8>` is the first 8 chars of `thread_id` (uniqueness guarantee).

**Idempotency**: path is deterministic from `(mailbox_slug, thread_id, first-message-date, subject)`. Re-ingesting the same thread always overwrites the same file. The robot never moves files.

## C. Universal frontmatter envelope (REQUIRED)
```yaml
source: gmail
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body markdown only (post-frontmatter)
provider_modified_at: <ISO 8601 with TZ>   # internalDate of last message
```

`content_hash` is computed over the body markdown ONLY. Same body bytes ⇒ same hash regardless of ingest time. This is the dedup signal.

## D. Gmail-specific frontmatter
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
  - "eclipse:label:Eclipse"            # <destination-ws>:<rule-marker>
  - "personal:rules.match[0]"
deleted_upstream: null                 # ISO 8601 if history.list reports messageDeleted
superseded_by: null                    # full path if a follow-up thread merges into this one
```

Field rules:
- `participants[].roles` ⊆ `{from, to, cc, bcc}`. Same address across multiple roles collapses to one entry with the union of roles.
- `labels` mirrors Gmail's `labelIds` exactly.
- `attachments[].id` is the first 8 chars of Gmail's `attachmentId`.
- `attachments[].message_index` is required.
- `routed_by` populated by `route.py`; format is `<destination-workspace>:<rule-marker>`.
- `deleted_upstream` and `superseded_by` are the ONLY fields the robot may modify post-write (see § H).

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
1. Messages chronological (`internalDate` ascending).
2. HTML→markdown via `html2text`. Prefer `text/plain` when both parts exist.
3. Quoted-history removal: drop everything from the first `^On <date> .* wrote:$` line; trim trailing `>`-prefixed blockquote lines.
4. Signature stripping: cut at first `^-- ?$` delimiter. Otherwise strip a trailing >10-line block matching legal-disclaimer patterns (`This email and any attachments...`, `CONFIDENTIALITY NOTICE`, `IRS Circular 230`). Conservative — leave noise rather than strip signal.
5. Inline images: reference as `[image: <filename>]`; metadata only.
6. PDF attachments < 10 MB: extract text via `pdftotext` (preferred) or `markitdown`, append as `### Attachment: <filename>`.
7. Larger / non-text attachments: metadata only, body says `Binary attachment, content not extracted.`
8. **No LLM calls.** All conversion deterministic.

## F. Pre-filter (deterministic, NO LLM)
Skip the entire thread if any of:
- **Size** > 25 MB (sum of attachment + body bytes across all messages).
- **First-message subject** matches `/^(out of office|automatic reply|undeliverable|delivery (status )?notification)\b/i`.
- **All senders blocklisted** — every message's `From:` matches the universal blocklist (case-insensitive):
  - `noreply@*`, `no-reply@*`, `*-noreply@*`, `donotreply@*`
  - `mailer-daemon@*`, `postmaster@*`
  - `calendar-notification@google.com`, `*@calendar.google.com`
  - `*@bounces.amazonses.com`, `*@accounts.google.com`
- **Labels** `SPAM` or `TRASH` on any message. (`DRAFT` preserved.)
- **MIME outside allowlist**: `{text/plain, text/html, application/pdf, image/*, multipart/*}`. Per-message warning; thread-skip only if every attachment is outside the allowlist.
- **Calendar-invite-only**: every attachment is a `.ics` (text/calendar) file.

This blocklist is universal. Per-mailbox or per-workspace exclusions belong in `sources.yaml`'s `api_query.exclude`.

## G. Dedup key
`gmail:<thread_id>`. Per-workspace ledger at `workspaces/<ws>/_meta/ingested.jsonl`, one JSON line per ingest:
```json
{"source":"gmail","key":"gmail:17abc...","content_hash":"blake3:...","raw_path":"raw/gmail/...","ingested_at":"...","run_id":"..."}
```

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | — | write file, append ledger row |
| present | matches | no-op (silent skip, log line) |
| present | mismatches | overwrite file, append a NEW ledger row (ledger is append-only) |

## H. Forbidden behaviors (immutable contract)
The robot **NEVER**:
1. Deletes a raw file based on Gmail-side deletion. `messageDeleted` events set `deleted_upstream` in the existing file's frontmatter; the file persists.
2. Moves files between paths. Path is fixed at write time. Mid-thread subject changes don't relocate the file.
3. Runs LLM / vision calls during ingest. PDF text via `pdftotext`/`markitdown` is fine; everything else is metadata-only.
4. Edits frontmatter post-write, except `deleted_upstream` and `superseded_by`. Every other re-ingest produces a fresh file.
5. Writes outside `workspaces/<ws>/raw/gmail/<mailbox-slug>/...`. Ledger / log appends happen in the dispatcher, not the rendering loop.
6. Skips the universal blocklist (§ F), even if a workspace's `api_query.include` would otherwise pull a blocklisted sender.

## I. Cross-references
- Workflow: `CONTEXT.md`.
- sources.yaml schema: `sources-schema.md` (§3).
- Runbook: `_shell/docs/runbook-gmail.md` (§9).
- Credentials: `_shell/docs/credentials-gmail.md` (§9).
