# Format: gmail (AUTHORITATIVE)

> Single source of truth for how Gmail becomes raw markdown.
> Routing decisions live in `sources.yaml`; this file controls everything else.

## Lock 1 — Path template

```
workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<filename>
```

**`<account-slug>`** — lowercase email; local-part + first domain segment;
non-`[a-z0-9]` runs → `-`; strip leading / trailing `-`. ASCII only.

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@synps.xyz` | `adithya-synps` |
| `adithya@eclipse.builders` | `adithya-eclipse` |
| `adithya.shak.kumar@gmail.com` | `adithya-shak-kumar-gmail` |

**`<YYYY>/<MM>`** — year + zero-padded month of the **first message** in
the thread. Stable forever; new replies don't relocate the file.

**`<filename>`** — `<date>__<subject-slug>__<threadid8>.md`.
- `<date>` — `YYYY-MM-DD` of first message.
- `<subject-slug>` — strip prefixes (case-insensitive, repeat to fixed
  point): `Re:`, `Fwd:`, `Fw:`, `FW:`, `AW:`, `RES:`, `TR:`, `[External]`,
  `[EXT]`, `[CONFIDENTIAL]`, `[SPAM]`, `AUTO:`. NFKD→ASCII; non-`[a-zA-Z0-9]`
  runs → `-`; lowercase; strip ends; truncate 60 chars; strip trailing `-`;
  empty → `no-subject`.
- `<threadid8>` — first 8 chars of Gmail `thread_id`.

**Idempotency**: path determined by `(account_slug, thread_id, first-date,
subject)`. Re-ingest overwrites in place. Robot never moves files.

## Lock 2 — Universal frontmatter envelope (REQUIRED)

```yaml
source: gmail
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body markdown only (post-frontmatter)
provider_modified_at: <ISO 8601 with TZ>   # internalDate of last message
```

`content_hash` is over body markdown ONLY. Same body bytes ⇒ same hash
regardless of ingest time. Dedup signal.

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
deleted_upstream: null                 # ISO 8601 if history.list reports messageDeleted
```

Field rules:
- `participants[].roles` ⊆ `{from, to, cc, bcc}`. Same address across roles collapses; roles unioned.
- `labels` stores friendly label names. System labels (`INBOX`, `SPAM`, `TRASH`, `IMPORTANT`, `UNREAD`, `CATEGORY_*`, `SENT`, `DRAFT`, etc.) pass through unchanged because their id == name. User labels arrive as opaque ids (`Label_19`) and are translated to their human name (`Eclipse`) via `users.labels.list`. Required so routing rules — humans write `label:Eclipse`, not `label:Label_19` — match what the robot stores.
- `attachments[].id` is first 8 chars of Gmail's `attachmentId`. `message_index` is required.
- `routed_by` lists every workspace that received this thread + the rule that fired. Same list in every workspace copy.
- `deleted_upstream` is the ONLY frontmatter field the robot may modify post-write (besides `labels` on `labelAdded` / `labelRemoved`).

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
3. Quoted-history removal: drop everything from the first `^On <date> .* wrote:$` line; trim trailing `>`-prefixed blockquote lines.
4. Signature stripping: cut at first canonical `^-- ?$` delimiter (RFC 3676). NO heuristic stripping. If no delimiter, keep everything.
5. Inline images: `[image: <filename>]`; metadata only.
6. PDF attachments < 10 MB: extract text via `pdftotext` (preferred) or `markitdown`, append as `### Attachment: <filename>`.
7. Larger / non-text attachments: metadata in frontmatter only; body says `Binary attachment, content not extracted.`
8. **No LLM calls.** Conversion is deterministic.

## Lock 5 — Pre-filter (deterministic, NO LLM)

Skip the entire thread if any of:

- **Size** > 25 MB (sum of attachments + bodies).
- **First-message subject** matches `/^(out of office|automatic reply|undeliverable|delivery (status )?notification)/i`.
- **All senders blocklisted** — every message's `From:` matches the universal blocklist (case-insensitive):
  - `noreply@*`, `no-reply@*`, `*-noreply@*`, `donotreply@*`, `mailer-daemon@*`, `postmaster@*`
  - `calendar-notification@google.com`, `*@calendar.google.com`, `*@bounces.amazonses.com`, `*@accounts.google.com`
