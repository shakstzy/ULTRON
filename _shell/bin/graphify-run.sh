#!/usr/bin/env bash
# graphify-run.sh — cross-workspace graph build using the safishamsi/graphify CLI.
#
# Adapter notes:
#   The upstream CLI does NOT expose `graphify build --root --workspace-aware`
#   as the original spec assumed. Real surface (v5):
#     - `graphify <path> [flags]` runs only via the `/graphify` skill inside
#       Claude Code; it is not a plain bash entrypoint.
#     - The Python CLI exposes post-build subcommands: `query`, `path`,
#       `explain`, `add`, `watch`, `update`, `cluster-only`, `merge-graphs`, ...
#     - Outputs land in `./graphify-out/` of the cwd at build time.
#
# Strategy (v1):
#   This script ONLY merges graphs that already exist at
#   `workspaces/<ws>/graphify-out/graph.json`. It does NOT build per-workspace
#   graphs itself, because the upstream graphify v5 build path is driven by
#   Claude Code (`/graphify <path>`) and not by a plain bash entrypoint.
#
#   To build a per-workspace graph, run `/graphify workspaces/<ws>/wiki` from
#   inside Claude Code while ULTRON is open. After per-workspace graphs exist,
#   re-run this script (manually or via the audit stage) to merge them into
#   `_graphify/GRAPH.json` and emit `_graphify/GRAPH_REPORT.md`.
#
# This script is best-effort. If `graphify` is not installed, it writes a
# placeholder report and exits 0 (audit must not block on graphify).
set -euo pipefail

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
RUN_DIR="$ULTRON_ROOT/_graphify/runs/$(date +%Y-%m-%d)"
mkdir -p "$RUN_DIR" "$ULTRON_ROOT/_graphify"

if ! command -v graphify >/dev/null 2>&1; then
  cat > "$ULTRON_ROOT/_graphify/GRAPH_REPORT.md" <<'EOF'
# Graphify Report — not generated

`graphify` CLI is not installed in PATH.

Install:
```
uv tool install graphifyy && graphify install
```

Then re-run `_shell/bin/graphify-run.sh`. Audit will skip the
"Graphify surprises" check until then.
EOF
  echo "graphify: not installed; placeholder report written" >&2
  exit 0
fi

# Iterate workspaces with wiki/ content.
PER_WS_GRAPHS=()
for ws_dir in "$ULTRON_ROOT/workspaces"/*/; do
  ws_name="$(basename "$ws_dir")"
  [[ "$ws_name" == _* ]] && continue
  wiki_dir="$ws_dir/wiki"
  [[ -d "$wiki_dir" ]] || continue
  # Skip workspaces with no wiki content.
  if [[ -z "$(find "$wiki_dir" -name '*.md' -print -quit)" ]]; then
    continue
  fi

  ws_graph="$ws_dir/graphify-out/graph.json"
  if [[ -f "$ws_graph" ]]; then
    PER_WS_GRAPHS+=("$ws_graph")
  fi
done

if (( ${#PER_WS_GRAPHS[@]} == 0 )); then
  cat > "$ULTRON_ROOT/_graphify/GRAPH_REPORT.md" <<'EOF'
# Graphify Report — no per-workspace graphs found

No `workspaces/<ws>/graphify-out/graph.json` files exist yet.

To build per-workspace graphs, open ULTRON in Claude Code and run:
```
/graphify workspaces/<ws>/wiki
```
for each workspace. Then re-run this script to merge.
EOF
  echo "graphify: no per-workspace graphs; placeholder report written" >&2
  exit 0
fi

# Merge.
graphify merge-graphs "${PER_WS_GRAPHS[@]}" \
  --out "$ULTRON_ROOT/_graphify/GRAPH.json" \
  > "$RUN_DIR/merge.log" 2>&1 || {
    echo "graphify merge-graphs failed; see $RUN_DIR/merge.log" >&2
    exit 0
  }

# Generate the cross-workspace report. Upstream does not produce a workspace-
# aware report directly; we emit a thin index pointing to the per-workspace
# reports plus the merged graph.
{
  echo "# Graphify Cross-Workspace Report"
  echo
  echo "Generated $(date -u +%FT%TZ)"
  echo
  echo "## Per-workspace graphs merged"
  echo
  for g in "${PER_WS_GRAPHS[@]}"; do
    ws="$(basename "$(dirname "$(dirname "$g")")")"
    echo "- \`workspaces/$ws/graphify-out/graph.json\`"
  done
  echo
  echo "## Merged graph"
  echo
  echo "\`_graphify/GRAPH.json\`"
  echo
  echo "## Per-workspace reports"
  echo
  for ws_dir in "$ULTRON_ROOT/workspaces"/*/; do
    ws_name="$(basename "$ws_dir")"
    [[ "$ws_name" == _* ]] && continue
    rpt="$ws_dir/graphify-out/GRAPH_REPORT.md"
    if [[ -f "$rpt" ]]; then
      echo "- [\`workspaces/$ws_name/graphify-out/GRAPH_REPORT.md\`](../workspaces/$ws_name/graphify-out/GRAPH_REPORT.md)"
    fi
  done
} > "$ULTRON_ROOT/_graphify/GRAPH_REPORT.md"

echo "graphify: $(date -u +%FT%TZ) — see $ULTRON_ROOT/_graphify/GRAPH_REPORT.md"
