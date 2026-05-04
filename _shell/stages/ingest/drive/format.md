# Format: drive (AUTHORITATIVE)

> Single source of truth for how Google Drive becomes raw markdown.
> Routing decisions live in `sources.yaml`; this file controls everything else.

## Lock 1 — Path template

```
workspaces/<ws>/raw/drive/<account-slug>/<folder-path>/<file-slug>__<file-id-short>.<ext>
```

**`<account-slug>`** — same algorithm as Gmail. Lowercase email; local-part +
first domain segment; non-`[a-z0-9]` runs → `-`; strip leading / trailing `-`;
ASCII only.

| Email | Slug |
|---|---|
| `adithya@outerscope.xyz` | `adithya-outerscope` |
| `adithya@synps.xyz` | `adithya-synps` |
| `adithya@eclipse.builders` | `adithya-eclipse` |
| `adithya.shak.kumar@gmail.com` | `adithya-shak-kumar-gmail` |

**`<folder-path>`** — mirrors Drive's folder hierarchy from the **designated
root folder** declared in `sources.yaml`, NOT from My Drive root. If the
designated root is `Eclipse Labs` and the file lives in
`Eclipse Labs/Q4 2025/Investor Updates/deck.pdf`, then
`<folder-path>` = `q4-2025/investor-updates`. Each segment kebab-case ASCII,
max 60 chars per segment (Lock 9). The designated root itself is NOT a
segment in `<folder-path>`; it's identified by `drive_designated_folder_id`
in frontmatter (Lock 3).

**`<file-slug>`** — Drive file name → kebab-case ASCII, max 60 chars (Lock 9).

**`<file-id-short>`** — first 8 hex chars of the Drive file ID. Guarantees
uniqueness even when two files share a name in the same folder.

**`<ext>`**:
- `.md` for Google Docs, PDFs, Google Slides
- `.csv` for Google Sheets
- (no other types reach this stage; see Lock 5)

**Idempotency**: path is deterministic from `(account_slug, folder_path,
file_slug, file_id)`. Re-ingest overwrites in place. Robot never moves files.
A folder rename in Drive is **prospective only**: existing raw files keep
their old paths; new ingests of newly-renamed/moved files land at the new
path. Reconciliation (Lock 6) hard-deletes stale paths.

## Lock 2 — Universal frontmatter envelope (REQUIRED)

```yaml
source: drive
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body bytes only (post-frontmatter)
provider_modified_at: <ISO 8601 with TZ>   # Drive modifiedTime
```

`content_hash` is over body bytes ONLY. Same body ⇒ same hash regardless of
ingest time. Dedup signal.

## Lock 3 — Drive-specific frontmatter

```yaml
drive_account: adithya@eclipse.builders
drive_account_slug: adithya-eclipse
drive_file_id: 1aBcD3F_g4HiJk5L6m_n7oPqR8sTuVwX
drive_file_id_short: 1abcd3f_
drive_raw_identity_id: 1aBcD3F_g4HiJk5L6m_n7oPqR8sTuVwX  # path-identity (= drive_file_id, except for shortcuts where it equals the shortcut's file id)
drive_mime_type: application/vnd.google-apps.document
drive_file_type: doc                   # pdf | doc | sheet | slide | other
drive_file_name: "Q4 Investor Update — Final v3.docx"
drive_file_size_bytes: 0               # 0 for native Google formats (no canonical bytes)
drive_web_view_link: https://docs.google.com/document/d/1aBcD3F.../edit
drive_created_at: 2026-03-12T09:14:00-05:00
drive_modified_at: 2026-04-22T18:42:11-05:00
drive_version: "1234"                  # revisionId or HEAD-revision id
drive_folder_path:
  - q4-2025
  - investor-updates
drive_folder_id_path:
  - 2gHiJkL_q4_folder_id
  - 3mNoPqR_investor_updates_folder_id
drive_designated_folder_id: 1abcDEF_eclipse_labs_folder_id
drive_designated_folder_name: "Eclipse Labs"
owner:
  email: sydney@eclipse.audio
  display_name: Sydney Hayes
last_modifier:
  email: adithya@eclipse.builders
  display_name: Adithya Kumar
  modified_at: 2026-04-22T18:42:11-05:00
shared_with:                           # populated via permissions.list (paginated)
  - { email: sydney@eclipse.audio, display_name: "Sydney Hayes", role: owner }
  - { email: adithya@eclipse.builders, display_name: "Adithya Kumar", role: writer }
shared_with_visible: true              # false if permissions.list returned 403; shared_with is then []
multi_tab_sheet: false                 # Sheets only; otherwise omit / false
sheet_tab_names: []                    # Sheets only; all tab names
sheet_exported_tab: null               # Sheets only; name of the exported tab
sheet_metadata_visible: true           # Sheets only; false if Sheets API failed
text_extraction_method: native         # native | pdftotext | markitdown | failed
text_extraction_succeeded: true
last_re_ingested_at: null              # ISO 8601 once re-ingested
re_ingest_count: 0
```

