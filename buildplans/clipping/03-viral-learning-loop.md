---
workspace: clipping
section: learning-loop
status: in-flight
last_updated: 2026-04-28
---

# Viral Learning Loop

Two coupled feedback loops feeding into a single set of priors that the ranker, composer, and caption generator all consume.

## External loop: viral-corpus mining

Reverse-engineer what currently goes viral so the pipeline learns from the platform, not from its own past biases.

### New schema additions

- `viral_corpus` (id, niche, source_account_handle, platform, url, posted_at, views, likes, comments, transcript_text, caption_text, visual_description, hook_first_3s, ingested_at)
- `viral_playbooks` (id, niche, hook_pattern, caption_formula, visual_rule, template_match, sample_corpus_ids json, score, last_observed_at, created_at)

### New stage

`stages/00-research/CONTEXT.md` (new, before discover):

Inputs:

- Hand-curated seed accounts per niche (3-5 each); brave-search expansion when seeds run dry.
- Viral threshold per platform (default: >50K views OR >5% engagement-rate, posted last 30 days).
- `_core/skills/instagram-summary/` for IG Reels (Whisper + visual via local Gemma).
- `_core/skills/youtube-summary/` for YT Shorts (transcript only; visual via separate ffmpeg-extracted thumbnail through Gemma).

Process:

1. For each niche, pull seed accounts' recent posts.
2. Filter by viral threshold.
3. For each viral post: invoke summary skill, persist as `viral_corpus` row.
4. Weekly: cluster the corpus by hook structure, caption formula, visual style, pacing. Send each cluster to Claude with a "what unifies these and how would I produce more" prompt. Output: structured `viral_playbooks` rows with versioned rules.

Outputs:

- `viral_corpus` rows (immutable, append-only).
- `viral_playbooks` rows (recreated weekly; old versions archived with status='superseded').
- `~/.quantum/clipping/learning/priors.json` (consolidated prior state for fast read).

## Internal loop: own-metrics feedback

### New schema additions

- `learning_signals` (publish_attempt_id, signal_type, value, computed_at)

Signal types:

- `view_velocity_6h` — views in first 6 hours.
- `view_velocity_24h` — views at 24 hour mark.
- `peer_cohort_percentile` — percentile vs same-niche same-account same-week clips.
- `suppression_score` — 1.0 if first-6h velocity is more than 2 std below cohort median.
- `hook_pattern` — categorical tag from a small enum (controversy, named-stat, contrarian, story, list, question).
- `template_id` — which Remotion composition was used.

### New module

`bot/src/learn.py`:

```
python bot/src/learn.py compute      # recompute signals for last 30 days of attempts
python bot/src/learn.py priors       # write consolidated priors.json from corpus + signals
python bot/src/learn.py kill-list    # extend track.py kill-list with cohort-level dead patterns
python bot/src/learn.py weekly-recluster  # rebuild viral_playbooks from latest viral_corpus
```

### Cohort math

A cohort is a `(niche, account, source_creator OR campaign, hook_pattern, template_id)` bucket. For each cohort with 5+ samples in last 30 days:

- `mean_views_24h`
- `median_views_24h`
- `payable_views_per_publish`
- `verdict`: live | watch | kill

Kill rule: 10+ posts averaging under 1K views. Watch rule: 5+ posts averaging under 3K views. Live rule: anything beating peer median by 2x.

## Where the loops merge

Both loops write into `~/.quantum/clipping/learning/priors.json` with shape:

```json
{
  "by_niche": {
    "b2b-saas": {
      "top_hook_patterns": ["controversy", "named-stat", "contrarian"],
      "top_caption_formulas": [...],
      "top_template_ids": [...],
      "viral_playbook_ids": [12, 14, 17],
      "killed_creators": ["@some-creator"],
      "killed_campaigns": ["whop-...-slug"]
    }
  },
  "last_recomputed_at": "..."
}
```

## Consumption sites

### `rank.py`

LLM prompt at `shared/prompts/rank-moments.md` gains a `__PRIORS__` slot. `rank.py` injects the relevant niche's priors before invoking Claude. Ranker scores candidates against playbooks, not from a static prompt.

### `compose.py`

Composer picks Remotion template from `viral_playbooks.template_match` for the candidate's niche, falling back to the v1 default if no playbook matches. Unblocks the template-variation work because templates become data-driven, not hardcoded.

### Caption generator

`bot/src/caption.py` (new) reads `caption_formula` from the matched playbook and fills slots from the candidate's hook + niche tags + disclosure tokens.

### `discover.py`

Reads `killed_campaigns` from priors and refuses to re-pursue those slugs in subsequent scrapes.

## Decay model

Each `viral_playbooks` entry has `last_observed_at`. Not refreshed in 14 days = score halves. Forces continuous relearning instead of locking in last quarter's patterns. After 30 days unrefreshed: status flips to `superseded`.

## Open question

Whether to trigger weekly recluster on cron (launchd) or on manual `learn weekly-recluster`. Default: launchd Sunday 3am once first payout has landed; before that, manual only to avoid wasting cycles on a system that does not yet make money.

## Why this is the right shape

A pipeline that learns from its own past is local-extrema-prone. A pipeline that mines what currently works on the platform is calibrated to the platform's actual classifier. Both together is required: external corpus tells you what to aim at; internal metrics tell you whether you're hitting it.
