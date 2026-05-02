---
name: link
description: Use this skill EVERY time you want to assert a structured relationship between two entities. Trigger on phrases like "Sandeep is colleague of Jake at Eclipse", "link these two", "they work together", "X co-founded Y", "X reports to Y", "X invested in Y", "they're married", "X mentors Y". Writes a typed edge into the source entity's frontmatter `relationships:` block. Always use this skill — never hand-edit `relationships:` lists.
---

# link

Asserts a structured relationship between two entities. The edge is recorded in the source entity's frontmatter `relationships:` block. If the relationship is symmetric (`colleague`, `friend`, `married_to`, `co_founded`), the reciprocal edge is written automatically.

## When to use

- You learn a stable factual relationship from a raw source (Gmail, Slack, contacts).
- You want to seed a fact that audit / Graphify will later use to find clusters.
- You're cleaning up after a `/promote` and want to record edges between the now-global entity and its peers.

## Modes

### `add <subject-slug> <relation> <object-slug> [--directed] [--note "<short>"]`
Adds an edge `subject — relation → object`. Default is symmetric (writes reciprocal). `--directed` means the edge is one-way.

### `remove <subject-slug> <relation> <object-slug>`
Removes the edge from both pages (if symmetric).

### `list <slug>`
Prints all edges for the entity.

## Relation vocabulary

These relations are recognized as **symmetric** (auto-reciprocal):
- `colleague`, `friend`, `partner`, `married_to`, `co_founded`, `co_author`, `sibling`, `roommate`

These are **directed**:
- `reports_to` ↔ `manages`
- `mentors` ↔ `mentee_of`
- `invested_in` ↔ `investor_of`
- `founded` ↔ `founder_of`
- `client_of` ↔ `vendor_of`
- `parent_of` ↔ `child_of`

For directed edges, the skill writes one edge on the subject and the inverse on the object (`reports_to` on subject → `manages` on object).

Custom relations are allowed but are NOT auto-reciprocated unless `--symmetric` is passed. Custom relations should be kebab-case verbs (`introduced-via`, `funded-by`, `co-presented`).

## Frontmatter shape

```yaml
relationships:
  - { type: colleague,    target: jake-paul,           workspace: eclipse, asserted: 2026-05-01 }
  - { type: reports_to,   target: sydney-hayes,        workspace: eclipse, asserted: 2026-05-01 }
  - { type: invested_in,  target: outerscope-ventures, workspace: outerscope, asserted: 2026-04-15, note: "lead, $250K" }
```

## Process

1. Resolve the subject and object pages — prefer global stubs, fall back to workspace pages.
2. Append the edge to the subject's `relationships:` list. If the list doesn't exist, create it.
3. If symmetric (or directed with a known inverse), append the inverse edge to the object's page.
4. Run `_shell/bin/build-backlinks.py` (relationships flow into backlinks via the future audit logic; for now they sit in frontmatter awaiting consumption).
5. Verify `check-routes.py`.

## Outputs

- Edges in `relationships:` frontmatter on subject and object pages.
- Log line in `_logs/link.log`.

## Self-review

- The same `(subject, relation, object)` is not duplicated.
- Reciprocal exists for symmetric / known-directed relations.
- `check-routes.py` clean.
- The asserted date is today's ISO date.
