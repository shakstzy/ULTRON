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

SOURCE=""
ACCOUNT=""

# 1. Stage validation BEFORE any state mutation.
case "$STAGE" in
  ingest|lint|audit|bootstrap|weekly-review|query) ;;
  apple-contacts-sync|ledger-compact|graphify-supermerge|graphify|granola-reconcile|rental-cycle|synthesize-voice-profiles|podcast-outreach|auditor-deadman) ;;
  ingest-source)
    # Per (source, account) mode. Args: ingest-source <source> <account>.
    SOURCE="${2:-}"
    ACCOUNT="${3:-}"
    WORKSPACE=""   # not workspace-scoped
    if [[ -z "$SOURCE" ]]; then
      echo "ingest-source requires <source> <account>" >&2
      exit 2
    fi
    ;;
  *)
    echo "unknown stage: $STAGE" >&2
    exit 2
    ;;
esac

# 2. Workspace requirement validation per stage.
case "$STAGE" in
  ingest|lint|bootstrap|graphify)
    if [[ -z "$WORKSPACE" ]]; then
      echo "$STAGE requires workspace" >&2
      exit 2
    fi
    ;;
esac

# 3. Stage-context existence check.
# Helper stages don't have a stages/<stage>/CONTEXT.md; they invoke a single
# script and exit. ingest-source uses the source's substage CONTEXT.md.
case "$STAGE" in
  apple-contacts-sync|ledger-compact|graphify-supermerge|graphify|granola-reconcile|rental-cycle|synthesize-voice-profiles|podcast-outreach|auditor-deadman) ;;
  ingest-source)
    if [[ ! -f "$ULTRON_ROOT/_shell/stages/ingest/$SOURCE/CONTEXT.md" ]]; then
      echo "missing source substage: $ULTRON_ROOT/_shell/stages/ingest/$SOURCE/CONTEXT.md" >&2
      exit 2
    fi
    ;;
  *)
    if [[ ! -f "$ULTRON_ROOT/_shell/stages/$STAGE/CONTEXT.md" ]]; then
      echo "missing stage CONTEXT.md: $ULTRON_ROOT/_shell/stages/$STAGE/CONTEXT.md" >&2
      exit 2
    fi
    ;;
esac

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
# For ingest-source the lock is keyed on (source, account) so independent
# per-account ingests run in parallel. Without this they all fell back to
# ${WORKSPACE:-cross} → one shared "/tmp/ultron-ingest-source-cross.lock" →
# at every :00 cron slot one winner ran and 3+ siblings silently exited 0
# ("already handled"), starving entire hours for the losers.
if [[ "$STAGE" == "ingest-source" ]]; then
  ACCOUNT_LOCK_SLUG="$(printf '%s' "$ACCOUNT" | tr -c 'A-Za-z0-9' '-')"
  LOCK="/tmp/ultron-ingest-source-${SOURCE}-${ACCOUNT_LOCK_SLUG}.lock"
else
  LOCK="/tmp/ultron-$STAGE-${WORKSPACE:-cross}.lock"
fi
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "ultron: another $STAGE${WORKSPACE:+ for $WORKSPACE} is running; exiting" >&2
  exit 0
fi

# 7. Resolve claude binary up front so we fail loudly if PATH is wrong (esp. under launchd).
# Stages that ACTUALLY call claude need the binary. Everything else doesn't.
NEEDS_CLAUDE=0
case "$STAGE" in
  lint|audit|bootstrap|weekly-review|query|ingest)
    NEEDS_CLAUDE=1
    ;;
esac

if (( NEEDS_CLAUDE )); then
  CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude || true)}"
  if [[ -z "$CLAUDE_BIN" ]]; then
    echo "ultron: 'claude' CLI not found on PATH ($PATH). Set CLAUDE_BIN or add /opt/homebrew/bin to PATH." >&2
    exit 2
  fi
else
  CLAUDE_BIN=""
fi

# 8. API budget guard (no-op while mtd_cap_usd is set high; see _shell/budget.yaml)
if [[ -x "$ULTRON_ROOT/_shell/bin/check-budget.py" ]]; then
  if ! "$ULTRON_ROOT/_shell/bin/check-budget.py"; then
    echo "ultron: API budget exceeded" >&2
    exit 1
  fi
fi

