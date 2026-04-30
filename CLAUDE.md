# ULTRON — Root

You are in `~/ULTRON/`, a markdown-only personal memory and knowledge management system. ULTRON is the canonical Life-OS for Adithya. It replaces the prior QUANTUM and SHAKOS systems.

## Tiers

- `_global/` — cross-workspace canonical entities, agent-learnings, wikilink rules. Read on session start.
- `_shell/` — stage contracts, bin scripts, agent prompts, run state.
- `workspaces/<ws>/` — domain workspaces. Each has its own CLAUDE.md, schema, voice.

## Workspaces

| Workspace | Domain |
|---|---|
| `eclipse` | Eclipse Labs — consent-verified audio data marketplace. Sydney is CEO. |
| `personal` | Music production, fitness lifestyle, dating, home, friends, music industry. |
| `health` | Workouts, nutrition, vitals, sleep, supplements, medical history. |
| `finance` | Accounts, transactions, investments, taxes, financial goals. |

Add more workspaces via `_shell/bin/run-stage.sh bootstrap <new-ws>`.

## Workspace entry protocol

When entering a workspace, read in order:
1. `workspaces/<ws>/CLAUDE.md`
2. `workspaces/<ws>/schema.md` (if not `wiki: false`)
3. `workspaces/<ws>/learnings.md` (if not `wiki: false`)
4. `workspaces/<ws>/identity.md` and `style.md` (if present)
5. `workspaces/<ws>/nomenclature.md` for navigation

Workspace-level `identity.md` and `style.md` OVERRIDE the global voice default below.

## Voice (global default — overridden per workspace)

Direct, low-decoration prose. No hedging. Opinionated where evidence supports. No corporate-speak. Plain words. Short sentences. No em dashes.

## Hard rules

1. Markdown-only canonical. YAML frontmatter OK; JSON for skill manifests and Graphify outputs only.
2. Files must respect line caps: CONTEXT.md ≤ 80; reference files ≤ 200; agent prompts ≤ 200.
3. Lint never deletes. Schema changes go through `_meta/schema-proposals.md`.
4. Routes are sacred. See `_shell/bin/check-routes.py` and the route-maintenance contract.
5. Cross-workspace canonicalization: `_global/entities/<type>/<slug>.md` is the identity stub + roster of backlinks. Workspace pages contain workspace-specific synthesis. Never duplicate.
6. Credentials live ONLY in `_credentials/` or `.claude/settings.local.json`. Both are gitignored. Never commit secrets.

## Stage execution

All stages run via `_shell/bin/run-stage.sh <stage> [<workspace>]`. See `_shell/stages/<stage>/CONTEXT.md` for each contract.

## Where to go for what

- New conversation about a person → check `_global/entities/people/<slug>.md` for backlinks, then drill into the workspace cited.
- Cross-workspace question ("what's everything we know about X?") → run `_shell/bin/build-backlinks.py` if stale, then read the global stub.
- New workspace → `_shell/bin/run-stage.sh bootstrap <new-ws>`.
- Cross-workspace graph view → see `_graphify/GRAPH_REPORT.md` (audit refreshes weekly).
