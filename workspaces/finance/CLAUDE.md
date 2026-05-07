---
workspace: finance
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Finance — Workspace Router

You are in workspace `finance` — Adithya's long-term financial picture.

## What this workspace is

Bank accounts, credit cards, recurring obligations, long-term holdings (index funds, retirement, employer equity, real-estate equity rolled up), tax docs, financial goals, net-worth trajectory. Pure factual archive — synthesis surfaces cash-flow patterns and long-term trajectory over months / years.

What does NOT belong here:

- Active trading, P&L per strategy, day-trade theses, options, prediction markets → `trading`
- Real-estate transactions in flight (buying / selling) → `real-estate`
- Rental property cash flow at the unit level → `property-management` (rolled-up equity / monthly NOI lands here)

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — precise voice override
4. `nomenclature.md` — file-system routing

## Voice

Precise, conservative, low-emotion. Numbers cited verbatim. Currencies always explicit (`$1,234.56`, `€500.00`). Dates ISO. No financial advice. See `identity.md`.

## Hard rules (workspace-specific)

1. Every dollar figure has a currency and a date. No bare `1234` numbers.
2. Account numbers, routing numbers, SSN, full credit-card numbers NEVER appear in `wiki/`. Last 4 only, and only when needed for disambiguation. Full numbers stay in `raw/`. (Note: `raw/` IS tracked in git per the spec; the privacy boundary is the wiki/raw split, not the .gitignore. If you want raw uncommitted, add a `.gitignore` rule.)
3. Synthesis pages over 200 lines split by year (`2026-cash-flow.md`, `2026-holdings.md`).
4. Commit messages: `chore(finance): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What accounts do I have? | `wiki/entities/accounts/` |
| Recent transactions on account X? | `raw/<source>/<latest>/...` for verbatim; `wiki/entities/accounts/<x>.md` for synthesis |
| Long-term holdings in brokerage / retirement Y? | `wiki/entities/accounts/<y>.md` `## Holdings` section |
| Recurring monthly bills? | `wiki/synthesis/recurring-obligations.md` |
| Net worth trajectory? | `wiki/synthesis/<year>-net-worth.md` |
| Tax docs for year Y? | `raw/manual/<Y>/tax/...` |
| Active-trading P&L? | `[[ws:trading/...]]` — out of scope here; cross-link only |

## Agents

- `agents/wiki-agent.md`
- `agents/lint-agent.md`

## Sources

Filtered Gmail (statements, alerts), manual notes (CSV exports, screenshots), optional Plaid CSV exports. Ingest deferred until credentials provisioned.
