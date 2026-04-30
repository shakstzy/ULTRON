# Shell Tier

You are in `_shell/`, the operational machinery for ULTRON. None of the user's domain content lives here. Everything in this tier is plumbing.

## Layout

- `stages/<stage>/CONTEXT.md` — The six stage contracts: `ingest`, `query`, `lint`, `audit`, `bootstrap`, `weekly-review`. Each ≤ 80 lines.
- `bin/` — Deterministic plumbing scripts (`run-stage.sh`, `check-routes.py`, `build-backlinks.py`, ingest scripts, etc.).
- `agents/` — Cross-workspace agent prompts (`audit-agent.md`, `bootstrap-agent.md`). Per-workspace agents live at `workspaces/<ws>/agents/`.
- `skills/` — Global skill manifests. Workspace-local skills live at `workspaces/<ws>/skills/`.
- `runs/<RUN_ID>/` — Ephemeral per-run state. Created by `run-stage.sh`, archived after. Gitignored.
- `plists/` — launchd plist source files. Versioned in git. Symlinked into `~/Library/LaunchAgents/` manually.
- `budget.yaml` — API spend cap config (currently disabled — Adithya is on Claude Max sub).

## How to invoke a stage

```bash
~/ULTRON/_shell/bin/run-stage.sh <stage> [<workspace>]
```

The dispatcher acquires a flock, builds the prompt by concatenating root CLAUDE.md → stage CONTEXT.md → workspace CLAUDE.md (if scoped), then dispatches to the stage-specific handler.

## Hard rules

1. Bin scripts are deterministic. No LLM calls without going through a stage contract.
2. Stage contracts are short (≤ 80 lines). Anything longer goes in the agent prompt or workspace files.
3. Agent prompts (`agents/*.md`) are loaded from disk by `run-stage.sh`. Never inlined.
4. Per-source ingest failures are isolated. One source failing does not abort sibling sources in the same workspace.

## When something breaks

- launchd job crashed → check `_logs/<job-name>.{out,err}.log`.
- Wikilink broken → run `bin/check-routes.py` and follow the route-maintenance contract.
- Bootstrap interview produced something off → re-run `run-stage.sh bootstrap <ws>` after `rm -rf workspaces/<ws>` (one-shot, idempotent abort if exists).
