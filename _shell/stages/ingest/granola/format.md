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
- `attendees[].email` lowercased. Self-attendee (creator) is excluded from `attendees[]`. Dedup key: lowercased email match against `creator.email`. If `creator.email` is absent, fall back to lowercased-trimmed-`name` match.
- `calendar_event` is `null` if `doc.google_calendar_event` is missing, `null`, or `{}`.
- `duration_ms` is `max(end_timestamp) - min(start_timestamp)` across transcript final segments **that have both timestamps populated**; `null` if no segment has both.
- `folders[]` is the FULL set, even if multiple are subscribed by different workspaces.
- `routed_by[]` is the subset of folder rules that caused THIS file to be written into THIS workspace.
- `valid_meeting` and `was_trashed`: emit the raw value (`true` / `false` / `null`). Don't coerce.

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

{rendered AI summary, see "AI Notes source" below. If no source resolves to non-empty content → section omitted.}

## Transcript

**Me:** {concatenated text of consecutive `source: microphone` segments, joined with " "}

**Other:** {concatenated text of consecutive `source: system` segments}

**Me:** ...
```

**AI Notes source (resolution order, first non-empty wins):**
1. `doc.notes_markdown` — verbatim, stripped of trailing whitespace.
2. `doc.last_viewed_panel.content` (ProseMirror JSON) → render via the ProseMirror→Markdown walker (Lock 4a). The robot must type-check first: `last_viewed_panel` is sometimes a string panel-id, sometimes a dict. String → no AI Notes.
3. None of the above → omit the `## AI Notes` heading entirely.

Live-probe finding: across all 45 sample Eclipse docs, `notes_markdown` was empty and the AI summary lived in `last_viewed_panel.content`. The walker is therefore the load-bearing path in practice.

**Lock 4a — ProseMirror → Markdown walker (minimum supported nodes/marks):**

| Node type | Render |
|---|---|
| `doc` | walk children |
| `paragraph` | render children + `\n\n` |
| `heading` | `#` * `attrs.level` (default 1, clamped 1-6) + ` ` + children + `\n\n` |
| `bulletList` | walk children |
| `orderedList` | walk children (numbering rebuilt by sibling index) |
| `listItem` | bullet (`- ` or `<n>. `) + children, indent nested lists by 2 spaces per depth |
| `blockquote` | prefix every rendered line with `> ` |
| `codeBlock` | `\`\`\`<attrs.language or "">\n{text}\n\`\`\`\n\n` |
| `horizontalRule` | `\n---\n\n` |
| `hardBreak` | two trailing spaces + `\n` |
| `text` | `text` after applying marks (innermost first) |
| anything else | walk children, ignore the wrapper |

| Mark type | Render |
|---|---|
| `bold` / `strong` | `**{text}**` |
| `italic` / `em` | `_{text}_` |
| `code` | `\`{text}\`` |
| `strike` | `~~{text}~~` |
| `underline` | `<u>{text}</u>` (HTML — markdown has no native underline) |
| `link` | `[{text}]({attrs.href})` |
| anything else | unwrapped (text passes through unchanged) |

Empty trailing whitespace is stripped from the final render. A render that contains only whitespace is treated as empty (omit the AI Notes section).

**Transcript rendering rules:**
- Use only segments where `is_final is True`. If `is_final` is missing on a segment, treat as final (rare; older Granola records).
- Sort by `(start_timestamp or "", original_index)` — null-safe sort that preserves API order on ties.
- Group runs of consecutive same-source segments into a single block; join texts with a single space.
- Source-to-label map: `microphone` → `**Me:**`, `system` → `**Other:**`, anything else (`phone_in`, `web_clip`, etc.) → `**{source}:**`.
- One blank line between blocks.

**Duration string in the H1 quote line:**
- `duration_ms is None` → omit the duration field entirely.
- ≥ 60_000 ms → `Xm Ys`.
- < 60_000 ms → `Ys`.

## Lock 5 — Pre-filter (deterministic, no LLM)

A doc is SKIPPED before any file write if any of these conditions hold:

1. `doc.was_trashed is True` (use Python `is`, not `==`. `None` does NOT skip.)
2. `doc.transcript_deleted_at is not None`
3. `doc.valid_meeting is False` (use Python `is`. `None` does NOT skip.)
4. The doc's folder set has empty intersection with the union of every subscribing workspace's `granola.folders`.
5. Transcript fetch returns 0 segments where `is_final` is `True` or missing (i.e. only interim `is_final: False` segments exist, OR the transcript array is empty).

Pre-filter is fail-closed: when in doubt, skip. Skipped docs are logged with reason; never written.

Live-probe data point (2026-05-04 Eclipse folder, 45 docs): `was_trashed` and `valid_meeting` are `None` for many docs that the user clearly considers valid meetings. Treating `None` as "skip" would silently drop most of the corpus. Hence the strict `is True` / `is False` checks.

## Lock 6 — Dedup ledger + rename handling

`workspaces/<ws>/_meta/ingested.jsonl` line per write:

```json
{"source":"granola","key":"<document_id>","content_hash":"blake3:<64hex>","path":"raw/granola/.../file.md","ingested_at":"<iso>"}
```

- Key uniqueness: `(source, key)` per workspace. The latest ledger row for a given `(source, key)` is the authoritative `last_known_path` and `content_hash`.
- Same key + same hash + same path → skip write entirely.
- Same key + same hash + DIFFERENT path → title rename in Granola (path is title-derived). Move: `os.replace(old_path, new_path)` if old exists, else just write new. Append a new ledger row recording the new path.
- Same key + different hash + same path → overwrite the file in place. Append new ledger row.
- Same key + different hash + different path → write to new path; if old path still exists on disk, `os.remove(old_path)`. Append new ledger row.
- Ledger is append-only; lint compacts on a separate cadence.

Live-probe data point: 18 of 45 Eclipse docs share the title `"Sydney <> Adi"`. The slug collapses identical titles, so disambiguation comes solely from `<docid8>` in the path. A title rename in Granola changes only the title-slug, not the docid8; the move-on-rename rule above is what keeps the `raw/` tree consistent with Granola's authoritative state instead of accumulating a graveyard of stale files.

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

On any 401, the entire read-refresh-write cycle MUST happen inside a `flock` on `/tmp/com.adithya.ultron.granola-token-refresh.lock`. The lock keeps the robot from racing the desktop app or another robot instance. Steps inside the lock:

1. Re-read `supabase.json` fresh. If `access_token` differs from the one that 401'd → use the new value, release the lock, retry. (Desktop app refreshed while we were idle.)
2. Otherwise call:
   ```
   POST https://api.workos.com/user_management/authenticate
   { "grant_type":"refresh_token",
     "refresh_token":<refresh_token>,
     "client_id":<JWT.client_id from access_token> }
   ```
   Response: `{ "access_token": ..., "refresh_token": ..., ...}`. Refresh token rotates.
3. Atomic-write the new tokens back to `supabase.json` (sibling `.tmp` + `os.replace`). Preserve every other key in the file untouched. Update `obtained_at` (ms epoch) and `expires_in`. Minimize the window between `json.load` of the fresh file and `os.replace` to reduce the chance of clobbering a desktop-app-side state field that changed underneath us.
4. Release the lock. Retry the original call once. Second 401 → fail loudly with a clear message instructing the user to bring the Granola desktop app to the foreground (which forces an in-app refresh).

DO NOT proactively refresh. Only on 401. WorkOS rotates the refresh token on every successful refresh, so concurrent refreshes invalidate each other. The flock + read-recheck-then-refresh pattern is what prevents the robot from invalidating a refresh token the desktop app just minted.

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