- **Labels** — any message on the thread carries `SPAM` or `TRASH`. (`issubset({SPAM,TRASH})` was the original check, but Gmail keeps `UNREAD` / `IMPORTANT` / `CATEGORY_*` on spam-flagged threads, so the subset form almost never fired.)
- **MIME outside allowlist**: skip only if EVERY attachment is outside `{text/plain, text/html, application/pdf, image/*, multipart/*}`.
- **Calendar-invite-only**: thread has attachments and every one is `.ics` (text/calendar).

This blocklist is universal. Per-account exclusions go in `sources.yaml`'s `api_query.exclude` (inline) or `api_query.exclude_from` (a path to a shared YAML at `_shell/config/account-excludes/<account-slug>.yaml` with a top-level `excludes:` list — used when the same noise sender list applies across multiple workspaces). Both are unioned post-fetch by `route.py`. Rule grammar supports compound predicates (`from:X subject:"Y"`) and negation (`-subject:"Z"`); see `route.py` docstring.

## Lock 6 — Dedup

Key: `gmail:<account-slug>:<thread_id>`. Account-namespaced because Gmail
thread ids are mailbox-scoped — two accounts that route to the same
workspace can produce identical thread ids, and a body-hash + tid collision
across mailboxes would otherwise silently skip the second account's write.
Pre-namespace ledger entries (`gmail:<thread_id>`) are still honored on
read for the same account (raw_path-prefix-disambiguated). Per-workspace
ledger at `workspaces/<ws>/_meta/ingested.jsonl`, one JSON line per ingest:

```json
{"source":"gmail","key":"gmail:adithya-outerscope:17abc...","content_hash":"blake3:...","raw_path":"raw/gmail/...","ingested_at":"...","run_id":"..."}
```

Ledger appends acquire an exclusive `fcntl.flock` per ingest; flock is
per-mailbox elsewhere, but two robots for different accounts can route to
the same workspace concurrently, and unlocked appends would interleave.

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | — | write file, append ledger row |
| present | matches | no-op (silent skip, log line) |
| present | mismatches | overwrite file, append NEW ledger row (append-only) |

## Lock 7 — Cursor + robot CLI

**Cursor file**: `_shell/cursors/gmail/<account-slug>.txt`. Stores last seen Gmail `historyId` (decimal integer, written as text).

**First run** (cursor missing/empty): `users.messages.list(q=<union>)` bounded by `GMAIL_INITIAL_LOOKBACK_DAYS` env var (default 365) via `after:`. Dedupe to threads; fetch each via `users.threads.get(format='full')`. Persist `historyId` from `users.getProfile()` after success.

**Subsequent runs** (cursor present): `users.history.list(startHistoryId=<cursor>, historyTypes=[messageAdded, messageDeleted, labelAdded, labelRemoved])`. Per event:
- `messageAdded` — fetch thread, normal pipeline.
- `messageDeleted` — locate existing raw file by `thread_id`, set `deleted_upstream` in frontmatter, rewrite. Don't delete the file.
- `labelAdded` / `labelRemoved` — re-evaluate routing. Update `labels` on existing copies; new matches → new workspace copies. Existing copies stay even if no longer matching.

Advance cursor to `users.getProfile().historyId` ONLY after the write phase succeeds. Mid-batch failure leaves cursor at previous value; next run replays.

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

**flock** at `/tmp/com.adithya.ultron.ingest-gmail-<account-slug>.lock`. Concurrent invocation for the same account exits 0 silently.

## Forbidden behaviors (immutable contract)

The robot **NEVER**:
1. Deletes a raw file based on Gmail-side deletion. `messageDeleted` events set `deleted_upstream`; file persists.
2. Moves files between paths. Path is fixed at write time.
3. Runs LLM / vision calls during ingest. PDF text via `pdftotext` / `markitdown` is fine; everything else metadata-only.
4. Edits frontmatter post-write, except `deleted_upstream` and `labels` (the latter only on `labelAdded` / `labelRemoved`).
5. Writes outside `workspaces/<ws>/raw/gmail/<account-slug>/...`.
6. Skips the universal blocklist (Lock 5), regardless of `api_query.include`.

## Cross-references

- Workflow: `CONTEXT.md`. sources.yaml schema: `sources-schema.md`. Runbook: `_shell/docs/runbook-gmail.md`. Credentials: `_credentials/INVENTORY.md`.
