#!/usr/bin/env bash
# run-stage.sh — universal dispatcher for ULTRON stages.
#
# Usage:
#   run-stage.sh <stage> [<workspace>]
#
# Stages: ingest | lint | audit | bootstrap | weekly-review | query
set -euo pipefail

STAGE="${1:-}"
WORKSPACE="${2:-}"

if [[ -z "$STAGE" ]]; then
  echo "usage: run-stage.sh <stage> [<workspace>]" >&2
  exit 2
fi

export ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"

# 1. Stage validation BEFORE any state mutation.
case "$STAGE" in
  ingest|lint|audit|bootstrap|weekly-review|query) ;;
  *)
    echo "unknown stage: $STAGE" >&2
    exit 2
    ;;
esac

# 2. Workspace requirement validation per stage.
case "$STAGE" in
  ingest|lint|bootstrap)
    if [[ -z "$WORKSPACE" ]]; then
      echo "$STAGE requires workspace" >&2
      exit 2
    fi
    ;;
esac

# 3. Stage-context existence check.
if [[ ! -f "$ULTRON_ROOT/_shell/stages/$STAGE/CONTEXT.md" ]]; then
  echo "missing stage CONTEXT.md: $ULTRON_ROOT/_shell/stages/$STAGE/CONTEXT.md" >&2
  exit 2
fi

# 4. Workspace router check (for stages that scope to a workspace, except bootstrap which CREATES the workspace).
if [[ "$STAGE" != "bootstrap" && -n "$WORKSPACE" ]]; then
  if [[ ! -f "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md" ]]; then
    echo "missing workspace router: $ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md" >&2
    exit 2
  fi
fi

# 5. Ensure log dir exists before any tool tries to write there.
mkdir -p "$ULTRON_ROOT/_logs"

RUN_ID="$(date +%Y-%m-%dT%H-%M-%S)-${STAGE}${WORKSPACE:+-$WORKSPACE}"
RUN_DIR="$ULTRON_ROOT/_shell/runs/$RUN_ID"
mkdir -p "$RUN_DIR/input" "$RUN_DIR/output"

# 6. Idempotency lock. Exit 0 on contention is intentional: launchd treats it as
# "already handled this run." If you want launchd to retry instead, change to 75.
LOCK="/tmp/ultron-$STAGE-${WORKSPACE:-cross}.lock"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "ultron: another $STAGE${WORKSPACE:+ for $WORKSPACE} is running; exiting" >&2
  exit 0
fi

# 7. Resolve claude binary up front so we fail loudly if PATH is wrong (esp. under launchd).
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude || true)}"
if [[ -z "$CLAUDE_BIN" ]]; then
  echo "ultron: 'claude' CLI not found on PATH ($PATH). Set CLAUDE_BIN or add /opt/homebrew/bin to PATH." >&2
  exit 2
fi

# 8. API budget guard (no-op while mtd_cap_usd is set high; see _shell/budget.yaml)
if [[ -x "$ULTRON_ROOT/_shell/bin/check-budget.py" ]]; then
  if ! "$ULTRON_ROOT/_shell/bin/check-budget.py"; then
    echo "ultron: API budget exceeded" >&2
    exit 1
  fi
fi

# 9. Build the prompt: root CLAUDE.md → stage CONTEXT → workspace CLAUDE.md (if scoped).
PROMPT_FILE="$RUN_DIR/prompt.md"
{
  cat "$ULTRON_ROOT/CLAUDE.md"
  echo; echo "---"; echo
  cat "$ULTRON_ROOT/_shell/stages/${STAGE}/CONTEXT.md"
  echo; echo "---"; echo
  if [[ -n "$WORKSPACE" && -f "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md" ]]; then
    cat "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md"
    echo; echo "---"; echo
  fi
  echo "RUN_ID: $RUN_ID"
  echo "WORKSPACE: ${WORKSPACE:-<cross-workspace>}"
} > "$PROMPT_FILE"

