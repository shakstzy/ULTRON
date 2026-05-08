# Network Nomenclature

This file documents file-system conventions and the routing manual for this workspace.

## File-system conventions

- LinkedIn raw deposits: `raw/linkedin/<slug>-linkedin.md` (one file per person, append-only thread events).
- Wiki entity pages (optional v1): `wiki/entities/people/<slug>.md`.
- `_meta/lint-<YYYY-MM-DD>.md` per lint run.

The slug is the LinkedIn vanity (the `/in/<vanity>` handle) lowercased + kebab-cased. Apple Contacts may use a different slug for the same person — `/alias` resolves the mismatch.

## Routing table — by query type

| Query type | Read first |
|---|---|
| "Who is X (professionally)?" | `_global/entities/people/<x>.md` (identity + roster), then `raw/linkedin/<x>-linkedin.md` (snapshot) |
| "What did X say to me on LinkedIn?" | `raw/linkedin/<x>-linkedin.md` `## Threads` section |
| "Outstanding sent invites" | run `node ~/ULTRON/_shell/skills/linkedin/scripts/run.mjs list-invites --direction sent` |
| "Recent received invites" | run `node ~/ULTRON/_shell/skills/linkedin/scripts/run.mjs list-invites --direction received` |
| "Search my professional network for <X>" | obsidian-base over `_global/entities/people/` filtered on `identifiers.linkedin` non-empty |

## When the LinkedIn skill creates a new raw deposit

1. Resolve canonical slug — read the target file's frontmatter; if `redirect_to:` is set, use the canonical slug instead.
2. Write the raw deposit with the standard ingest frontmatter (source/workspace/ingested_at/ingest_version/content_hash/provider_modified_at) plus LinkedIn-specific fields and `entity:` wikilink up to global stub.
3. Auto-create a thin global stub at `_global/entities/people/<slug>.md` if one doesn't exist, tagged `entity_status: provisional`. If a global stub already exists, enrich its `identifiers.linkedin` field — never duplicate the snapshot into it.

## When source naming conflicts

If LinkedIn returns two different vanities for the same person (e.g., they re-vanitied), both write to their own `<slug>-linkedin.md` and `/alias` is used to merge. The deprecated slug becomes a redirect stub; future writes resolve to canonical via the redirect-honor logic in `entity-store.upsertPerson`.
