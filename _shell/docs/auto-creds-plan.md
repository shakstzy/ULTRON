# Auto-creds plan — ULTRON credential health system

> Draft 1, 2026-05-07. Pre-build. Not yet approved by Adithya.
> Do not start implementation until reviewed by Codex + Gemini and approved by Adithya.

## Problem

Credentials in `~/ULTRON/_credentials/` rot on different cadences:

| Class | Examples | Failure mode | Cadence |
|---|---|---|---|
| Google OAuth refresh tokens (Testing-status app) | 4 `gmail-*.json` | Refresh token revoked by Google → all gmail ingest 401s | Every 7 days, hard cliff |
| Persistent Chrome session profiles | `browser-profiles/{chatgpt,discord,higgsfield,linkedin,x}` | Cookie/session invalidation → patchright skill logs out | 30–90+ days, soft drift |
| WhatsApp bridge pairing | bridge daemon | Pair re-required | ~20 days |
| Telethon session | `telegram.session` | Session invalidated | Rare (months) |
| Gemini OAuth pool | `~/.gemini/accounts/*.json` | Daily quota hits, account cycle | Daily / per-call |

The Google one is the active pain point — it expires on a cliff and breaks every gmail-driven workspace stage every 7 days.

## Goals

1. Eliminate the weekly Google manual re-auth by automating the OAuth re-consent flow.
2. Stand up a generic registry/handler/scheduler framework that other credential classes plug into later (one new handler per class, no framework rewrites).
3. Halt loud and durably (iMessage to Adithya) on any failure that requires human action — never silently leave an expired token in place.
4. Be observable: `cred-mgr status` shows everything in one table.

## Non-goals (v1)

- MCP-server-managed credentials (Claude Code owns those).
- Telegram, WhatsApp, Slack, Gemini — out of scope until they actually rot.
- Credential discovery / auto-registration. Registry is hand-edited.
- Browser-session refresh for chatgpt/discord/etc. — v2, after we observe drift patterns.
- Multi-machine coordination. Adithya runs one Mac.

## v1 scope

- Google OAuth re-consent automation for the 4 mailbox creds in `_credentials/gmail-*.json`.
- Daily cron at 04:00 (low interactive use).
- Halt-loud iMessage on any deviation (2FA prompt, captcha, login required, getProfile fail).

## Critical premise to verify before build

**Google "Testing" OAuth apps revoke refresh tokens 7 days after issuance, regardless of use.** This is the basis for the whole design. Verify before building:

