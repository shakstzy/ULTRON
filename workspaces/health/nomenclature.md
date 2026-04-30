# Health Nomenclature

File-system conventions and routing for workspace `health`.

## File-system conventions

- Raw archive: `raw/<source>/<YYYY-MM>/<slug>.md`
- Apple Health exports: `raw/apple-health/<YYYY-MM>/<export-date>.md` (one file per export run, vitals as YAML lists).
- Manual workout logs: `raw/manual/<YYYY-MM>/<YYYY-MM-DD>-<workout-slug>.md`.
- Lab results: `raw/manual/<YYYY-MM>/labs/<YYYY-MM-DD>-<lab-name>.md`.
- Wiki entity pages: `wiki/entities/<type>/<slug>.md`.
- Synthesis pages: `wiki/synthesis/<topic-slug>.md`.

## Routing table — by query type

| Query type | Read first |
|---|---|
| "Recent weight trend?" | `wiki/synthesis/weight-trend.md` |
| "What was my last workout?" | latest file in `raw/manual/<latest>/` matching `*-workout-*` |
| "What supplements am I on?" | `wiki/entities/supplements/` filtered by `status: active` |
| "Who's my X provider?" | `wiki/entities/providers/<x>.md` |
| "Last lab values?" | `raw/manual/<latest>/labs/` |

## When the wiki agent appends a vital reading

1. Read the raw entry (Apple Health export row, or manual entry).
2. Append a dated bullet to `wiki/entities/vitals/<vital-slug>.md` `## Recent values` section.
3. Update `last_touched` frontmatter.
4. If 3+ new readings since last synthesis update, regenerate `wiki/synthesis/<vital>-trend.md`.

## When the wiki agent appends a workout session

1. Match the workout to an existing `wiki/entities/workouts/<slug>.md` (by name, kebab-cased).
2. If no match, create the workout entity from `schema.md` template.
3. Append a dated bullet to `## Sessions`.
4. Update `last_touched`.
