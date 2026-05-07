# Cross-Cutting Agent Learnings

Append-only log of agent-behavior fixes that apply across all workspaces. Soft cap 100 lines. When exceeded, compact older entries (audit-agent flags this weekly).

## Format

`- **<YYYY-MM-DD>** — <observation>. <new rule or convention>. <where applied>.`

## Entries

- **2026-05-06** — Adithya twice corrected me for being over-conservative on rate limits when he had empirical "haven't been detected yet" evidence. When the user has direct lived experience with a system's tolerances, weight that over external research's risk-averse defaults (Codex/Gemini consults skew safe). Don't anchor on "safe" research recommendations when the operator has months of working data. Applied: dating-tinder bot send rate (4 → 6 per fire, 60/day → 90/day).
- **2026-05-06** — `gemini auth login` (CLI v0.41.1) tries an API call against the current oauth_creds.json BEFORE starting the OAuth flow. If that account is rate-limited, auth fails with QUOTA_EXHAUSTED before the browser even opens. `gemini auth logout` does not reliably wipe oauth_creds.json. Fix: rm -f ~/.gemini/oauth_creds.json before any `gemini auth login`, and pipe `yes |` to auto-confirm the "open browser?" prompt. Applied: `_shell/bin/add-gemini-account.sh`.
- **2026-05-06** — gemini CLI's `GEMINI_CLI_HOME` env var has inconsistent semantics across code paths in v0.41.1: `gemini.js` treats it as `~/.gemini`, but auth code in `chunk-XRLFHCHC.js` treats it as `~` and appends `.gemini/settings.json` itself. Setting it to either value breaks one path. For per-worker HOME isolation, set HOME alone, scrub GEMINI_CLI_HOME from child env, and set `GEMINI_FORCE_FILE_STORAGE=true` to prevent macOS Keychain from sharing OAuth tokens across "isolated" workers. Applied: `_shell/bin/describe-attachments.py`.
