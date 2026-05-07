# Auto-creds plan — ULTRON credential health system

> Draft 2, 2026-05-07. Pre-build. Reviewed by Codex + Gemini. Not yet approved by Adithya.
> Major restructure after both reviewers flagged the original plan as architecturally backwards.

## Headline finding from review

**The original plan defaulted to patchright UI automation. Both reviewers independently said: that's last-resort, not first-resort.** The 7-day refresh-token expiry is specific to OAuth apps with **External user type + Testing publishing status**. Two zero-code GCP console changes likely eliminate the entire problem:

- **Internal** user type → for OAuth clients owned by a Google Workspace org. Only that org's users can use it. No 7-day expiry.
- **In Production** publishing status → no 7-day Testing cliff. With Gmail's restricted scopes, an unverified-app warning may still show on first consent (one-time click), but tokens persist.

If both apply across the 4 mailboxes, this build collapses to **no code at all** — just two console changes plus a re-consent for each account once.

## Updated plan shape

| Phase | What | Cost | Eliminates the 7-day cliff for |
|---|---|---|---|
| 0 — Audit + flip | Inspect the gogcli OAuth client in GCP, switch user type / publishing status as appropriate, re-consent affected accounts once | Zero code, one GCP session | All accounts where Internal or In-Production applies (likely all 4) |
| 1 — Manual `cred-mgr login` | Minimal CLI: generate auth URL + localhost callback + atomic write. User clicks consent themselves in their normal browser. | ~150 lines Python, no patchright | Any mailbox that still needs periodic re-consent — turns "remember 7 gog flags" into one command |
| 2 — Patchright automation | Original plan, scoped to ONLY the irreducible case | ~400 lines + ongoing selector maintenance | Only the mailbox that can't be fixed by Phase 0 and where weekly manual is unacceptable |

Phase 2 may never be needed. Build it only if Phase 0 leaves at least one account stuck AND Phase 1 manual is too painful.

## Phase 0 — GCP audit (do first)

1. Open GCP Console for the project that owns `gogcli-oauth-client.json`. (`client_id` in the JSON identifies the project.)
2. Inspect:
   - **OAuth consent screen** → User Type (External / Internal), Publishing status (Testing / In Production).
   - **OAuth client** → Type (Desktop / Web). Loopback `http://localhost` only works cleanly for Desktop clients.
   - **Scopes** — confirm `https://mail.google.com/` is the granted scope. Restricted scope means In-Production stays unverified without verification submission.
3. Decide per mailbox:
   - `adithya@eclipse.builders`, `@outerscope.xyz`, `@synps.xyz` — if any of these is a Workspace org and owns the GCP project, set User Type to **Internal**. Tokens stop expiring.
   - `adithya.shak.kumar@gmail.com` — personal Gmail, can't be Internal. Move project to **In Production**. Tokens stop expiring on the 7-day timer; first consent shows unverified-app warning (click "Advanced > Go to app").
4. Re-consent each affected account once via the existing `gog auth login -a <email>` flow. Verify the new token's expiry behavior: wait 8 days, call `users.getProfile`, confirm still 200.
5. **Exit criterion:** all 4 mailboxes survive a >7-day idle period. If any do, those don't need automation.

Open question for Adithya before this phase: which of `outerscope`, `synps`, `eclipse.builders` are GCP Workspace orgs that own the OAuth project? If unclear, the GCP console will show under "OAuth consent screen → Application home" and IAM ownership.

## Phase 1 — Minimal `cred-mgr login` (build only if needed)

Purpose: turn the manual re-consent into a single command without UI automation.

```
cred-mgr login <name>      # generates URL, opens user's default browser, captures callback, writes atomically
cred-mgr status            # table of all creds + last health check + days since last consent
cred-mgr check <name>      # call users.getProfile, no refresh
```

