---
workspace: clipping
status: v1-shipped
last_updated: 2026-04-28
canonical_code: ~/QUANTUM/workspaces/clipping/
---

# Clipping Buildplan

Bounty-compliance + distribution system for paid UGC clipping. Shipped to QUANTUM 2026-04-28; learning loop + scraper layer + template variation queued for v1.1.

## Files

| File | Purpose |
|---|---|
| `00-architecture.md` | SQLite control-plane spine, gate enforcement, ICM stage layout |
| `01-codex-reviews.md` | Three codex adversarial passes (research, plan, code) + applied vs deferred fixes |
| `02-gemma-systemic-risks.md` | Three platform-level failure modes (template fingerprint, rights drift, feedback latency) |
| `03-viral-learning-loop.md` | External viral-corpus mining + internal metrics feedback into rank.py |
| `04-niche-strategy.md` | B2B SaaS / AI / fintech-disclosed pivot from saturated business-gurus |
| `05-open-questions.md` | Deferred items, decisions needed, v2 roadmap |

## North-star metric

`paid_views_per_approved_publish = sum(payable_views) / count(qa_approved publishes)`

Optimized for paid-eligible distribution, not raw render throughput. Per Codex adv-review v2: render is replaceable; the campaign/account/rights ledger is what keeps the operation alive.

## Quick links

- Workspace root: `~/QUANTUM/workspaces/clipping/`
- DB: `~/.quantum/clipping/clipping.db`
- Logs: `~/.quantum/clipping/logs/`
- Remotion project: `~/QUANTUM/workspaces/clipping/remotion/`
- Skill: `~/QUANTUM/_core/skills/remotion/SKILL.md`
