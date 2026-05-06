---
name: instagram-summary
description: Fetch an Instagram post or reel and summarize it. Posts return caption + metadata + visual analysis. Reels also return an audio transcript. Trigger when Adithya pastes an instagram.com URL with /p/, /reel/, /reels/, /tv/, or /share/ and asks to summarize, explain, recap, tl;dr, or extract takeaways.
allowed-tools: Bash
---

# instagram-summary

Visual+text synthesis is delegated to the global `cloud-llm` skill at `~/ULTRON/_shell/skills/cloud-llm/` (gemini cycled across accounts → claude sonnet fallback). Carousels analyze up to 10 items. Entrypoint is `fetch.py`; venv at `~/.ultron/instagram-summary/.venv/`.

## When this fires

Trigger phrases (semantic, non-exhaustive): "summarize this insta", "tldr this reel", "what's in this post", "explain this reel", "what's this carousel about", "extract takeaways from this post", or any prompt where Adithya pastes one of these URL shapes:

- `instagram.com/p/...` (single post or carousel)
- `instagram.com/reel/...` or `/reels/...`
- `instagram.com/tv/...`
- `instagram.com/share/p/...` or `/share/reel/...`

Do NOT fire for:
- Profile pages (no shortcode). Tell Adithya we need a specific post URL.
- Stories. Different surface, not supported here.
- DM links or live stream links.
- Re-uploads on other platforms (TikTok, YouTube Shorts). Use the matching skill.

## Prereqs

Whisper model cached for reel audio (~470MB, one-time):

```
~/.ultron/instagram-summary/.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small.en')"
```

Posts work as soon as cloud-llm has at least one healthy engine. Reels also need Whisper.

## Procedure

```
~/.ultron/instagram-summary/.venv/bin/python ~/ULTRON/_shell/skills/instagram-summary/fetch.py <URL>
```

Output blocks:

- **Post**: `TYPE`, `AUTHOR`, `DATE`, `LIKES`, `COMMENTS`, optional `CAROUSEL: M items`, `CAPTION`, `VISUAL+SYNTHESIS SUMMARY`.
- **Reel**: same fields plus `AUDIO TRANSCRIPT` before the synthesis block.

Lead the reply with `VISUAL+SYNTHESIS SUMMARY`. Quote the transcript or caption only when Adithya asks for more detail. If a reel has `(no speech detected)` and the visual is thin, say it's a music or aesthetic clip rather than padding.

stderr carries `[pipeline: Xs]` timing and instaloader retry chatter — both ignorable.

## Errors

- `cloud-llm dispatch failed`: every gemini account 429'd AND claude -p also failed. See `~/ULTRON/_shell/skills/cloud-llm/SKILL.md`. Wait for caps to reset.
- `LoginRequired`: Instagram demanding auth. Run once with a burner:

  ```
  ~/.ultron/instagram-summary/.venv/bin/instaloader --login=<username>
  ```

- `yt-dlp failed`: Instagram changed its download surface. `brew upgrade yt-dlp`.
- Shortcode parse failure: confirm URL has `/p/`, `/reel/`, `/reels/`, `/tv/`, or `/share/(p|reel)/`.

## ULTRON notes

- If Adithya asks to save the summary, drop it under the appropriate workspace's `raw/library/YYYY-MM-DD-<author>-<shortcode>.md`. Slug pattern: `ig-<author>-<shortcode>`.
