# ULTRON cron jobs (launchd)

This directory holds compiled plist files. **Do NOT hand-edit them.** They are generated from YAML schedules by the `schedule` skill.

## Source of truth

- Per-workspace cadence: `workspaces/<ws>/config/schedule.yaml`
- Cross-workspace cadence: `_shell/config/global-schedule.yaml`

Skill spec: `_shell/skills/schedule/SKILL.md`.

## Common operations

```bash
# Regenerate plists from YAML (does NOT load them):
/schedule compile

# Show what exists, what is loaded, last run per job:
/schedule status

# Load a specific job (requires explicit chat confirmation):
/schedule load com.adithya.ultron.ingest-gmail-adithya-eclipse

# Load everything (heavy — boots every agent at once):
/schedule load --all

# Unload a specific job:
/schedule unload com.adithya.ultron.<job>

# Retire a job permanently (unload + delete plist file):
/schedule remove com.adithya.ultron.<job>
```

## Anatomy of one plist

Every generated plist sets:
- `EnvironmentVariables`: `PATH`, `ULTRON_ROOT`, `HOME`.
- `StandardOutPath` → `_logs/<label>.out.log`.
- `StandardErrorPath` → `_logs/<label>.err.log`.
- `WorkingDirectory` → ULTRON root.
- `RunAtLoad: false`.
- `StartCalendarInterval` translated from the cron string in the source YAML.

Command shape: `flock -n /tmp/<label>.lock $ULTRON_ROOT/_shell/bin/run-stage.sh <args>`. flock keeps a delayed scheduled run from colliding with one still in flight.

## Caveats

1. **Full Disk Access required for iMessage ingest.** macOS blocks reads of `~/Library/Messages/chat.db` until you grant Full Disk Access to whatever process launchd spawns (typically `/bin/bash`). System Settings → Privacy & Security → Full Disk Access → add `/bin/bash`.
2. **Lock contention exits 0.** If a previous run hasn't finished by the next scheduled tick, the new one logs "another run in flight; exiting" and exits 0. launchd waits for the next slot.
3. **Orphans are reported, not removed.** `/schedule compile` lists plists in this directory that no schedule.yaml entry produces. Use `/schedule remove <label>` to retire them.
4. **plists are output, not source.** Edit YAML and re-compile. Never edit files in this directory by hand.
