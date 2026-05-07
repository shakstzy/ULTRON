# Real Estate Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| property | `wiki/entities/properties/` | A specific real-estate parcel (residence, investment property, prospect). Slug is street-address kebab. |
| person | `wiki/entities/people/` | Agent, lender, inspector, attorney, contractor, counterparty, neighbor. |
| company | `wiki/entities/companies/` | Brokerage, lender, title company, inspection company, contractor company. |
| market | `wiki/entities/markets/` | A market / submarket Adithya is researching (e.g. `austin-travis-county`, `denver-cherry-creek`). |

## Per-type page format

### property

```yaml
---
slug: <street-address-kebab>     # e.g. 1234-elm-st-austin-tx
type: property
address: <full-street-address>
city: <city>
state: <state-abbrev>
zip: <zip>
status: <prospect | offer-out | under-contract | closed | sold | passed>
purpose: <residence | investment | flip | airbnb | mixed>
acquired_at: <YYYY-MM-DD>        # null until closed
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Property facts`, `## Comps`, `## Pipeline notes`, `## Backlinks`. Sensitive numbers (final price, financing, equity) live in `raw/` only.

### person

Standard person frontmatter plus:

```yaml
role: <agent | lender | inspector | attorney | contractor | counterparty | neighbor>
license_number: <string>          # only for agents / inspectors / lenders
```

### company

Standard company frontmatter plus:

```yaml
relationship: <brokerage | lender | title | inspection | contractor | insurance | other>
```

### market

```yaml
---
slug: <kebab>                     # e.g. austin-travis-county
type: market
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Overview`, `## Comp baselines`, `## Trend signals`, `## Backlinks`.

## Vocabulary

- "comps" — comparable sales for valuation
- "MLS" — Multiple Listing Service
- "ARV" — after-repair value
- "Cap rate" — net operating income / property value
- "the home market" — Travis County / Austin

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly.
