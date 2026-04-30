# Finance Nomenclature

File-system conventions and routing for workspace `finance`.

## File-system conventions

- Raw archive: `raw/<source>/<YYYY-MM>/<slug>.md`.
- Plaid CSV exports: `raw/plaid/<YYYY-MM>/<account-last4>-<YYYY-MM-DD>.md` (CSV converted to markdown table).
- Tax docs: `raw/manual/<YEAR>/tax/<doc-name>.md`.
- Wiki entity pages: `wiki/entities/<type>/<slug>.md`.
- Synthesis pages: `wiki/synthesis/<topic-slug>.md` or `wiki/synthesis/<YEAR>-<topic>.md` for year-bounded.

## Routing table — by query type

| Query type | Read first |
|---|---|
| "What accounts do I have?" | `wiki/entities/accounts/` filtered by `status: active` |
| "Holdings in account X?" | `wiki/entities/accounts/<x>.md` `## Holdings` section |
| "Recent activity on account X?" | `raw/<source>/<latest>/...` |
| "What recurring bills do I have?" | `wiki/synthesis/recurring-obligations.md` |
| "Net worth trend?" | `wiki/synthesis/<year>-net-worth.md` |
| "Tax docs for year Y?" | `raw/manual/<Y>/tax/` |

## When the wiki agent processes a transaction file

1. Read the raw transactions (CSV / email summary).
2. For each transaction, decide: routine (stay in raw, summarize at month-end) or noteworthy (≥ $1,000 USD, or unusual category, or first-time vendor).
3. For noteworthy transactions, create or update `wiki/entities/transactions/<slug>.md`.
4. Update the parent account's `## Recent activity` with month-roll-up bullets, NOT per-transaction bullets.
5. After 3+ months of accumulation, regenerate `wiki/synthesis/<year>-cash-flow.md`.

## Disambiguation

Same institution may host multiple accounts. Always disambiguate via `<institution-slug>-<account_type>-<last4>` if needed.
