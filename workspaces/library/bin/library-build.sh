#!/usr/bin/env bash
# library-build.sh — run stages 02 → 03 → 04 in sequence over raw/books/.
#
# Capture (stage 01) is on-demand via bin/ingest-*.py. This orchestrator
# handles the deterministic + synthesis pipeline that runs over whatever's
# already in raw/.
#
# Usage:
#   library-build.sh                              # all stages on all books
#   library-build.sh --stage extract              # 02 only
#   library-build.sh --stage chapterize           # 03 only
#   library-build.sh --stage wiki                 # 04 only
#   library-build.sh --book clear-atomic-habits   # scope to one book
#   library-build.sh --force                      # re-run stages regardless of hash
#   library-build.sh --dry-run                    # report intended work, no writes
#
# Exit codes: 0 = clean, 1 = at least one stage reported failures, 2 = arg error.

set -euo pipefail

STAGE="all"
BOOK=""
AUTHOR=""
FORCE=""
DRY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)     STAGE="$2"; shift 2 ;;
    --book)      BOOK="$2"; shift 2 ;;
    --author)    AUTHOR="$2"; shift 2 ;;
    --force)     FORCE="--force"; shift ;;
    --dry-run)   DRY="--dry-run"; shift ;;
    -h|--help)
      sed -n '/^# library-build/,/^# Exit codes/p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *)
      echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$STAGE" in
  all|extract|chapterize|wiki) ;;
  *) echo "--stage must be one of: all | extract | chapterize | wiki" >&2; exit 2 ;;
esac

WS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$WS_ROOT/bin"

SCOPE=()
[[ -n "$BOOK" ]]   && SCOPE+=(--book "$BOOK")
[[ -n "$AUTHOR" ]] && SCOPE+=(--author "$AUTHOR")
[[ -n "$FORCE" ]]  && SCOPE+=("$FORCE")
[[ -n "$DRY" ]]    && SCOPE+=("$DRY")

run_stage() {
  local label="$1"; shift
  echo "=== stage: $label ==="
  if ! "$@"; then
    echo "  ! stage $label exited non-zero" >&2
    return 1
  fi
}

EXIT=0

if [[ "$STAGE" == "all" || "$STAGE" == "extract" ]]; then
  run_stage "02-extract" python3 "$BIN/stage-extract-book.py" "${SCOPE[@]+"${SCOPE[@]}"}" || EXIT=1
fi

if [[ "$STAGE" == "all" || "$STAGE" == "chapterize" ]]; then
  run_stage "03-chapterize" python3 "$BIN/stage-chapterize-book.py" "${SCOPE[@]+"${SCOPE[@]}"}" || EXIT=1
fi

if [[ "$STAGE" == "all" || "$STAGE" == "wiki" ]]; then
  # Stage 04 is currently the /graphify --wiki call. If/when stage-wiki-build.py
  # ships, swap the line below for that script.
  echo "=== stage: 04-wiki-build ==="
  echo "  → run from Claude session: /graphify --wiki workspaces/library"
  echo "  (stage-wiki-build.py is not yet shipped; see stages/04-wiki-build/CONTEXT.md)"
fi

exit "$EXIT"
