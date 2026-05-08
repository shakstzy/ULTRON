# Voice clone setup (Adithya, one-time, before phase 2)

Phase 1 (`dial.sh`) doesn't need any of this. Phase 2 (real-time cloned-voice agent) does.

## What you do

1. **Sign up at elevenlabs.io** if you don't have an account. The Creator tier ($22/mo) is enough for early testing — gives you ~100K characters/mo, voice cloning, and Flash v2.5 access. Bump to Pro later if call volume grows.
2. **Clone your voice.** Two options:
   - **Instant Voice Clone** (cheapest, in-product): record or upload a 1-minute clean sample of you talking. Done in 30 seconds. Quality is good for cold calls.
   - **Professional Voice Clone**: 30+ minute studio-quality sample. Higher fidelity, takes ~24h to train. Worth it if phase 2 ships and quality matters.
3. **Grab the voice ID** from the ElevenLabs UI (Voices → your clone → copy the ID, looks like `21m00Tcm4TlvDq8ikWAM`).
4. **Save the API key + voice ID** to `~/ULTRON/_credentials/elevenlabs.env`:
   ```
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=21m00...
   ```
5. **Sign up at deepgram.com** ($200 free credit, no card required for the trial) and grab an API key. Save to `~/ULTRON/_credentials/deepgram.env`:
   ```
   DEEPGRAM_API_KEY=...
   ```

That's it. Ping me ("phase 2 ready") when those two env files exist and I'll wire the Pipecat agent.

## What the agent will need (so you know what you're authorizing in advance)

- **BlackHole 2ch** as the system input device for FaceTime (already installed, just needs to be selected when a call is active).
- **Multi-Output Device** so you still hear the call audio through your speakers/headphones while it's also routed to BlackHole for STT.
- **A short cold-call script** per campaign (system prompt). Stays in `~/ULTRON/_shell/skills/phone/scripts/<campaign>.md`.

## TCPA reminder

FCC ruled in Feb 2024 that AI voice clones on calls to US cell phones need prior express written consent under TCPA. Fine for: warm leads, your existing contacts, recruiting follow-ups, founder outreach where they opted-in. NOT fine for: pure cold-sales dialing of strangers without consent. Phase 2 will ship a `--consent-confirmed` flag that you must pass per call; the dialer refuses without it for any number not in your Apple Contacts.
