# Rental Manager Nomenclature

This workspace is pipeline-only (`wiki: false`). No wiki entities, no schema. Just structured raw data + operational state.

## File-system layout

```
workspaces/rental-manager/
  CLAUDE.md                                router
  nomenclature.md                          this file
  config/
    schedule.yaml                          cron jobs (compiled to launchd plists)
    sources.yaml                           declared sources
  playbooks/
    zillow-rental-manager/                 the active automation
      PLAYBOOK.md                          end-to-end docs
      package.json
      scripts/
        paths.mjs                          single source of truth for paths
        browser.mjs                        Chrome control + breaker
        daemon.mjs                         long-lived Chrome daemon
        login.mjs                          one-time sign-in flow
        pacing.mjs                         velocity governor
        inbox.mjs                          pull + send GraphQL surface
        storage.mjs                        two-tier persistence
        run.mjs                            CLI dispatcher
        batch-followup.mjs                 one-shot blast across all leads
        application-template.md            Gemini parsing template
  raw/
    leads/<slug>.md                        committed; one per lead, idempotent
    applications/<slug>/source.pdf         committed PDF + parsed markdown appended
  state/                                   gitignored except for run markers
    threads/<conversationId>.json          per-thread canonical state
    audit/<yyyy-mm-dd>/<id>/                immutable send bundles + screenshots
    network/<yyyy-mm-dd>/                   redacted GraphQL captures
    batch-followup/<runId>.{ndjson,start,done,aborted,crashed}
    pacing.json                            atomic call log
    breaker.json                           circuit breaker state
    chrome-profile/                        Chrome user-data-dir
    threads.jsonl                          append-only observation log
```

## Lead slug format

`<first>-<last>-zillow-<listingAlias>` when last name available.
Falls back to `<first>-<phone-last4>-zillow-<alias>` then `<first>-<cidLast4>-zillow-<alias>`.
Defined in `playbooks/zillow-rental-manager/scripts/storage.mjs:leadSlug`.

## When the playbook creates a new lead markdown

1. Compute slug from name + listingAlias + phone.
2. File path: `raw/leads/<slug>.md`.
3. Idempotent: same slug always rewrites the same file from observed state.
4. Frontmatter includes `phone` (E.164), `email` (lowercase), `conversation_id`, `listing_alias`, `status_label`.

## Slug collisions

Phone-suffix and cid-suffix disambiguation make collisions vanishingly rare. The lint pass (TODO) flags any duplicates.
