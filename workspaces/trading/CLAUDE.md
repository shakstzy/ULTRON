---
workspace: trading
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Trading — Workspace Router

You are in workspace `trading` — Adithya's active markets activity.

## What this workspace is

Active trading: stocks, crypto, prediction markets (Polymarket, Kalshi), arbitrage, options. Strategies, theses, executions, P&L by strategy, post-mortems. Distinct from `finance` (personal accounts, taxes, recurring subs, net worth) — `finance` is the steady state, `trading` is the discretionary action layer.

The arbitrage-trading pattern from SHAKOS lives here (cross-exchange detection + execution).

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice override
4. `nomenclature.md` — file-system routing

## Voice override

Numbers-precise. Position sizes verbatim. Stops verbatim. Theses tagged confidence (high / medium / low / hunch). No retroactive narrative-fitting. See `identity.md`.

## Hard rules (workspace-specific)

1. **No execution from this workspace's automation without `CONFIRM` gate.** Trade orders are user-driven. Bots monitor, surface, and propose; humans submit.
2. Strategies resolve via `schema.md`'s `strategy` type. Each strategy has its own page with thesis, entry rules, exit rules, sizing, P&L log.
3. Tickers / instruments resolve via `instrument` type (`<exchange>-<symbol>` slug for disambiguation).
4. Trades resolve via `trade` type, dated, linked to `strategy` and `instrument`.
5. Post-mortems live in `wiki/synthesis/postmortems/<YYYY-MM-DD>-<topic>.md`. Mandatory after any closed loss > 5% of strategy capital.
6. Sensitive account details (account numbers, exchange API keys) live ONLY in `_credentials/`. Never in raw / wiki.
7. Commit messages: `chore(trading): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What's strategy X? | `wiki/entities/strategies/<x>.md` |
| Status of instrument Y? | `wiki/entities/instruments/<y>.md` |
| Open positions / pipeline | `wiki/synthesis/open.md` |
| Recent trades log | `raw/manual/trades/<YYYY-MM>.md` |
| Polymarket / Kalshi opps | `raw/manual/opps/<YYYY-MM-DD>.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: manual entries in `raw/manual/_inbox/`. Exchange CSV exports land in `raw/manual/exports/`. Future: arbitrage-detection cron from SHAKOS pattern.
