# Tool Flows (canonical)

Per-tool UI selectors, backend slugs, and body schemas for the five Higgsfield tool families. **Reference doc, not imported by scripts.** The live catalogs are hardcoded in `scripts/image.mjs`, `scripts/video.mjs`, `scripts/marketing.mjs`, `scripts/cinema.mjs`. When slugs / costs / labels drift, update both this doc AND the script catalog.

## API pattern (all tools)

- Submit: `POST https://fnf.higgsfield.ai/jobs/<BACKEND_SLUG>` with `Authorization: Bearer <ClerkJWT>` and body `{ params: {...}, use_unlim: bool, use_free_gens: bool }`
- Lifecycle:
  - `GET /jobs/<id>` full job (accepts `?cluster=true`)
  - `GET /jobs/<id>/status` light status
  - `PUT /jobs/<id>/cancel` cancel
  - `POST /jobs/<id>/publish | /unpublish`
- Multi-job batches (Cinema, Marketing): `GET /job-sets/<id>`, polled up to 10 attempts
- Status stream: `GET https://notification.higgsfield.ai/notifications/stream` (SSE, `accept: text/event-stream`)
- Media init: `POST /media/batch`
- Video upload: `POST /video`, `GET /video/<id>/meta`
- Free gen quota: `GET /user/free-gens/v2`
- Wallet: `GET /workspaces/wallet`, `GET /user` (returns `subscription_credits`)

Auth refresh: `POST https://clerk.higgsfield.ai/v1/client/sessions/<sid>/tokens`. 60 second JWT TTL.

## Nano Banana Pro

- Frontend URL: `https://higgsfield.ai/ai/image?model=nano-banana-pro`
- Backend slug: `nano_banana_2`
- Body (confirmed live 2026-04-21):
  ```json
  {
    "params": {
      "prompt": "STRING",
      "input_images": [],
      "width": 896,
      "height": 1200,
      "batch_size": 1,
      "aspect_ratio": "3:4",
      "is_storyboard": false,
      "is_zoom_control": false,
      "use_unlim": false,
      "resolution": "1k"
    },
    "use_unlim": false,
    "use_seedream_bonus": false
  }
  ```
- Cost: 2 credits at 1K / 3:4 / batch 1
- Aspect options: `3:4`, `1:1`, `4:3`, `16:9`, `9:16`
- Resolution options: `1k`, `2k`
- Key selectors (update when UI shifts):
  - Prompt textbox: `textbox[aria-label="Describe the scene you imagine"]`
  - Aspect button: `button[aria-haspopup="listbox"]` with text `3:4` / etc.
  - Resolution button: `button[aria-haspopup="listbox"]` with text `1K` / `2K`
  - Generate button: `button` containing text `Generate`
  - Result: `img` within `main` section, `src` starts `https://images.higgs.ai/`, original at embedded `url=` param decoded to `d8j0ntlcm91z4.cloudfront.net/...`

## Soul Cinematic

- Frontend URL: `https://higgsfield.ai/ai/image?model=soul-cinematic`
- Backend slug: `soul_cinematic` (new) or `text2image_soul_v2` (legacy prompt-only). Prefer `soul_cinematic`.
- Body keys: `prompt`, `characterStyleId`, `styleId`, `aspect_ratio`, `batch_size`, `soul_v2_preset`, `use_unlimited`
- LocalStorage side-channel: `soul-v2-seed`, `soul-v2-style-strength`, `soul-v2-custom-reference-strength` (read when present, otherwise default).
- Cost: 0.125 credits at 16:9 / 2K with unlim plan (else higher)
- Aspect default: `16:9`; resolution default: `2k`
- Extra controls: Color Transfer, Soul Hex, Character link (optional)

## AI Video

