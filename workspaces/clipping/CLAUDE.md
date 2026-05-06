---
workspace: clipping
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Clipping — Workspace Router

You are in workspace `clipping` — Adithya's UGC bounty / clipping operation.

## What this workspace is

Paid clipping bounties via Whop, Vyro, and adjacent UGC platforms. End-to-end pipeline: source-monitor (livestreams, podcasts, long-form video) → capture (yt-dlp) → transcribe (mlx-whisper) → clip-detect (Claude / Gemma multimodal) → craft (caption + hook + reframe via Remotion) → distribute (TikTok / IG / YT Shorts via the future ULTRON-local Zernio publish flow) → track (anonymous metrics polling) → learn (niche-pattern aggregation).

Workflow-shaped. Stages live under `stages/<NN>-<name>/CONTEXT.md` (porting the SHAKOS clip-factory ICM pattern). Wiki captures patterns, niches, top performers; bulk video files stay outside ULTRON git.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice override
4. `nomenclature.md` — file-system routing

## Voice override

Ops-tight. Numbers verbatim (views, completion rate, click-through, payout). Niche / hook patterns named explicitly. No vague "this performed well" — say what specifically and how much. See `identity.md`.

## Hard rules (workspace-specific)

1. **HITL gates on publish.** Every cross-platform distribution call passes through `PUBLISH`. Paid boost / promotion calls pass through `LAUNCH-AD`.
2. **Bulk video files do NOT live in ULTRON git.** Use `_credentials/clipping-storage.yaml` to declare an external scratch path; wiki references files by external path and content hash.
3. Sources / streams resolve via `schema.md`'s `source` type. Clips via `clip` type. Niches via `niche` type. Each clip links to source + niche.
4. Performance metrics live in `raw/metrics/<platform>/<YYYY-MM-DD>.json`. Wiki rolls up weekly into `wiki/synthesis/<niche>-performance.md`.
5. Stage outputs feed next stage's inputs (ICM pattern). Stage contracts in `stages/<NN>-<name>/CONTEXT.md`.
6. Commit messages: `chore(clipping): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What's niche X performing like? | `wiki/synthesis/<niche>-performance.md` |
| Who is creator / source X? | `wiki/entities/sources/<x>.md` |
| Top clips this week | `wiki/synthesis/top-clips.md` |
| Pipeline state | `stages/<NN>-<name>/output/` |
| Receipts from Whop / Vyro | `raw/gmail/<account>/<YYYY-MM>/...` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: manual stream / clip declarations in `raw/manual/_inbox/`, gmail (Whop / Vyro receipts). Future: yt-dlp captures, mlx-whisper transcripts, anonymous metrics polling.