# claude_invoke: non-interactive (--print) call.
claude_invoke() {
  local agent_prompt_file="$1"
  local result_file="$2"
  local stderr_file="$3"
  local args=(
    --print
    --output-format json
    --add-dir "$ULTRON_ROOT"
  )
  if [[ -n "$agent_prompt_file" && -f "$agent_prompt_file" ]]; then
    args+=(--append-system-prompt "$(cat "$agent_prompt_file")")
  fi
  "$CLAUDE_BIN" "${args[@]}" "$(cat "$PROMPT_FILE")" \
    > "$result_file" 2> "$stderr_file"
}

EC=0

case "$STAGE" in
  ingest)
    python3 "$ULTRON_ROOT/_shell/bin/ingest-driver.py" "$WORKSPACE" "$RUN_ID" \
      > "$RUN_DIR/output/ingest-driver.log" 2>&1 || EC=$?

    # Skip wiki-agent invocation if ingest itself failed — synthesizing on a
    # partial / corrupted raw set is worse than skipping.
    if [[ $EC -eq 0 ]]; then
      NEW_RAW="$RUN_DIR/input/new-raw.txt"
      WIKI_AGENT="$ULTRON_ROOT/workspaces/$WORKSPACE/agents/wiki-agent.md"
      if [[ -s "$NEW_RAW" && -f "$WIKI_AGENT" ]]; then
        WIKI_FLAG="$(grep -E '^\s*wiki:\s*true' "$ULTRON_ROOT/workspaces/$WORKSPACE/config/sources.yaml" 2>/dev/null || true)"
        if [[ -n "$WIKI_FLAG" ]]; then
          claude_invoke \
            "$WIKI_AGENT" \
            "$RUN_DIR/output/wiki-result.json" \
            "$RUN_DIR/output/wiki-stderr.log" || EC=$?
        fi
      fi
    fi
    ;;
  lint)
    "$ULTRON_ROOT/_shell/bin/check-routes.py" --workspace "$WORKSPACE" \
      --output "$RUN_DIR/output/check-routes.txt" || true
    "$ULTRON_ROOT/_shell/bin/build-backlinks.py" --dry-run --workspace "$WORKSPACE" \
      > "$RUN_DIR/output/backlinks.txt" 2>&1 || true
    claude_invoke \
      "$ULTRON_ROOT/workspaces/$WORKSPACE/agents/lint-agent.md" \
      "$RUN_DIR/output/result.json" \
      "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
  audit)
    "$ULTRON_ROOT/_shell/bin/build-backlinks.py" \
      > "$RUN_DIR/output/backlinks.txt" 2>&1 || true
    "$ULTRON_ROOT/_shell/bin/graphify-run.sh" \
      > "$RUN_DIR/output/graphify.log" 2>&1 || true
    claude_invoke \
      "$ULTRON_ROOT/_shell/agents/audit-agent.md" \
      "$RUN_DIR/output/result.json" \
      "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
  bootstrap)
    if [[ -d "$ULTRON_ROOT/workspaces/$WORKSPACE" ]]; then
      echo "workspace exists: $WORKSPACE" >&2
      exit 3
    fi
    cp -r "$ULTRON_ROOT/workspaces/_template" "$ULTRON_ROOT/workspaces/$WORKSPACE"
    # Bootstrap is interactive. Pass the prompt as the positional initial-message
    # argument (NOT via stdin) so claude can keep stdin attached to the user's
    # terminal for follow-up answers.
    "$CLAUDE_BIN" \
      --add-dir "$ULTRON_ROOT" \
      --append-system-prompt "$(cat "$ULTRON_ROOT/_shell/agents/bootstrap-agent.md")" \
      "$(cat "$PROMPT_FILE")" \
      || EC=$?
    ;;
  weekly-review|query)
    claude_invoke "" "$RUN_DIR/output/result.json" "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
esac

echo "$(date -u +%FT%TZ) | $RUN_ID | exit=$EC" >> "$ULTRON_ROOT/_logs/dispatcher.log"
exit $EC
