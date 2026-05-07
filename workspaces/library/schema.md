# Library Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| book | `wiki/entities/books/` | A book ingested from Anna's Archive / LibGen, or a manual deposit. |
| paper | `wiki/entities/papers/` | An academic paper (arxiv, doi, or PDF URL). |
| article | `wiki/entities/articles/` | A web article / blog post via defuddle. |
| podcast | `wiki/entities/podcasts/` | A podcast episode (transcript-based). Reserved for future ingest. |
| lecture | `wiki/entities/lectures/` | A standalone talk / lecture / course session. Reserved for future ingest. |
| youtube-video | `wiki/entities/youtube-videos/` | A single YouTube video, transcript ingested. |
| youtube-channel | `wiki/entities/youtube-channels/` | A YouTube channel (collection of videos). |
| reel | `wiki/entities/reels/` | An Instagram reel (caption + transcript + visual description). |
| person | `wiki/entities/people/` | Author, speaker, channel host, paper author, interviewer, interviewee. |
| concept | `wiki/concepts/` | An idea recurring across 3+ sources, auto-promoted by the wiki agent. |

## Curator-owned fields (all source types)

The curator (`bin/library-next.py`) reads and writes these fields. The wiki agent sets them on creation only and never modifies them after.

| Field | Type | Values |
|---|---|---|
| `read_status` | string | `queued`, `ingesting`, `ingested`, `summarized`, `delivered`, `archived` |
| `delivered_at` | date or null | Last time the curator served this entity. Null if never. |
| `bite_size_minutes` | integer | Estimated minutes to absorb the takeaways. Wiki agent sets at creation; curator reads only. |
| `delivery_count` | integer | Number of times served by the curator. Defaults to 0. |

## Wiki-agent-owned fields (all source types)

| Field | Type | Values |
|---|---|---|
| `slug` | string | Per `nomenclature.md`. Kebab-case ASCII. |
| `type` | string | One of the entity types above. |
| `tags` | list of strings | Topic / domain tags. Free-form. Used by curator for variety scoring. |
| `mentioned_concepts` | list of concept slugs | Used for concept promotion at 3+ source threshold. |
| `mentioned_books` | list of book slugs | Used for the hybrid book-video co-location resolver. |
| `last_touched` | date | YYYY-MM-DD. Updated on meaningful content change. |

## Per-type page format

### book

```yaml
---
slug: <author-last>-<title-3-words>     # e.g. clear-atomic-habits
type: book
title: <Title in Title Case>
authors: [<person-slug>...]
isbn: <isbn-or-null>
year: <integer-or-null>
language: en
source_url: <annas-archive-url-or-null>
ingested_at: <YYYY-MM-DD>
read_status: ingested
delivered_at: null
bite_size_minutes: <integer>
delivery_count: 0
tags: [<tag>...]
mentioned_concepts: []
mentioned_books: []
last_touched: <YYYY-MM-DD>
---
```

Body sections in order: `## TL;DR`, `## Key takeaways`, `## Quote`, `## Why it matters`, `## Connections`, `## Backlinks`.

### paper

```yaml
---
slug: <first-author>-<title-3-words>-<year>
type: paper
title: <Title>
authors: [<person-slug>...]
venue: <journal-or-conference-or-null>
year: <integer>
arxiv_id: <id-or-null>
doi: <doi-or-null>
source_url: <url>
ingested_at: <YYYY-MM-DD>
read_status: ingested
delivered_at: null
bite_size_minutes: <integer>
delivery_count: 0
tags: [<tag>...]
mentioned_concepts: []
mentioned_books: []
last_touched: <YYYY-MM-DD>
---
```

### article

```yaml
---
slug: <source-domain>-<title-4-words>
type: article
title: <Title>
authors: [<person-slug>...]
source_domain: <domain>
url: <full-url>
published_at: <YYYY-MM-DD-or-null>
ingested_at: <YYYY-MM-DD>
read_status: ingested
delivered_at: null
bite_size_minutes: <integer>
delivery_count: 0
tags: [<tag>...]
mentioned_concepts: []
mentioned_books: []
last_touched: <YYYY-MM-DD>
---
```

### youtube-video

```yaml
---
slug: <channel-handle>-<title-4-words>
type: youtube-video
title: <Title>
video_id: <11-char-yt-id>
url: <youtube-url>
channel: <channel-slug>
channel_handle: <@handle>
authors: [<person-slug>...]      # speakers / hosts identified
duration_minutes: <integer>
published_at: <YYYY-MM-DD>
ingested_at: <YYYY-MM-DD>
read_status: ingested
delivered_at: null
bite_size_minutes: <integer>     # usually duration_minutes / 3 — transcript reads faster than the video runs
delivery_count: 0
tags: [<tag>...]
mentioned_concepts: []
mentioned_books: []               # if non-empty, video is co-located under one of these books
last_touched: <YYYY-MM-DD>
---
```

### youtube-channel

```yaml
---
slug: <channel-handle>
type: youtube-channel
title: <Channel Name>
handle: <@handle>
url: <channel-url>
host: [<person-slug>...]
subscriber_count_at_ingest: <integer-or-null>
video_count_ingested: <integer>
first_ingested_at: <YYYY-MM-DD>
last_ingest_at: <YYYY-MM-DD>
tags: [<tag>...]
last_touched: <YYYY-MM-DD>
---
```

Channel pages are reference-only (no `read_status`). They aggregate links to per-video entity pages.

### reel

```yaml
---
slug: <creator-handle>-<YYYY-MM-DD>-<5char>
type: reel
url: <instagram-url>
creator_handle: <@handle>
authors: [<person-slug>...]
caption: <single-line-truncated>
duration_seconds: <integer>
published_at: <YYYY-MM-DD>
ingested_at: <YYYY-MM-DD>
read_status: ingested
delivered_at: null
bite_size_minutes: 1                    # reels are always 1-minute bites
delivery_count: 0
tags: [<tag>...]
mentioned_concepts: []
mentioned_books: []
last_touched: <YYYY-MM-DD>
---
```

### person

```yaml
---
slug: <first>-<last>
type: person
canonical_name: <Full Name>
role: [author, speaker, channel-host, interviewer, interviewee]   # multi-valued
domain: <e.g. neuroscience, economics, philosophy>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Context`, `## Authored / hosted`, `## Backlinks`. Promotion to `_global/entities/people/` happens via the `promote-entity` skill when the person crosses workspaces.

### concept

```yaml
---
slug: <kebab-noun-phrase>
type: concept
sources: [<entity-slug>...]      # all source pages where this concept appears
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Definition`, `## How sources frame it`, `## Synthesis`, `## Backlinks`.

## Vocabulary

- **the corpus** — everything in this workspace's `wiki/`
- **a bite** — one curator output (one entity's TL;DR + takeaways), sized for the moment
- **TIL** — today-I-learned takeaway
- **promote** — when a concept appears in 3+ sources, lift to `wiki/concepts/`
- **internalized voice** — takeaways rewritten in Adithya's voice, not author-faithful
- **provenance quote** — the one ≤ 15 word quote per page that anchors the takeaways to the source

## Hard rule on quotes

Per ULTRON copyright rules: at most ONE direct quote per wiki page, ≤ 15 words, in quotation marks, with attribution (`— <Author>, <chapter / page / timestamp>`). Do NOT reproduce paragraphs of source material. The full source content lives in `raw/`, gitignored for books and papers.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent and applied by Adithya manually. Lint agent never modifies this file directly.
