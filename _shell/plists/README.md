# ULTRON Cron Jobs (launchd)

This directory holds 10 plist files that drive ULTRON's scheduled work via macOS launchd.

**None of them are loaded yet.** They live here as source-of-truth (versioned in git). Symlink + load only when you are ready to test live runs.

## The 10 jobs

| # | Plist | Schedule | What it does |
|---|---|---|---|
| 1 | `com.adithya.ultron.ingest-eclipse.plist` | Daily 02:30 | `run-stage.sh ingest eclipse` — pulls new Gmail / Slack / Drive / manual into `workspaces/eclipse/raw/`, then runs Eclipse wiki agent if new files arrived. |
| 2 | `com.adithya.ultron.ingest-personal.plist` | Daily 02:35 | `run-stage.sh ingest personal` — Gmail / iMessage / manual notes for personal life context. |
| 3 | `com.adithya.ultron.ingest-health.plist` | Daily 02:40 | `run-stage.sh ingest health` — manual workout logs, Apple Health exports, filtered Gmail. |
| 4 | `com.adithya.ultron.ingest-finance.plist` | Daily 02:45 | `run-stage.sh ingest finance` — filtered Gmail, Plaid CSV exports, manual notes. |
| 5 | `com.adithya.ultron.lint-eclipse.plist` | Daily 04:00 | `run-stage.sh lint eclipse` — route integrity, schema drift, stale entities, schema-specific rules; writes `workspaces/eclipse/_meta/lint-<date>.md`. |
| 6 | `com.adithya.ultron.lint-personal.plist` | Daily 04:05 | `run-stage.sh lint personal` |
| 7 | `com.adithya.ultron.lint-health.plist` | Daily 04:10 | `run-stage.sh lint health` |
| 8 | `com.adithya.ultron.lint-finance.plist` | Daily 04:15 | `run-stage.sh lint finance` |
| 9 | `com.adithya.ultron.audit.plist` | **Sunday 05:00** | `run-stage.sh audit` — cross-workspace conscience: misplaced content, alias collisions, stale workspaces, schema drift across workspaces, backfill patterns, Graphify surprises, global stub freshness. Writes `_audit/weekly/<YYYY-WW>.md`. |
| 10 | `com.adithya.ultron.weekly-review.plist` | **Sunday 07:00** | `run-stage.sh weekly-review` — composes the weekly review packet at `_audit/reviews/<YYYY-WW>.md` from all the prior week's lint + audit reports + open proposals. |

Stagger between ingests (5 min apart) avoids API rate-limit collisions; lint comes after all ingests are done; audit waits until Sunday so it has a full week of data.

## Common settings (every plist)

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  <key>ULTRON_ROOT</key><string>/Users/shakstzy/ULTRON</string>
  <key>HOME</key><string>/Users/shakstzy</string>
</dict>
<key>StandardOutPath</key><string>/Users/shakstzy/ULTRON/_logs/<job>.out.log</string>
<key>StandardErrorPath</key><string>/Users/shakstzy/ULTRON/_logs/<job>.err.log</string>
<key>RunAtLoad</key><false/>
<key>WorkingDirectory</key><string>/Users/shakstzy/ULTRON</string>
```

The PATH includes `/opt/homebrew/bin` so `claude`, `python3`, `graphify`, and `flock` resolve. `RunAtLoad: false` means loading does NOT immediately execute; jobs wait for their scheduled time.

## How to load a single job (smoke test)

```bash
ln -sf ~/ULTRON/_shell/plists/com.adithya.ultron.ingest-eclipse.plist ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/com.adithya.ultron.ingest-eclipse.plist
launchctl start com.adithya.ultron.ingest-eclipse        # run immediately to verify
tail -f ~/ULTRON/_logs/ingest-eclipse.{out,err}.log      # watch output
```

## How to load all 10 at once

```bash
for plist in ~/ULTRON/_shell/plists/*.plist; do
  ln -sf "$plist" ~/Library/LaunchAgents/
  launchctl load -w ~/Library/LaunchAgents/"$(basename "$plist")"
done
launchctl list | grep com.adithya.ultron
```

## How to UNLOAD a job (before editing the plist)

```bash
launchctl unload ~/Library/LaunchAgents/com.adithya.ultron.ingest-eclipse.plist
# Edit the plist in ~/ULTRON/_shell/plists/, then re-load.
```

## How to UNLOAD ALL ULTRON jobs

```bash
for plist in ~/Library/LaunchAgents/com.adithya.ultron.*.plist; do
  launchctl unload "$plist"
  rm "$plist"
done
launchctl list | grep com.adithya.ultron   # should be empty
```

## Status / debugging

```bash
# All ULTRON jobs
launchctl list | grep com.adithya.ultron

# Last exit code for a job (column 1: PID, column 2: last exit code, column 3: label)
launchctl list com.adithya.ultron.ingest-eclipse

# Inspect a job's last run output
tail -50 ~/ULTRON/_logs/ingest-eclipse.out.log
tail -50 ~/ULTRON/_logs/ingest-eclipse.err.log

# Dispatcher's run summary log (every stage invocation gets one line)
tail -20 ~/ULTRON/_logs/dispatcher.log
```

## Known caveats

1. **Ingest is currently no-op.** Until OAuth credentials land in `_credentials/<source>-<workspace>.json`, every ingest script logs "no credentials, skipping" and exits 0. The pipeline runs end-to-end but produces no new raw files. Lint will still run. Wiki agent will not be invoked because `new-raw.txt` will be empty.
2. **`claude` CLI must be on PATH at launchd run time.** The plists hardcode `/opt/homebrew/bin` first; if Adithya moves Homebrew, edit the PATH in each plist.
3. **Full Disk Access required for iMessage ingest.** macOS will block reads of `~/Library/Messages/chat.db` until you grant Full Disk Access to whatever process launchd spawns (typically `bash`). System Settings > Privacy & Security > Full Disk Access > add `/bin/bash` (or the wrapper).
4. **Lock contention exits 0.** If a previous run hasn't finished by the time the next is scheduled, the new one logs "another <stage> for <ws> is running; exiting" and exits 0. launchd treats that as success and waits for the next slot. (Change to `exit 75` if you want launchd to retry sooner.)
5. **No API budget cap.** `_shell/budget.yaml` is set to 999999 since you are on Claude Max. If you ever switch to per-call billing, lower `mtd_cap_usd` and a real tally lands in `_logs/anthropic-mtd.json` (not yet wired — TODO when needed).
6. **plists are the source of truth.** `~/Library/LaunchAgents/` is just a symlink target. Edit only `~/ULTRON/_shell/plists/` and re-load.
