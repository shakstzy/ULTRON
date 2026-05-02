---
name: contacts-sync
description: Use this skill EVERY time you want to synchronize Apple Contacts into `_global/entities/people/` as canonical entity stubs. Always bypasses `raw/` — Contacts is reference data, not a stream. Trigger on phrases like "sync contacts", "update people", "refresh contact stubs", "import my contacts", "pull Apple Contacts". Always use this skill — never manually create `_global/entities/people/` files.
---

# contacts-sync

Reads Apple Contacts via the macOS AppleScript bridge. For each contact, upserts `_global/entities/people/<slug>.md`. Body content (any prose Adithya or the wiki agent has written) is preserved across runs; frontmatter is overwritten because Contacts is the source of truth for identity / handles.

## When to use

- Nightly via launchd (cron lives in `_shell/config/global-schedule.yaml` → `apple_contacts_sync`).
- Manually after a big batch of contact edits in Apple Contacts.
- After Apple Contacts merges with iCloud changes from another device.

## Process

1. Query `Contacts.app` via `osascript`. The skill emits a small AppleScript that returns one line per contact in a parseable shape.
2. For each contact:
   a. Derive a stable slug per the priority below.
   b. Compute `content_hash` over the parsed identifiers + display name (NOT over the body).
   c. Read the existing `_global/entities/people/<slug>.md` if present. Preserve the body verbatim. Overwrite the frontmatter.
   d. If new: write a fresh file with placeholder body `## Notes\n\n(populated by user / wiki agent)\n\n## Backlinks\n\n(rebuilt by build-backlinks.py)\n`.
3. After all contacts processed, run `_shell/bin/build-backlinks.py` so the new stubs get backlink sections.
4. Log summary: `<N> total, <M> new, <K> updated, <U> unchanged, <C> conflicts`.

## Slug derivation (priority)

1. Apple Contacts full name → kebab-case ASCII, max 40 chars.
2. Email local-part + domain stem (`sydney@eclipse.audio` → `sydney-eclipse`).
3. E.164 phone (`+15125551234` → `phone-15125551234`).
4. Hash-prefix fallback (`unknown-a1b2c3d4`).

The slug is recorded in frontmatter `slug:` and is stable forever once chosen, even if the contact later gets a name in Contacts.

## Frontmatter (overwritten on every run)

```yaml
---
source: apple-contacts
workspace: _global
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3 of identifiers + display name>
provider_modified_at: <Apple Contacts modificationDate>

title: Sydney Hayes
slug: sydney-hayes
type: person
canonical_uri: lifeos:_global/entities/people/sydney-hayes
aliases: ["Syd"]
identifiers:
  email: ["sydney@eclipse.audio", "sydney.hayes@gmail.com"]
  phone: ["+15125551234"]
  slack: []
last_synced: <ISO 8601>
global: true
---
```

## Body (preserved, never touched after first creation)

```markdown
## Notes

(populated by user / wiki agent)

## Backlinks

(rebuilt by build-backlinks.py)
```

## Self-review (~150 tokens)

- Every Contacts entry produced a corresponding `_global/entities/people/<slug>.md`.
- No identifier collisions: two slugs claiming the same email or phone.
- Body content of pre-existing files is byte-identical before/after.
- `build-backlinks.py` ran and the new stubs have non-empty `## Backlinks` (or "(no workspace pages reference this entity)" if none yet).
- Conflict count is zero in the log; if non-zero, list each conflict for manual resolution.

## Hard rules

- Body is never modified after first creation.
- Frontmatter overwritten in full each run — local manual edits to frontmatter will be lost.
- No `raw/` files created. Contacts data does NOT flow through workspace `ingested.jsonl` ledgers.
- Permissions error from Contacts.app → log and exit 0; the skill is best-effort and must not block other scheduled jobs.
