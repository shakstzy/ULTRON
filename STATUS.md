# ULTRON — Status

Snapshot of what is built, what is pending, what each workspace owns. Updated when significant scaffolding lands; not auto-generated.

Last updated: 2026-05-06.

## Workspaces (16 total)

| slug | scope | wiki | private (super-graphify) | sources wired | maturity |
|---|---|---|---|---|---|
| eclipse | Eclipse Labs B2B ops | yes | no | gmail + slack + drive + granola + manual | live |
| outerscope | venture studio (parent of mosaic + synapse) | yes | no | drive + manual | scaffolded |
| seedbox | advisory (Seedbox Labs) | yes | no | gmail (label:Seedbox) | scaffolded |
| synapse | Synapse startup (synps.xyz) | yes | no | gmail (synps.xyz) + manual | scaffolded |
| mosaic | Outerscope-spawned project | yes | no | drive + granola + manual (TBD folder names) | scaffolded |
| personal | catch-all (friends / family / home / day-to-day) | yes | no | gmail + imessage + manual | live |
| health | fitness + nutrition + medical (one workspace) | yes | no | gmail + apple-health + manual | scaffolded |
| finance | long-term holds + taxes + recurring | yes | no | gmail + plaid + manual | scaffolded |
| trading | active markets + arbitrage | yes | no | manual (TBD exchange CSVs) | scaffolded |
| real-estate | personal RE transactions / investing | yes | no | gmail (TBD label) + manual | scaffolded |
| property-management | rental ops, tenants, leases | yes | no | gmail (TBD) + zillow-rental-mgr (port pending) + manual | scaffolded |
| dating | dating-app activity, matches | yes | no | manual + imessage + tinder bot (live) | scaffolded + bot-running |
| onlyfans | creator-business ops | yes | **yes** | manual (TBD platform scrape) | scaffolded |
| library | books / papers / articles / podcasts | yes | no | manual (TBD defuddle / docling / yt-summary) | scaffolded |
| music | music production + releases + gear | yes | no | gmail + manual + distrokid (port pending) | scaffolded |
| clipping | UGC bounty pipeline | yes | no | manual + gmail (TBD whop / vyro) | scaffolded |

## What is built today

- Root [CLAUDE.md](CLAUDE.md) routing + escalation chain.
- [`_shell/`](\_shell/) infrastructure: 32 bin scripts, 6 stage CONTEXTs, `run-stage.sh` dispatcher, `gate.sh` (pending), 26 plists from `schedule.yaml` files.
- [`_shell/docs/`](\_shell/docs/) specs:
  - [source-routing.md](\_shell/docs/source-routing.md) — central per-source / per-account / per-scope routing matrix; many TBD rows.
  - [HITL-gates.md](\_shell/docs/HITL-gates.md) — SEND / PUBLISH / LAUNCH-AD / CONFIRM / load definitions.
  - [entity-stub-format.md](\_shell/docs/entity-stub-format.md) — canonical `_global/entities/` format.
  - [icm-stage-pattern.md](\_shell/docs/icm-stage-pattern.md) — when / how to formalize numbered stages.
  - [gmail-current-state.md](\_shell/docs/gmail-current-state.md) — pre-existing.
- [`_global/`](\_global/) layer: schema declared, `agent-learnings.md` and `wikilink-resolution.md` files exist (mostly empty), [`contact-sets.yaml`](\_global/contact-sets.yaml) scaffolded with named sets (members empty).
- All 9 new workspaces scaffolded with: CLAUDE.md, schema.md (workspace-specific entity types), learnings.md, nomenclature.md, identity.md (4 of 9), style.md, agents/wiki-agent.md, agents/lint-agent.md, config/sources.yaml, config/schedule.yaml, _meta/, wiki/. All clean on `check-routes.py`.
- Credentials in [`_credentials/`](\_credentials/) gitignored. 4 Gmail OAuth + Drive + Slack configs present.

## What is pending

### Tier 1 (foundation, blocks other work)

- Populate [`_global/entities/`](\_global/entities/) — currently empty. Needs first canonical stubs for high-frequency people / companies / projects. Run `audit-agent` after first round of ingest to surface candidates.
- Wire `gate.sh` callable functions from [HITL-gates.md](\_shell/docs/HITL-gates.md) spec. (Spec is done; impl pending.)
- Wire agent-learnings auto-inject hook in [`.claude/settings.json`](\.claude/settings.json) (UserPromptSubmit, ≤1KB grep-injected).
- Wire `ingest-driver.py` to read [`source-routing.md`](\_shell/docs/source-routing.md) and refuse TBD rows.
- Update each new workspace's `agents/wiki-agent.md` and `agents/lint-agent.md` with workspace-specific `Schema-specific rules` sections (currently still generic templates).

### Tier 2 (operational)

- Bootstrap graphify (has never run; [`_graphify/GRAPH_REPORT.md`](\_graphify/GRAPH_REPORT.md) confirms no graphs).
- Schedule the audit loop (every 30 min self-heal mirroring QUANTUM's icm-audit).
- `.gitignore` hygiene: dating bot Chrome profile + node_modules currently 1.3GB+ tracked.
- `schedule compile` to generate plists for the 9 new workspaces (lint job each); load deferred until Adithya says go.

### Tier 3 (skill ports, ULTRON-local copies, no symlinks)

- distrokid (music workspace)
- zillow-rental-manager (property-management workspace) — Adithya is handling this in another session
- real-estate (Redfin / Zillow scrape)
- patchright bots: bumble, hinge (tinder is live in dating)
- Zernio: zernio-post + zernio-ads
- LLM dispatch: cloud-llm + local-llm
- Comms: slack-write, discord-write, notion-write, linear-write
- Media: higgsfield, remotion (remotion already vendored at `remotion/`)
- Browser-driven: x-read, grok-web, gpt-images
- icm-audit (the 15-30 min self-heal loop)

## Routing matrix TBDs (Adithya fills)

[`_shell/docs/source-routing.md`](\_shell/docs/source-routing.md) has rows marked `TBD` for:
- gmail label names per workspace (real-estate, property-management, music, clipping, onlyfans, trading, library, mosaic, synapse)
- drive folder names (MOSAIC, SYNAPSE, OUTERSCOPE)
- granola folder names (MOSAIC, SYNAPSE, OUTERSCOPE)
- imessage contact-set memberships in [`_global/contact-sets.yaml`](\_global/contact-sets.yaml) (dating, music, property-mgmt, fitness-coach, finance-pro)

Once these are filled, ingest can run.
