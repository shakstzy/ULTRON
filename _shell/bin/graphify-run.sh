#!/usr/bin/env bash
# graphify-run.sh — Tier 2 (super-merge) for ULTRON's two-tier Graphify model.
#
# Tier 1 (per-workspace) is run from inside Claude Code:
#   /graphify workspaces/<ws>/wiki
# It produces `workspaces/<ws>/graphify-out/{graph.json, GRAPH_REPORT.md}`.
#
# Tier 2 (this script) merges those per-workspace graph.json files into a
# cross-workspace `_graphify/super/{graph.json, GRAPH_REPORT.md}`. The audit
# stage consumes Tier 2.
#
# Workspaces with `exclude_from_super_graphify: true` in their CLAUDE.md
# frontmatter are skipped.
#
# Best-effort. If `graphify` is not installed or no Tier-1 graphs exist, the
# script writes a placeholder report and exits 0 (audit must not block on this).
set -euo pipefail

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
SUPER_DIR="$ULTRON_ROOT/_graphify/super"
RUN_DIR="$ULTRON_ROOT/_graphify/runs/$(date +%Y-%m-%d)"
mkdir -p "$SUPER_DIR" "$RUN_DIR"

# `graphify` is installed via `uv tool install` to ~/.local/bin, which is
# not on launchd's default PATH. Prepend it so this script works under
# both cron and interactive shells.
export PATH="$HOME/.local/bin:$PATH"

if ! command -v graphify >/dev/null 2>&1; then
  cat > "$SUPER_DIR/GRAPH_REPORT.md" <<'EOF'
# Super-Graph Report — graphify CLI not installed

`graphify` is not on PATH. Install:

```
uv tool install graphifyy && graphify install
```

Then run `/graphify workspaces/<ws>/wiki` from inside Claude Code per workspace,
and re-run this script to merge.
EOF
  echo "graphify: not installed; placeholder report written" >&2
  exit 0
fi

# Collect per-workspace Tier-1 graphs, honoring exclude_from_super_graphify.
GRAPHS=()
EXCLUDED=()
MISSING=()
for ws_dir in "$ULTRON_ROOT"/workspaces/*/; do
  ws="$(basename "$ws_dir")"
  [[ "$ws" == _* ]] && continue

  ws_claude="$ws_dir/CLAUDE.md"
  if [[ -f "$ws_claude" ]] && grep -q "^exclude_from_super_graphify: true" "$ws_claude" 2>/dev/null; then
    EXCLUDED+=("$ws")
    continue
  fi

  graph_file="$ws_dir/graphify-out/graph.json"
  if [[ -f "$graph_file" ]]; then
    GRAPHS+=("$graph_file")
  else
    MISSING+=("$ws")
  fi
done

if (( ${#GRAPHS[@]} == 0 )); then
  {
    echo "# Super-Graph Report — no per-workspace graphs found"
    echo
    echo "Tier-1 graphs (\`workspaces/<ws>/graphify-out/graph.json\`) do not exist for any workspace."
    echo
    echo "Build them by running \`/graphify workspaces/<ws>/wiki\` from inside Claude Code per workspace."
    if (( ${#MISSING[@]} > 0 )); then
      echo
      echo "## Missing per-workspace graphs"
      for w in "${MISSING[@]}"; do
        echo "- $w"
      done
    fi
    if (( ${#EXCLUDED[@]} > 0 )); then
      echo
      echo "## Excluded from super-graph"
      for w in "${EXCLUDED[@]}"; do
        echo "- $w"
      done
    fi
  } > "$SUPER_DIR/GRAPH_REPORT.md"
  echo "graphify: no per-workspace graphs to merge; placeholder report written"
  exit 0
fi

if (( ${#GRAPHS[@]} == 1 )); then
  cp "${GRAPHS[0]}" "$SUPER_DIR/graph.json"
  {
    echo "# Super-Graph Report — only one workspace has a Tier-1 graph"
    echo
    echo "Copied \`${GRAPHS[0]#$ULTRON_ROOT/}\` to \`_graphify/super/graph.json\` as-is."
    if (( ${#MISSING[@]} > 0 )); then
      echo; echo "## Missing per-workspace graphs"
      for w in "${MISSING[@]}"; do echo "- $w"; done
    fi
    if (( ${#EXCLUDED[@]} > 0 )); then
      echo; echo "## Excluded from super-graph"
      for w in "${EXCLUDED[@]}"; do echo "- $w"; done
    fi
  } > "$SUPER_DIR/GRAPH_REPORT.md"
  echo "graphify: only one Tier-1 graph; copied through to super/graph.json"
  exit 0
fi

# 2+ graphs: merge.
if ! graphify merge-graphs "${GRAPHS[@]}" --out "$SUPER_DIR/graph.json" \
      > "$RUN_DIR/merge.log" 2>&1; then
  echo "graphify merge-graphs failed; see $RUN_DIR/merge.log" >&2
  exit 0
fi

# Compose a thin index report.
{
  echo "# Super-Graph Report"
  echo
  echo "Generated $(date -u +%FT%TZ)"
  echo
  echo "## Per-workspace graphs merged (${#GRAPHS[@]})"
  echo
  for g in "${GRAPHS[@]}"; do
    rel="${g#$ULTRON_ROOT/}"
    ws="$(basename "$(dirname "$(dirname "$g")")")"
    echo "- \`$rel\` ($ws)"
  done
  echo
  echo "## Merged graph"
  echo
  echo "\`_graphify/super/graph.json\`"
  echo
  echo "## Per-workspace reports"
  echo
  for ws_dir in "$ULTRON_ROOT/workspaces"/*/; do
    ws="$(basename "$ws_dir")"
    [[ "$ws" == _* ]] && continue
    rpt="$ws_dir/graphify-out/GRAPH_REPORT.md"
    if [[ -f "$rpt" ]]; then
      rel_link="../workspaces/$ws/graphify-out/GRAPH_REPORT.md"
      echo "- [$ws]($rel_link)"
    fi
  done
  if (( ${#MISSING[@]} > 0 )); then
    echo
    echo "## Missing per-workspace graphs"
    for w in "${MISSING[@]}"; do echo "- $w"; done
  fi
  if (( ${#EXCLUDED[@]} > 0 )); then
    echo
    echo "## Excluded from super-graph"
    for w in "${EXCLUDED[@]}"; do echo "- $w"; done
  fi
} > "$SUPER_DIR/GRAPH_REPORT.md"

echo "graphify: merged ${#GRAPHS[@]} per-workspace graphs → $SUPER_DIR/graph.json"
