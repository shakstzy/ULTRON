# Stage: bootstrap

## Purpose
Interview-driven creation of a new workspace. One-shot.

## Invocation
`run-stage.sh bootstrap <new-workspace-slug>`

## Inputs
- `workspaces/_template/` skeleton.
- `_shell/agents/bootstrap-agent.md` (interview script).
- Interactive user input.

## Process
1. Copy `workspaces/_template/` to `workspaces/<new-workspace-slug>/`.
2. Load the bootstrap agent prompt.
3. Conduct the interview (see `_shell/agents/bootstrap-agent.md`).
4. From interview answers, produce:
   - `CLAUDE.md` (workspace router)
   - `schema.md` (entity types + page formats)
   - `learnings.md` (skeleton)
   - `nomenclature.md` (routing manual)
   - `identity.md` (optional, only if user wants override)
   - `style.md` (optional, only if user wants override)
   - `config/sources.yaml`
   - `config/schedule.yaml`
   - `agents/wiki-agent.md` (with schema rules baked in)
   - `agents/lint-agent.md` (with schema rules baked in)
5. If `wiki: false`, skip schema.md, learnings.md, wiki/ scaffolding entirely.
6. Generate the launchd plist files in `_shell/plists/com.adithya.ultron.<stage>-<workspace>.plist`. Symlink to `~/Library/LaunchAgents/` ONLY when user explicitly approves.
7. Run `check-routes.py --workspace <new-ws>` to confirm clean.
8. Run a synthetic-source smoke ingest to validate the pipeline.

## Outputs
- A fully scaffolded workspace.
- Plist files generated; loading is deferred to user.

## Idempotency
No. If `workspaces/<new-workspace-slug>/` exists, abort with error.
