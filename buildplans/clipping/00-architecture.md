---
workspace: clipping
section: architecture
status: shipped
last_updated: 2026-04-28
---

# Clipping Architecture

Bounty-compliance and distribution system that happens to render clips. The render stack is replaceable; the campaign/account/rights ledger is what keeps the operation alive.

## The spine

A SQLite control plane at `~/.quantum/clipping/clipping.db` is the source of truth. Filesystem is artifact storage.

11 tables, schema v3:

- `campaigns` (slug, source, payer, niche, rate_per_1k_usd, scam_score, verified_at, status, rules_json)
- `sources` (source_video_id, url, creator, audio_hash, campaign_id, rights_status, rights_evidence, filepath)
- `transcripts` (source_id, model_version, audio_hash, filepath) - UNIQUE on (source_id, model_version), cached forever
- `clip_candidates` (source_id, campaign_id, start_s, end_s, hook, rank_score, ngram_hash, perceptual_hash, duplicate_score, status)
- `renders` (candidate_id, template, filepath, render_hash)
- `qa_reviews` (candidate_id, reviewer, decision, reasons, per-check booleans, platform_risk_score)
- `accounts` (alias, platform, zernio_account_id, niche, daily_post_cap, hourly_post_cap, status)
- `gate_decisions` (candidate_id, account_id, passed, failed_checks, full_checks_json, caption) - see Gate Enforcement below
- `publish_attempts` (candidate_id, render_id, account_id, gate_decision_id NOT NULL, status, caption, zernio_post_id, platform_url)
- `metrics_snapshots` (publish_attempt_id, views, likes, comments, shares, measured_at) - time series, INSERT-only
- `payout_claims` (campaign_id, publish_attempt_id, expected_usd, paid_usd, status)

## Gate enforcement at the schema layer

Per Codex code review #1, the gate is enforced as a database invariant, not application code:

`publish_attempts.gate_decision_id INTEGER NOT NULL REFERENCES gate_decisions(id)`

The only public API path that creates a publish attempt is `db.create_publish_attempt_after_gate(...)`, which runs in a `BEGIN IMMEDIATE` transaction:

1. Insert `gate_decision` row with full check JSON
2. If passed: insert `publish_attempt` referencing the gate_decision
3. Commit atomically

Bypass attempt verified blocked: `INSERT INTO publish_attempts(...)` without `gate_decision_id` returns `NOT NULL constraint failed: publish_attempts.gate_decision_id`.

## ICM workspace layout

```
workspaces/clipping/
  CLAUDE.md, CONTEXT.md, TODO.md
  setup/{questionnaire.md, decisions.md}
  shared/
    schema.sql                                        # the spine
    policy/{scam-checklist, banned-niches, ftc-disclosure, pre-publish-gate, platform-risks}.md
    prompts/{extract-campaign, rank-moments}.md
  stages/01-discover .. 07-track                      # 7 CONTEXT.md per ICM Pattern 1
  bot/src/{db, discover, source, transcribe, rank, fingerprint, cut, clip, compose, gate, publish, track}.py
  bot/src/lib/{banned, claude}.py
  bot/scripts/{status, discover, source, clip, render, qa, publish, reconcile, run, smoke, smoke-bypass}.sh
  remotion/                                           # Remotion 4.0.454 project
  requirements.txt
  .venv/
```

## Pipeline shape

```
01-discover -> campaigns (verified, scam-screened)
02-source   -> sources (rights_status documented) + raw video
03-clip     -> transcripts (cached) + clip_candidates (ranked, fingerprinted)
04-render   -> renders (only after dedup gate)
05-qa       -> qa_reviews (gate must be all-green)
06-publish  -> publish_attempts (one per (candidate, account))
07-track    -> metrics_snapshots + payout_claims
```

Stages 04 through 06 enforce the 10-check gate.

## The 10-check pre-publish gate

Every check must be green or the publish_attempt is created with status='dry_run' (failed-gate variant); none of the failed checks can post.

1. `campaign_verified` - `campaigns.status='active' AND verified_at IS NOT NULL`
2. `rights_check` - `sources.rights_status` in (`authorized`, `campaign_allowed`, `fair_use_review`)
3. `duplicate_check` - `duplicate_score == 0.0` (any match fails; previously was <0.5 which let duplicates through)
4. `account_cadence_available` - under daily and hourly caps
5. `account_niche_fit` - exact match between campaign niche and account niche
6. `originality_check` - at least one transformative element (hook overlay or custom captions)
7. `disclosure_resolved` - caption passes tightened disclosure regex (URLs stripped, standalone tokens required)
8. `qa_status` - latest `qa_reviews` decision is `approve`
9. `platform_risk_score` - under 30 for the target platform
10. `banned_niche_clean` - no hits against banned-niches regex (gambling, crypto-trading, manosphere, OnlyFans, conspiracy, get-rich-quick, etc.)

## North-star metric

`paid_views_per_approved_publish` - tracked daily by `track.py northstar`. Anything that does not move this metric is decoration.

## State paths

- DB: `~/.quantum/clipping/clipping.db`
- Source mp4s: `~/.quantum/clipping/sources/<source_video_id>.mp4`
- Transcripts cache: `~/.quantum/clipping/transcripts/<source_video_id>-<model>.json`
- Rendered candidates: `~/.quantum/clipping/candidates/<candidate-id>.mp4`
- Logs: `~/.quantum/clipping/logs/`
- Payout receipts inbox: `~/.quantum/clipping/inbox/payouts/`

## Skills wired

| Skill | Used by | Purpose |
|---|---|---|
| firecrawl | 01-discover | Scrape Whop/Vyro campaign pages |
| brave-search | 01-discover | Find new campaign sources |
| remotion | 04-render | Vertical 9:16 compose with word-level captions |
| zernio-post | 06-publish | Direct REST publish to TT/IG/YT |
| youtube-summary | 02-source | Cross-validate YT long-form transcripts |
| local-llm (Gemma) | 03-clip | Optional second-opinion moment ranking |
| instagram-summary | 03-research (v1.1) | External viral corpus mining |