Stack: Python stdlib only — `http.server` for callback, `urllib.request` for token exchange, `webbrowser.open()` for the consent URL. No patchright. No selectors. No flock-coordination of headed browsers.

Output of `login`:
- Spawns localhost on a fixed port (registered in GCP as the redirect URI for a Desktop client — desktop clients accept any localhost port; web clients need exact match).
- Opens the user's normal Chrome (whichever has Adithya logged into the right account).
- User clicks Continue, the callback writes the new token atomically.
- Validates with `getProfile`.
- Writes JSON in the existing INVENTORY shape.

Files:
```
_shell/bin/cred-mgr.py
_shell/lib/creds/registry.py        # parse credentials.yaml
_shell/lib/creds/state.py           # atomic state file w/ flock
_shell/lib/creds/atomic_write.py    # tmp+rename+fsync helper
_shell/config/credentials.yaml
_credentials/creds-state.json       # gitignored
```

This phase intentionally does NOT include cron, halt-loud, or background refresh. Adithya runs `cred-mgr login <name>` when prompted. The prompt is a `BROKEN` artifact left by Phase 1's `cred-mgr check` (which the existing schedule lint stage can run nightly without any new infrastructure).

## Phase 2 — Patchright re-consent (only if Phase 0 fails AND Phase 1 manual is unacceptable)

If — after Phase 0 — there is exactly one mailbox stuck on 7-day refresh and Adithya doesn't want to click weekly, automate that one. Do not build a generic framework yet; one mailbox does not justify it.

Specific corrections from review:

1. **Drop the legacy mirror** (`_credentials/google-accounts/<email>.json`). Both reviewers flagged the two-file rotation as not atomic. Refactor any consumers (gog-direct calls only?) to read from `_credentials/gmail-<slug>.json`. If a consumer can't be moved, leave it stale and accept that gog-direct re-auth is manual.
2. **Server-issued `consented_at` only.** Don't infer expiry from local `minted_at`. Read the OAuth response timestamp; if missing, mark the cred `UNKNOWN` and force a re-consent.
3. **`BROKEN` artifact is primary, iMessage is secondary.** Any failure → write `_credentials/<name>.BROKEN` with timestamp + classified reason + run-log path. THEN attempt iMessage. Lint stage picks up `.BROKEN` files and flags them in the daily summary regardless of iMessage delivery.
4. **State file needs its own flock**, separate from per-cred locks. Otherwise two refreshes racing the state file can corrupt it.
5. **Consumer read-lock pattern.** Ingest jobs that read `gmail-*.json` should `flock --shared <file>.lock` before reading. The refresher's exclusive lock then guarantees no consumer reads mid-rotation.
6. **OAuth error classification preserved verbatim.** Store the actual `error` / `error_description` / HTTP status from Google's response. Don't squash everything to `EXCHANGE_FAILED`. Reasons: `invalid_grant` (token revoked, full re-consent), `redirect_uri_mismatch` (config bug), `access_denied` (user/admin denied), `admin_policy_enforced` (Workspace policy blocks it), etc. each need different fixes.
7. **Scope handling: acceptable-set, not equality.** Compare returned scopes against an allowed set. Reject if returned scopes are broader than expected (excessive grant) or missing required scopes.
8. **Browser profile dirs as secrets.** `chmod 0700` on `_credentials/browser-profiles/*/`. Add to Time Machine exclusion. Scrub OAuth screenshots before persisting (redact `code=` query params, email addresses).
9. **Cron jitter.** Don't fire all 4 refreshes at exactly 04:00. `LaunchAgents` doesn't support jitter natively; achieve by scattering minutes (04:13, 04:27, 04:41, 04:55) in `global-schedule.yaml`.
10. **Refresh-token churn.** Google caps live refresh tokens at 100 per (account, client). Track issuance count in state; revoke superseded tokens via `https://oauth2.googleapis.com/revoke` if churn climbs.
11. **Dry-run is misleading.** Rename `--dry-run` → `--exercise-flow`; document that walking through consent mints a real token whether or not we write it.
12. **`refresh` from cron must be careful.** Cron-launched headed Chrome at 04:00 is a bot signal. If Phase 2 ships, scope to one account, randomize within a window, and back off aggressively on any 2FA/captcha hit (don't retry).

## Risks (consolidated, post-review)

The original plan's risk table now mostly applies only to Phase 2. The high-impact risks for Phase 0/1:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GCP project isn't owned by any Workspace org → Internal not available for any account | Med | Stays at Phase 1 manual or Phase 2 | Phase 1 is still much better than the status quo. Acceptable outcome. |
| In-Production for personal Gmail still 7-day-expires due to some Google policy change | Low | Phase 0 doesn't fix gmail.com | Verify with 8-day idle test before declaring Phase 0 done |
| Switching to Internal removes external test users we need | Low | Lose some access | Audit current External test users list before flipping |
| Re-consent token replaces the 4 existing in-flight tokens, breaks something | Low | Brief outage | Do during low-traffic window; gog ingest is idempotent on retry |

Phase 2-specific risks — see Draft 1 of this plan in git history.

## Testing strategy (Phase 1)

1. Unit: registry parse, atomic-write semantics, state-file flock.
2. End-to-end: `cred-mgr login gmail-adithya-synps` (lowest-stakes), confirm new token works.
3. Idempotency: run `cred-mgr login` twice; second run notices token is fresh and exits early.
4. Status: `cred-mgr status` correctly classifies a known-good and a `.BROKEN`-flagged cred.
5. Concurrency: simultaneous `check` + `login` block correctly via flock.

## Rollout

| Phase | Exit criterion |
|---|---|
| 0a — GCP audit | Document per-mailbox: User Type, Publishing Status, Client Type, owning org. Decision per mailbox: Internal / In-Production / Stuck. |
| 0b — Console flips | All eligible mailboxes flipped, all accounts re-consented once via existing gog flow, 8-day idle test passes |
| 1 — Build cred-mgr | Only if any mailbox is Stuck OR Adithya wants the convenience even for non-Stuck ones |
| 2 — Patchright | Only if Phase 1 manual is unacceptable for a Stuck mailbox |

## Open questions for Adithya

1. **GCP ownership audit** — which (if any) of the 3 work domains (`outerscope.xyz`, `synps.xyz`, `eclipse.builders`) is a Workspace org that owns the `gogcli` GCP project? If you don't know off the top of your head, I can read the OAuth client JSON and check IAM via the GCP API.
2. **In-Production for personal Gmail** — any reason not to flip the project to In Production? Caveat: it'll show an unverified-app warning on first consent (click-through). After that, no 7-day cliff.
3. **Phase 1 worth building?** Even if Phase 0 fixes everything, a unified `cred-mgr` is nice-to-have for future credential classes. But it's not free. Do you want it built, or wait until something else rots?
4. **Scope reduction** — `https://mail.google.com/` is the broadest Gmail scope (full read/write/delete). If ULTRON only ingests, `gmail.readonly` would work and is non-restricted (no unverified-app warning, no 100-user cap). Worth a one-time consent-screen reconfig?

## What changed from Draft 1

- Restructured around Phase 0 / 1 / 2, demoting patchright from default to last-resort.
- Removed the misleading "exchange-only refresh" alternative (Codex correctly noted it's not a real alternative — refresh-token grant doesn't mint a new refresh token).
- Eliminated legacy-mirror updates entirely (atomicity correctness).
- Made BROKEN file primary, iMessage secondary (halt-loud reliability).
- Added consumer read-lock pattern and state-file lock.
- Replaced `lifetime_days` config with server-observed `consented_at`.
- Added scope acceptable-set validation, OAuth error preservation, profile-dir security, cron jitter, refresh-token churn awareness.
- Renamed `--dry-run` → `--exercise-flow` with side-effect warning.
