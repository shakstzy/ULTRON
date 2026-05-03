# Setup: ingest-slack

> Slack app provisioning, scopes, token install, rate-limit behavior,
> and the activation procedure for the Slack robot. Read alongside
> `format.md` (data spec) and `CONTEXT.md` (workflow).

## 1. Slack app + user token (REQUIRED)

The robot uses a **user token** (`xoxp-...`), not a bot token. User
tokens see everything the user sees: every channel they belong to,
every DM, every group DM. Bot tokens require explicit channel invites
and miss DMs entirely.

Steps:

1. Open https://api.slack.com/apps → **Create New App** → **From
   scratch**.
2. App name: `ULTRON Ingest`. Pick the workspace (e.g., Eclipse Labs).
3. **OAuth & Permissions** → **User Token Scopes** → add all 12 below.
4. **Install to Workspace** (admin approval may be required if this is
   the first app; ask the workspace admin if blocked).
5. Copy the **User OAuth Token** (starts `xoxp-`).
6. Save to `_credentials/slack-<workspace-slug>.json` (mode `0600`):
   ```json
   {
     "workspace_slug": "eclipse-labs",
     "team_id": "T02ABC123",
     "user_token": "xoxp-...",
     "scopes": ["channels:history", "channels:read", "..."],
     "minted_at": "2026-05-02T12:00:00-05:00"
   }
   ```
7. Verify: `chmod 600` the file, confirm it's gitignored
   (`_credentials/` is, by repo policy).

## 2. Required user-token scopes (all 12)

| Scope | Why |
|---|---|
| `channels:history` | Read messages in public channels you've joined |
| `channels:read` | List public channels + read channel metadata |
| `groups:history` | Read messages in private channels you're in |
| `groups:read` | List private channels + read metadata |
| `im:history` | Read 1:1 DM messages |
| `im:read` | List your DM containers |
| `mpim:history` | Read group DM messages |
| `mpim:read` | List your group DM containers |
| `users:read` | Resolve user IDs → display names |
| `users:read.email` | Capture email in user profiles (priority-3 slug fallback) |
| `team:read` | Workspace metadata (team.info → workspace name + URL) |
| `files:read` | Attachment metadata + permalinks |

If any scope is denied at install time, the robot logs an actionable
error on first call and exits 0. Do NOT auto-rotate tokens; surface
the missing scope to the operator.

## 3. Workspace ID retrieval

Two paths:
1. **Inside Slack**: workspace settings → "About this workspace"
   shows the team ID (`T02...`).
2. **Via API after install**:
   ```bash
   curl -s -H "Authorization: Bearer xoxp-..." \
     https://slack.com/api/team.info | jq '.team | {id, name, domain}'
   ```
   Save the `id` as `team_id` in the credential JSON. The robot also
   re-fetches and writes the team snapshot into the workspace
   `_profile.md` on every run (per `format.md` Lock 7).

## 4. Auto-detection of "me"

On every run, the robot calls `auth.test`:
```bash
curl -s -H "Authorization: Bearer xoxp-..." \
  https://slack.com/api/auth.test | jq '{user_id, user, team_id, team}'
```

The returned `user_id` is mapped to canonical slug
`adithya-shak-kumar` and cached in
`_shell/cursors/slack/<workspace-slug>/me.txt`:
```
user_id: U02XYZ789
canonical_slug: adithya-shak-kumar
```

