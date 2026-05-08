#!/usr/bin/env python3
"""Cron job runner: executes a command, captures result, logs to ledger and Google Calendar.

Usage:
    cron-runner.py <label> -- <cmd> [args...]

Wraps a launchd job. Inherits stdout/stderr from launchd's redirected fds (real-time
logging, no memory buffering, no SIGKILL data loss). Captures exit code + duration +
stderr-tail-from-disk. Appends a JSONL row to the ledger (file-locked) and posts a
colored event to the ULTRON Crons Google Calendar. Calendar/ledger failures never fail
the underlying job.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import pathlib
import subprocess
import sys
import time

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
GOG = "/Users/shakstzy/.local/bin/gog"
LOG_DIR = pathlib.Path("/Users/shakstzy/ULTRON/_logs")
STDERR_TAIL_LIMIT = 1500


def file_size(path: pathlib.Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def read_tail(path: pathlib.Path, max_bytes: int) -> str:
    """Read up to `max_bytes` from end of file as text. Empty if missing.

    Bounded read protects against OOM when a job emits hundreds of MB of
    stderr (we only ever surface the tail in the calendar event anyway)."""
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return ""
    try:
        with open(path, "rb") as f:
            f.seek(max(0, size - max_bytes))
            return f.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


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

    err_log = LOG_DIR / f"{label}.err.log"
    out_log = LOG_DIR / f"{label}.out.log"
    err_offset = file_size(err_log)
    out_offset = file_size(out_log)

    start_dt = datetime.datetime.now().astimezone()
    start_ts = time.monotonic()

    # Inherit stdout/stderr — launchd already redirected them to .out/.err log files.
    # Real-time logging, no buffering, no OOM, no data loss on SIGKILL mid-run.
    proc = subprocess.run(cmd)

    # monotonic for duration so an NTP step backwards mid-run can't produce a
    # negative duration_ms in the ledger.
    end_ts = time.monotonic()
    end_dt = datetime.datetime.now().astimezone()
    duration_ms = int((end_ts - start_ts) * 1000)

    # Byte deltas — file_size after vs offset captured at start. Cheap, no read.
    err_delta = max(0, file_size(err_log) - err_offset)
    out_delta = max(0, file_size(out_log) - out_offset)
    # Tail-read only what we actually surface, bounded to STDERR_TAIL_LIMIT.
    stderr_tail = read_tail(err_log, STDERR_TAIL_LIMIT) if err_delta else ""
    success = proc.returncode == 0

    row = {
        "label": label,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "duration_ms": duration_ms,
        "exit_code": proc.returncode,
        "success": success,
        "cmd": cmd,
        "stderr_bytes": err_delta,
        "stdout_bytes": out_delta,
    }
    try:
        with open(cfg["ledger_path"], "a") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(json.dumps(row) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
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
