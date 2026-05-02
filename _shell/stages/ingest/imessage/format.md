# Format: imessage

## File granularity
One markdown file per `(contact, year-month)`. Group chats live in `groups/<slug>/...`; 1:1 chats in `individuals/<slug>/...`.

## Path
`workspaces/<ws>/raw/imessage/{individuals|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md`

## Slug derivation (priority, recorded once in `_profiles/<slug>.md`)
1. Apple Contacts full name → kebab-case ASCII, max 40 chars.
2. Email local-part + domain stem (`sydney@eclipse.audio` → `sydney-eclipse`).
3. E.164 phone (`+15125551234` → `phone-15125551234`).
4. Hash-prefix fallback (`unknown-a1b2c3d4`).

Slug is stable forever once chosen. The `_profiles/<slug>.md` file records:
```yaml
---
slug: sydney-hayes
contact_type: individual
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes
slug_derivation: contacts_full_name
first_seen: 2024-08-12
---
```

## Frontmatter (per month file)

```yaml
---
source: imessage
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <latest message date in this month>

contact_slug: sydney-hayes
contact_type: individual                       # individual | group
contact_handles: ["+15125551234", "sydney@eclipse.audio"]
contact_name: Sydney Hayes
month: 2026-04
date_range: [2026-04-02, 2026-04-29]
message_count: 142
attachments:
  - { id: 8473, filename: IMG_2384.HEIC, mime: image/heic, size_bytes: 4321099 }
chat_db_message_ids: { min: 12483, max: 13901 }
---
```

## Body

```markdown
# Sydney Hayes — April 2026

## 2026-04-02 (Tuesday)

**09:14 — Sydney:** want to grab dinner thursday?
**09:21 — me:** yes book me
**09:22 — Sydney:** [reaction: laugh to "yes book me"]

## 2026-04-04 (Thursday)

**18:43 — Sydney:** running 10 min late
**18:44 — me:** np
> **18:45 — Sydney (replying to "np"):** thanks ❤️
**19:02 — me:** [unsent at 19:03]
**19:05 — me (edited):** outside, table by the window
```

Conventions:
- Day groups: `## YYYY-MM-DD (DayOfWeek)` headers.
- Lines: `**HH:MM — sender:** body`. Sender is display name from Contacts, or `me` for outgoing.
- Reactions: `[reaction: <type> to "<original snippet>"]`.
- Replies (iOS message replies): `> **HH:MM — sender (replying to "<snippet>"):** body`.
- Edits: `(edited)` flag on the latest version, prior version preserved as a `> previously: ...` line below if material.
- Unsends: `[unsent at HH:MM]` (preserves the existence of the message, not its body).
- Attachments referenced by `_id_` only; content extraction deferred to wiki promotion.

## Pre-filter
- Skip handles matching `_shell/config/imessage-routing.yaml` `skip_handles`.
- Skip groups matching `skip_groups`.
- Skip if total message body bytes for the month + attachment metadata > 5 MB (large group chats need separate handling).

## Dedup key
`imessage:<contact_slug>:<YYYY-MM>` — month granularity.
Same key + same content_hash → skip. Different hash → overwrite.

## Default for unrouted contacts
**SKIP** (privacy-first; opposite of Gmail). Workspaces must explicitly allowlist contacts in their `sources.yaml` for them to land.
