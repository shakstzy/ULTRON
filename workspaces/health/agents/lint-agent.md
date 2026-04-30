# Lint Agent — Health

Read-only audit. You only propose.

## Inputs

- All wiki pages, all `_meta/*` files.
- `schema.md`, `learnings.md`, `identity.md`, `nomenclature.md`.
- Output of `_shell/bin/check-routes.py --workspace health`.
- Output of `_shell/bin/build-backlinks.py --dry-run --workspace health`.

## Process

Write `_meta/lint-<YYYY-MM-DD>.md` with sections:

### 1. Route integrity
Broken wikilinks: `path:line → broken-target`.

### 2. Schema drift
Pages missing required frontmatter (especially `units:` on vitals), wrong type folder, unknown enum values.

### 3. Stale entities
- Workout `status: active` with no session in 30+ days → flag.
- Supplement `status: active` with no `last_touched` update in 60+ days → flag.
- Provider with no visit in 365 days → recommend `status: archived` (not auto).

### 4. Backfill candidates
Entities mentioned 3+ times in raw without their own page.

### 5. Schema-specific rules (Health)

- Flag any vital reading without explicit units in the value (e.g., a bullet like `- 2026-04-15: 175` should be `- 2026-04-15: 175 lb`).
- Flag any date format that isn't ISO `YYYY-MM-DD`.
- Flag any wiki page that contains a specific lab value that should have stayed in `raw/`.
- Flag any workout entity with sessions on dates that aren't ISO format.
- Flag any supplement entity with `dose` field missing units.

### 6. Schema-proposal accumulation
Entries open > 14 days.

### 7. Learning-proposal accumulation
Entries open > 7 days.

## Output

`_meta/lint-<YYYY-MM-DD>.md`. Each finding: location, evidence, recommendation. NO fixes. If zero issues, write "No issues found."
