---
workspace: clipping
section: systemic-risks
status: captured
last_updated: 2026-04-28
source: local Gemma 4 26B, second-opinion architectural review
---

# Three Platform-Level Failure Modes

Captured from a Gemma second-opinion review of the shipped architecture. These are NOT code bugs. They are how the system fails in real operation when the code is correct.

Cross-injected into `~/QUANTUM/raw/learnings/2026-04-28-clip-distribution-failure-modes.md` so Graphify picks them up.

## 1. Algorithmic fingerprinting at the TEMPLATE layer

Even with file-level dedupe (perceptual hash plus transcript n-gram), TikTok and IG classify the *style* of output. Same Remotion template (word-by-word captions, hook overlay), same caption tone, same metadata pattern across multiple accounts shows up as an automated low-effort content cluster. They shadow-ban the *style*, not just the file.

The shipped v1 has ONE Remotion composition. Three accounts running it = pattern fingerprint.

Mitigation queued for v1.1:

- 3-4 visually distinct Remotion compositions, picked per account.
- Vary caption fonts, colors, layouts, hook positions.
- Mix word-by-word vs phrase-by-phrase captioning.
- Optionally rotate accents (US, UK, AU) for any narrated overlay.

Rule of thumb: if I can describe the visual style in one sentence and that sentence applies to all three accounts, the fingerprint is too tight.

## 2. Rights-status drift via DMCA, not law

Even when source `rights_status = authorized` (creator publicly invites clips), a single manual DMCA strike from that creator on a single platform causes account-level reputation hits. The "authorized" flag is a legal classification; platforms enforce *behavioral* signals from creators. A creator who perceives a clip account as theft will strike regardless of stated permission.

The shipped v1 documents `rights_status` once at source ingest and never re-checks.

Mitigation queued:

- Daily DMCA-watch script: poll account inboxes for takedown notices. Any incoming notice from a source creator pauses every clip from that creator across all accounts immediately, not just the platform that issued the strike.
- `sources.rights_status` becomes mutable (today it is set-once). Allowed transitions: `authorized -> revoked`, `campaign_allowed -> revoked`, `fair_use_review -> revoked`. The gate fails closed on `revoked`.
- Add to `learnings.md` (workspace-level): which creators issued strikes, when, on which platforms. Inform discover stage to deprioritize their content.

## 3. Feedback loop latency: ranker optimizes for what platform suppresses

The LLM moment-ranker uses static virality heuristics (controversial hook, self-contained payoff). Platform distribution algorithms shift on a 24-72h window. The pipeline ships clips faster than the platform's feedback comes back. Without dampening, the ranker keeps producing high-virality candidates that the algorithm is actively de-prioritizing this week.

The shipped v1 has no feedback loop into the ranker.

Mitigation queued for v1.1 (see `03-viral-learning-loop.md`):

- Track per-clip view-velocity in the first 6 hours.
- Compute peer-cohort percentile for the (niche, account, source-creator) bucket.
- Suppression score: clips far below cohort median in the first 24h.
- Feed into ranker as a prior: "in the last 30 days, clips of source creator X averaged 2,300 views with hook pattern Y averaging 8,400; favor Y, deprioritize creator X next week."
- Decay older signals (14d half-life) so the system tracks current algorithm behavior, not last quarter's.

## Why these matter

A perfectly-built pipeline that ignores these three modes will:

1. Produce content nobody sees because the platforms classify the output style as automated.
2. Get accounts terminated despite stated permissions when a creator decides to enforce.
3. Optimize for virality patterns the platform is actively suppressing this week.

The shipped pipeline is correct. It is not yet adaptive. The v1.1 work converts it from correct to adaptive.

## Cross-domain pattern

These three modes apply to any content-distribution pipeline, not just clipping. The take-home: file-level dedupe is necessary but not sufficient; distribution is a multi-day adversarial game with the platform's classifier; optimize for *delivered* views, not *produced* views.
