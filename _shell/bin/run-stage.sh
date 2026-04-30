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

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
RUN_ID="$(date +%Y-%m-%dT%H-%M-%S)-${STAGE}${WORKSPACE:+-$WORKSPACE}"
RUN_DIR="$ULTRON_ROOT/_shell/runs/$RUN_ID"
mkdir -p "$RUN_DIR/input" "$RUN_DIR/output"

# Idempotency lock
LOCK="/tmp/ultron-$STAGE-${WORKSPACE:-cross}.lock"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "ultron: another $STAGE${WORKSPACE:+ for $WORKSPACE} is running; exiting" >&2
  exit 0
fi

# API budget guard (no-op while mtd_cap_usd is set high; see _shell/budget.yaml)
if [[ -x "$ULTRON_ROOT/_shell/bin/check-budget.py" ]]; then
  if ! "$ULTRON_ROOT/_shell/bin/check-budget.py"; then
    echo "ultron: API budget exceeded" >&2
    exit 1
  fi
fi

# Build the prompt: root CLAUDE.md → stage CONTEXT → workspace CLAUDE.md (if scoped)
PROMPT_FILE="$RUN_DIR/prompt.md"
{
  cat "$ULTRON_ROOT/CLAUDE.md"
  echo; echo "---"; echo
  cat "$ULTRON_ROOT/_shell/stages/${STAGE}/CONTEXT.md"
  echo; echo "---"; echo
  if [[ -n "$WORKSPACE" ]]; then
    cat "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md"
    echo; echo "---"; echo
  fi
  echo "RUN_ID: $RUN_ID"
  echo "WORKSPACE: ${WORKSPACE:-<cross-workspace>}"
} > "$PROMPT_FILE"

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
  cat "$PROMPT_FILE" | claude "${args[@]}" \
    > "$result_file" 2> "$stderr_file"
}

EC=0

case "$STAGE" in
  ingest)
    [[ -n "$WORKSPACE" ]] || { echo "ingest requires workspace" >&2; exit 2; }
    python3 "$ULTRON_ROOT/_shell/bin/ingest-driver.py" "$WORKSPACE" "$RUN_ID" \
      > "$RUN_DIR/output/ingest-driver.log" 2>&1 || EC=$?
    ;;
  lint)
    [[ -n "$WORKSPACE" ]] || { echo "lint requires workspace" >&2; exit 2; }
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
    [[ -n "$WORKSPACE" ]] || { echo "bootstrap requires new-workspace name" >&2; exit 2; }
    if [[ -d "$ULTRON_ROOT/workspaces/$WORKSPACE" ]]; then
      echo "workspace exists: $WORKSPACE" >&2
      exit 3
    fi
    cp -r "$ULTRON_ROOT/workspaces/_template" "$ULTRON_ROOT/workspaces/$WORKSPACE"
    # Bootstrap is interactive — invoke claude WITHOUT --print so the user can answer questions.
    cat "$PROMPT_FILE" | claude \
      --add-dir "$ULTRON_ROOT" \
      --append-system-prompt "$(cat "$ULTRON_ROOT/_shell/agents/bootstrap-agent.md")" \
      || EC=$?
    ;;
  weekly-review|query)
    claude_invoke "" "$RUN_DIR/output/result.json" "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
  *)
    echo "unknown stage: $STAGE" >&2
    exit 2
    ;;
esac

mkdir -p "$ULTRON_ROOT/_logs"
echo "$(date -u +%FT%TZ) | $RUN_ID | exit=$EC" >> "$ULTRON_ROOT/_logs/dispatcher.log"
exit $EC
