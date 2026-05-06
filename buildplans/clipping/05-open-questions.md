---
workspace: clipping
section: open-questions
status: tracking
last_updated: 2026-04-28
---

# Open Questions and Deferred Items

What is parked, what needs decisions, what gets the v2 work.

## Decisions Adithya owes

| Item | Default if unanswered | Impact |
|---|---|---|
| Account identity strategy | Hybrid: keep `@adithya.shak.kumar` IG personal, repurpose `@stunnashak` TT (low follower, low loss), spin up burners. Adithya stated burners on the way; default may be moot. | Brand-call, blocks live publish |
| Niche per account | Burner 1 = b2b-saas, Burner 2 = ai-tools, Burner 3 = fintech-disclosed | Locks account-niche-fit gate |
| Viral threshold for corpus | >50K views OR >5% engagement, last 30d | Tunes external loop sensitivity |
| Seed accounts per niche | Brave-search bootstrap + filter by follower count | Slower and noisier than hand-pick |
| Whop account access | Paste-only mode (operator copies pages into markdown) | Slower; prevents auto-discover |
| Launchd cron activation | Manual until first payout | Avoids wasting cycles on unproven system |

None of these block scaffold or smoke. All block live publish at scale.

## Engineering work in flight (v1.1)

In priority order:

1. **Scraper layer for Whop / Vyro / Discord clipper bounties.** Whop and Vyro APIs are seller-facing, not browse-other-people's-campaigns. Must scrape. Built on firecrawl + per-platform selector layer. Live-test, diag, fix per browser-skill memory.
2. **Viral learning loop end-to-end.** Schema additions, `learn.py`, prompt updates in rank.py and compose.py. See `03-viral-learning-loop.md`.
3. **Template variation.** 3-4 distinct Remotion compositions. Picked per account by playbook match. Unblocked by viral_playbooks table once mining returns first cluster.
4. **End-to-end real-video smoke.** yt-dlp + mlx-whisper tiny model + render. Validates the whisper path which the synthetic test skipped.
5. **Codex pass on the v1.1 publish-payload assembly.** v1 minimal payload will likely 4xx on first live attempt.

## Deferred from Codex code review (TODO.md captures details)

- M1 SQLite TOCTOU across logical units. Theoretical risk in single-operator setting.
- M2 Quota-check race in publish path. Documented "no parallel publish" rule for v1.
- M3 Brittle exact-SHA n-gram. Move to MinHash or shingle-Jaccard at >= 0.75 in v2.
- M4 `campaign_id NOT NULL` as paid heuristic. Add explicit `compensation_expected` etc fields.
- M5 Face tracking quality. Replace Haar with MediaPipe FaceMesh at 5-10fps. Fix Remotion math (objectFit cover, pixel offsets, clamp).
- M6 Zernio payload v1 minimal. Will fail 4xx on first live attempt; default dry-run protects user.

## Architecture questions parked for after first payout

- **DMCA-watch automation.** Per Gemma risk #2, a daily watch on takedown notices that flips `sources.rights_status` to `revoked` across all accounts. Today the field is set-once.
- **Suppression detection automation.** Per Gemma risk #3, first-6h view velocity vs cohort median. Schema is in place via `metrics_snapshots` time series; logic queued in `learn.py`.
- **Multi-account orchestration.** Today publish.py loops accounts sequentially. At 5+ accounts the sequential loop becomes slow. Move to a per-account worker model with the `BEGIN IMMEDIATE` quota reservation.
- **Caption humanizer pass.** Per humanizer-messaging memory: every outbound caption should run through humanizer skill before persistence. Today caption gen is template-string formatting.

## Hypotheses to validate after first 30 days of operation

- Does the gate's `originality_check` reduce ban rate vs a stripped pipeline?
- Does the FTC `#ad` disclosure cost views, or is engagement neutral within margin?
- Does the perceptual-hash + n-gram dedup actually catch real duplicates, or is it a Maginot line that catches nothing because no one re-posts identical clips this week?
- Does the cohort-level kill-list pause campaigns BEFORE Adithya gets paid less than spent on Whop fees?

Each hypothesis has a one-line measurement plan in `track.py northstar` output (TODO: extend the JSON to include these signals once data is in).

## When this file gets updated

After each weekly metrics review. Move resolved items to `setup/decisions.md` (workspace-local, locked). Move newly discovered items here. This file is a living scratchpad; `setup/decisions.md` is the contract.
