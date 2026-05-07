#!/bin/bash
# Reload (bootout + bootstrap) every currently-loaded com.adithya.ultron.* job.
# Use this after editing plist files in place to make launchd pick up the changes.

set -u
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

labels=$(launchctl list | awk '$3 ~ /^com\.adithya\.ultron\./ {print $3}')
count_ok=0
count_fail=0

for label in $labels; do
    plist_path="$HOME/Library/LaunchAgents/${label}.plist"
    if [[ ! -e "$plist_path" ]]; then
        echo "[reload] SKIP $label (no symlink at $plist_path)"
        continue
    fi
    # Bootout, ignore "no such service" failures (28).
    launchctl bootout "${DOMAIN}/${label}" 2>/dev/null || true
    if launchctl bootstrap "${DOMAIN}" "$plist_path" 2>/dev/null; then
        echo "[reload] OK   $label"
        count_ok=$((count_ok + 1))
    else
        echo "[reload] FAIL $label"
        count_fail=$((count_fail + 1))
    fi
done

echo
echo "[reload] done: ok=$count_ok fail=$count_fail"
