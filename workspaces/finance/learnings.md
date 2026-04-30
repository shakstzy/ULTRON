# Finance Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines.

## Voice and tone

- Numbers cited verbatim. Never round dollar figures unless explicitly stated as estimates.
- Currency always explicit. `$1,234.56` not `1234`.
- Dates ISO `YYYY-MM-DD`.
- No financial advice. You record and synthesize patterns; Adithya makes the calls.

## Operational rules

- Account numbers, routing numbers, SSNs, full card numbers NEVER in `wiki/`. Last 4 only. Full numbers stay in `raw/`.
- Tax-relevant artifacts (W2, 1099, K1, brokerage 1099-B) live in `raw/manual/<YEAR>/tax/` only. Wiki notes existence and provider, not content.
- Recurring transactions: not a wiki entity. They become a synthesis page (`recurring-obligations.md`).
- One-off transactions get their own entity page only when ≥ $1,000 USD and worth tracking individually (large transfers, asset purchases, taxes paid). Routine spending stays in `raw/`.

## Past patterns

- (none yet)

## Mental models

- "Cash flow" = inflow minus outflow per month, net of transfers. Synthesis page rolls this up.
- "Net worth" = sum(account balances) + sum(holdings at current value) - sum(loan balances). Recompute monthly.
- Distinguish "account" (where money sits) from "holding" (specific position inside the account).
