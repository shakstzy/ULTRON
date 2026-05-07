# Trading Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| strategy | `wiki/entities/strategies/` | A named trading strategy with thesis, rules, and P&L log. |
| instrument | `wiki/entities/instruments/` | A specific tradable: ticker, contract, market resolution. |
| trade | `wiki/entities/trades/` | A single round-trip (entry + exit + P&L). |
| post-mortem | `wiki/synthesis/postmortems/` | Mandatory after any closed loss > 5% of strategy capital. |
| person | `wiki/entities/people/` | Source / analyst / counterparty. Rare. |

## Per-type page format

### strategy

```yaml
---
slug: <kebab>
type: strategy
status: <active | paused | retired>
asset_class: <equity | crypto | options | prediction-market | arbitrage>
thesis_confidence: <high | medium | low | hunch>
inception_date: <YYYY-MM-DD>
capital_allocated_usd: <number>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Thesis`, `## Entry rules`, `## Exit rules`, `## Sizing`, `## P&L log`, `## Lessons`, `## Backlinks`.

### instrument

```yaml
---
slug: <exchange>-<symbol>           # e.g. nyse-spy, polymarket-trump-2028
type: instrument
exchange: <exchange-id>
symbol: <symbol>
asset_class: <equity | crypto | option | future | prediction-market>
last_touched: <YYYY-MM-DD>
---
```

### trade

```yaml
---
slug: <YYYY-MM-DD>--<strategy-slug>--<instrument-slug>--<seq>
type: trade
strategy: <strategy-slug>
instrument: <instrument-slug>
direction: <long | short>
opened_at: <YYYY-MM-DDTHH:MM>
closed_at: <YYYY-MM-DDTHH:MM>
size_usd: <number>
pnl_usd: <number>
pnl_pct: <number>
---
```

Body sections: `## Setup`, `## Execution`, `## Outcome`, `## Backlinks`.

### post-mortem

```yaml
---
slug: <YYYY-MM-DD>--<topic>
type: post-mortem
strategy: <strategy-slug>
related_trades: [<trade-slug>...]
loss_usd: <number>
loss_pct_of_capital: <number>
---
```

Body sections: `## What I expected`, `## What happened`, `## Specific error`, `## Rule change`, `## Backlinks`.

## Vocabulary

- "thesis" — written prediction with falsification criteria
- "size" — dollar exposure
- "stop" — predetermined exit on adverse move
- "post-mortem" — required write-up after closed loss > 5%

## Hard rule on numbers

Position sizes, entries, exits, stops cited verbatim. No rounding to "about $5k" — write `$4,820`. No retrofitting "I felt good about it" after an outcome — record what was actually written before close.

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent.
