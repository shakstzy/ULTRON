---
workspace: clipping
section: niche-strategy
status: locked-2026-04-28
last_updated: 2026-04-28
source: codex adv-review pass 1, web-search 2026-04
---

# Niche Strategy

The niche pivot is the highest-leverage decision in this build. Adv-review pass 1 corrected an early namedrop-driven plan and locked the v1 starting bet.

## What changed from the first plan

Initial plan: streamer (Kai Cenat / N3on) and business-guru (Iman / Hormozi) clipping. Codex pass 1 hit hard:

- Kai Cenat Whop pages mostly fan-run, low-trust, scam complaints visible in reviews.
- N3on real rate is `$0.40-0.50/1K`, not the `$2-5/1K` the early plan quoted. The famous `$1.4M paid in 5 weeks` figure conflated total spend with elite-clipper rate.
- Iman Whop pages advertise UGC creator-campaign offers ("up to $2K per video") not faceless repost rates.
- Business-guru clip output is saturated and policy-sensitive. Drift into "make money" / "passive income" claims trips banned-niche regex.

## Locked v1 starting bet

| Niche | Rate | Why |
|---|---|---|
| **B2B SaaS / AI tools** | $3-5/1K | Less saturated, low ToS risk, paid by software companies running real ads |
| **Fintech with disclosure** | $4-6/1K | Higher rate but tighter compliance; caption MUST hit `#ad` |
| **Sports-licensed** (campaign-supplied assets only) | $1-5/1K | Only when campaign supplies rights-cleared assets; raw NBA/NFL/UFC reposting is copyright-risky |

## Banned niches (auto-reject at three checkpoints)

Enforced by `bot/src/lib/banned.py` regex against campaign rules at discover, transcript at clip, and caption at gate.

- Gambling / sportsbook / casino / poker / slot machines / odds boost
- Crypto trading / coin shilling / pump-and-dump / presale memecoin
- Get-rich-quick / passive-income / guaranteed-returns
- Medical / supplement health claims (cure / treats / reverses)
- Financial advice without disclaimers (buy this stock / day trade now)
- Adult / OnlyFans / sugar / NSFW promotion
- Manosphere / red-pill / sigma grindset / hypergamy / MGTOW
- Conspiracy / health misinformation / vaccines-cause / new-world-order
- Weight-loss before-after with claims (lose N pounds / weight-loss secret)
- Political paid endorsement (vote for / endorsing candidate)

Updates to this list: edit `bot/src/lib/banned.py` PATTERNS, also update `shared/policy/banned-niches.md` for human reference. Re-run audit on existing campaigns.

## Account-niche binding

Each account in `accounts` table has a `niche` column. Cross-niche posting is a ban-vector and is blocked by `gate._account_niche_fit`.

Default v1 mapping (overridable):

- Burner 1: `b2b-saas`
- Burner 2: `ai-tools`
- Burner 3: `fintech-disclosed`

Adithya's existing branded accounts (`@stunnashak`, `@adithya.shak.kumar`, `@shakstzy`) are NOT auto-assigned. Repurposing them changes their public identity and is a brand-call.

## Saturation check

Re-evaluate the lock if:

- More than 10 active campaigns in the same niche all want the same source-creator (saturation signal; pivot to adjacent niche).
- Top viral_playbook in the niche stops refreshing for 30 days (signal that platform has classified the niche pattern).
- Three or more accounts in the same niche see suppression scores above 0.7 in same week.

## Long-shot upgrade niches (track, do not pursue v1)

- AI productivity tools when an enterprise SaaS sponsor enters the market.
- Climate-tech and energy when carbon credit sponsors emerge.
- Healthcare-adjacent (telemedicine, mental wellness apps with proper disclaimers).

These have policy-aware sponsors with deep budgets and lower clipper saturation than current B2B SaaS. Watch for the first authorized campaign in any of them as a pivot signal.
