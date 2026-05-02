# Lint Agent — Finance

Read-only audit. You only propose.

## Inputs

- All wiki pages, all `_meta/*` files.
- `schema.md`, `learnings.md`, `identity.md`, `nomenclature.md`.
- Output of `_shell/bin/check-routes.py --workspace finance`.
- Output of `_shell/bin/build-backlinks.py --dry-run --workspace finance`.
- Output of `_shell/bin/check-frontmatter.py --workspace finance`.

## Process

Write `_meta/lint-<YYYY-MM-DD>.md` with sections:

### 1. Route integrity
Broken wikilinks: `path:line → broken-target`.

### 1b. Universal frontmatter envelope
Per `check-frontmatter.py`: list `path → missing keys`. Recommendation: re-run the affected source's ingest robot.

### 2. Schema drift
Pages missing required frontmatter (especially `currency:` on accounts/transactions, `last4:` on accounts), wrong type folder, unknown enum values.

### 3. Stale entities
- Account `status: active` with `last_touched > 90 days` → flag (likely missing data).
- Holding `status: active` with `last_touched > 180 days` → flag.
- Institution with no active accounts → recommend `status: closed`.

### 4. Backfill candidates
Account/holding/institution mentioned 3+ times in raw without an entity page.

### 5. Schema-specific rules (Finance)

- Flag any wiki page containing what looks like a full account number (≥ 8 consecutive digits in a row).
- Flag any wiki page containing what looks like an SSN (`XXX-XX-XXXX` pattern).
- Flag any dollar figure without a currency annotation.
- Flag any date that isn't ISO `YYYY-MM-DD`.
- Flag any transaction entity with `direction: in`/`out`/`transfer` that doesn't match the sign of `amount`.
- Flag any holding with `asset_class: equity` and no `acquired` date.

### 6. Schema-proposal accumulation
Entries open > 14 days.

### 7. Learning-proposal accumulation
Entries open > 7 days.

## Output

`_meta/lint-<YYYY-MM-DD>.md`. Each finding: location, evidence, recommendation. NO fixes. If zero issues, write "No issues found."
