---
workspace: rental-manager
wiki: false
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Rental Manager — Workspace Router

You are in workspace `rental-manager` — owner-side automation for Adithya's rental listings on Zillow Rental Manager (and future platforms). Pipeline-only workspace (no wiki).

## What this workspace is

Drives the owner inbox at zillow.com/rental-manager: pulls new leads, persists them as committed markdown under `raw/leads/`, replies to inquiries, runs follow-up cadence. Future siblings under `playbooks/` may add Apartments.com, Facebook Marketplace, Craigslist.

## Reading order on entry

1. `playbooks/zillow-rental-manager/PLAYBOOK.md` — the active automation
2. `nomenclature.md` — file-system layout
3. `config/schedule.yaml` — cron jobs
4. `config/sources.yaml` — declared sources

## Hard rules (workspace-specific)

1. **Self-contained.** Every path the playbook touches resolves under this workspace dir. No `~/.shakos/`, no `~/QUANTUM/`. Single source of truth lives in `playbooks/zillow-rental-manager/scripts/paths.mjs`.
2. **Real Chrome only.** The daemon spawns `/Applications/Google Chrome.app` (binary fingerprint matters for PerimeterX). Bundled Chromium is NOT an option per Gemini diagnostic 2026-05-05.
3. **rebrowser-playwright on the CDP attach path.** Stock Playwright leaks `Runtime.enable` to PX. rebrowser-playwright patches it.
4. **Pacing is sacred.** Hard ceilings 150/hr, 600/24h, 4s gap floor. Env can lower, never raise. Edits to `pacing.mjs` ceilings require a Codex/Gemini consult and a 24h soak.
5. **Live sends gated.** `--live` is required to actually click Send. Default is dry-run. Audit bundle written either way.
6. **Auth lapse aborts the batch.** `err.code === 'AUTH_LAPSED' | 'AUTH_OR_PX' | 'BREAKER_HALTED'` halts the run, writes an `aborted` marker, surfaces a re-login command. No silent retries.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is lead X? | `raw/leads/<slug>.md` |
| Application packet for lead X? | `raw/applications/<slug>/source.pdf` |
| What was the last batch run? | `state/batch-followup/run-<runId>.{ndjson,start,done,aborted,crashed}` |
| Is the daemon up? | `cd playbooks/zillow-rental-manager && node scripts/run.mjs status` |
| Pacing budget? | same dir, `node scripts/run.mjs pacing-status` |
| Breaker tripped? | `state/breaker.json` |

## Commands (run from `playbooks/zillow-rental-manager/`)

```bash
node scripts/run.mjs login                     One-time visible-Chrome sign-in
node scripts/run.mjs status                    Profile + breaker + daemon + pacing
node scripts/run.mjs daemon-start              Spawn long-lived Chrome (port 9222)
node scripts/run.mjs daemon-stop               Stop the daemon
node scripts/run.mjs pull-inbox [--max=N]      Pull deltas via checkpoint optimization
node scripts/run.mjs pull-thread <cid>         Pull single thread by id
node scripts/run.mjs send-reply <cid> "<body>" [--live]
node scripts/run.mjs reset-breaker             Clear 24h halt after manual captcha solve
node scripts/run.mjs reset-pacing              Wipe paced-call log

node scripts/batch-followup.mjs --dry --limit 3            # smoke
node scripts/batch-followup.mjs --live [--resume <runId>]  # live send across all leads
```

## Recovery runbook

- **Captcha during nav** → `reset-breaker` after solving in normal browser, OR wipe `state/chrome-profile/`, hotspot, re-login.
- **`AUTH_LAPSED` in batch** → `node scripts/run.mjs login`, then resume with `--resume <runId>`.
- **Profile poisoned (every nav captcha-walls)** → `rm -rf state/chrome-profile/` and re-login from a fresh IP (iPhone hotspot).
- **Daemon hung** → `daemon-stop && daemon-start`.
