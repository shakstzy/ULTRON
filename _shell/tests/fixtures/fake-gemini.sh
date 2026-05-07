#!/usr/bin/env bash
# Fake `gemini` CLI for tests. Emits "envcheck:" lines for each tracked env var
# and returns a canned description per the BEHAVIOR file in $HOME/.gemini/.
#
# BEHAVIOR file is JSON: {"mode": "ok|rate_limit|refusal|fail|empty", "desc": "..."}.
# Default mode is "ok" with desc derived from $HOME basename so tests can verify
# which account ran the call.
#
# Also writes a per-call audit line to $FAKE_GEMINI_AUDIT (if set) — one line
# per invocation: <epoch_ns> <home_basename> <args>

set -u

audit_line() {
    if [[ -n "${FAKE_GEMINI_AUDIT:-}" ]]; then
        echo "$(date +%s%N) $(basename "$HOME") $*" >> "$FAKE_GEMINI_AUDIT"
    fi
}

audit_line "$@"

# Env probes — visible in stdout for env-passthrough tests
echo "envcheck:HOME=$HOME"
echo "envcheck:GEMINI_CLI_HOME=${GEMINI_CLI_HOME:-UNSET}"
echo "envcheck:GEMINI_FORCE_FILE_STORAGE=${GEMINI_FORCE_FILE_STORAGE:-UNSET}"
echo "envcheck:GEMINI_CLI_TRUST_WORKSPACE=${GEMINI_CLI_TRUST_WORKSPACE:-UNSET}"
echo "envcheck:GEMINI_API_KEY=${GEMINI_API_KEY:-UNSET}"
echo "envcheck:GOOGLE_API_KEY=${GOOGLE_API_KEY:-UNSET}"
echo "envcheck:GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI:-UNSET}"
echo "envcheck:GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-UNSET}"
echo "envcheck:CLOUDSDK_CONFIG=${CLOUDSDK_CONFIG:-UNSET}"

BEHAVIOR_FILE="$HOME/.gemini/test-behavior.json"
MODE="ok"
DESC=""
if [[ -f "$BEHAVIOR_FILE" ]]; then
    MODE=$(grep -o '"mode"[[:space:]]*:[[:space:]]*"[^"]*"' "$BEHAVIOR_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
    DESC=$(grep -o '"desc"[[:space:]]*:[[:space:]]*"[^"]*"' "$BEHAVIOR_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
fi

case "$MODE" in
    rate_limit)
        echo "Error: 429 rate limit exceeded for this user" >&2
        exit 1
        ;;
    refusal)
        echo "I cannot access that file path."
        exit 0
        ;;
    fail)
        echo "Some unrelated error" >&2
        exit 2
        ;;
    empty)
        exit 0
        ;;
    *)
        if [[ -z "$DESC" ]]; then
            DESC="OK from $(basename "$HOME")"
        fi
        echo "$DESC"
        exit 0
        ;;
esac
