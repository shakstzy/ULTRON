# HITL Gate Tokens

Human-in-the-loop gates that block automation until Adithya types the gate token in the chat. Single-operator system; gates protect against irreversible / public / money-moving / cross-account actions.

## Tokens

### `CONFIRM`

Generic destructive / cross-account / irreversible. Default token when no other applies.

Gates:
- `ffmpeg` calls with `-y` flag (overwrite source)
- `git push --force` (any branch)
- `git rm` of more than 5 files in one call
- Linear / Notion bulk-delete
- Gmail bulk-modify on >100 messages
- `launchctl bootstrap` of a plist (also covered by `load`; either gate satisfies)
- Any database `DROP` / `TRUNCATE` / mass `DELETE`
- Workspace deletion (`rm -rf workspaces/<ws>`)
- Trade order submission (separate from research / monitoring)

### `SEND`

Outbound message to a specific human via a real channel.

Gates:
- iMessage / SMS send
- Slack DM send
- Email send (any account)
- WhatsApp / Telegram / Discord DM send
- Tinder / Bumble / Hinge / OnlyFans DM (per-platform pacing rules also apply)
- LinkedIn message send

NOT gated by SEND: drafts written to a workspace's outbound queue (e.g. `04-outbound/drafts/`), replies queued but not actually transmitted.

### `PUBLISH`

Public / mass / one-to-many output.

Gates:
- Zernio organic post (Instagram, YouTube, TikTok, Twitter, Discord server)
- Notion page changed from private to public
- GitHub release published (not `gh release create --draft`)
- PR merged to main / master
- OnlyFans PPV / mass message
- DistroKid release submission (music going to streaming services)
- Any HTTP POST to a `/publish`, `/post`, `/release` endpoint of a 3rd-party platform

NOT gated by PUBLISH: drafts in `wiki/synthesis/`, internal Slack messages (use SEND), opening a PR (use CONFIRM).

### `LAUNCH-AD`

Money-spending paid distribution.

Gates:
- Zernio paid ad creation / boost (Meta, Google, LinkedIn, TikTok, Pinterest, X)
- Custom audience upload that triggers billing
- Boost button click on any platform
- API call to any `/ads`, `/campaign`, `/promote` endpoint that triggers billing
- OnlyFans paid promotion / cross-promo

LAUNCH-AD always implies PUBLISH; both gates fire serially when the action is paid public distribution.

### `load`

Schedule-skill loading of plists into launchd.

Gates:
- `schedule load <name>` — load a single plist via `launchctl bootstrap`
- `schedule load --all`

NOT gated by `load`: `schedule compile` (regenerates plists from `schedule.yaml`), `schedule status`, `schedule unload` (uses CONFIRM instead, since unload is reversible).

## Gate execution model

Each gate is a bash function in `_shell/bin/gate.sh`:

```bash
gate_confirm   "<action description>"           || exit 1
gate_send      "channel:<chan> length:<chars>"  || exit 1
gate_publish   "platform:<plat> audience:<est>" || exit 1
gate_launch_ad "platform:<plat> budget:<usd>"   || exit 1
gate_load      "plist:<name>"                   || exit 1
```

Each function: prints the gate token name + action description to stderr, reads stdin for the gate token (case-sensitive, exact match), returns 0 on match, 1 otherwise. One-line entry appended to `_logs/gates.log` on every fire (action, token, accepted-or-aborted).

When invoked from within a Claude session, the agent surfaces the gate prompt via chat and waits for Adithya to type the token literally. The agent does NOT auto-fill the token.

## Skill / stage declaration

Skills and stage scripts declare `hitl_gates: [<TOKEN>...]` in their YAML header. The dispatcher (`run-stage.sh`) checks the list before invoking the underlying script and calls the appropriate `gate_*` function. The script itself can also call gates inline for sub-steps that need separate confirmation.

## Failure handling

If a gate fails: skill / stage exits with code 1, dispatcher writes `gate-aborted` to the run dir, no partial side effects from the gated action commit. User can re-invoke; gate re-fires from scratch. No retry / cool-off / lockout — Adithya is the only operator.

## What gates do NOT do

- Identity logging (single-operator system)
- Encryption / signing
- Cool-off period or rate limit beyond the in-session prompt
- Audit trail beyond `_logs/gates.log`
