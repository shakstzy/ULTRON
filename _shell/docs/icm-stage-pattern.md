# ICM Numbered-Stage Pattern

When and how to lay out numbered stages inside a workspace. Ported from SHAKOS's interpretable-context methodology.

## When a workspace gets stages

A workspace adopts `stages/<NN>-<name>/CONTEXT.md` when it has a multi-step pipeline where each step's output is the next step's input AND the steps repeat on a cadence.

Workspaces that MERIT staging:

- `clipping` — source-monitor → capture → transcribe → clip-detect → craft → distribute → track
- `dating` (partially staged via `bot/`) — pull → swipe → reply → escalate → archive
- `property-management` — lead-intake → screen → lease → onboard → ops (when formalized)
- `real-estate` — search → comp → offer → diligence → close (when formalized)
- `onlyfans` — content-plan → produce → schedule → ship → metrics (when formalized)
- `trading` — signal → size → execute → reconcile (when formalized)

Workspaces that do NOT merit staging (pure-wiki, no pipeline):

- `personal`, `health`, `library`, `finance`, `seedbox`, `outerscope`, `mosaic`, `synapse`, `eclipse`, `music`

## File layout

```
workspaces/<ws>/stages/
├── 01-<name>/
│   ├── CONTEXT.md              ≤ 80 lines (stage contract)
│   ├── input/                  populated by stage N-1 (or manual seed)
│   ├── output/                 read by stage N+1
│   └── scripts/                impl details
├── 02-<name>/
│   └── ...
└── ...
```

`input/` and `output/` are real directories, not symlinks. Stage N+1 reads stage N's `output/` directly via path.

## CONTEXT.md template (≤ 80 lines)

```md
# Stage <NN>: <name>

## Purpose
One paragraph.

## Invocation
`run-stage.sh <stage-name> <ws>`

## Inputs
- Path: workspaces/<ws>/stages/<NN-1>-<prior>/output/...
- Format: <md / json / ndjson / binary>
- Required credentials / config

## Process
Numbered, high-level. Implementation lives in scripts/.

## Outputs
- Path: workspaces/<ws>/stages/<NN>-<name>/output/<pattern>
- Format: <md / json / ndjson / binary>

## HITL gates
List required gates (CONFIRM / SEND / PUBLISH / LAUNCH-AD / load). None if pure read.

## Idempotency
Yes / No / partial. Describe re-run behavior.

## Triggered
schedule | manual | both
```

## Dispatcher integration

The global `run-stage.sh` has six built-in stage types (`ingest`, `lint`, `audit`, `bootstrap`, `weekly-review`, `query`). For per-workspace stages, the dispatcher resolves: if `workspaces/<ws>/stages/<stage-name>/CONTEXT.md` exists, run `workspaces/<ws>/stages/<stage-name>/run.sh` (or `scripts/run.sh`) with `RUN_ID` and `ULTRON_ROOT` exported.

A workspace may ship its own `bin/run.sh` if its stages need workspace-specific argument shapes; the global dispatcher delegates if `workspaces/<ws>/bin/run.sh` exists.

## Manually triggered stages

Stages that should NOT run on a cron declare `## Triggered: manual` in CONTEXT.md. Audit agent does not flag them as stale; schedule skill does not generate a plist for them.

## Adopting stages on an existing workspace

Adithya gives the call workspace-by-workspace. When he says "formalize stages for `<ws>`":

1. Propose the stage list (3-7 stages typically) in `_meta/stage-proposals.md`.
2. On approval, scaffold `stages/<NN>-<name>/` with stub CONTEXT.md and empty `input/`, `output/`.
3. Move existing pipeline scripts into the right `scripts/` directory.
4. Update the workspace CLAUDE.md routing table to point to stage outputs.
5. Update `config/schedule.yaml` with cron entries for any auto-triggered stages.

Do NOT formalize stages without a per-workspace ask.

## Stage versus skill

A stage runs as part of a workspace's pipeline; a skill is a portable capability invoked across workspaces. If the same code logically belongs in 2+ workspaces, it is a skill. If it is one workspace's pipeline step, it is a stage.

When in doubt, start as a stage. Promote to skill only when reuse pressure shows up.