- Frontend URL: `https://higgsfield.ai/ai/video`
- Model picker maps to backend slug. Supported slugs:
  - `kling3_0` (default), `kling2_6`, `kling2_6_motion_control`, `kling3_0_motion_control`, `kling_omni_image`
  - `seedance_2_0`, `seedance_2_0_fast` (shares backend slug `seedance_2_0`; variant differentiated by body param), `seedance_2_0_beta`, `seedance1_5`, `seedance` / `seedance_pro`
  - `veo3_1`, `veo3_1_lite`, `veo3_1_speak`, `veo3`
  - `wan2_7`, `wan2_6`, `wan2_5_video`, `wan2_5_speak`, `wan2_2_video`, `wan2_2_animate` (+ `_v2`, `_v3`, `_faceswap`, `_revoice`)
  - `open_sora_video` (frontend `sora-2`), `sora2_video` family (`sora-pro`, `sora-2-max`, `sora-2-pro-max`), `sora2_video_upscale`, `sora2_video_deflicker`
  - `minimax_hailuo`, `minimax-fast`
- Common body keys: `prompt`, `duration` (default 5), `aspect_ratio` (default varies per model), `resolution` (720p default, 1080p available), plus model-specific keys:
  - Kling 2.6: `cfg_scale` (0.5), `sound` (bool), `motion_id`, `negative_prompt`
  - Kling v2/v2.1: `preset_id`, `camera_control`, `is_camera_control_enabled`, `isPresetFlf`
  - Kling Omni: `videos`, `images`, `imageFirstFrameId`, `imageLastFrameId`, `elements`, `mode` (pro / std)
  - Seedance: `fixedLens`, `generateAudio` (true), `use_unlimited`
  - Veo 3.1: `veo3_1Fields.input_images[]`, `generateAudio`
  - Sora: `soraFields.sketchStyle`, `opacity` (flag-gated), `mode` (nano-banana prepass or raw)
  - Wan 2.5+: `enhance` toggle, `quality` select
- Cost: 10 to 100 credits per model
- Key controls in UI: Start frame (optional file), End frame (optional file), Multi-shot toggle, Model picker, Elements, Duration, Aspect ratio, Resolution

## Marketing Studio V2 (released 2026-04-30)

- Frontend URL: `https://higgsfield.ai/marketing-studio[?marketing-project-id=X]`
- Backend slug: `marketing_studio_video` (V1 — V2 slug TBD; smoke test 2026-05-08 timed out, use `recon` + `HF_DEBUG=1` to discover real V2 slug from page POSTs)
- V2 layout (recon 2026-05-08):
  - Left rail: `Product`/`App` mode tabs (x=297, role=tab)
  - Center top: `UGC`, `Hook`, `Setting` config tabs (x=389-687, y=357)
  - Left sidebar: `Url to Ad`, `Ad Reference` (x=6) — paste viral ad URL or upload reference
  - Right: `PRODUCT`, `AVATAR`, `GENERATE` (x=959-1131, y=306, 80x80 each)
  - Default project: a sample product (e.g. "Sleek Coffee Grinder") may auto-populate
- Content modes (10 total): `UGC`, `Product Review`, `Tutorial`, `Unboxing`, `TV Spot`, `Virtual Try-On`, `UGC Virtual Try-On`, `Cleanshot UGC`, `Hyper Motion`, `Wild Card`. Legacy V1 names (`Testimonial`, `How-To`, `Founder Story`, `Product Showcase`) may still resolve.
- Hermes Agent (viral hooks): "Pick a proven opener, Marketing Studio builds the rest around your product." Click `Hook` tab to access.
- Avatar library: 40+ pre-built AI presenters (pin/rename/reuse). Click `AVATAR` button.
- Ad Reference tool: upload a viral ad, AI extracts its structure and applies to your product. Click `Ad Reference` left sidebar.
- Bulk variant generation: 50+ ad variants for A/B testing (V2 feature, exact UI TBD).
- 20 ad effects (Ads & Products app library): Click to Ad, ASMR Add-On, Poster, Bullet Time Scene, Bullet Time White/Splash, Giant Product, Billboard Ad, Graffiti Ad, Truck Ad, Volcano Ad, Fridge Ad, Magic Button, Kick Ad, Packshot, Macroshot, Macro Scene, Chameleon, ASMR Host, ASMR Classic.
- Cost: 40 to 48 credits per gen (V1); V2 cost TBD post-recon.
- Skill flags: `--preset NAME` (preset selection), `--hook NAME` (viral hook), `--avatar NAME` (avatar library), `--project-id X | --new`.