# 9. Build the prompt: root CLAUDE.md → stage CONTEXT → workspace CLAUDE.md (if scoped).
# Only stages that invoke claude need a prompt.
PROMPT_FILE="$RUN_DIR/prompt.md"
if (( NEEDS_CLAUDE )); then
  {
    cat "$ULTRON_ROOT/CLAUDE.md"
    echo; echo "---"; echo
    if [[ "$STAGE" == "ingest-source" ]]; then
      cat "$ULTRON_ROOT/_shell/stages/ingest/$SOURCE/CONTEXT.md"
    else
      cat "$ULTRON_ROOT/_shell/stages/${STAGE}/CONTEXT.md"
    fi
    echo; echo "---"; echo
    if [[ -n "$WORKSPACE" && -f "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md" ]]; then
      cat "$ULTRON_ROOT/workspaces/$WORKSPACE/CLAUDE.md"
      echo; echo "---"; echo
    fi
    echo "RUN_ID: $RUN_ID"
    echo "WORKSPACE: ${WORKSPACE:-<cross-workspace>}"
    [[ -n "$SOURCE" ]] && echo "SOURCE: $SOURCE"
    [[ -n "$ACCOUNT" ]] && echo "ACCOUNT: $ACCOUNT"
  } > "$PROMPT_FILE"
fi

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

# Records a helper failure into EC, preserving the FIRST non-zero exit so a
# late-stage success can't mask an earlier crash. Stage helpers in lint/audit
# previously used `|| true` which silently dropped failures off the cron ledger.
record_failure() {
  local rc=$?
  (( EC == 0 )) && EC=$rc
  echo "[stage] helper failed (exit=$rc): $*" >&2
}

