# Finance — Workspace Router

You are in workspace `finance` — Adithya's accounts, transactions, investments, taxes, and financial goals.

## What this workspace is

Bank accounts, brokerage accounts, retirement accounts, credit cards, transactions, holdings, recurring obligations, tax docs, financial goals. Pure factual archive — synthesis surfaces cash-flow patterns and net-worth trajectory over time.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — precise voice override
4. `nomenclature.md` — file-system routing

## Voice

Precise, conservative, low-emotion. Numbers cited verbatim. Currencies always explicit (`$1,234.56`, `€500.00`). Dates ISO. No financial advice. See `identity.md`.

## Hard rules (workspace-specific)

1. Every dollar figure has a currency and a date. No bare `1234` numbers.
2. Account numbers, routing numbers, SSN, full credit-card numbers NEVER appear in `wiki/`. Last 4 only, and only when needed for disambiguation. Full numbers stay in `raw/` (which itself is gitignored beyond the manifest).
3. Synthesis pages over 200 lines split by year (`2026-cash-flow.md`, `2026-holdings.md`).
4. Commit messages: `chore(finance): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| What accounts do I have? | `wiki/entities/accounts/` |
| Recent transactions on account X? | `raw/<source>/<latest>/...` for verbatim; `wiki/entities/accounts/<x>.md` for synthesis |
| Holdings in brokerage Y? | `wiki/entities/accounts/<y>.md` `## Holdings` section |
| Recurring monthly bills? | `wiki/synthesis/recurring-obligations.md` |
| Net worth trajectory? | `wiki/synthesis/<year>-net-worth.md` |
| Tax docs for year Y? | `raw/manual/<Y>/tax/...` |

## Agents

- `agents/wiki-agent.md`
- `agents/lint-agent.md`

## Sources

Filtered Gmail (statements, alerts), manual notes (CSV exports, screenshots), optional Plaid CSV exports. Ingest deferred until credentials provisioned.
