# Format: gmail

## File granularity
One markdown file per email **thread** (not per message).

## Path
`workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<date>__<subject-slug>__<threadid8>.md`

- `<account-slug>`: local-part + domain-stem of the Gmail address. `adithya@outerscope.xyz` → `adithya-outerscope`.
- `<YYYY>/<MM>`: from the FIRST message date in the thread. Stable; the file does not move when new replies arrive.
- `<date>`: ISO `YYYY-MM-DD` of the first message.
- `<subject-slug>`: kebab-case ASCII, max 60 chars. Strip these prefixes before slugging: `Re:`, `Fwd:`, `FW:`, `[External]`, `[CONFIDENTIAL]`, `AUTO:`. Empty subject → `no-subject`.
- `<threadid8>`: first 8 chars of Gmail `thread_id`. Uniqueness guarantee.

Re-runs OVERWRITE the same file. Stable filename = idempotent ingest. New replies regenerate the entire file with the longer thread.

## Frontmatter

```yaml
---
# Universal envelope (REQUIRED)
source: gmail
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3 of body>
provider_modified_at: <ISO 8601 of last message in thread>

# Gmail-specific
account: adithya@outerscope.xyz
thread_id: 17abc123def4567
message_ids:
  - <CABx@mail.gmail.com>
  - <CABy@mail.gmail.com>
subject: Q3 deck review
participants:
  - { name: Sydney Hayes, email: sydney@eclipse.audio, roles: [from, to] }
  - { name: Adithya, email: adithya@outerscope.xyz, roles: [from, to, cc] }
labels: [INBOX, Eclipse/Investors]
first_message: 2026-04-15T14:23:00-05:00
last_message: 2026-04-22T09:11:00-05:00
message_count: 7

# Attachments (metadata; content extracted inline in body)
attachments:
  - { id: a3f8d9, filename: deck-v3.pdf, size_bytes: 1234567, mime: application/pdf }

# Lifecycle (set when applicable)
deleted_upstream: null
superseded_by: null
---
```

## Body

```markdown
# Q3 deck review

## 2026-04-15 14:23 — Sydney Hayes <sydney@eclipse.audio>

Body in plain markdown. HTML stripped via html2text. Quoted history
("On <date> wrote:" blocks) removed because prior messages already live
above in the same file.

Long boilerplate signatures stripped (>10 lines of footer, legal
disclaimers, "This email and any attachments..." patterns).

**Attachments referenced:** deck-v3.pdf (1.2MB)

### Attachment: deck-v3.pdf

<Extracted markdown from the PDF via pdftotext or markitdown if PDF.
Vision call to Sonnet if image (under 10 MB). Otherwise: "Binary
attachment, content not extracted.">

## 2026-04-15 16:01 — Adithya <adithya@outerscope.xyz>

Reply text.
```

## Pre-filter (deterministic, NO LLM)

Skip the entire thread if any of:
- Total thread size > 25 MB (sum of attachment sizes + body bytes).
- Subject matches `^(out of office|automatic reply|undeliverable)`.
- Sender domain matches the blocklist:
  - `noreply@*`, `*-noreply@*`, `no-reply@*`
  - `calendar-notification@google.com`, `*@calendar.google.com`
  - `*@bounces.amazonses.com`, `*@accounts.google.com`
- Label matches `SPAM` or `TRASH`. (`DRAFT` is preserved.)
- MIME entirely outside the allowlist: `text/plain`, `text/html`, `application/pdf`, `image/*`.
- Calendar invites (`.ics` attachments): SKIP entire thread.

## Dedup key
`gmail:<thread_id>` — Gmail `thread_id` is provider-stable.

Storage: `workspaces/<ws>/_meta/ingested.jsonl`.
Row format:
```json
{"source":"gmail","key":"gmail:17abc...","content_hash":"...","raw_path":"raw/gmail/adithya-outerscope/2026/04/...","ingested_at":"..."}
```

Behavior on re-ingest:
- Same key + same content_hash → skip (no-op).
- Same key + different content_hash → overwrite.
