---
name: distrokid
description: Use this skill EVERY time Adithya wants to ship one of his Logic-Pro-bounced tracks to DistroKid (which fans out to Spotify, Apple Music, YouTube Music, TikTok, all 23 default stores plus Snapchat and Roblox). Trigger on phrases like "ship <track> to distrokid", "upload <track> to distrokid", "drop <track>", "release <track>", "put <track> on spotify / apple", "publish <track>", "distrokid <track>". Also fires on "remove <track> from stores", "takedown <track>", "delete <track> from distrokid". Patchright-driven full form-fill against distrokid.com/new/ — single command goes from `.wav` + cover JPG to `/new/done/`. Always use this skill — never ask Adithya to fill the DistroKid form himself.
---

# distrokid

Patchright-driven DistroKid uploads. The actual scripts live in QUANTUM at `~/QUANTUM/workspaces/distrokid/`. This skill is the trigger surface and operating doctrine.

## When this fires

Trigger phrases (semantic, non-exhaustive): "ship <track>", "upload <track> to distrokid", "drop <track>", "release <track>", "put <track> on Spotify / Apple Music / streaming", "publish <track>", "distrokid <track>", or any phrasing where Adithya wants a finished mix on streaming services. Takedown/removal phrases also fire here: "remove <track> from stores", "takedown <track>", "delete <track> from distrokid".

Do NOT fire for:
- DistroLock (timestamping ownership) — separate flow, not implemented.
- Bandcamp / SoundCloud / direct uploads to other platforms — different services.
- "Mix this track" / "master this track" — those are Logic / Mixea operations, not distribution.

## Auth

One-time visible login captures cookies into a persistent Chrome profile at `~/.quantum/chrome-profiles/distrokid/`. After that, every run reuses the session silently — Adithya doesn't re-enter creds.

To re-login (cookies expired, account swap, etc):
```bash
cd ~/QUANTUM/workspaces/distrokid && node scripts/login.mjs
```
Visible Chrome opens at distrokid.com/signin. Sign in normally. Close the window when done.

## Implementation home

All Node scripts live at `~/QUANTUM/workspaces/distrokid/scripts/`:

| Script | Purpose |
|---|---|
| `login.mjs` | One-time manual login. |
| `upload.mjs` | Full form-fill + submit + Mixea upsell + done page. The main verb. |
| `recon.mjs` | Dumps the /new/ form's selectors to JSON (for selector drift debugging). |
| `resume.mjs` | Picks up an in-progress draft from any URL stage (Mixea / done). Fallback if `upload.mjs` is killed mid-run. |
| `takedown-locate.mjs` | Step 1 of takedown — finds the release row on /mymusic. |

Persistent profile: `~/.quantum/chrome-profiles/distrokid/`.
Per-run artifacts: `~/.quantum/distrokid/runs/<timestamp>/` (screenshots, metadata.json).

## Procedure (ship a track)

**Do NOT re-prompt for any parameter in "Locked defaults" below.** When Adithya says "ship <track>" / "upload <track>", that phrase is full pre-authorization for the entire skill — including release date (today), artist (Shak STZY), label (Outerscope), genre (Hip Hop/Rap → Pop), explicit (yes), all 23 stores + Snapchat + Roblox, and auto-generated cover art via gpt-images. **Generate the cover, default the date to today, run the upload.** Only re-prompt when Adithya explicitly overrides a default in the trigger message ("drop superdrugs as Pharma" → title override; "drop dime clean" → explicit=false). Asking "what artist?" / "do you have cover art?" / "what release date?" is wrong — those are answered.

When Adithya says "ship <track>" / "upload <track>", do this:

1. **Resolve the WAV path.** Logic projects bounce to one of two patterns:
   - `~/Music/Logic/<project>/Bounces/<song>.wav` (per-project — most common)
   - `~/Music/Logic/Bounces/<song>.wav` or `~/Music/Logic/Bounces/<sub>/<song>.wav` (root — used for some songs)
   Use `find ~/Music/Logic -iname "*<track>*" -type f` to locate. If multiple matches (e.g. `finesse.wav` and `finesse-repo/finesse.wav`), default to the **most recent** by mtime. Tell Adithya which one you picked.
