# Property Management Schema

Workspace schema. Defines entity types, page formats, and the vocabulary the wiki agent uses when ingesting and synthesizing.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| property | `wiki/entities/properties/` | A specific rental unit. Slug is street-address kebab. |
| tenancy | `wiki/entities/tenancies/` | A specific tenancy at a property (separate entity from person and property). |
| person | `wiki/entities/people/` | Tenant, applicant, lead, vendor, contractor, neighbor. |
| company | `wiki/entities/companies/` | Property management software, vendor companies, insurance providers, utility providers. |

## Per-type page format

### property

```yaml
---
slug: <street-address-kebab>
type: property
address: <full-street-address>
city: <city>
state: <state-abbrev>
zip: <zip>
status: <vacant | occupied | listed | offline | sold>
unit_count: <number>
acquired_at: <YYYY-MM-DD>
last_touched: <YYYY-MM-DD>
---
```

Body sections: `## Property facts`, `## Active tenancy`, `## Maintenance log`, `## Backlinks`.

### tenancy

```yaml
---
slug: <property-slug>--<tenant-first>--<start-date>
type: tenancy
property: <property-slug>
tenant: <person-slug>
start_date: <YYYY-MM-DD>
end_date: <YYYY-MM-DD>            # null while active
monthly_rent_usd: <number>
deposit_usd: <number>
status: <active | ended | evicted | broken-lease>
---
```

Body sections: `## Lease summary`, `## Payment history`, `## Issues`, `## Move-in / move-out`, `## Backlinks`. Lease document and ID copies live in `raw/leases/<property>/<tenancy>/`.

### person

Standard person frontmatter plus:

```yaml
role: <tenant | applicant | lead | vendor | contractor | neighbor | other>
phone: <E.164>                    # full number stays in raw/; wiki uses last 4
```

### company

Standard company frontmatter.

## Vocabulary

- "Zillow Rental Manager" — primary lead source platform
- "tenancy" — distinct from tenant; one tenancy = one continuous lease term
- "lead" — inquiry that has not signed a lease
- "applicant" — has submitted application but lease not yet signed
- "tenant" — current or former lessee
- "showing" — physical visit to the unit
- "turn" — vacate-to-occupy cycle

## Schema change protocol

Schema changes are proposed in `_meta/schema-proposals.md` by the lint agent. Adithya applies changes weekly.
