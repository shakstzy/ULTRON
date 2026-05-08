---
name: higgsfield
description: Drive higgsfield.ai from Claude Code to generate images (Nano Banana Pro, Soul Cinematic, GPT Image, Seedream, FLUX, Reve, Grok Imagine, etc.), videos (Kling, Seedance, Wan, Minimax), Marketing Studio ads, and Cinema Studio scenes. Browser automation via patchright over a dedicated persistent Chrome profile. Saves outputs locally with full metadata. Triggers on "higgsfield image", "higgsfield video", "nano banana", "soul cinematic", "marketing ad on higgsfield", "cinema studio scene", "seedance", "kling", "wan", "minimax".
---

# Higgsfield Skill

Five tool families on higgsfield.ai, one Node CLI. UI automation via patchright, DataDome-aware stealth, durable per-run state for paid-job recovery.

## When this fires

Trigger phrases (non-exhaustive): "generate a higgsfield image", "higgsfield video", "make a marketing ad", "cinema studio scene", "nano banana", "soul cinematic", "seedance", "kling 2.5", "wan", "minimax", "make me a video / image of X" when context implies higgsfield.

Do NOT fire for:
- Other AI services (DALL-E, Midjourney, Runway — use their own skills/APIs).
- Text generation, music generation, audio generation.
- Edit / remix / inpaint flows on higgsfield (out of scope).
- Character or location creation (`/character`, Soul Cast/Location).

## ULTRON integration

This is a **generative skill** — it produces NEW media, not personal-knowledge data. Outputs do NOT enter ULTRON's `raw/` workspace structure or graph.

| Item | Path |
|---|---|
| Skill home | `_shell/skills/higgsfield/` (real files, not symlinked) |
| Chrome profile | `_credentials/browser-profiles/higgsfield/` (gitignored) |
| Per-run output | `_shell/skill-output/higgsfield/<YYYYMMDD-HHMMSS>-<slug>/` (gitignored) |
| Registration | `~/.claude/skills/higgsfield → _shell/skills/higgsfield/` |

## Browser runtime contract

| Item | Path / Value |
|---|---|
| Profile directory | `/Users/shakstzy/ULTRON/_credentials/browser-profiles/higgsfield/` |
| Login command | `node scripts/run.mjs login` |
| Pidfile | `<profile>/.skill.pid` (atomic `openSync(..., 'wx')`) |
| Breaker file | `<profile>/.breaker.json` |
| Breaker trip | Two consecutive 403s in 24h OR captcha DOM detection |
| Breaker cooldown | 24h halt; `--force` to override |
| Auth probe | Clerk JWT capture from outgoing page traffic |

## First-time setup

```bash
cd _shell/skills/higgsfield
npm install                       # patchright + Chrome (~200MB)
node scripts/run.mjs login        # visible Chrome window for Clerk OAuth
```

Future runs reuse the persistent profile silently. If session expires, run `login` again.

## Commands

```bash
node scripts/run.mjs image     --model nano-banana-pro --prompt "..." [--aspect 3:4] [--res 1k] [--batch 1] [--ref PATH]...
node scripts/run.mjs image     --model soul-cinematic  --prompt "..." [--aspect 16:9]
node scripts/run.mjs video     --model seedance_2_0_fast --prompt "..." [--duration 8s] [--ref PATH]
node scripts/run.mjs video     --model sora_2          --prompt "..."                # Sora 2 (added 2026-04)
node scripts/run.mjs video     --model veo3_1          --prompt "..."                # Veo 3.1 (lip-sync)
node scripts/run.mjs marketing --preset UGC            --prompt "..." [--project-id X | --new] [--ref PATH] [--hook NAME] [--avatar NAME]
node scripts/run.mjs cinema    --mode image|video      --scene "..." [--project-id X | --new] [--duration 8s] [--genre Action|Horror|Comedy|Noir|Drama|Epic|General] [--style NAME]
node scripts/run.mjs batch     --jobs <jobs.jsonl>     [--concurrency 1]    # sequential by default
node scripts/run.mjs resume    <run-dir>                                    # download-only recovery
node scripts/run.mjs recon                                                  # inventory new UI surfaces (writes JSON)
node scripts/run.mjs status                                                 # wallet + breaker + pidfile
node scripts/run.mjs reset-breaker                                          # clear 24h cooldown
```

### Marketing Studio V2 (released 2026-04-30)

10 content format modes: `UGC`, `Product Review`, `Tutorial`, `Unboxing`, `TV Spot`, `Virtual Try-On`, `UGC Virtual Try-On`, `Cleanshot UGC`, `Hyper Motion`, `Wild Card`. Pass via `--preset NAME`. Legacy V1 names (`Testimonial`, `How-To`, `Founder Story`, `Product Showcase`) still accepted. Viral hook templates and 40+ avatar library accessed via `--hook` / `--avatar` flags (selectors verified via `recon`).

### Cinema Studio 3.5

7 genre modes: `Action`, `Horror`, `Comedy`, `Noir`, `Drama`, `Epic`, `General`. 27 style options (see `rules/tool-flows.md`). Up to 9 reference images. Native audio sync (SFX + speech + music) on video mode.

Global flags: `--output DIR`, `--dry-run`, `--debug`, `--force`, `--unlim`, `--free-gens`, `--cost-cap N`.

## Resume semantics (download-only)

`resume <run-dir>` reads the run's `state.json` for `job_uuid`, opens the History panel, finds the matching completed asset, downloads it. **Never re-submits.** This protects against "I paid for a 30-min video, the CLI process died" by recovering the asset that the server already produced. If the matching asset isn't yet in History, resume polls until it appears or times out (5 min for image, 30 min for video).