2. **Derive the title.** Strip extension from the bounce filename, title-case. `ex.wav` → "Ex". `cold shak.wav` → "Cold Shak". `superdrugs.wav` → "Superdrugs". Adithya's newer naming is camelCase (`romanticHomicide.wav` → "Romantic Homicide"). Override with explicit `--title` if Adithya named one.
3. **Generate the cover** via the gpt-images skill (drives chatgpt.com via patchright):
   ```bash
   cd ~/QUANTUM/_core/skills/gpt-images && node scripts/run.mjs generate "<prompt>"
   ```
   Cover prompt template (mandatory rules — Adithya's brand):
   - **No people, no faces, no human figures whatsoever.**
   - Large stylized **"SHAKSTZY"** text prominently displayed.
   - Title-aware imagery: derive concept from the track name (Ex → broken/crumbled, Finesse → gold/cars/cash, Superdrugs → vials/pills/neon, etc.). When unsure, default to dark cinematic moody hip-hop aesthetic.
   - Square 1:1, professional album art quality, no website URLs, no streaming-service logos.
   Output: `~/.quantum/skill-output/gpt-images/<run-id>/image-1.png` (1024×1024 PNG).
4. **Convert PNG → 3000×3000 JPG** via ffmpeg:
   ```bash
   ffmpeg -y -i <png> -vf "scale=3000:3000:flags=lanczos" -q:v 2 ~/.quantum/distrokid/cover-<slug>.jpg
   ```
5. **Run the upload** (single command, end-to-end including Mixea):
   ```bash
   cd ~/QUANTUM/workspaces/distrokid && node scripts/upload.mjs \
     --wav "<wav-path>" \
     --title "<title>" \
     --cover "$HOME/.quantum/distrokid/cover-<slug>.jpg"
   ```
   Default is `--submit true` (full auto). Pass `--submit false` for a dry-run that fills the form and stops at the Continue button so Adithya can eyeball.
6. **Verify success.** Look for `[url] https://distrokid.com/new/done/?albumuuid=<uuid>` in the output. If URL is still on `/new/` after submit → check `runs/<ts>/post-submit.png` for validation errors.
7. **Update the song stub.** Add a frontmatter block to `~/ULTRON/workspaces/personal/wiki/entities/songs/<slug>.md` with `status: released`, `albumuuid: <uuid>`, `released: <ISO date>`. Create the file if it doesn't exist.

## Locked defaults (Adithya's preferences)

- Stores: all 23 default-checked + Snapchat (own 100% publishing) + Roblox (all 4 eligibility checks).
- Single, Shak STZY, today's date, Outerscope Records, English, Hip Hop/Rap → Pop.
- Songwriter: Adithya Shakthi Kumar, "I wrote this song", music + lyrics.
- Apple credits: Performer = Shak STZY (Singing & vocals), Producer = Shak STZY (Producer).
- Explicit: Yes (hardcoded — clean releases not yet supported in upload.mjs).
- Facebook profile: leave default "No" — selecting "Yes group" requires a real FB artist URL and DistroKid rejects without one.
- All 7 mandatory checkboxes: yes (auto).
- Paid extras (Social Media Pack, Leave a Legacy, Discovery Pack, Store Maximizer, DistroVid, Loudness Normalization): **all skip** unless Adithya specifies.
- Mixea upsell: pick "Use my originals" ($0).

## Footguns / known issues

- **`.areyousure` checkboxes are CSS-hidden.** Must flip via `page.evaluate(() => { el.checked = true; el.dispatchEvent('change'); })`. Direct Playwright `.click()` fails with "Element is not visible".
- **Apple Music credits requires both a name input AND a role select dropdown.** Performer role = "Singing & vocals", Producer role = "Producer". Both gated red until set.
- **Facebook "Yes group" needs a real URL** — leave at default "No".
- **Submit click stays on `/new/` for ~5s** before navigating to `/new/mixea/`. Don't bail too early on `waitForURL`.
- **Mixea page uses styled radio cards.** Click via `page.getByText(/use my originals/i).click()`, not raw radio targeting.
- **Profile is single-instance locked.** Kill any open patchright Chrome with `pkill -9 -f "user-data-dir=$HOME/.quantum/chrome-profiles/distrokid"` before re-launching.

## Takedown procedure (HITL — instructive flow)

Removing a release is high-stakes (royalty implications, can break followers' libraries). Always step-by-step with confirmation:

1. `node scripts/takedown-locate.mjs <track-slug>` — finds the album row + albumuuid on /mymusic. Reports URL, screenshots, closes.
2. **Adithya confirms** the located albumuuid is correct.
3. Open the album detail page, identify the takedown / "Remove from stores" control. Screenshot, **don't click yet**.
4. **Adithya confirms** before clicking takedown.
5. Click takedown, capture confirmation modal. **Adithya confirms** the modal copy matches expected.
6. Click final confirm. Snap result.

Never auto-click takedown. Always HITL each gate.

## Examples

```bash
# Adithya says: "ship cold shak"
# 1. Resolve: ~/Music/Logic/weirdo/Bounces/cold shak.wav
# 2. Title: "Cold Shak"
# 3. Cover prompt: hip-hop, no people, SHAKSTZY text, dark moody cold-themed (ice, glass, blue tones)
# 4. ffmpeg → 3000x3000 JPG
# 5. node scripts/upload.mjs --wav "..." --title "Cold Shak" --cover "..."

# Adithya says: "drop superdrugs as Pharma"
# 1. Resolve: ~/Music/Logic/builtin3/Bounces/superdrugs.wav
# 2. Title OVERRIDE: "Pharma" (per Adithya's instruction)
# 3. Cover prompt: title-aware on "Pharma" not "Superdrugs"
# 4-5. Same flow.

# Adithya says: "remove dime from stores"
# Takedown HITL flow. Step 1, ask confirmation, step 2, etc.
```

## Verbs not yet implemented

- Edit metadata of a live release (cover swap, title change). DistroKid restricts most edits post-submission anyway.
- Bulk batch upload (queue 5 tracks, ship all). Doable but not requested yet.
- Royalty / stream stats scrape. Future verb.
- Hyperfollow link generation. Future verb.

If Adithya asks for one of these, build it as a new script under `~/QUANTUM/workspaces/distrokid/scripts/` and add a row above.
