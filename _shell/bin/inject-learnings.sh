#!/usr/bin/env bash
# inject-learnings.sh — UserPromptSubmit hook for ULTRON.
#
# Reads _global/agent-learnings.md and prints up to 1KB of relevant entries to
# stdout. Output is appended to the Claude session's system prompt so durable
# lessons persist across sessions.
#
# Wired in .claude/settings.json under hooks.UserPromptSubmit.

set -euo pipefail

LEARNINGS="$HOME/ULTRON/_global/agent-learnings.md"
[[ -f "$LEARNINGS" ]] || exit 0

# Skip if file is essentially empty (just headers / scaffold).
LINE_COUNT="$(wc -l < "$LEARNINGS" | tr -d '[:space:]')"
[[ "$LINE_COUNT" -lt 5 ]] && exit 0

# v1: emit the most recent 1KB of learnings. Future: keyword-grep against the
# user prompt (passed via $1 by Claude Code). Format the output so it reads as
# system-prompt context, not arbitrary noise.

cat <<'HEADER'
=== ULTRON agent-learnings (most recent) ===
The following durable lessons apply across sessions. Honor them.

HEADER

tail -c 1024 "$LEARNINGS"

cat <<'FOOTER'

=== end agent-learnings ===
FOOTER