case "$STAGE" in
  ingest-source)
    # Per (source, account) ingest. Dispatches to the source's robot.
    ROBOT="$ULTRON_ROOT/_shell/bin/ingest-${SOURCE}.py"
    if [[ ! -x "$ROBOT" ]]; then
      echo "ingest-source: no robot at $ROBOT" >&2
      exit 2
    fi
    python3 "$ROBOT" --account "$ACCOUNT" --run-id "$RUN_ID" \
      > "$RUN_DIR/output/ingest-${SOURCE}.log" 2>&1 || EC=$?
    ;;
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
      --output "$RUN_DIR/output/check-routes.txt" || record_failure check-routes
    "$ULTRON_ROOT/_shell/bin/build-backlinks.py" --dry-run --workspace "$WORKSPACE" \
      > "$RUN_DIR/output/backlinks.txt" 2>&1 || record_failure build-backlinks
    claude_invoke \
      "$ULTRON_ROOT/workspaces/$WORKSPACE/agents/lint-agent.md" \
      "$RUN_DIR/output/result.json" \
      "$RUN_DIR/output/stderr.log" || record_failure lint-agent
    ;;
  audit)
    "$ULTRON_ROOT/_shell/bin/build-backlinks.py" \
      > "$RUN_DIR/output/backlinks.txt" 2>&1 || record_failure build-backlinks
    "$ULTRON_ROOT/_shell/bin/graphify-run.sh" \
      > "$RUN_DIR/output/graphify.log" 2>&1 || record_failure graphify-run
    "$ULTRON_ROOT/_shell/bin/audit-system-health.sh" \
      > "$RUN_DIR/output/system-health.md" 2>&1 || record_failure audit-system-health
    "$ULTRON_ROOT/.venv/bin/python3" "$ULTRON_ROOT/_shell/bin/find-cross-workspace-slugs.py" \
      > "$RUN_DIR/output/cross-workspace-slugs.log" 2>&1 || record_failure find-cross-workspace-slugs
    "$ULTRON_ROOT/.venv/bin/python3" "$ULTRON_ROOT/_shell/bin/generate-candidate-edges.py" \
      > "$RUN_DIR/output/candidate-edges.log" 2>&1 || record_failure generate-candidate-edges
    claude_invoke \
      "$ULTRON_ROOT/_shell/agents/audit-agent.md" \
      "$RUN_DIR/output/result.json" \
      "$RUN_DIR/output/stderr.log" || record_failure audit-agent
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
  weekly-review)
    # 1. Build the structured packet first.
    python3 "$ULTRON_ROOT/_shell/bin/build-weekly-packet.py" \
      > "$RUN_DIR/output/packet.log" 2>&1 || true
    # 2. Hand to Claude for prose synthesis on top.
    claude_invoke "" "$RUN_DIR/output/result.json" "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
  query)
    claude_invoke "" "$RUN_DIR/output/result.json" "$RUN_DIR/output/stderr.log" || EC=$?
    ;;
  apple-contacts-sync)
    "$ULTRON_ROOT/.venv/bin/python3" "$ULTRON_ROOT/_shell/skills/contacts-sync/scripts/sync.py" \
      > "$RUN_DIR/output/contacts-sync.log" 2>&1 || EC=$?
    ;;
  synthesize-voice-profiles)
    # Refresh voice_profile + conversation_summary on stale entity stubs.
    # Default --limit 20 keeps quota usage bounded; bump in schedule.yaml if needed.
    python3 "$ULTRON_ROOT/_shell/bin/synthesize-voice-profiles.py" \
      --limit "${VOICE_PROFILE_LIMIT:-20}" \
      > "$RUN_DIR/output/synthesize-voice-profiles.log" 2>&1 || EC=$?
    ;;
  rental-cycle)
    # Owner-side rental-manager full cycle: ingest → auto-book → contextual-send → application-notifier.
    # All gated by ZRM_DRY_RUN=1 if you want a no-mutate run.
    node "$ULTRON_ROOT/workspaces/rental-manager/playbooks/zillow-rental-manager/scripts/cron-cycle.mjs" \
      > "$RUN_DIR/output/rental-cycle.log" 2>&1 || EC=$?
    ;;
  podcast-outreach)
    # Eclipse podcast licensing outreach: scan-replies → discover (if low) → send.
    # Defaults to LIVE; pass DRY_RUN=1 in the env to force dry-run.
    node "$ULTRON_ROOT/_shell/skills/podcast-outreach/scripts/cron-cycle.mjs" \
      > "$RUN_DIR/output/podcast-outreach.log" 2>&1 || EC=$?
    ;;
  ledger-compact)
    python3 "$ULTRON_ROOT/_shell/bin/compact-ledger.py" \
      > "$RUN_DIR/output/compact-ledger.log" 2>&1 || EC=$?
    ;;
  auditor-deadman)
    # Watchdog-of-the-watchdog: pages directly via iMessage if cron-auditor's
    # state.json hasn't been updated within MAX_AUDITOR_LAG_HOURS. Wrapped via
    # cron-runner so the auditor itself sees deadman entries in the ledger -
    # both mutually monitor through different mechanisms.
    "$ULTRON_ROOT/.venv/bin/python3" "$ULTRON_ROOT/_shell/bin/auditor-deadman.py" \
      > "$RUN_DIR/output/auditor-deadman.log" 2>&1 || EC=$?
    ;;
  graphify-supermerge)
    bash "$ULTRON_ROOT/_shell/bin/graphify-run.sh" \
      > "$RUN_DIR/output/graphify-supermerge.log" 2>&1 || EC=$?
    ;;
  granola-reconcile)
    python3 "$ULTRON_ROOT/_shell/bin/ingest-granola.py" \
      --account adithya@outerscope.xyz --reset-cursor --run-id "$RUN_ID" \
      > "$RUN_DIR/output/granola-reconcile.log" 2>&1 || EC=$?
    ;;
  graphify)
    # Per-workspace Tier-1 maintenance. Re-extracts changed files into the
    # existing graph at workspaces/<ws>/graphify-out/graph.json.
    #
    # Initial graph creation requires LLM orchestration via /graphify in
    # Claude Code. This stage only handles incremental updates — if no graph
    # exists yet, write a placeholder and exit 0 so launchd doesn't keep
    # retrying.
    GRAPH_DIR="$ULTRON_ROOT/workspaces/$WORKSPACE/graphify-out"
    GRAPH_FILE="$GRAPH_DIR/graph.json"
    OUT_LOG="$RUN_DIR/output/graphify.log"
    GRAPHIFY_BIN="$(command -v graphify || true)"
    if [[ ! -f "$GRAPH_FILE" ]]; then
      echo "graphify: no graph at $GRAPH_FILE — run /graphify workspaces/$WORKSPACE/wiki interactively to bootstrap" > "$OUT_LOG"
      EC=0
    elif [[ -z "$GRAPHIFY_BIN" ]]; then
      echo "graphify: CLI not on PATH ($PATH)" > "$OUT_LOG"
      EC=0
    else
      # Subshell so cd doesn't leak; capture exit explicitly because
      # `graphify update` exits non-zero when the wiki has no code files
      # to re-extract (which is the normal state for a markdown wiki).
      set +e
      ( cd "$ULTRON_ROOT/workspaces/$WORKSPACE" && "$GRAPHIFY_BIN" update wiki ) > "$OUT_LOG" 2>&1
      gxc=$?
      set -e
      # Treat "no code files" as success — that's expected for markdown wikis.
      if (( gxc != 0 )) && grep -q "No code files found" "$OUT_LOG" 2>/dev/null; then
        echo "graphify: no code files (markdown-only wiki); update is a no-op." >> "$OUT_LOG"
        EC=0
      else
        EC=$gxc
      fi
    fi
    ;;
esac

echo "$(date -u +%FT%TZ) | $RUN_ID | exit=$EC" >> "$ULTRON_ROOT/_logs/dispatcher.log"
exit $EC
