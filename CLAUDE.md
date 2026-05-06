# ULTRON — Root

You are in `~/ULTRON/`, a markdown-only personal memory and knowledge management system. ULTRON is the canonical Life-OS for Adithya.

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

## Escalation chain (exhaust before pinging Adithya)

ULTRON is autonomous and long-running. Before asking Adithya anything, walk this chain in order. Skip a step only if it cannot possibly hold the answer (e.g., skip step 1 for a question about a JS framework version). Never ask Adithya for anything resolvable by steps 1–3.

1. **Local wiki (workspace-shaped questions).** If the question is about a person, project, event, fact, or convention that could live in the graph, query it first:
   - `cd ~/ULTRON && /graphify query "<question>"` for cross-cutting "what do we know about X."
   - Read `_global/entities/<type>/<slug>.md` for canonical entity stubs and backlinks.
   - Read `workspaces/<ws>/{schema,learnings,nomenclature,identity,style}.md` for workspace conventions.
   - Read raw under `workspaces/<ws>/raw/<source>/` for source material.
2. **Sonnet + web search (current external facts).** For "what's the latest," docs lookup, recent news, third-party API behavior, or anything time-sensitive: spawn a fresh-context Sonnet subagent — `Agent({ subagent_type: "general-purpose", model: "sonnet", prompt: "<self-contained question>. Use WebSearch." })`. Cheaper and faster than Codex/Gemini for read-only research.
3. **Codex / Gemini (engineering, framework, naming, threshold, pattern decisions).** Per global CLAUDE.md "Autonomous Escalation": `codex exec --skip-git-repo-check "..."` or `gemini -m gemini-3-pro-preview -p "..." -o text`. Default to Codex for code, Gemini for very recent web facts or when Codex is rate-limited. Both for high-stakes diffs.
4. **Adithya.** Only the 5 buckets in global CLAUDE.md: feature requests, voice/brand calls, money/vendor commits, explicit HITL gates (`SEND`, `PUBLISH`, `LAUNCH-AD`, `CONFIRM`, `load`), or earlier-instruction conflicts.

If a step returns "I don't know" or "not in the graph," move to the next step. Don't stall, don't ask permission to consult — just fire and quote one-line results in the TL;DR.

## Hard rules

1. Markdown-only canonical. YAML frontmatter OK; JSON for skill manifests and Graphify outputs only.
2. Files must respect line caps: CONTEXT.md ≤ 80; reference files ≤ 200; agent prompts ≤ 200.
3. Lint never deletes. Schema changes go through `_meta/schema-proposals.md`.
4. Routes are sacred. See `_shell/bin/check-routes.py` and the route-maintenance contract.
5. Cross-workspace canonicalization: `_global/entities/<type>/<slug>.md` is the identity stub + roster of backlinks. Workspace pages contain workspace-specific synthesis. Never duplicate.
6. Credentials live ONLY in `_credentials/` or `.claude/settings.local.json`. Both are gitignored. Never commit secrets.

## Stage execution

All stages run via `_shell/bin/run-stage.sh <stage> [<workspace>]`. See `_shell/stages/<stage>/CONTEXT.md` for each contract.

## Scheduling

Recurring jobs (ingest cron, lint, graphify, audit, weekly-review) are declared in YAML, not hand-written plist XML. Source of truth:

- Per-workspace: `workspaces/<ws>/config/schedule.yaml`
- Cross-workspace: `_shell/config/global-schedule.yaml`

The `schedule` skill compiles those into launchd plists at `_shell/plists/` and loads them with `launchctl bootstrap`. Always invoke the skill — never write plist XML or call `launchctl` directly. Modes: `compile`, `load`, `unload`, `status`, `remove`. `load` requires explicit confirmation in chat.

## Where to go for what

- New conversation about a person → check `_global/entities/people/<slug>.md` for backlinks, then drill into the workspace cited.
- Cross-workspace question ("what's everything we know about X?") → run `_shell/bin/build-backlinks.py` if stale, then read the global stub.
- New workspace → `_shell/bin/run-stage.sh bootstrap <new-ws>`.
- Cross-workspace graph view → see `_graphify/GRAPH_REPORT.md` (audit refreshes weekly).
