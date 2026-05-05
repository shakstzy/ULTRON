# Format: granola (AUTHORITATIVE)

> Locked. Every Granola file written by `ingest-granola.py` must conform
> to this spec exactly. The 8 locks below are the contract.

## Lock 1 — Path template

```
workspaces/<ws>/raw/granola/<account-slug>/<YYYY>/<MM>/<YYYY-MM-DD>__<title-slug>__<docid8>.md
```

**`<account-slug>`** — Granola account email, sluggified the same way Gmail does it: lowercase email; local-part + first domain segment; non-`[a-z0-9]` runs → `-`; strip leading / trailing `-`. ASCII only.

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@eclipse.builders` | `adithya-eclipse` |

**`<YYYY>/<MM>/<YYYY-MM-DD>`** — local-timezone date of `doc.created_at`. Stable forever; updates do not relocate the file.

**`<title-slug>`**:
- NFKD → ASCII fold.
- Strip leading `Re:` / `Fwd:` style prefixes (case-insensitive, repeat to fixed point): `Re:`, `Fwd:`, `Fw:`. Granola titles rarely carry these but we normalize for safety.
- Non-`[a-zA-Z0-9]` runs → `-`.
- Lowercase. Strip leading / trailing `-`. Truncate at 60 chars; strip trailing `-` after truncate.
- Empty after sluggification → `untitled-meeting`.

**`<docid8>`** — first 8 chars of Granola's `id` (UUID v4), lowercased. Used to disambiguate same-day same-title docs.

**Idempotency**: path is determined by `(account_slug, document_id, created_at, title)`. Re-ingest with a different `content_hash` overwrites in place. Robot never moves files. A title rename in Granola creates a NEW path (since title is part of the slug); the old file stays — left for lint to surface, not for the robot to delete.

## Lock 2 — Universal frontmatter envelope (REQUIRED)

```yaml
source: granola
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body markdown only (post-frontmatter)
provider_modified_at: <ISO 8601 with TZ>   # doc.updated_at
```

`content_hash` is over body markdown ONLY. Same body bytes ⇒ same hash regardless of ingest time. Dedup signal.

## Lock 3 — Granola-specific frontmatter

```yaml
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 88a5648d-0b9d-4e31-b27a-51e90c5ce6a5    # full UUID
document_id_short: 88a5648d                          # first 8 chars
title: "Podcast data licensing and human X lead follow-up with Adithya"   # original
created_at: 2026-04-13T18:39:35.743Z                 # doc.created_at
updated_at: 2026-04-13T18:59:01.618Z                 # doc.updated_at
folders:                                             # every Granola folder containing this doc
  - { id: 84a8f86d-16f6-4529-a4b3-11a687032b07, title: "ECLIPSE" }
creator:
  name: "Adithya"
  email: "adithya@outerscope.xyz"
attendees:
  - { name: "Sydney Hayes", email: "sydney@eclipse.audio" }
calendar_event:                                      # nullable
  title: "Adithya / Sydney sync"
  start: 2026-04-13T18:30:00-05:00
  end:   2026-04-13T19:00:00-05:00
  url:   "https://calendar.google.com/event?eid=..."
  conferencing_url: "https://zoom.us/j/..."
  conferencing_type: zoom
transcript_segment_count: 188
duration_ms: 1166000
valid_meeting: true
was_trashed: false
routed_by:
  - { workspace: eclipse, rule: "folder:ECLIPSE" }
```

Field rules:
- `attendees[].email` lowercased. Self-attendee (creator) appears in `creator` only, not duplicated in `attendees[]`.
- `calendar_event` is `null` if `doc.google_calendar_event` is missing or empty `{}`.
- `duration_ms` is `max(end_timestamp) - min(start_timestamp)` across transcript final segments; `null` if no timestamps.
- `folders[]` is the FULL set, even if multiple are subscribed by different workspaces.
- `routed_by[]` is the subset of folder rules that caused THIS file to be written into THIS workspace.

## Lock 4 — Body markdown

```markdown
# {title}

> {created_at local} · duration {Xm Ys} · {n} attendees

## Attendees

- **{creator.name}** (creator) <{creator.email}>
- {attendee.name} <{attendee.email}>
...

## Calendar Event

- Title: {calendar_event.title}
- Start: {calendar_event.start}
- End:   {calendar_event.end}
- URL:   {calendar_event.url}
- Conferencing: {calendar_event.conferencing_type} {calendar_event.conferencing_url}