- If true → re-consent flow is the only fix (planned design).
- If false (e.g. refresh tokens are renewable by exchange) → drop most of this; just exchange for a new refresh_token weekly via stdlib `urllib`.
- Alternative path that sidesteps the whole thing: change the OAuth consent screen "User Type" to **Internal** for org-owned accounts (`adithya@eclipse.builders` and `outerscope`/`synps` if they're Workspace orgs). Internal apps don't expire refresh tokens. This is a one-time GCP console change, no code, and shrinks v1 from 4 mailboxes to 1 (the `@gmail.com` personal account, which can't be Internal).

Verification step before build: read Google's current OAuth identity-platform docs, confirm Testing-app token expiry behavior, and check the consent-screen "User Type" of the gogcli OAuth client. If switching to Internal works for 3 of 4 mailboxes, propose to Adithya we do that first and only auto-refresh the 4th.

## Architecture

```
_shell/bin/cred-mgr.py          # single-entry CLI
_shell/lib/creds/
  registry.py                   # loads + validates credentials.yaml
  state.py                      # reads/writes creds-state.json (atomic)
  lock.py                       # flock per cred-file
  halt.py                       # iMessage halt-loud helper
  handlers/
    oauth_google.py             # v1
    browser_cookie.py           # v2
_shell/config/credentials.yaml  # registry
_credentials/creds-state.json   # mutable state (gitignored)
_credentials/browser-profiles/google-<slug>/   # per-mailbox Chrome profile (gitignored)
```

CLI subcommands:

- `cred-mgr status` — table of all creds + health + days_until_expiry + last_refresh
- `cred-mgr check <name>` — single health check, no refresh
- `cred-mgr refresh <name> [--force]` — force refresh
- `cred-mgr health-check-all` — check all, refresh anything in EXPIRES_SOON window (cron entrypoint)
- `cred-mgr login <name>` — one-time interactive bootstrap (visible Chrome, manual Google login)

Health states: `OK` / `EXPIRES_SOON` / `EXPIRED` / `BROKEN` / `UNKNOWN`.

## Registry schema (`_shell/config/credentials.yaml`)

```yaml
credentials:
  gmail-adithya-eclipse:
    type: google-oauth
    file: ~/ULTRON/_credentials/gmail-adithya-eclipse.json
    email: adithya@eclipse.builders
    handler: oauth-google
    lifetime_days: 7
    refresh_at_days_left: 2     # refresh when ≤2 days remain
    profile_dir: ~/ULTRON/_credentials/browser-profiles/google-adithya-eclipse
    health_check:
      kind: gmail-getprofile     # call users.getProfile() with the access_token
  gmail-adithya-shak-kumar-gmail:
    type: google-oauth
    # ... same shape
```

## Handler: `oauth-google` (the v1 critical path)

Purpose: take an existing `gmail-<slug>.json` whose refresh_token is about to expire, run the OAuth consent flow inside a logged-in Chrome profile via patchright, capture the new refresh_token from the localhost callback, write it atomically.

Steps:

1. **Acquire flock** on `<file>.lock` (60s timeout). On timeout → halt loud (concurrent run conflict).
2. **Pre-flight health check** with current token (call `users.getProfile`). If still OK and `days_left > refresh_at_days_left`, exit early (idempotent).
3. **Bind localhost server** on a random free port. Generate state token (CSRF). Build auth URL with `client_id` (from `gogcli-oauth-client.json`), `redirect_uri=http://localhost:<port>`, `scope=https://mail.google.com/`, `prompt=consent`, `access_type=offline`, `login_hint=<email>`, `state=<csrf>`.
4. **Launch patchright** with persistent profile dir for THIS email (not the freeform browser-profiles/x or /linkedin — a dedicated `google-<slug>` profile). Honor focus-restore-via-osascript pattern (do not steal focus from active work). Headless=False (Google bot-detects headless).
5. **Navigate to auth URL.** Wait for one of these terminal states (with bounded timeouts and concrete selectors):
   - Account chooser → click matching account by email text. (login_hint usually skips it.)
   - Password prompt → halt loud `LOGGED_OUT`.
   - 2FA prompt → halt loud `TWO_FACTOR_REQUIRED`.
   - Captcha (`recaptcha` iframe) → halt loud `CAPTCHA`.
   - "App not verified" warning → click "Advanced" → "Go to <app> (unsafe)" (this is gog's own client, expected for Testing apps).
   - Consent screen → click "Continue" / "Allow". Verify scopes shown match expected (gmail.com).
   - Navigated to `http://localhost:<port>/?code=...` → capture from server callback.
6. **Exchange code → tokens** via POST to `oauth2.googleapis.com/token`. Receive `refresh_token`, `access_token`, `expires_in`.
7. **Validate** by calling `users.getProfile` with the new access_token + matching the email field.
8. **Atomic write**: write new contents (refresh_token + minted_at + scopes) to `<file>.tmp`, fsync, rename over `<file>`. Mode 0600. Same shape as INVENTORY.md spec.
9. **Update state**: `creds-state.json` with `last_refresh_at`, `last_health_check_at`, clear `last_error`.
10. **Update legacy mirror** if `_credentials/google-accounts/<email-stem>.json` exists, also update its refresh_token (per INVENTORY rotation note).
11. **Release flock**, close browser.

Failure handling: any step's exception → halt loud with classified reason → NO write to creds file (atomic guarantee preserved, old token still works for whatever days_left remains).

## State file (`_credentials/creds-state.json`)

```json
{
  "version": 1,
  "creds": {
    "gmail-adithya-eclipse": {
      "last_refresh_at": "2026-05-07T04:00:13Z",
      "last_health_check_at": "2026-05-07T04:00:01Z",
      "last_health": "OK",
      "last_error": null,
      "consecutive_failures": 0
    }
  }
}
```

Mode 0600. Atomic writes via tmp+rename. Gitignored.

## Locking

Each cred has `<file>.lock` (flock). Refresh waits 60s. Halt loud on timeout (assume operator is mid-interactive use). Health checks use the same lock to avoid racing a refresh.

## Halt-loud format

iMessage to Adithya via the existing imessage skill:

```
🔴 [creds] gmail-adithya-eclipse refresh failed
reason: TWO_FACTOR_REQUIRED
last good: 2026-04-30T04:00 (7 days ago)
fix: cd ~/ULTRON && _shell/bin/cred-mgr.py login gmail-adithya-eclipse
```

Reasons enum: `LOGGED_OUT` / `TWO_FACTOR_REQUIRED` / `CAPTCHA` / `LOCK_TIMEOUT` / `GETPROFILE_FAILED` / `EXCHANGE_FAILED` / `WRITE_FAILED` / `UNKNOWN`.

Rate-limit: don't iMessage twice for the same cred within 24h (track via state.consecutive_failures + last_error_at).

## Schedule

Add to `_shell/config/global-schedule.yaml`:

```yaml
cross_workspace:
  creds_health_check:
    cron: "0 4 * * *"           # Nightly 04:00
```

`cred-mgr health-check-all` is the cron entrypoint. It iterates every cred, computes days_until_expiry, refreshes those with `days_left ≤ refresh_at_days_left`. For 7-day Google tokens with `refresh_at_days_left=2`, this means refresh between day 5 and day 7 — averaging once every ~5 days, gives 2 buffer days for retry.

## Risks + mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 7-day refresh-token claim is wrong | Med | Plan rebuild | Verify in docs before build. If wrong, plan collapses to a stdlib refresh_token exchange. |
| Google flags account → 2FA / captcha on auto-flow | Med | Halt loud, manual fix | Persistent profile + same residential IP + 04:00 timing minimizes signals. Halt-loud catches it. Eclipse.builders Workspace org may have stricter triggers. |
| Concurrent profile use (Adithya browses Gmail at 04:00) | Low | Refresh fails | flock + 04:00 schedule. Profile is dedicated `google-<slug>`, not Adithya's daily Chrome. |
| Atomic-write race vs ingest job | Low | Stale token loaded mid-rotation | Ingest jobs read on startup, finish in seconds. tmp+rename is atomic on APFS. flock prevents concurrent refreshers. |
| Patchright selectors break (Google UI changes) | Med | All 4 refreshes fail same night | Multi-strategy selectors (text + role + aria), screenshot dump on failure to `_shell/runs/cred-mgr/<ts>/`, halt-loud has the screenshot path so Adithya can debug. |
| iMessage halt-loud silently fails | Low | Adithya doesn't know creds expired | imessage skill is well-tested. Belt-and-suspenders: also write a `BROKEN.md` flag to `_credentials/` that lint can flag, and the next interactive Claude session reads. |
| Old `outerscope.json` / `synps.json` legacy mirror diverges | Low | gog-direct calls fail | Update both files in lockstep within the atomic-rename window. INVENTORY.md flags this requirement. |
| OAuth client itself is rate-limited by Google | Low | Refresh blocks | 4 refreshes/week per client_id is well below any quota. |
| Scopes drift between old token and new | Low | Some Gmail API calls fail | Validate scopes returned in the consent response match expected; halt loud on mismatch. |
| `--force` / `login` accidentally invoked from cron | Low | Visible Chrome opens at 04:00 | `login` requires `--interactive` flag and refuses if STDIN is not a TTY. |
| Internal-app alternative invalidates this whole build | Med | Most of code becomes dead weight | Resolve before build: confirm User-Type policy for org accounts. Build only what's needed. |

## Testing strategy

1. **Unit tests** (`_shell/tests/test_cred_mgr.py`): registry parsing, state read/write atomicity, halt-loud formatting, flock semantics.
2. **OAuth handler unit test**: mock localhost server + mock Google token endpoint, verify code-exchange + atomic-write + getProfile-validation paths.
3. **Live dry-run**: pick the lowest-stakes mailbox (`adithya@synps.xyz` — 165 messages total). Run `cred-mgr refresh --dry-run gmail-adithya-synps`. Should walk through patchright, hit consent, NOT write the file, just log what it would do.
4. **Live real-run**: actual refresh on synps. Verify new token works via getProfile. Watch for 2 cycles (10 days) before scaling.
5. **Halt-loud test**: induce a fake `CAPTCHA` reason, confirm iMessage arrives. Confirm 24h dedup.
6. **Concurrency test**: run `refresh` and `check` simultaneously, verify flock serializes them.

## Rollout

| Phase | Scope | Exit criterion |
|---|---|---|
| 0 — Verify premises | Confirm 7-day expiry behavior + Internal-app option | One paragraph in this doc updated with verdict |
| 1 — Skeleton | CLI + registry + state + lock + halt — no live refreshes | `cred-mgr status` works on registry of 4 mailboxes, all OK |
| 2 — oauth-google handler | Implement, unit-tested | Synps refresh succeeds end-to-end manually |
| 3 — Cron synps only | Cron at 04:00 with synps-only registry | 2 successful nightly cycles, no halts |
| 4 — All 4 mailboxes | Full registry | 1 week clean, gmail ingest never breaks |
| 5+ — v2 handlers | browser-cookie, etc. | Per-handler |

## Open questions for Codex / Gemini review

1. Is the 7-day-refresh-token claim accurate for current (May 2026) Google OAuth Testing-status apps?
2. Is the OAuth re-consent flow the right approach, or is there a cheaper exchange-only refresh I'm missing?
3. Will Google's bot-detection flag patchright running headed-but-cron'd at 04:00? Is there a mitigation beyond "use the same profile and same IP"?
4. Is per-mailbox dedicated Chrome profile correct, or should all 4 share one profile and use account chooser? Tradeoff: shared profile is simpler but a single profile corruption nukes all 4.
5. Atomic-write strategy — tmp+rename on APFS is generally atomic, any reason to use a different approach (e.g. `O_TMPFILE` + linkat, fsync of containing dir)?
6. Halt-loud rate limit: 24h per cred? Or per-reason? Or per-(cred, reason)?
7. Should `cred-mgr login` use a one-shot disposable browser context, or the persistent profile, for first-time bootstrap?
8. Anything obvious I missed.

## Open questions for Adithya (post-review)

1. Are the org accounts (`outerscope.xyz`, `synps.xyz`, `eclipse.builders`) GCP Workspace orgs where we could change User Type to Internal? If yes, Internal sidesteps this entirely for 3 of 4 — different/smaller build.
2. v1 scope: only Google OAuth, agreed? Or fold in any of the patchright session profiles now (chatgpt etc.)?
3. Are you OK with refreshes running at 04:00? You're rarely up but if you ever are, the dedicated profile means it won't conflict with your active Chrome.
4. iMessage halt-loud only, or also a BROKEN.md flag the lint stage picks up next morning?
