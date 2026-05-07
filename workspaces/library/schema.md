# Library Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| book | `wiki/entities/books/` | A book Adithya has read or is reading. |
| paper | `wiki/entities/papers/` | An academic paper. |
| article | `wiki/entities/articles/` | A web article / blog post. |
| podcast | `wiki/entities/podcasts/` | A podcast episode. |
| lecture | `wiki/entities/lectures/` | A talk / lecture / course session. |
| person | `wiki/entities/people/` | Author, speaker, interviewer, interviewee. |
| concept | `wiki/concepts/` | An idea recurring across 3+ sources, gets its own page. |

## Per-type page format

### book

```yaml
---
slug: <author-kebab>-<title-kebab>     # e.g. graeber-debt-first-5000
type: book
authors: [<person-slug>...]
isbn: <isbn>
year: <number>
read_status: <queued | reading | finished | abandoned>
finished_at: <YYYY-MM-DD>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Summary`, `## Key takeaways`, `## Quotes` (≤ 15 words each, attributed), `## Connections`, `## Backlinks`.

### paper

```yaml
---
slug: <first-author>-<short-title>-<year>
type: paper
authors: [<person-slug>...]
venue: <journal-or-conference>
year: <number>
arxiv_id: <id>
doi: <doi>
read_status: <queued | reading | finished | skimmed>
---
```

### article

```yaml
---
slug: <author>-<short-title>
type: article
authors: [<person-slug>...]
url: <url>
published_at: <YYYY-MM-DD>
read_at: <YYYY-MM-DD>
---
```

### podcast / lecture

Same shape as article, with `type: podcast` or `type: lecture`, plus `duration_minutes` and `host` / `speaker` field.

### person

Standard person frontmatter plus `role: <author | speaker | interviewer | interviewee>`.

### concept

```yaml
---
slug: <kebab>
type: concept
sources: [<book-or-paper-or-article-slug>...]
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Definition`, `## Sources`, `## Synthesis`, `## Backlinks`.

## Vocabulary

- "the corpus" — everything in this workspace's wiki
- "TIL" — today-I-learned takeaway
- "promote" — when a concept appears in 3+ sources, promote to `wiki/concepts/`

## Hard rule on quotes

Per ULTRON copyright rules: at most ONE direct quote per page, ≤ 15 words, in quotation marks, with attribution. Do NOT reproduce paragraphs of source material.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent.