The `submitted` state-machine transition writes `job_uuid` to `state.json` immediately on POST response, so resume always has something to read once the page-side submit succeeds.

## Batch concurrency

Default `--concurrency 1` (sequential UI submits). Parallel typing/clicking on a single browser cross-wires keyboard focus and creates picker-dropdown races. The wait/poll phase still overlaps server-side. Bump to 2-4 for image batches only when the UI is reliably stable; ceiling 8 (account cap).

`jobs.jsonl` format (one JSON object per line):
```
{"prompt":"...", "cmd":"image", "model":"nano-banana-pro", "aspect":"1:1"}
{"prompt":"...", "cmd":"video", "model":"seedance_2_0_fast", "duration":"5"}
{"prompt":"...", "cmd":"marketing", "preset":"UGC", "ref":["/path.webp"]}
{"prompt":"...", "cmd":"cinema", "mode":"image"}
```
All jobs in one batch share a `cmd` (mixed-cmd batches rejected — different tool pages).

## Procedure

1. **Pre-flight.** Catalog lookup (image/video model, marketing preset, cinema mode) sets `expected_cost`. Wallet preflight enforces 2× safety floor unless `--unlim`. Cost cap defaults to 500 credits.
2. **Launch.** Single browser context, off-screen window (`--window-position=-2400,-2400`), persistent profile, stealth init script, JWT capture listener.
3. **Submit via UI.** Browse phase → fill prompt (most-visible textarea) → select model + pickers → upload refs → click Generate (humanClick + bezier mouse on the primary action; force-click everywhere else). The page composes its own POST body with full DataDome JS context; we capture `job_sets[0].id` from the response.
4. **Poll via History.** Open the History panel, scrape user-owned cloudfront/cdn.higgsfield.ai URLs, wait for `expectCount` new assets (5 min image, 30 min video).
5. **Download.** Stream-download with byte cap, content-type allowlist, sha256, atomic `.partial → rename`. Video thumbnails resolve to mp4 via uuid-based URL derivation.
6. **Finalize.** Write `metadata.json` with cost delta, file paths, sha256s.

## Circuit breaker

Two 403s in 24h OR any captcha DOM detection trips a 24h halt. Override with `--force` (strongly discouraged) or `node scripts/run.mjs reset-breaker` after solving captcha manually in your normal browser.

## Composing into workflows

Each run produces a deterministic `<runDir>` with `state.json` (job_uuid, prompt, params) and `metadata.json` (local_path, sha256, cost_credits_actual).

```bash
RUN_DIR=$(node _shell/skills/higgsfield/scripts/run.mjs image \
  --model nano-banana-pro --prompt "..." --aspect 1:1 --res 1K \
  | grep -oE "/Users/.*skill-output/higgsfield/[^ ]+")
LOCAL_PATH=$(jq -r '.local_path' "$RUN_DIR/metadata.json")
# now hand $LOCAL_PATH to ffmpeg / iMessage / wherever
```

## Files

- `scripts/run.mjs` — CLI dispatcher
- `scripts/{image,video,marketing,cinema,batch}.mjs` — per-tool handlers
- `scripts/{browser,job,state,download,ui-submit,jwt,behavior,fingerprint}.mjs` — shared infra
- `scripts/login.mjs` — one-time Clerk OAuth via visible Chrome
- `rules/tool-flows.md` — per-tool selectors & body schemas (reference)
- `rules/datadome-defenses.md` — stealth stack & breaker rules (reference)
- `rules/output-conventions.md` — output folder layout & metadata.json schema (reference)

## Smoke test status (last verified 2026-05-08)

| Handler | Status | Notes |
|---|---|---|
| `image` | ✅ working | nano-banana-pro tested, free with `--unlim` |
| `video` | ✅ working | seedance_2_0_fast 8s tested, free with `--unlim`. NOTE: 5s no longer accepted — use 8s minimum |
| `marketing` | ⚠️ V2 rework needed | UI restructured 2026-04-30 (Product/App tabs + UGC/Hook/Setting sub-tabs). Generate clicks but no `/jobs/` POST fires. CLI flags (`--hook`, `--avatar`) wired but require post-recon UI flow. |
| `cinema` | ⚠️ 3.5 partial | Mode switch fixed (aria-selected verification), `--genre`/`--style` wired. Generate clicks but no `/jobs/` POST fires — likely page-side gating (model/genre/style required). |

For marketing/cinema fixes, run `node scripts/run.mjs recon` to dump current DOM, then use `--debug` flag to leave the browser open and inspect what Generate is doing.

## Out-of-scope (v1)

- No audio gen, character/location creation, edit/remix/inpaint
- No automatic upscale or post-processing
- Resume is download-only (no re-submit)

## Troubleshooting

| Problem | Action |
|---|---|
| `Profile locked by pid N` | Wait or kill stale pid |
| `Session expired` | `node scripts/run.mjs login` |
| `403 from DataDome` | Breaker halt 24h. Wait, reset-breaker, or `--force` |
| `Captcha in DOM` | Same — solve manually in your browser, then `reset-breaker` |
| Downloaded file size 0 / mismatch | `resume <run-dir>` retries download only |
| `Insufficient credits` | Top up. Skill surfaces wallet pre-submit |
| CLI timeout on long video | `resume <run-dir>` to recover the paid asset |

## ToS

Automated access to higgsfield.ai likely violates ToS; DataDome bypass is circumvention of technical protection. Use at your discretion. Burner account recommended for heavy production use.