If `me.txt` exists with a different `user_id`, the robot logs a
warning ("token belongs to a different user than profile records")
and exits 0. This catches token-swap mistakes (re-using one
workspace's token for another).

## 5. Rate limits + retry behavior

Slack Tier-3 methods (`conversations.history`, `conversations.replies`,
`users.info`) cap at ~50 req/min, 100 messages/page. For the Eclipse
Labs allowlist (6 channels + N DMs):
- **First run** (cursor empty, full lookback): 5–15 minutes for a
  modestly active workspace; longer on noisy ones.
- **Incremental runs**: seconds to a minute or two depending on
  daily message volume.
- **Schema-only re-renders** (`--no-attachments`): a few minutes for
  the active month.

The robot:
- Honors the `Retry-After` header on 429.
- Falls back to exponential backoff + jitter if no header is set.
- Retries up to 5 times per request.
- After exhaustion, defers the container to a per-run deferred queue,
  logs the deferral, and continues with the next container. Never
  hard-crashes the run.

## 6. Realistic timing expectations

For Eclipse Labs (6 channels + handful of DMs):
- **First run**: plan for 10–20 minutes. The N+1 thread-fetch pattern
  is the bottleneck — one `conversations.replies` call per parent
  with thread replies. Cached within the run, so a single thread
  pulled across multiple day-files only fetches once.
- **Daily incremental**: under a minute on most days.
- **Activation smoke test** (`--max-days 5 --channel deals`):
  ~30 seconds.

## 7. Activation procedure (flipping `IMPLEMENTATION_READY`)

Do NOT flip until ALL of the below are green:

1. Slack app provisioned with all 12 scopes (§ 2).
2. User token installed and saved to
   `_credentials/slack-eclipse-labs.json` mode 0600 (§ 1).
3. `auth.test` returns expected `user_id`; verified manually:
   ```bash
   curl -s -H "Authorization: Bearer $(jq -r .user_token \
     _credentials/slack-eclipse-labs.json)" \
     https://slack.com/api/auth.test
   ```
4. At least one workspace `sources.yaml` has a `slack` block with the
   workspace_id and at least one channel allowlisted.
5. Validators green:
   ```bash
   python3 _shell/bin/check-routes.py
   python3 _shell/bin/check-frontmatter.py
   python3 _shell/tests/test_rename_slug.py
   ```
6. Dry-run produces sane output (still gated by
   `IMPLEMENTATION_READY = False` — flip a temporary local copy if
   needed, never commit `True` until the smoke test passes):
   ```bash
   python3 _shell/bin/ingest-slack.py \
     --workspace eclipse-labs --max-days 5 --channel deals \
     --dry-run --show
   ```

When all green, edit `_shell/bin/ingest-slack.py` and set:
```python
IMPLEMENTATION_READY = True
```
First live run should be `--max-days 5 --channel deals` to validate
end-to-end before unlocking the full workspace.

## 8. Troubleshooting

- **`missing_scope` from API**: a scope wasn't checked at install
  time. Reinstall the app with all 12 scopes (§ 2). The `xoxp` token
  changes; update the credential JSON.
- **`account_inactive` / `token_revoked`**: token was rotated by an
  admin or by you. Mint a new one (§ 1).
- **`not_in_channel`** for a public channel that the user IS in:
  rare Slack consistency lag; retry on the next run.
- **`not_found` / `channel_not_found`**: container was archived or
  deleted upstream. Robot sets `container_archived: true` on
  `_profile.md` and continues. No action required.
- **Sustained 429s on first run**: workspace is large enough that the
  default lookback is too aggressive. Run with `--max-days 30` first
  to populate the active month, then lift the cap on the next run.
- **`me.txt` user_id mismatch warning**: you swapped a token between
  workspaces. Either update `me.txt` (if intentional) or re-mint the
  correct token (if not).

## 9. v1 vs v1.5 caveats (deferred work)

| Gap | v1 behavior | v1.5 plan |
|---|---|---|
| Reactions | Skipped entirely | Render inline below the message they target |
| Edit history | Current text + edit count only | Walk `message_changed` history events, render prior versions |
| Attachment binaries | Metadata + permalinks only | Optional copy to `_attachments/` mirroring iMessage Lock 7 |
| Channel allowlist filter | Routing-time only | Fetch-time filter when allowlist is small + workspace is huge |
| Voice clips | `[file: clip.m4a — Xs]` placeholder | Whisper transcription via separate skill |
| Cross-source merge (DM → iMessage → WhatsApp) | Per-source archives independent | Wiki entity page synthesizes |
| Privacy compartmentalization | Per-workspace routing only | `private` workspace can opt out of `_graphify/` |

## 10. Cross-references

Data spec: `format.md`. Workflow: `CONTEXT.md`. Routing: `route.py`.
Universal envelope check: `_shell/bin/check-frontmatter.py`.
Credential inventory: `_credentials/INVENTORY.md`.