## Cinema Studio

- Frontend URL: `https://higgsfield.ai/cinema-studio[?cinematic-project-id=X&workflow-project-id=X]`
- Backend slugs (confirmed live 2026-04-24):
  - Cinema Studio 3.5 video: `cinematic_studio_video_3_5` (cost 96 @ 1080p 8s)
  - Cinema Studio image: `cinematic_studio_image` (cost 2; the stale `cinematic_studio_image_v2` form returns 404)
  - Additional video slugs (less commonly routed): `hf_fnf_video` / `cinematic_studio_3_0`, `cinematic_studio_3_0_beta`
  - Additional image slugs: `cinematic_studio_3_0_image_edit`, `cinematic_studio_2_5`, `cinematic_studio_image_3d`, `cinematic_studio_image_grid`
  - Cinema Studio Soul Cast / Location: `cinematic_studio_soul_cast`, `cinematic_studio_soul_location`
  - Cinema Studio cinematic base: `soul_cinema_studio`
- Body keys: `model`, `prompt`, `style`, `characterSheetId`, `locationId`, `genre`, `mood`
- Style catalog (hardcoded in bundle): `Abstract Cartoon`, `Adventure Tales`, `Big Bob`, `Bikini Bottom`, `Child Art`, `Fairy Tale`, `Family Boss`, `Flat Cartoon`, `Gravity Force`, `Ink Sketch`, `Jack Horse`, `Old Anime`, `Old Cartoon`, `Pop Cartoon`, `Voxel Art`, `West Park`, `Balloon`, `Bender`, `Bricks`, `Clay`, `Crayon`, `Gumstyle`, `Manga`, `Muppet`, `Simps`, `Regular`, `General`
- Modes: Image tab or Video tab (separate slugs per). **Cinema 3.5 (May 2026) renders THREE Image/Video tab pairs in the DOM**: header strip (y<50, browser nav), left-rail (x<260), and config bar (x~356). Either left-rail OR config-bar tab actually controls the active panel — the working strategy is to click each role=tab matching label that is NOT aria-selected, then verify by re-reading aria-selected on the same element. `selectCinemaMode` does this in `cinema.mjs`; cost-readout verification is unreliable in 3.5 because BOTH Generate buttons (image=2, video=96) render simultaneously regardless of active mode.
- Dual Generate buttons: cinema-studio renders TWO overlapping `<button>` elements with text "Generate" (image and video panel each have their own). Both visible simultaneously. Pick the one inside the active tabpanel (`[role="tabpanel"][data-state="active"]` or `[role="tabpanel"]:not([hidden]):not([aria-hidden="true"])`). `ui-submit.mjs` does this via structural filter first, cost-line2 filter second.
- Cinema 3.5 additions: `Genre:` selector (Action/Horror/Comedy/Noir/Drama/Epic/General), `Style:` selector (27 options), `Camera:` per-shot control, `AI Director` toggle, `Audio` sync toggle, `Type` selector, `Character` linking, `Unlimited` toggle, `Edit` mode. Up to 9 reference images.
- Skill flags: `--genre NAME` (best-effort tile click), `--style NAME` (best-effort tile click), `--mode image|video`, `--duration Ns`, `--ref PATH`.
- Duration options: commonly 5s or 8s video; image is single-frame
- Resolution: 1080p default for video
- Create-new vs operate-existing: `--project-id` navigates to project; `--new` creates a fresh project first.

## Cross-tool notes

