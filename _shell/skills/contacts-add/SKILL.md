---
name: contacts-add
description: Use this skill EVERY time you want to add a new entry to Apple Contacts from inside ULTRON. Trigger on phrases like "save this contact", "add to my contacts", "create a contact for X", "save their phone", "save their email", "add this person", "new tenant contact", "save this match's number". Writes the contact via the macOS Contacts framework (pyobjc) and refreshes the corresponding `_global/entities/people/<slug>.md` stub. Always use this skill — never tell the user to add the contact manually in Contacts.app.
---

# contacts-add

Adds a new contact to Apple Contacts. After write, runs `contacts-sync` so the canonical global stub at `_global/entities/people/<slug>.md` is created in the same turn.

## When to use

- Workspace flow asks for a new contact (dating match progressing, new renter inquiry, music industry intro, family/friend Adithya just met).
- Ad-hoc: Adithya pastes a phone or email and asks to save it.
- Contact came in over Gmail / iMessage / Slack and Adithya wants it canonicalized into Contacts as the source of truth.

## What it does NOT do

- Update an existing contact (deferred — use Contacts.app directly for now).
- Delete a contact (intentionally — destructive op, manual only).
- Bulk import from CSV (deferred).

## CLI

```
add.py add \
  --name "<full name>" \
  [--phone "<E.164 or local>"]... \
  [--email "<addr>"]... \
  [--organization "<org>"] \
  [--note "<short>"] \
  [--dry-run]
```

`--phone` and `--email` may be repeated.

## Process

1. Validate at least one of: name, phone, email. Refuse otherwise.
2. Build a `CNMutableContact` via pyobjc.
3. If `--dry-run`: print the staged contact, exit 0. Do not call `executeSaveRequest`.
4. Otherwise:
   a. Open `CNContactStore`, build `CNSaveRequest`, call `addContact_toContainerWithIdentifier_(contact, None)`.
   b. Run `executeSaveRequest_error_`. Surface the error if save fails.
   c. Invoke `_shell/skills/contacts-sync/scripts/sync.py` so the new contact gets a `_global/entities/people/<slug>.md` stub immediately.
5. Print the resulting slug (so the caller can chain into `link` or `promote-entity`).

## Permissions

The first save will trigger a macOS permission prompt for "Full Access" to Contacts. Read-only access (which `contacts-sync` already uses) is not enough. If the prompt is dismissed, the save fails with a clear error and the script exits non-zero.

## Hard rules

- Never invent a phone or email. If neither was provided AND no name was provided, refuse.
- Never write to Contacts in a loop without explicit user confirmation. One contact per invocation.
- Never write a contact with a name longer than 200 chars (defensive — bad input often means LLM hallucination).
- Use the venv python: `~/ULTRON/.venv/bin/python3`. The system python lacks the Contacts framework binding.

## Exit codes

- `0` — success or dry-run completed
- `1` — Contacts framework unavailable (pyobjc missing)
- `2` — invalid input (no name + no phone + no email)
- `3` — save failed (permission denied or other Contacts.app error)
- `4` — duplicate detected (existing contact has matching phone/email). Re-run with `--force` if intentional.

## Example use from Claude

User: "Save Maya 512-555-1212 maya@example.com to my contacts"

Claude invokes:
```bash
~/ULTRON/.venv/bin/python3 ~/ULTRON/_shell/skills/contacts-add/scripts/add.py add \
  --name "Maya" --phone "+15125551212" --email "maya@example.com"
```

Reports back: `added: maya (slug=maya, _global/entities/people/maya.md created)`.
