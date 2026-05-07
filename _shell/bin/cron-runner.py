#!/usr/bin/env python3
"""Cron job runner: executes a command, captures result, logs to ledger and Google Calendar.

Usage:
    cron-runner.py <label> -- <cmd> [args...]

Wraps a launchd job. Captures stdout/stderr (passthrough so launchd log paths still work),
exit code, duration. Appends a JSONL row to the ledger and posts a colored event to the
ULTRON Crons Google Calendar. Calendar/ledger failures never fail the underlying job.
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
import time

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
GOG = "/Users/shakstzy/.local/bin/gog"


def main():
    if len(sys.argv) < 4 or sys.argv[2] != "--":
        sys.stderr.write(f"usage: {sys.argv[0]} <label> -- <cmd> [args...]\n")
        sys.exit(2)

    label = sys.argv[1]
    cmd = sys.argv[3:]

    try:
        cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    except Exception as e:
        sys.stderr.write(f"[cron-runner] config load failed: {e}; running cmd unwrapped\n")
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)

    start_dt = datetime.datetime.now().astimezone()
    start_ts = time.time()

    proc = subprocess.run(cmd, capture_output=True, text=True)

    end_ts = time.time()
    end_dt = datetime.datetime.now().astimezone()
    duration_ms = int((end_ts - start_ts) * 1000)

    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)

    success = proc.returncode == 0
    stderr_tail = (proc.stderr or "")[-1500:]

    row = {
        "label": label,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "duration_ms": duration_ms,
        "exit_code": proc.returncode,
        "success": success,
        "cmd": cmd,
        "stderr_chars": len(proc.stderr or ""),
        "stdout_chars": len(proc.stdout or ""),
    }
    try:
        with open(cfg["ledger_path"], "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception as e:
        sys.stderr.write(f"[cron-runner] ledger write failed: {e}\n")

    short_label = label.replace("com.adithya.ultron.", "")
    mark = "✓" if success else "✗"
    duration_s = duration_ms / 1000.0
    if duration_s >= 60:
        dur_str = f" ({duration_s/60:.1f}m)"
    elif duration_s >= 1:
        dur_str = f" ({duration_s:.1f}s)"
    else:
        dur_str = f" ({duration_ms}ms)"
    title = f"{mark} {short_label}{dur_str}"
    color = cfg["color_success"] if success else cfg["color_failure"]

    desc_lines = [
        f"Job: {label}",
        f"Exit: {proc.returncode}",
        f"Duration: {duration_ms}ms",
        f"Started: {start_dt.isoformat()}",
        f"Cmd: {' '.join(cmd)}",
    ]
    if not success and stderr_tail.strip():
        desc_lines.append("")
        desc_lines.append("--- stderr tail ---")
        desc_lines.append(stderr_tail)
    description = "\n".join(desc_lines)

    cal_start = start_dt
    cal_end = end_dt if (end_dt - start_dt).total_seconds() >= 60 else (start_dt + datetime.timedelta(minutes=1))

    try:
        cal_args = [
            GOG, "-a", cfg["account"], "cal", "create", cfg["calendar_id"],
            "--summary", title,
            "--from", cal_start.isoformat(),
            "--to", cal_end.isoformat(),
            "--description", description,
            "--event-color", color,
            "--transparency", "transparent",
            "--private-prop", f"ultron_label={label}",
            "--private-prop", "ultron_kind=run",
            "--no-input",
            "--json",
        ]
        cal = subprocess.run(cal_args, capture_output=True, text=True, timeout=30)
        if cal.returncode != 0:
            sys.stderr.write(f"[cron-runner] calendar post failed (exit {cal.returncode}): {cal.stderr[:500]}\n")
    except Exception as e:
        sys.stderr.write(f"[cron-runner] calendar post error: {e}\n")

    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