Field rules:
- `drive_file_id_short` is the first 8 hex chars of `drive_file_id` (lowercase,
  trailing `_` if Drive ID has non-hex chars in those 8 — see Lock 9).
- `drive_file_type` is one of the four allowed types (Lock 5). `other` is
  reserved for future expansion; v1 never writes `other`.
- `drive_folder_path` and `drive_folder_id_path` are parallel arrays from the
  designated root downward. Empty arrays mean the file is directly inside
  the designated root.
- `shared_with` is rendered only when the token can read the permissions
  list. If `permissions.list` returns 403 (limited sharing visibility), the
  field is `[]` and a `shared_with_visible: false` flag is set.
- `last_re_ingested_at` and `re_ingest_count` are the ONLY frontmatter fields
  the robot may modify post-write. All other fields are recomputed from
  scratch on every re-ingest.

## Lock 4 — Body format

**PDFs** (`.md`):

```markdown
[plain markdown of pdftotext output, or markitdown fallback]
```

If extraction fails, body is empty. Frontmatter records
`text_extraction_method: failed` and `text_extraction_succeeded: false`. File
is still written so reconciliation tracks it. Wiki promotion skips files with
failed extraction.

**Google Docs** (`.md`):

```markdown
[direct markdown from Drive API export(mimeType="text/markdown")]
```

Skip comments and suggestions. Embedded images render as `[image: <inline>]`
metadata-only — the robot never fetches binaries.

**Google Sheets** (`.csv` + sidecar `.csv.frontmatter.yaml`):

The body file is pure CSV (no frontmatter fences, no comment headers — must
parse cleanly with any CSV reader). The universal envelope + Drive
frontmatter (Locks 2 + 3) lives in a sidecar at
`<file-slug>__<file-id-short>.csv.frontmatter.yaml`, same directory as the
body. The sidecar carries the same YAML block that would otherwise be the
frontmatter on a `.md` file.

```
[CSV content of the FIRST tab only — no markdown wrapper, no frontmatter
fences in the body]
```

V1: first tab only. The sidecar's `multi_tab_sheet: true` flag and full
`sheet_tab_names` list flag the rest for manual follow-up.

`check-frontmatter.py` exempts `.csv` files from the body-frontmatter
requirement; the sidecar carries the universal envelope instead. Sidecar
files MUST be hard-deleted alongside their body file during reconciliation
(Lock 6).

**Google Slides** (`.md`):

```markdown
# <slide 1 title (extracted from PDF text)>

<slide 1 body text>

---

# <slide 2 title>

<slide 2 body text>

---
```

Title detection is best-effort from the PDF text. If a slide has no
extractable title, omit the heading and just render the body. `---` markdown
horizontal rule separates every slide.

**No LLM calls anywhere in body rendering.** All conversions are deterministic
(`pdftotext` / `markitdown` / Drive native exports).

## Lock 5 — Pre-filter (deterministic, NO LLM)

**Skip outright** (no file written, no metadata) when ANY of:

- File is in trash (`trashed: true`) — feed this to reconciliation as a
  removal event.