- Every form submission goes through the Generate button; mouse must arrive via bezier path, dwell 120ms, then click.
- DataDome's `x-datadome-clientid` cookie is reset between tools; skill treats each tool session as a fresh behavioral context (browse phase before first click per tool).
- Free gens (`use_free_gens: true`) are charged zero against wallet but have a daily cap per `/user/free-gens/v2`. The `--free-gens` CLI flag is documented but not currently wired (TODO).
- Unlim (`use_unlim: true`) is charged zero against subscription credits for supported models on `has_unlim: true` plans. Skill auto-enables when user has unlim. `--no-unlim` flag is not implemented (TODO).
- **Slug path is case-sensitive but underscore/hyphen varies.** Some live URLs use hyphens (`/jobs/nano-banana-2`), others underscores (`/jobs/v2/seedance_2_0`, `/jobs/v2/cinematic_studio_image`). `waitForJobPostResponse` in `ui-submit.mjs` accepts either via `slug.replace(/[_-]/g, '[_-]')`.
- **localStorage side-channel.** Every tool page hydrates `inputImages` / `mediasV3` / `medias` / `assets` from `hf:*` localStorage keys. DOM-chip clearing is NOT enough; `clearPersistedAttachments(page)` must run post-JWT and pre-submit for every flow (see `ui-submit.mjs`).
- **Shared backend slugs.** Some frontend model variants share one backend slug (e.g. Seedance 2.0 and Seedance 2.0 Fast both POST to `/jobs/v2/seedance_2_0`, differentiated only by body param). When adding a catalog entry for a new variant, always probe the live POST URL with `HF_DEBUG=1` before writing a new `backend_slug`.

## Environment flags

- `HF_VISIBLE=1`: show the Chrome window. Default is off-screen (`--window-position=-2400,-2400`) so batches don't steal focus. `login.mjs` auto-sets this.
- `HF_DEBUG=1`: verbose logging in `ui-submit.mjs` (and video/cinema mode pickers): every non-match `/jobs/*` POST from fnf.higgsfield.ai is printed, the chosen Generate button is dumped, response bodies (first 400 chars) are logged. Essential for diagnosing slug mismatches and mode-switch failures. One-iteration diagnostic.
- `HF_STEALTH=0`: disable the patchright stealth init script (debug only; DataDome will flag).
- `HF_MAX_CONCURRENT=N`: ceiling for `batch` concurrency, default 4, max 8.

## Batch command

`node scripts/run.mjs batch --jobs <file.jsonl> [--concurrency N]` submits N jobs in one browser session, one at a time, letting Higgsfield queue them server-side.

Per-line JSONL shape:
```json
{"cmd": "image|video|marketing|cinema", "prompt": "STRING", ...}
```

- `image`: requires `model` (catalog key from image.mjs); optional `aspect` / `res` / `batch` / `ref` (list).
- `video`: requires `model` (catalog key from video.mjs `VIDEO_CATALOG`); optional `aspect` / `res` / `duration` / `ref`.
- `marketing`: optional `preset` (tile label, e.g. "UGC"). No `model` required; slug is always `marketing_studio_video`.
- `cinema`: optional `mode: image|video` (default video). Optional `cinemaModel` (frontend label for cinema model picker).

All jobs in a batch must share `cmd` (each cmd lives on a different tool page). Mixed batches are rejected. Reaper correlates assets to jobs by aspect-ratio first, FIFO second; mismatches surface as `_dim_warning` in metadata.json.

## Cinema-studio mode switch (reference implementation)

Cinema-studio's mode switch is the most fragile UI surface in the skill. Canonical flow:

1. `readCinemaGenerateCost(page)` reads the LARGEST-by-area Generate button's line-2 (cost). Image mode = 2, video mode = 96.
2. If current cost matches target, return true (fast path).
3. Query `[role="tab"]` elements with line-1 == target label AND `aria-selected !== "true"` AND `x >= 300` (excludes sidebar nav).
4. Click via Playwright (not `el.click()` in evaluate: React synthetic events).
5. Poll cost for up to 5s (panel transition unmounts/remounts the Generate button).
6. If still wrong, iterate other candidate tabs.
