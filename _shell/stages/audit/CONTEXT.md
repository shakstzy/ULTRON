# Stage: audit

## Purpose
Cross-workspace conscience. Surfaces problems for human review. NEVER auto-fixes anything.

## Invocation
`run-stage.sh audit` (no workspace argument — runs across all)

## Inputs
- All workspaces' `wiki/`, `_meta/log.md`, `_meta/lint-*.md`.
- `_graphify/GRAPH_REPORT.md` (latest run, if available).
- `_global/entities/`, `_global/agent-learnings.md`.

## Process
Run these checks:

1. **Misplaced content** — Entity in workspace A's `wiki/` whose raw citations are mostly from workspace B. Surface "consider moving or splitting."
2. **Alias collisions** — Same name with different slugs across workspaces. Cross-check against `_global/entities/`.
3. **Stale workspaces** — No ingests in 30 days.
4. **Schema drift across workspaces** — Same entity type defined inconsistently.
5. **Backfill patterns** — Entities mentioned 3+ times in raw without wiki page.
6. **Graphify surprises** — Read `GRAPH_REPORT.md` "Unexpected connections" or equivalent section; flag cross-workspace links that look meaningful.
7. **Global stub freshness** — Run `build-backlinks.py` and refresh global stubs' `## Backlinks` sections.
8. **`_global/agent-learnings.md` length** — If over 100 lines, propose compaction in `_meta/agent-learnings-compaction-proposal.md`.

## Outputs
- `_audit/weekly/<YYYY-WW>.md` with sections per check.
- Refreshed `_global/entities/<type>/<slug>.md` `## Backlinks` sections (this is the ONE thing audit writes — but only the auto-generated backlink section).

## Idempotency
Yes. Read-only on workspace content; only writes are global backlink sections (deterministic from current state) and the audit report itself.
