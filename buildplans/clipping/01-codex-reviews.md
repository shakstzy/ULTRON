---
workspace: clipping
section: adversarial-reviews
status: codex-applied
last_updated: 2026-04-28
---

# Codex Adversarial Reviews

Three codex passes ran during the build. Each cross-family review caught failure modes Claude self-review missed.

## Pass 1: research-conclusions review

Sent the four research workers' synthesis to codex. Verdict: directionally right, too bullish, namedrop-driven, underweighted enforcement and scams.

Critical corrections folded into the build:

- N3on's real rate is `$0.40-0.50/1K` views, NOT `$2-5/1K`. The earlier number conflated his $1.4M total spend with elite-clipper rates.
- Iman/Kai Whop pages mostly advertise UGC creator-campaign offers, not faceless repost rates. The headline `$2/1K` Kai page is fan-run and has scam complaints.
- Best 2026 niche is NOT business gurus. Those are saturated and policy-risky. Real opportunity: B2B SaaS, AI tools, fintech-with-disclosure at `$3-5/1K`. Sports-licensed clips when campaigns supply rights-cleared assets.
- Time to first $100 is realistically 2-6 weeks for a competent operator. Not days.
- 95% of clippers fail not because they cannot render but because they ship duplicative non-approved views into bad campaigns.

Output: `setup/decisions.md` baked all five corrections in as locked answers.

## Pass 2: plan review

Sent the workspace plan to codex before scaffolding. Verdict identified the core architectural mistake.

Key finding: "The stage-folder pipeline hides the real object: a campaign-qualified clip attempt. Build a SQLite control plane before scaling render throughput. Do not build a clip factory; build a bounty compliance and distribution system that happens to render clips."

Acted on:

- Added 11-table SQLite spine before any render code.
- Added `clip_fingerprint` (perceptual + transcript n-gram) before publish.
- Added `campaign_contract.json`-equivalent (rules_json + scam_score + verified_at) before any source download.
- Added pre-publish checklist as a runnable `gate.py` module.
- Switched core metric from `clips/day` to `paid_views_per_approved_publish`.
- Switched architecture from direct render-to-publish to quota-aware scheduler.

## Pass 3: code review on shipped pipeline

Sent actual files to codex with read-only sandbox. Ten findings; five were must-fixes applied in-session, five were acceptable v1 limits documented in `TODO.md`.

### Must-fix subset (applied)

- `#1 Gate not enforced by ledger`. Added `gate_decisions` table + `publish_attempts.gate_decision_id NOT NULL FK`. Removed public `insert_publish_attempt`. Only `create_publish_attempt_after_gate` writes attempts, atomically with the gate row.
- `#2 Caption not passed to zernio`. Publish path now uploads media first, then assembles a payload JSON with caption + disclosure flags + zernio_account_id, then `zernio.sh post payload.json`.
- `#5 Duplicate score logic backwards`. Any duplicate match now sets `score=1.0`; gate fails on any non-zero score (was permissive `<0.5`).
- `#6 Hex-char hamming, not bit-hamming`. Switched to `(int(a,16) ^ int(b,16)).bit_count()`. Threshold raised to 24 bits for the 256-bit pHash output.
- `#8 Disclosure regex too lax`. URLs stripped first; require standalone disclosure tokens (`#ad`, `Paid partnership`, `paid promotion`, `sponsored by`, `advertisement`, `ad:`); guards against `ad-free` and `#ad` inside URL fragments. Verified with 8/8 edge cases.

### Deferred to v2 (in TODO.md)

- `M1 SQLite TOCTOU` across logical units. Theoretical in single-operator setting. Fix: transaction-scoped DB functions with `BEGIN IMMEDIATE`.
- `M2 Quota check race` between gate.cadence and publish.insert. Documented "never run two publish.py concurrently" rule. Fix v2: move cadence check INTO `create_publish_attempt_after_gate` transaction.
- `M3 Brittle exact-SHA n-gram`. One ASR correction creates a different hash. Fix v2: store individual normalized 8-gram shingles in a `clip_shingles` table; Jaccard `>= 0.75`.
- `M4 campaign_id NOT NULL is wrong paid heuristic`. Today every candidate is treated as paid (over-disclosure direction is safe). Fix v2: add `compensation_expected`, `promotional_relationship`, `audience_connection_obvious` columns and gate those.
- `M5 Face tracking quality`. Haar at 1Hz with EMA. Visible quality issue, not safety. Fix v2: MediaPipe FaceMesh or YOLOv8-face at 5-10 fps with hold-last-known fallback. Remotion math: switch to `objectFit: cover` and compute pixel offsets from source dims and cover scale.
- `M6 Zernio payload is v1 minimal`. Will likely 4xx on first live attempt because per-platform shape is missing. Default is dry-run so this does not silently fail. Fix v2: parse `_core/skills/zernio-post/references/<platform>.md` and assemble full `platformSpecificData`.

## Codex review pattern as a workflow rule

Per the autonomy rule in global CLAUDE.md: any non-trivial diff goes to a cross-family adversarial review BEFORE shipping. Same-family review (Claude reviewing Claude) has confirmation bias on shared architectural blind spots. Codex caught issues a self-review missed because it sees the system fresh.

Going forward: every new pipeline addition (learning loop, viral corpus, template variation) gets its own codex pass before the smoke test loop closes.
