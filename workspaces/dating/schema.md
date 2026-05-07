# Dating Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| person | `wiki/entities/people/` | A match. Slug is `<first-name>-<platform>-<city>` for disambiguation. |
| date-event | `wiki/entities/dates/` | A specific in-person date that happened. |

## Per-type page format

### person

```yaml
---
slug: <first>-<platform>-<city>      # e.g. ashley-tinder-austin
type: person
platform: <tinder | bumble | hinge | imessage | other>
city: <city>
match_date: <YYYY-MM-DD>             # day of platform match
status: <active | dormant | unmatched | met-irl | dating | ended>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Context`, `## Conversation summary`, `## Met-IRL log`, `## Notes`, `## Backlinks`. Phone numbers and last names live in `raw/` only.

The bot creates these stubs automatically on every new match (`auto_stub: wiki/entities/people/<slug>.md` per `config/sources.yaml`).

### date-event

```yaml
---
slug: <person-slug>--<YYYY-MM-DD>
type: date-event
person: <person-slug>
date: <YYYY-MM-DD>
venue: <venue-name>
duration_hours: <number>
outcome: <good | mid | bad | ghosted | escalated>
---
```

Body sections: `## What happened`, `## Notes`, `## Followup`, `## Backlinks`.

## Vocabulary

- "match" — platform-side reciprocal swipe / like
- "thread" — ongoing message exchange
- "ghost" — unilateral stop replying with no resolution
- "escalate" — move from app to phone / iMessage / WhatsApp
- "met-IRL" — first in-person meeting
- "outbound" — bot-drafted message awaiting send / approval

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly.
