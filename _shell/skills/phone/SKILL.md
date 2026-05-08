---
name: phone
description: Use this skill EVERY time Adithya wants to place an actual phone call from his Mac through iPhone Continuity calling. Triggers on phrases like "call <name>", "dial <number>", "ring <name>", "phone <name>", "cold-call X". Lives at `~/ULTRON/_shell/skills/phone/`. AppleScript opens `tel:` URLs which FaceTime hands to the iPhone over Continuity, so the call goes out from Adithya's actual cell number. Phase 1 (current): dialer only with Apple Contacts resolution. Phase 2 (next): real-time cloned-voice conversational agent for cold-call automation, requires ElevenLabs voice clone + Deepgram key. Default is `--dry-run`; live calls require `--send` and explicit Adithya confirmation. For texts use the `imessage` / `whatsapp` / `telegram` skills.
---

# phone

ULTRON-native phone dialer. Lives at `~/ULTRON/_shell/skills/phone/`. Consumed via the global symlink `~/.claude/skills/phone/`.

## Why this exists

Adithya wants ULTRON to place outbound phone calls without him touching the iPhone. iPhone Continuity calling lets the Mac trigger calls that route over the iPhone's cell radio, so the call actually shows up on the recipient's phone as coming from Adithya's real cell number — important for cold-call answer rates.

Phase 1 (this commit) is the dialer alone: resolve a contact name or E.164 number, ask the iPhone to ring it. Phase 2 will wire a real-time conversational agent on top using BlackHole audio routing + Pipecat + ElevenLabs cloned voice + Deepgram STT + Claude. The dialer ships first so the path is provable end-to-end before adding the voice loop.

For SMS/iMessage use `imessage`. For WhatsApp use `whatsapp`. For Telegram DMs use `telegram`. This skill is the only path for actual phone calls.

## Pre-flight

The Mac must have FaceTime configured AND iPhone Continuity calling enabled. To enable on the iPhone: Settings → Cellular → Calls on Other Devices → toggle on "Allow Calls on Other Devices" and select the Mac. Then on the Mac: open FaceTime → Settings → enable "Calls from iPhone".

Verify with:
```bash
ls /System/Applications/FaceTime.app                   # FaceTime present
defaults read com.apple.FaceTime CallsFromiPhone 2>/dev/null  # 1 if enabled
```

If the user has not enabled Continuity calling, the `--send` action will open the FaceTime UI but the cellular dial will be silently skipped (FaceTime falls back to FaceTime Audio over IP, which is wrong). The dispatcher does not auto-enable this — surface the missing toggle and ask Adithya to flip it once.

## Recipient resolution

Same gating as `imessage`. NEVER ask Adithya for a phone number — resolve, then confirm draft+recipient before `--send`. Order:

1. **Direct E.164** (`+15125551234`) → use as-is.
2. **US-style 10 digits** (`5125551234`) → prefix `+1`.
3. **Apple Contacts name** (`"Mom"`, `"Sydney"`) → `osascript` query against `Contacts.app` for that exact name. Single phone match → use it. Multiple phones on one contact → prefer the first `mobile` / `iPhone` label, else fail loud and ask. Multiple contacts with the same name → fail loud and surface candidates with phones for Adithya to pick.
4. **Cross-check entity stub** at `_global/entities/people/<slug>.md` for canonical handle. If Apple Contacts and the stub disagree, trust Contacts and surface the mismatch so Adithya can fix the stub.

When NOT to ask Adithya:
- Single confident match with one phone → just dial in `--dry-run` mode and surface the resolved E.164 + name. He confirms the dry-run output → re-run with `--send`.
- Adithya already specified the recipient unambiguously.

## CLI

```bash
# Dry-run (default) — resolves recipient, prints what WOULD be dialed, never opens FaceTime.
~/ULTRON/_shell/skills/phone/dial.sh --to "Mom"
~/ULTRON/_shell/skills/phone/dial.sh --to "+15125551234"

# Live — actually opens FaceTime and triggers the cellular dial via iPhone Continuity.
~/ULTRON/_shell/skills/phone/dial.sh --to "Mom" --send
```

Output (stdout JSON):
```json
{"handoff":"ok","mode":"dry-run|send","recipient_input":"Mom","resolved_e164":"+15125551234","resolved_name":"Mom","action":"would-dial|dialing"}
```

Exit codes:
- `0` — dry-run printed, or call handed to FaceTime
- `2` — arg error (missing `--to`, conflicting flags)
- `3` — resolution error (no contact match, ambiguous match, FaceTime missing, Continuity disabled)

**Live-call gating.** A `--send` invocation IS an explicit-permission action and a SEND. Per the May 7 send-skill incident, the rule is: every smoke test of recipient resolution uses `--dry-run`, never a live dial. The dispatcher prints a 3-second-countdown warning before actually opening FaceTime, so Ctrl-C is possible if the resolution looks wrong.

## Phase 2: cloned-voice real-time agent (NOT YET BUILT)

When Adithya provides:
1. An ElevenLabs voice clone of himself (Instant or Professional, voice ID stored in `_credentials/elevenlabs.env`).
2. A Deepgram API key in `_credentials/deepgram.env` (or `--stt whisper-local` flag for on-device STT with worse latency).

…build `agent.py` with:
- **Pipecat** (`pip install pipecat-ai`) as the orchestration framework. Open-source, MIT, has built-in adapters for Deepgram + ElevenLabs + Anthropic.
- **LocalAudioTransport** with input device = call audio capture (Multi-Output Device routing FaceTime audio to BlackHole 2ch), output device = BlackHole 2ch (FaceTime mic input).
- **Pipeline**: BlackHole → Deepgram Nova-3 streaming STT → Claude Sonnet 4.6 (with cold-call script as system prompt + dynamic objection handling) → ElevenLabs Flash v2.5 TTS with Adithya's cloned voice → BlackHole back into FaceTime.
- **Setup utility** `setup-audio.sh` to verify BlackHole 2ch is the system input + Multi-Output Device exists with FaceTime → BlackHole + speakers, otherwise abort the call.
- **Hangup AppleScript** triggered by Claude when objective met or hangup keyword detected.
- **Call recording** to `~/ULTRON/_shell/skills/phone/recordings/<timestamp>__<recipient>.wav` for QA.

Realistic latency: 600-1000ms voice-to-voice in steady state. Pipecat docs claim <500ms with optimized turn detection. Adithya's "200ms" target is achievable for time-to-first-audio-byte from the TTS, not full round trip.

**TCPA guardrail.** AI voice clones on calls to US cell phones need prior express written consent under FCC's Feb 2024 ruling. Phase 2 ships with a hardcoded denylist for cold-sales numbers without consent flag. Warm leads, recruiting, follow-ups, his own contacts: fine.

See `VOICE-CLONE-SETUP.md` in this dir for the one-time human steps Adithya does before phase 2 wiring.

## Self-review checklist

After any change to `dial.sh` or AppleScript helpers:
- `--dry-run` is still the default mode (zero `open` or `osascript` activate calls fire when `--send` absent).
- Recipient resolution returns the SAME E.164 across `--dry-run` and `--send` for the same input.
- Smoke tests of resolution use `--dry-run` only — never a real dial to a real number. Even Adithya's own iPhone counts as live; dry-run first, confirm with him, then send.
- Exit codes are 0 / 2 / 3 only — no silent fallthroughs.
- JSON-on-stdout shape unchanged so any downstream consumer keeps parsing.
