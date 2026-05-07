---
workspace: real-estate
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Real Estate — Workspace Router

You are in workspace `real-estate` — Adithya's personal real estate footprint: buying, selling, investment properties, market research.

## What this workspace is

Personal real-estate transactions and investment research. Home purchase / sale, investment property acquisition, comps, market data, lender / agent / inspector / title relationships. Travis County (Austin) is the home market; other markets enter as research.

Distinct from `property-management` (operations of rental units already owned). This workspace stops once a property closes; ongoing tenant / repair / lease ops move to `property-management`.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `nomenclature.md` — file-system routing

(No identity.md / style.md override — uses global default voice.)

## Voice

Default ULTRON voice. Numbers verbatim. Comps cited by source (Redfin / Zillow / MLS / county tax record). Speculation about market direction tagged.

## Hard rules (workspace-specific)

1. Property references resolve through `schema.md`'s `property` type, slugged by address (`<street-address-kebab>`).
2. People (agent, lender, inspector, attorney, contractor, counterparty) resolve via `person` type. Companies (brokerage, lender, title co.) resolve via `company`.
3. Comps and pricing data live in `raw/` (verbatim). Wiki synthesis surfaces takeaways, not raw comp tables.
4. Closed-deal sensitive terms (final price, financing terms, equity) live only in `raw/`. Wiki notes the deal's existence and status.
5. Commit messages: `chore(real-estate): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (agent / lender / inspector)? | `wiki/entities/people/<x>.md` then `[[@x]]` |
| What about property at address Y? | `wiki/entities/properties/<y-slug>.md` |
| Current pipeline (offers out, in escrow, under contract) | `wiki/synthesis/pipeline.md` |
| Comps research for a market | `wiki/synthesis/<market>-comps.md` |
| Market overview (Austin, etc.) | `wiki/concepts/<market>-market.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: gmail (real-estate-labeled threads from Adithya's primary mailbox), Redfin / Zillow / Travis CAD via the `real-estate` skill at `skills/real-estate/` (symlinked from `~/QUANTUM/_core/skills/real-estate/`), manual notes.

## Property research workflow

For any property prospect:

```bash
~/.claude/skills/real-estate/re lookup "<address>" --merged-only
```

Drop the JSON into a new page using `wiki/_templates/property-research.md` as the starting point. Use `re rent-estimate "<address>"` for rental comps and `re cad lookup "<address>"` for owner / appraised value when the address is in Travis County.
