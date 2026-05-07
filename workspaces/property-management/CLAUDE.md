---
workspace: property-management
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Property Management — Workspace Router

You are in workspace `property-management` — operations side of Adithya's rental units.

## What this workspace is

Day-to-day ops of rental units already owned: tenant relationships, leases, rent collection, repairs, vendors, listings during vacancy, lead triage from Zillow Rental Manager, inspections, insurance, property tax. One property may have multiple tenants over time; track tenancy as a separate entity from the property and the person.

Distinct from `real-estate` (acquisition / disposition / investment research). When a unit goes on the market for sale, the deal moves there; when it returns to operations, it returns here.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Operational. Numbers verbatim (rent, security deposits, repair costs). Vendor / contractor names spelled exactly. No marketing language in synthesis.

## Hard rules (workspace-specific)

1. Property references resolve via `schema.md`'s `property` type. Tenancy is its own entity (`tenancy`), not a sub-record of person.
2. Lead triage (Zillow Rental Manager inquiries) lives in `raw/zillow-rental-manager/`. Synthesis of lead patterns goes to `wiki/synthesis/lead-funnel.md`.
3. Lease docs, signed agreements, ID copies, deposit records: `raw/leases/<property>/<tenancy>/`. Sensitive PII (SSN, full name, banking) NEVER lands in wiki.
4. Repair / vendor receipts: `raw/manual/receipts/<YYYY-MM>/`.
5. Commit messages: `chore(property-mgmt): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is tenant / lead / vendor X? | `wiki/entities/people/<x>.md` then `[[@x]]` |
| What's the status of unit Y? | `wiki/entities/properties/<y-slug>.md` |
| Active tenancies | `wiki/synthesis/active-tenancies.md` |
| Open repair / maintenance items | `wiki/synthesis/maintenance-open.md` |
| Recent inquiries from Zillow | `raw/zillow-rental-manager/<YYYY-MM>/...` |
| Save a tenant / lead / vendor's phone / email to Apple Contacts | `_shell/skills/contacts-add/SKILL.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: gmail (property-management-labeled threads), Zillow Rental Manager browser scrape (future ULTRON-local skill mirroring SHAKOS's `zillow-rental-manager`), manual receipts.
