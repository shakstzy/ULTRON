---
slug: <street-address-kebab>
type: property
address: <full-street-address>
city: <city>
state: <state-abbrev>
zip: <zip>
status: prospect
purpose: residence
acquired_at: null
last_touched: <YYYY-MM-DD>
---

# <Address>

How to fill this page:

```bash
~/.claude/skills/real-estate/re lookup "<address>" --merged-only
```

Drop the merged JSON into `## Raw lookup` below, then promote the load-bearing numbers into `## Property facts`. Sensitive deal terms (offer price, financing, equity) go in `raw/` only — this page stays safe to share.

## Property facts

- Price (list / Zestimate / Redfin Estimate):
- Beds / baths / sqft / year built / lot:
- HOA / property tax rate:
- CAD owner / appraised value (if Travis):
- Homestead-exempt: <yes / no — investor signal>
- Last deed date:

## Comps

`re rent-estimate "<address>"` for rent, then a manual top 3:

| Address | Status | $ | $/sqft | Beds | Sqft | Source |
|---|---|---|---|---|---|---|

## Cash flow

```bash
~/.claude/skills/real-estate/re cashflow "<address>"
# duplex / multi-unit:
~/.claude/skills/real-estate/re cashflow "<address>" --units 2 --rent-per-unit <amt>
```

Defaults are Central-TX investor (20% down, 7% rate, 30yr, 8% vacancy, 4% PM, 5% maintenance, 5% capex, 0.5% insurance, 3% closing). Two scenarios are emitted: `stabilized` and `year_1_with_warranty`.

| Scenario | NOI / mo | Cash flow / mo | Cap rate | CoC | Breakeven rent |
|---|---|---|---|---|---|
| stabilized | | | | | |
| year 1 (warranty) | | | | | |

Verdict: <cash-flows | breaks even | bleeds — needed price drop OR rent jump>.

## Pipeline notes

- <YYYY-MM-DD> first looked: <why this property>
- Open questions:
- Next action:

## Raw lookup

<details>
<summary>re lookup output</summary>

```jsonc
// paste merged-only JSON here
```

</details>

## Backlinks
