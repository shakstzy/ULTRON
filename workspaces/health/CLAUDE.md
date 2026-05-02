---
workspace: health
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Health — Workspace Router

You are in workspace `health` — Adithya's health, fitness, nutrition, sleep, and medical context.

## What this workspace is

Workout logs, nutrition, vitals (weight, BP, resting HR, HRV), sleep patterns, supplements taken, medical history (providers, visits, labs). Pure factual archive — synthesis surfaces patterns over time.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — clinical voice override
4. `nomenclature.md` — file-system routing

## Voice

Clinical, factual, low-emotion. Units explicit on every measurement (lb, kg, mg, mins, bpm, ms). Dates always present. No interpretation beyond what the source supports. See `identity.md`.

## Hard rules (workspace-specific)

1. Every measurement has units in frontmatter or inline.
2. Dates are ISO `YYYY-MM-DD`. No fuzzy "last week."
3. Medical specifics (lab values, prescriptions, diagnoses) live in `raw/` only — wiki summarizes patterns, not clinical specifics.
4. Commit messages: `chore(health): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What's my recent weight trend? | `wiki/synthesis/weight-trend.md` (regenerated weekly) |
| What was my last workout? | `wiki/entities/workouts/<latest-slug>.md` or `raw/manual/<latest>/` |
| What supplements am I on? | `wiki/entities/supplements/` (current = `status: active`) |
| Who's my doctor for X? | `wiki/entities/providers/<x>.md` |
| What did my last lab say? | `raw/manual/<latest>/labs/...` |

## Agents

- `agents/wiki-agent.md`
- `agents/lint-agent.md`

## Sources

Manual notes (workout logs, weigh-ins), Apple Health export (CSV/XML), filtered Gmail (lab results, doctor follow-ups). Ingest deferred until credentials provisioned.
