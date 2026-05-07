#!/usr/bin/env bash
# audit-system-health.sh — read-only check of the ULTRON daemon footprint.
#
# Compares declared (`_shell/plists/`) vs. loaded (`launchctl list`), surfaces
# failing jobs, foreign jobs (non-ULTRON personal labels), orphan locks, and
# log bloat. Output is markdown on stdout — the audit-agent reads it and folds
# it into the weekly report.
#
# Pure read. Never unloads, deletes, or touches launchd state.

set -uo pipefail

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
PLIST_DIR="$ULTRON_ROOT/_shell/plists"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
LOG_DIR="$ULTRON_ROOT/_logs"

echo "# System Health"
echo
echo "_Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)_"
echo

# --- 1. Declared vs loaded ---------------------------------------------------

declared=$(ls "$PLIST_DIR"/com.adithya.ultron.*.plist 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\.plist$//' | sort)
loaded=$(launchctl list | awk '$3 ~ /^com\.adithya\.ultron\./ {print $3}' | sort)

declared_not_loaded=$(comm -23 <(echo "$declared") <(echo "$loaded"))
loaded_not_declared=$(comm -13 <(echo "$declared") <(echo "$loaded"))

echo "## Declared but not loaded"
if [[ -z "$declared_not_loaded" ]]; then
  echo "- None."
else
  while IFS= read -r label; do
    [[ -z "$label" ]] && continue
    echo "- \`$label\` — plist exists at \`_shell/plists/\` but launchctl is not running it."
  done <<< "$declared_not_loaded"
fi
echo

echo "## Loaded but not declared"
if [[ -z "$loaded_not_declared" ]]; then
  echo "- None."
else
  while IFS= read -r label; do
    [[ -z "$label" ]] && continue
    echo "- \`$label\` — launchctl has it loaded but no source plist in \`_shell/plists/\`. Possibly stale; investigate."
  done <<< "$loaded_not_declared"
fi
echo

# --- 2. Failing ULTRON jobs --------------------------------------------------

echo "## Failing ULTRON jobs (last exit non-zero)"
failing=$(launchctl list | awk '$3 ~ /^com\.adithya\.ultron\./ && $2 != "0" && $2 != "-" {print $3" exit="$2}')
if [[ -z "$failing" ]]; then
  echo "- None."
else
  while IFS= read -r line; do
    label=$(awk '{print $1}' <<< "$line")
    exit_code=$(awk -F= '{print $2}' <<< "$line")
    last_log=""
    if [[ -f "$LOG_DIR/$label.err.log" ]]; then
      last_log=$(tail -3 "$LOG_DIR/$label.err.log" 2>/dev/null | tr '\n' ' ' | cut -c1-200)
    fi
    echo "- \`$label\` — exit $exit_code. Last stderr: \`$last_log\`"
  done <<< "$failing"
fi
echo

# --- 3. Foreign personal jobs ------------------------------------------------

echo "## Foreign personal jobs (non-ULTRON)"
echo "_Anything in \`~/Library/LaunchAgents/\` or \`launchctl list\` matching personal naming conventions that ISN'T \`com.adithya.ultron.*\` or \`com.shakstzy.ultron-autosync\`._"
echo
foreign_files=$(ls "$LAUNCH_AGENTS"/com.shakos.*.plist "$LAUNCH_AGENTS"/com.shakstzy.quantum-*.plist "$LAUNCH_AGENTS"/com.shakstzy.farm-*.plist 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\.plist$//' | sort)
foreign_loaded=$(launchctl list | awk '($3 ~ /^com\.shakos\./ || $3 ~ /^com\.shakstzy\.quantum/ || $3 ~ /^com\.shakstzy\.farm/) {print $3}' | sort)
foreign_all=$(printf "%s\n%s\n" "$foreign_files" "$foreign_loaded" | grep -v '^$' | sort -u)

if [[ -z "$foreign_all" ]]; then
  echo "- None. System is clean."
else
  while IFS= read -r label; do
    [[ -z "$label" ]] && continue
    label_clean="${label%.plist}"
    has_file=""
    has_loaded=""
    [[ -f "$LAUNCH_AGENTS/$label_clean.plist" ]] && has_file="file"
    if launchctl list | awk '{print $3}' | grep -qx "$label_clean"; then
      has_loaded="loaded"
    fi
    state=$(printf "%s%s%s" "$has_file" "${has_file:+,}" "$has_loaded" | sed 's/,$//')
    echo "- \`$label_clean\` — state: $state. Recommendation: unload + delete."
  done <<< "$foreign_all"
fi
echo

# --- 4. Orphan lock files ----------------------------------------------------

echo "## Orphan lock files"
orphans=$(find /tmp -maxdepth 1 -name 'ultron-*.lock' -mmin +60 2>/dev/null)
orphans+=$'\n'$(find /tmp -maxdepth 1 -name 'com.adithya.ultron.*.lock' -mmin +60 2>/dev/null)
orphans=$(echo "$orphans" | grep -v '^$' | sort -u)
if [[ -z "$orphans" ]]; then
  echo "- None."
else
  while IFS= read -r f; do
    age_min=$(( ( $(date +%s) - $(stat -f %m "$f" 2>/dev/null || echo 0) ) / 60 ))
    echo "- \`$f\` — ${age_min}m old. Crashed run; safe to remove."
  done <<< "$orphans"
fi
echo

# --- 5. Log bloat ------------------------------------------------------------

echo "## Log directory size"
if [[ -d "$LOG_DIR" ]]; then
  total=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
  total_bytes=$(du -sk "$LOG_DIR" 2>/dev/null | awk '{print $1}')
  echo "- \`_logs/\` total: $total"
  if [[ -n "$total_bytes" ]] && (( total_bytes > 51200 )); then
    echo "- **Over 50 MB.** Consider rotation."
    echo
    echo "Top 5 largest log files:"
    du -h "$LOG_DIR"/*.log 2>/dev/null | sort -hr | head -5 | awk '{printf "  - `%s` — %s\n", $2, $1}'
  fi
else
  echo "- \`_logs/\` does not exist."
fi
echo

# --- 6. Stale plists in _shell/plists/ that are loaded but never logged ------

echo "## Possibly-never-fired ULTRON jobs"
echo "_Loaded ULTRON jobs whose \`_logs/<label>.out.log\` is missing or empty._"
echo
silent=""
while IFS= read -r label; do
  [[ -z "$label" ]] && continue
  log="$LOG_DIR/$label.out.log"
  if [[ ! -s "$log" ]]; then
    silent+="$label"$'\n'
  fi
done <<< "$loaded"
silent=$(echo "$silent" | grep -v '^$')
if [[ -z "$silent" ]]; then
  echo "- None."
else
  while IFS= read -r label; do
    echo "- \`$label\` — no output logged. Either hasn't fired since install or stdout is being suppressed."
  done <<< "$silent"
fi
echo

exit 0
