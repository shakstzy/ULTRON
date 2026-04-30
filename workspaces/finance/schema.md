# Finance Schema

Workspace schema for accounts, institutions, holdings, transactions.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| account | `wiki/entities/accounts/` | A specific bank, brokerage, retirement, or credit account. |
| institution | `wiki/entities/institutions/` | The financial firm that hosts one or more accounts. |
| holding | `wiki/entities/holdings/` | A specific security or asset position (ticker, real estate, private equity stake). |
| transaction | `wiki/entities/transactions/` | A noteworthy one-off transaction worth its own page (large transfer, asset purchase). Routine transactions stay in `raw/`. |

## Per-type page format

### account

```yaml
---
slug: <kebab>
type: account
canonical_name: <name>
account_type: checking | savings | brokerage | retirement | credit-card | loan | other
institution: <wikilink to institution>
last4: <last 4 digits, for disambiguation only>
currency: USD | EUR | GBP | other
status: active | dormant | closed
last_touched: <YYYY-MM-DD>
---
```

Body: `## Overview`, `## Recent activity` (dated bullets), `## Holdings` (if applicable), `## Backlinks`.

### institution

```yaml
---
slug: <kebab>
type: institution
canonical_name: <name>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Overview`, `## Accounts here`, `## Notes`, `## Backlinks`.

### holding

```yaml
---
slug: <kebab>
type: holding
canonical_name: <name or ticker>
asset_class: equity | etf | mutual-fund | bond | crypto | real-estate | private | cash
account: <wikilink to account>
acquired: <YYYY-MM-DD>
status: active | sold | matured
last_touched: <YYYY-MM-DD>
---
```

Body: `## Description`, `## Position` (units, cost basis), `## Decisions` (dated bullets), `## Backlinks`.

### transaction

```yaml
---
slug: <kebab>
type: transaction
canonical_name: <one-line description>
date: <YYYY-MM-DD>
amount: <number>
currency: USD | EUR | GBP | other
direction: in | out | transfer
account: <wikilink to account>
category: income | expense | investment | transfer | tax | other
last_touched: <YYYY-MM-DD>
---
```

Body: `## Context`, `## Documentation`, `## Backlinks`.

## Vocabulary

- "holding" = a discrete position in a security or asset.
- "recurring" = a transaction that happens on a fixed cadence.
- "fixed cost" = a recurring obligation (rent, utilities, subscriptions).
- "discretionary" = non-fixed spend.

## Schema change protocol

Schema changes flow through `_meta/schema-proposals.md`.
