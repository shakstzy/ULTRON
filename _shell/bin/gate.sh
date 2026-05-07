#!/usr/bin/env bash
# gate.sh — HITL gate functions for ULTRON.
#
# Spec: _shell/docs/HITL-gates.md
# Usage:
#   source _shell/bin/gate.sh
#   gate_confirm   "<action>" || exit 1
#   gate_send      "channel:<chan> length:<n>" || exit 1
#   gate_publish   "platform:<plat> audience:<n>" || exit 1
#   gate_launch_ad "platform:<plat> budget:$<n>" || exit 1
#   gate_load      "plist:<name>" || exit 1
#
# Approval mechanism:
#   1. Env override: ULTRON_GATE_<TOKEN>=approved (Claude agent sets this after
#      Adithya types the token in chat). Single-shot — function unsets it after
#      consumption so a stale env does not approve the next call.
#   2. Interactive stdin: if a TTY is attached, prompt and read the literal token.
#   3. Otherwise: reject with stderr message; caller exits 1.

set -u

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"

_gate_log() {
  local token="$1" outcome="$2" msg="$3"
  local ts
  ts="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  mkdir -p "$ULTRON_ROOT/_logs"
  printf '%s | %s | %s | %s\n' "$ts" "$token" "$outcome" "$msg" \
    >> "$ULTRON_ROOT/_logs/gates.log"
}

_gate_check() {
  local token="$1" msg="$2"
  local env_var="ULTRON_GATE_${token//-/_}"

  printf 'GATE: %s required\n  Action: %s\n' "$token" "$msg" >&2

  # Env override (single-shot)
  if [[ "${!env_var:-}" == "approved" ]]; then
    unset "$env_var"
    _gate_log "$token" "approved-via-env" "$msg"
    return 0
  fi

  # Interactive
  if [[ -t 0 ]]; then
    printf '  Type the token to confirm: ' >&2
    local input=""
    read -r input
    if [[ "$input" == "$token" ]]; then
      _gate_log "$token" "approved-interactive" "$msg"
      return 0
    fi
    _gate_log "$token" "rejected-interactive" "$msg"
    printf '  GATE rejected: input did not match %s\n' "$token" >&2
    return 1
  fi

  # Non-interactive without env approval
  _gate_log "$token" "rejected-no-tty" "$msg"
  printf '  GATE rejected: non-interactive context, no env approval\n' >&2
  return 1
}

gate_confirm()   { _gate_check "CONFIRM"   "${1:-(no description)}"; }
gate_send()      { _gate_check "SEND"      "${1:-(no description)}"; }
gate_publish()   { _gate_check "PUBLISH"   "${1:-(no description)}"; }
gate_launch_ad() { _gate_check "LAUNCH-AD" "${1:-(no description)}"; }
gate_load()      { _gate_check "load"      "${1:-(no description)}"; }

# If invoked directly (not sourced), run a self-test.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "gate.sh self-test (non-interactive, no env): all gates should reject"
  for fn in gate_confirm gate_send gate_publish gate_launch_ad gate_load; do
    if "$fn" "self-test from $0" </dev/null 2>/dev/null; then
      echo "FAIL: $fn returned 0"
      exit 1
    fi
  done
  echo "PASS: all gates rejected in non-interactive context"
fi
