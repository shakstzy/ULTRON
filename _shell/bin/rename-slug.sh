#!/usr/bin/env bash
# rename-slug.sh — thin shim around rename-slug.py.
#
# Usage:
#   rename-slug.sh <old> <new> [<type>] [<workspace>]
#
# Positional arguments preserved for backwards compatibility with the spec;
# the Python implementation is the canonical version.
set -euo pipefail

OLD="${1:-}"
NEW="${2:-}"
TYPE="${3:-}"
WS="${4:-}"

if [[ -z "$OLD" || -z "$NEW" ]]; then
  echo "usage: rename-slug.sh <old> <new> [<type>] [<workspace>]" >&2
  exit 2
fi

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"

args=("$OLD" "$NEW")
[[ -n "$TYPE" ]] && args+=("--type" "$TYPE")
[[ -n "$WS"   ]] && args+=("--workspace" "$WS")

exec python3 "$ULTRON_ROOT/_shell/bin/rename-slug.py" "${args[@]}"
