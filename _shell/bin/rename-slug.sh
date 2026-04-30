#!/usr/bin/env bash
# rename-slug.sh — atomically rename an entity slug across ULTRON.
#
# Usage:
#   rename-slug.sh <old> <new> [<type>] [<workspace>]
#
# If <type> is given AND <workspace> is given, moves
#   workspaces/<ws>/wiki/entities/<type>/<old>.md → <new>.md
# If <type> is given without <workspace>, moves the global stub:
#   _global/entities/<type>/<old>.md → <new>.md
#
# Then patches all `[[old]]`, `[[@old]]`, `[[ws:<any>/old]]` wikilinks across
# the appropriate scope, rebuilds backlinks, and runs check-routes.
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

if [[ -n "$WS" ]]; then
  scope_dir="$ULTRON_ROOT/workspaces/$WS"
else
  scope_dir="$ULTRON_ROOT"
fi

# 1. Move the canonical file(s)
if [[ -n "$TYPE" && -n "$WS" ]]; then
  src="$ULTRON_ROOT/workspaces/$WS/wiki/entities/$TYPE/$OLD.md"
  dst="$ULTRON_ROOT/workspaces/$WS/wiki/entities/$TYPE/$NEW.md"
  if [[ -f "$src" ]]; then
    mv "$src" "$dst"
    echo "moved: $src → $dst"
  fi
elif [[ -n "$TYPE" ]]; then
  src="$ULTRON_ROOT/_global/entities/$TYPE/$OLD.md"
  dst="$ULTRON_ROOT/_global/entities/$TYPE/$NEW.md"
  if [[ -f "$src" ]]; then
    mv "$src" "$dst"
    echo "moved: $src → $dst"
  fi
fi

# 2. Patch wikilinks across the scope. macOS sed (BSD) needs an explicit ''
# argument after -i; GNU sed does not. Detect and adapt.
if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(-i)
else
  SED_INPLACE=(-i '')
fi

# Use a NUL-delimited file list so paths with spaces work.
find "$scope_dir" -name "*.md" -not -path "*/_shell/runs/*" -print0 | \
  xargs -0 sed "${SED_INPLACE[@]}" \
    -e "s|\\[\\[${OLD}\\]\\]|[[${NEW}]]|g" \
    -e "s|\\[\\[@${OLD}\\]\\]|[[@${NEW}]]|g" \
    -e "s|\\[\\[ws:\\([^/]*\\)/${OLD}\\]\\]|[[ws:\\1/${NEW}]]|g"

# 3. Rebuild backlinks
"$ULTRON_ROOT/_shell/bin/build-backlinks.py"

# 4. Verify
if [[ -n "$WS" ]]; then
  "$ULTRON_ROOT/_shell/bin/check-routes.py" --workspace "$WS"
else
  "$ULTRON_ROOT/_shell/bin/check-routes.py"
fi