(`## Calendar Event` section omitted entirely when calendar_event is null.)

## AI Notes

{doc.notes_markdown, verbatim. Trailing whitespace stripped. If empty → `_(none)_`.}

## Transcript

**Me:** {concatenated text of consecutive `source: microphone` segments, joined with " "}

**Other:** {concatenated text of consecutive `source: system` segments}

**Me:** ...
```

Transcript rendering rules:
- Use only `is_final: true` segments. Drop interim segments.
- Sort by `start_timestamp` ascending.
- Group runs of consecutive same-source segments into a single block.
- Render `microphone` as `**Me:** `, `system` as `**Other:** `, anything else as `**{source}:** `.
- One blank line between blocks.

## Lock 5 — Pre-filter (deterministic, no LLM)

A doc is SKIPPED before any file write if any of these conditions hold:

1. `doc.was_trashed == true`
2. `doc.transcript_deleted_at` is not null
3. `doc.valid_meeting == false`
4. The doc's folder set has empty intersection with the union of every subscribing workspace's `granola.folders`.
5. Transcript fetch returns 0 final segments (`[s for s in transcript if s.is_final]`).

Pre-filter is fail-closed: when in doubt, skip. Skipped docs are logged with reason; never written.

## Lock 6 — Dedup ledger

`workspaces/<ws>/_meta/ingested.jsonl` line per `(source, key)`:

```json
{"source":"granola","key":"<document_id>","content_hash":"blake3:<64hex>","path":"raw/granola/.../file.md","ingested_at":"<iso>"}
```

- Key uniqueness: `(source, key)` per workspace. Same key + same hash → skip write entirely.
- Same key + different hash → overwrite the file at the deterministic path; append a NEW ledger row (don't mutate prior rows).
- Ledger is append-only; lint compacts on a separate cadence.

## Lock 7 — Auth + token refresh

Authoritative source: `~/Library/Application Support/Granola/supabase.json`.

```python
raw  = json.load(open(SUPABASE_JSON))
toks = json.loads(raw["workos_tokens"])  # NB: this field is itself a JSON string
access_token  = toks["access_token"]
refresh_token = toks["refresh_token"]
```

Required headers on every Granola API call:

```
Authorization:  Bearer <access_token>
Content-Type:   application/json
X-Client-Version: 7.195.0
Accept-Encoding: identity
```

Setting `Accept-Encoding: identity` disables gzip. Without `X-Client-Version` the API returns 200 + `{"message":"Unsupported client"}`. Both headers required.

On any 401:
1. Re-read `supabase.json`. If `access_token` differs → use new value, retry. (Desktop app may have refreshed.)
2. Otherwise call:
   ```
   POST https://api.workos.com/user_management/authenticate
   { "grant_type":"refresh_token",
     "refresh_token":<refresh_token>,
     "client_id":<JWT.client_id from access_token> }
   ```
   Response: `{ "access_token": ..., "refresh_token": ..., ...}`. Refresh token rotates.
3. Atomic-write the new tokens back to `supabase.json` (sibling `.tmp` + `os.replace`). Preserve every other key in the file untouched. Update `obtained_at` (ms epoch) and `expires_in`.
4. Retry the original call once. Second 401 → fail loudly.

DO NOT proactively refresh. Only on 401. The desktop app's refresh-token rotation rule says: whoever refreshes last wins; concurrent refreshes invalidate each other. We minimize blast radius by refreshing only when we have to.

## Lock 8 — Endpoints + rate

| Purpose | Method + Path | Body |
|---|---|---|
| List folders | POST `/v1/get-document-lists-metadata` | `{include_document_ids: true, include_only_joined_lists: false}` |
| Fetch docs | POST `/v1/get-documents-batch` | `{document_ids: [...]}` (≤ 20 ids per call) |
| Fetch transcript | POST `/v1/get-document-transcript` | `{document_id: "<uuid>"}` |

Base URL: `https://api.granola.ai`.

Rate budget (personal use, courtesy):
- Serial calls; ≤ 1 req/sec sustained.
- 429 → exponential backoff (2 s, 4 s, 8 s, 16 s, 32 s; max 5 attempts), then fail loudly.
- 5xx → same backoff.
- 4xx other than 401/429 → fail loudly without retry.

## Cursor

```
_shell/cursors/granola/<account-slug>.txt
```

Single line: ISO 8601 timestamp of the max `updated_at` across all docs successfully written in the prior run. Missing → first-run mode (ingest all matching). Cursor advances atomically (sibling tmp + `os.replace`).
