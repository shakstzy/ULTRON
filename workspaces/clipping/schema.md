# Clipping Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| source | `wiki/entities/sources/` | A creator / channel / podcast / livestream Adithya clips from. |
| clip | `wiki/entities/clips/` | A single clip artifact (file lives outside git, referenced by content hash). |
| niche | `wiki/entities/niches/` | A content niche / vertical (e.g. `crypto-doomsday`, `mens-health`, `startup-stories`). |
| hook-pattern | `wiki/entities/hook-patterns/` | A repeatable opening / cold-cut style that performs (e.g. `cold-controversy`, `surprise-stat`). |
| campaign | `wiki/entities/campaigns/` | A bounty campaign on Whop / Vyro / etc. Tracks payout and total earnings. |
| person | `wiki/entities/people/` | Creator (often same as source) / contact at Whop / Vyro / sponsor. |

## Per-type page format

### source

```yaml
---
slug: <creator-handle-kebab>
type: source
platform: <youtube | twitch | tiktok | podcast | other>
handle: <native-handle>
url: <canonical-url>
last_clipped: <YYYY-MM-DD>
status: <active | dormant | banned-from-clipping>
---
```

Body sections: `## Source notes`, `## What clips well`, `## Avoid`, `## Backlinks`.

### clip

```yaml
---
slug: <YYYY-MM-DD>--<source-slug>--<topic-kebab>
type: clip
source: <source-slug>
niche: <niche-slug>
hook_pattern: <hook-pattern-slug>
duration_seconds: <number>
content_hash: <blake3>             # references file in external scratch
external_path: <path>              # NOT in git
created_at: <YYYY-MM-DD>
distributed_to: [tiktok, ig, yt-shorts]
status: <draft | shipped | taken-down | archived>
---
```

Body sections: `## Caption`, `## Performance`, `## Backlinks`.

### niche

```yaml
---
slug: <kebab>
type: niche
status: <experiment | active | retired>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Audience`, `## What works`, `## What does not`, `## Top clips`, `## Backlinks`.

### hook-pattern

```yaml
---
slug: <kebab>
type: hook-pattern
example_clips: [<clip-slug>...]
performance_baseline: <number>      # avg completion rate
last_touched: <YYYY-MM-DD>
---
```

### campaign

```yaml
---
slug: <platform>--<campaign-name>
type: campaign
platform: <whop | vyro | other>
sponsor: <company-slug>
start_date: <YYYY-MM-DD>
end_date: <YYYY-MM-DD>
payout_per_unit: <number>
total_earned_usd: <number>
status: <active | ended | banned>
---
```

### person

Standard person frontmatter plus `role: <creator | sponsor-contact | platform-contact | other>`.

## Vocabulary

- "source" — original long-form content
- "clip" — short-form derivative ready to ship
- "niche" — content vertical that has its own audience
- "hook" — first 1-3 seconds of a clip
- "pattern" — repeatable hook / structure that performs
- "ship" — distribute (PUBLISH-gated)

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent.
