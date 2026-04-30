#!/usr/bin/env python3
"""
ingest-driver.py — orchestrate per-source ingest scripts for one workspace.

Reads `workspaces/<ws>/config/sources.yaml`, dispatches one subprocess per
source, isolates failures (one source failing does not abort siblings),
collects the new-raw file list, optionally invokes the workspace wiki agent.

Usage:
    ingest-driver.py <workspace> <run_id>
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("missing dep: pip install pyyaml\n")
    sys.exit(2)

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_sources_config(workspace: str) -> dict:
    cfg_path = ULTRON_ROOT / "workspaces" / workspace / "config" / "sources.yaml"
    if not cfg_path.exists():
        sys.stderr.write(f"no sources config: {cfg_path}\n")
        return {"workspace": workspace, "wiki": False, "sources": []}
    return yaml.safe_load(cfg_path.read_text()) or {}


def load_existing_raw_paths(workspace: str) -> set[str]:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "ingested.jsonl"
    if not log.exists():
        return set()
    out: set[str] = set()
    for line in log.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        rp = obj.get("raw_path")
        if rp:
            out.add(rp)
    return out


def append_log_line(workspace: str, line: str) -> None:
    log = ULTRON_ROOT / "workspaces" / workspace / "_meta" / "log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(line + "\n")


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ingest-driver.py <workspace> <run_id>\n")
        return 2

    workspace = sys.argv[1]
    run_id = sys.argv[2]

    cfg = load_sources_config(workspace)
    sources = cfg.get("sources", []) or []
    wiki_enabled = cfg.get("wiki", False)

    bin_dir = ULTRON_ROOT / "_shell" / "bin"
    run_dir = ULTRON_ROOT / "_shell" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input").mkdir(exist_ok=True)
    (run_dir / "output").mkdir(exist_ok=True)

    log_dir = ULTRON_ROOT / "_logs"
    log_dir.mkdir(exist_ok=True)

    raw_before = load_existing_raw_paths(workspace)

    for source in sources:
        source_id = source.get("id", "<unknown>")
        bin_name = source.get("bin")
        if not bin_name:
            stype = source.get("type", "")
            bin_name = f"ingest-{stype}.py"
        script = bin_dir / bin_name
        if not script.exists():
            sys.stderr.write(f"ingest-driver: missing script {script} for source {source_id}\n")
            continue

        out_log = log_dir / f"{workspace}-{source_id}.out.log"
        err_log = log_dir / f"{workspace}-{source_id}.err.log"

        sys.stderr.write(f"ingest-driver: running {bin_name} for {source_id}\n")
        try:
            with out_log.open("a") as out, err_log.open("a") as err:
                subprocess.run(
                    [sys.executable, str(script), workspace, run_id],
                    stdout=out, stderr=err, check=False,
                )
        except OSError as exc:
            sys.stderr.write(f"ingest-driver: {source_id} failed: {exc}\n")
            continue

    raw_after = load_existing_raw_paths(workspace)
    new_raw = sorted(raw_after - raw_before)

    new_raw_file = run_dir / "input" / "new-raw.txt"
    new_raw_file.write_text("\n".join(new_raw) + ("\n" if new_raw else ""))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    append_log_line(
        workspace,
        f"{ts} | ingest | new-raw={len(new_raw)} | run={run_id}",
    )

    if wiki_enabled and new_raw:
        # Hand off to the wiki agent — invoked by run-stage.sh's claude_invoke
        # in a follow-on call. For now we just stage the input list.
        sys.stderr.write(
            f"ingest-driver: {len(new_raw)} new raw files staged for wiki agent at "
            f"{new_raw_file}\n"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