- File is in spam / abuse-flagged state.
- File has `restricted: true` (DRM/IRM-locked, can't extract).
- File size > 100 MB.
- `mimeType` is in the skip list:
  - `video/*` (any video)
  - `audio/*` (any audio)
  - `application/zip`, `application/x-tar`, `application/gzip`,
    `application/x-7z-compressed`, `application/x-rar-compressed`
    (archives)
  - `application/octet-stream` (binary blobs)
  - `application/vnd.google-apps.script` (Apps Script)
  - `application/vnd.google-apps.form` (Forms)
  - `application/vnd.google-apps.drawing` (Drawings — v1 skip)
  - `application/vnd.google-apps.site` (Sites)
  - `image/*` (no images-only files; embedded images in Docs are also
    skipped per Lock 4)

**Allowed types** (everything else is rejected):

| MIME | drive_file_type |
|---|---|
| `application/pdf` | `pdf` |
| `application/vnd.google-apps.document` | `doc` |
| `application/vnd.google-apps.spreadsheet` | `sheet` |
| `application/vnd.google-apps.presentation` | `slide` |

**Shortcuts** (`application/vnd.google-apps.shortcut`):

1. Resolve via `shortcutDetails.targetId` and `shortcutDetails.targetMimeType`.
2. If target MIME is in the skip list → skip.
3. If target MIME is allowed → ingest the **target file's content** at the
   **shortcut's path location**. Frontmatter records BOTH
   `drive_file_id` (target's id) and `drive_shortcut_origin_id` (the
   shortcut's id, so reconciliation can detect the shortcut leaving its
   designated folder).

This pre-filter is universal. It runs BEFORE routing and BEFORE
`sources.yaml` per-folder excludes apply.

## Lock 6 — Reconciliation (THE SOURCE OF TRUTH)

A reconciliation run for `(account, designated_folder)` is the algorithm
that guarantees `raw/drive/<account-slug>/...` matches Drive. Cursor-based
incremental (Lock 7) is a fast-path optimization; reconciliation is the
safety net.

**Algorithm**:

1. **Enumerate Drive side**:
   - Recursively list every file under `designated_folder_id` (descend into
     every subfolder unless excluded via `exclude_subfolders` in
     `sources.yaml`).
   - Apply Lock 5 pre-filter. Drop everything that fails.
   - Build `drive_set = { drive_file_id : (modified_at, deterministic_path) }`.

2. **Enumerate raw side**:
   - Walk `workspaces/<ws>/raw/drive/<account-slug>/` recursively.
   - Read frontmatter from each file.
   - Skip files whose `drive_designated_folder_id` does NOT match the
     current designated folder (those belong to a different reconciliation
     scope).
   - Build `raw_set = { drive_file_id : (provider_modified_at, current_path) }`.

3. **Compute deltas**:

   | Delta | Condition | Action |
   |---|---|---|
   | `new_files` | in `drive_set`, not in `raw_set` | ingest |
   | `modified_files` | in both, `drive_set.modified_at > raw_set.provider_modified_at` | re-ingest (overwrite at deterministic path) |
   | `moved_files` | in both, `drive_set.path != raw_set.path` | hard-delete old path, ingest at new path |
   | `removed_files` | in `raw_set`, not in `drive_set` | HARD DELETE from raw |

   (`moved` and `removed` collapse to "delete the path that no longer
   matches drive_set"; the new ingest happens through the `new` or
   `modified` arms.)

4. **Apply deltas** in order:
   - **Hard deletes FIRST**, atomically. Any file leaving its designated
     folder, entering Drive trash, or whose containing folder was deleted
     upstream is removed from raw. No archive directory, no
     `deleted_upstream` field, no soft-delete. Outright remove.
   - **New ingests** + **re-ingests** follow.

5. **After successful reconciliation**:
   - Persist a fresh `changes.list` page token to the cursor (Lock 7).
   - Append a run record to `_logs/drive-<account-slug>-<run-id>.log`.

**Atomicity**: a reconciliation run can take minutes. During the run, Drive
state can change. Mitigations:
- The cursor for the run is captured **at start**, not end (so events
  during the run replay on the next incremental).
- A file disappearing between `list` and `fetch` is treated as a removal on
  the next run.
- Hard deletes happen at the **end** of the run, after all reads complete
  and after every new ingest succeeds. This guarantees raw never
  half-transitions.
- Failure mid-run leaves partial state; the next reconciliation reconciles
  to consistency.

**Cadence**: reconciliation is the daily authoritative pass. Cursor-based
incremental (Lock 7) can fire more frequently for fast updates.

## Lock 7 — Cursor (fast-path)

**Cursor file**: `_shell/cursors/drive/<account-slug>.txt`. Stores the Drive
`changes.list` page token (opaque string, written verbatim).

**First run** (cursor missing/empty):
1. Get the current page token via `changes.getStartPageToken`.
2. Persist it to the cursor.
3. Run a **full reconciliation** (Lock 6) to ingest everything in every
   designated folder.

**Subsequent incremental runs** (cursor present):
1. Call `changes.list(pageToken=cursor, includeRemoved=true)` and follow
   `nextPageToken` until exhausted; collect every event.
2. For each event, classify and act:

   | Event | Condition | Action |
   |---|---|---|
   | added/moved-into | file appears under a designated folder for an account we ingest | ingest (Lock 4) |
   | modified | file already in raw, `modifiedTime` newer than `provider_modified_at` | re-ingest in place (overwrite) |
   | moved-out | file's parent chain no longer includes any designated folder | hard-delete from raw |
   | trashed | `trashed: true` | hard-delete from raw |
   | untrashed-into | `trashed: false` AND parent chain includes a designated folder | ingest |
   | hard-deleted | `removed: true` from changes.list | hard-delete from raw |
   | non-ingested | event for a file outside our designated folders, or in skip list | no-op |

3. Persist the new `nextPageToken` (or `newStartPageToken` when the stream
   exhausts) to the cursor **only after** the write phase succeeds.

**Cursor is fast-path, not authoritative.** Reconciliation (Lock 6) is the
safety net that catches drift (cursor expiry, missed events, ACL changes
that hide a file from one run and re-expose it later, etc.). Cron schedules
both: incremental hourly, full reconciliation daily.

**Cursor expiry**: if `changes.list` returns 410 Gone (token expired), the
robot deletes the cursor and falls through to first-run behavior (full
reconciliation).

## Lock 8 — Robot CLI

```
ingest-drive.py
  --account <email>             required; e.g. adithya@outerscope.xyz
  [--workspaces <a,b,c>]        subset; default = every workspace claiming a folder
                                from this account in its sources.yaml
  [--mode reconcile|incremental] default: reconcile (v1; flips to incremental once Lock 7 ships)
                                 reconcile = full Lock 6 enumeration
                                 incremental = Lock 7 cursor-driven (first-run falls back to reconcile)
  [--dry-run]                   parse + render, no writes/deletes; cursor untouched
  [--show]                      in --dry-run, print full content to stdout
  [--max-files <int>]           hard cap on files processed (debugging)
  [--folder <id>]               restrict to one designated folder ID (debugging)
  [--reset-cursor]              delete cursor; force full reconciliation
  [--no-content]                skip text extraction; write frontmatter-only files
                                (debugging path mapping without paying extraction cost)
  [--run-id <id>]               tag for ledger / log lines
```

**flock** at `/tmp/com.adithya.ultron.ingest-drive-<account-slug>.lock`.
Concurrent invocation for the same account exits 0 silently. (Different
accounts run in parallel.)

## Lock 9 — Slug derivation

**Account slug**: same algorithm as Gmail. Defined in Lock 1.

**Folder segment slug** (each Drive folder name in `<folder-path>`):
1. NFKD-normalize → ASCII (drop combining marks).
2. Lowercase.
3. Replace any run of non-`[a-z0-9]` characters with `-`.
4. Strip leading/trailing `-`.
5. Truncate to 60 characters.
6. If empty after the above, use `untitled-folder`.

**File slug** (Drive file name → `<file-slug>`):
1. Strip the file extension if present (slug is the stem; the renderer adds
   the canonical extension per Lock 1).
2. Apply the folder-segment slug pipeline (steps 1–5 above).
3. If empty, use `untitled-file`.

**File ID short**: first 8 characters of the Drive file ID, lowercased, with
any non-`[a-z0-9]` character replaced by `_`. Drive IDs are base64url-ish
and can contain `-` and `_`; the substitution keeps the slug filename-safe
without losing uniqueness (the full ID is in frontmatter).

**Collision handling**: `(file-slug, file-id-short)` is unique by
construction — Drive guarantees `file_id` is globally unique, so the 8-char
prefix collides only when two files share their first 8 chars (~1 in 4
billion for a typical Drive ID alphabet). If a collision IS detected at
write time, append more chars from the file ID (`__<file-id-12>`); robot
logs a warning so the operator can spot it.

## Lock 10 — sources.yaml drive block

In each workspace's `config/sources.yaml`:

```yaml
sources:
  drive:
    accounts:
      - account: adithya@outerscope.xyz
        folders:
          - id: 1abcDEF_folder_id        # from the Drive folder URL
            name: "Eclipse Labs"          # human-readable, for config clarity
          - id: 2ghiJKL_folder_id
            name: "Investor Updates"
            exclude_subfolders:
              - id: 9xyzPDQ_drafts_folder_id
                name: "Drafts"
      - account: adithya.shak.kumar@gmail.com
        folders:
          - id: 3mnoSTU_folder_id
            name: "Personal Documents"
```

Schema:
- `accounts[].account` — required. Full email; must match a credential file.
- `accounts[].folders[].id` — required. Drive folder ID (from the URL).
- `accounts[].folders[].name` — required. Human-readable name.
  Configuration-only; the robot does NOT use this for routing or matching.
  It exists so the YAML reads sensibly when the operator audits it.
- `accounts[].folders[].exclude_subfolders[]` — optional. Each entry is
  `{ id, name }`. The validator (`_shell/bin/validate-drive-config.py`)
  confirms each `exclude_subfolders[].id` is a descendant of the parent
  folder when run with `--live`.
- Designated folders are **recursive by default** (descend into every
  subfolder, except those listed in `exclude_subfolders`).

**Multi-account on one Drive identity**: each unique upstream `account` gets
its own robot invocation (one credential file, one cursor, one flock).
Multiple accounts in the same workspace are fine; they fan out to N robot
runs.

**Multi-workspace claims**: by default, a folder ID is claimed by exactly
one workspace. If two workspaces claim the same folder ID, the validator
flags it as an error. To intentionally fork a folder into multiple
workspaces, the routing layer (deferred to a later session) introduces an
`also_route_to:` mechanism in `sources.yaml`.

## Forbidden behaviors (immutable contract)

The robot **NEVER**:
1. Writes outside the deterministic raw path defined in Lock 1.
2. Runs LLM / vision calls during ingest. Text extraction via `pdftotext` /
   `markitdown` / Drive native exports is fine; everything else is
   metadata-only.
3. Writes metadata-only files for skipped types (Lock 5). Skipped means
   skipped — no record in raw.
4. Preserves files that have left their designated folder. Reconciliation
   (Lock 6) hard-deletes them.
5. Modifies Drive in any way. All operations are read-only (`files.list`,
   `files.get`, `files.export`, `changes.list`, `permissions.list`). Even
   though the OAuth scope is over-permissioned (`drive`, not
   `drive.readonly`) for legacy reasons, the robot is hard-coded to
   read-only API methods.
6. Fetches images, embedded media, attachment binaries, or comments.
7. Exports Sheets beyond the first tab in v1.
8. Deletes a folder out from under another workspace's claim (each robot
   run is scoped to one account; reconciliation only enumerates folders
   declared for THAT account in `sources.yaml`).
9. Edits frontmatter post-write, except `last_re_ingested_at` and
   `re_ingest_count` on subsequent re-ingests. Every other field is
   re-derived from scratch.

## Cross-references

- Workflow: `CONTEXT.md`. Setup / OAuth / activation: `SETUP.md`.
- Routing: `route.py`. Validator: `_shell/bin/validate-drive-config.py`.
- Universal envelope check: `_shell/bin/check-frontmatter.py`.
- Credential inventory: `_credentials/INVENTORY.md`.
