# Stage: lint

## Purpose
Read-only health check on a single workspace.

## Invocation
`run-stage.sh lint <workspace>`

## Inputs
- All files in `workspaces/<ws>/`.
- `workspaces/<ws>/agents/lint-agent.md` (the per-workspace agent prompt with schema-specific rules baked in).
- Output of `_shell/bin/check-routes.py --workspace <ws>`.
- Output of `_shell/bin/build-backlinks.py --dry-run --workspace <ws>`.

## Process
1. Run `check-routes.py` and `build-backlinks.py --dry-run`. Capture outputs to `_shell/runs/<RUN_ID>/output/`.
2. Load the per-workspace lint agent prompt.
3. Run the lint agent over the workspace.
4. Lint agent writes `_meta/lint-<YYYY-MM-DD>.md`.

## Outputs
- `_meta/lint-<YYYY-MM-DD>.md` with all findings.
- Run artifacts in `_shell/runs/<RUN_ID>/`.

## Idempotency
Yes. Read-only.

## What lint never does
- Never modifies wiki/, schema.md, learnings.md, nomenclature.md.
- Never deletes any file.
- Never auto-fixes broken routes — only reports.
