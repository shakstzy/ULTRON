#!/usr/bin/env python3
"""Daily ULTRON cron digest — sends an iMessage summary of today's runs.

Reads cron-ledger.jsonl, scopes to today (local), summarizes:
  - total runs, successes, failures, total runtime
  - chronic offenders (jobs with >=3 failures today)
  - stale locks cleaned by the auditor today (parsed from today's audit reports)
"""

import datetime
import json
import pathlib
import re
import subprocess
import sys

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
IMESSAGE_SEND = "/Users/shakstzy/.claude/skills/imessage/send.sh"

# Generous bound: 218 jobs × ~10 runs/day × ~500 bytes/row ≈ 1MB/day. 8MB tail
# easily covers today even with bursty days. Keeps daily digest O(constant).
LEDGER_TAIL_BYTES = 8 * 1024 * 1024


def _ok(r: dict) -> bool:
    """True if the run succeeded. Older ledger rows pre-date the `success`
    field — fall back to exit_code==0 so historical rows don't read as failed."""
    return r.get("success", r.get("exit_code") == 0)


def main():
    try:
        cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"[digest] config load failed: {e}\n")
        sys.exit(1)
    phone = cfg.get("operator_phone")
    if not phone:
        sys.stderr.write("[digest] config missing operator_phone; nothing to send\n")
        sys.exit(1)
    now = datetime.datetime.now().astimezone()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    ledger_path = pathlib.Path(cfg["ledger_path"])
    runs = []
    if ledger_path.exists():
        size = ledger_path.stat().st_size
        seek_to = max(0, size - LEDGER_TAIL_BYTES)
        with open(ledger_path, "rb") as f:
            f.seek(seek_to)
            if seek_to > 0:
                f.readline()  # discard partial first line
            for raw in f:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    start = datetime.datetime.fromisoformat(r["start"])
                except Exception:
                    continue
                if start >= day_start:
                    runs.append(r)

    body_lines = [f"ULTRON cron · {now:%a %b %d}"]

    if not runs:
        body_lines.append("No runs today.")
    else:
        successes = sum(1 for r in runs if _ok(r))
        failures = len(runs) - successes
        total_runtime_h = sum(r.get("duration_ms", 0) for r in runs) / 1000.0 / 3600.0
        by_label: dict[str, dict] = {}
        for r in runs:
            slot = by_label.setdefault(r["label"], {"runs": 0, "fails": 0})
            slot["runs"] += 1
            if not _ok(r):
                slot["fails"] += 1

        body_lines.append(
            f"✓ {successes}/{len(runs)} runs · {len(by_label)} jobs · {total_runtime_h:.1f}h runtime"
        )
        if failures:
            body_lines.append(f"✗ {failures} failures")

        chronic = sorted(
            (label.replace("com.adithya.ultron.", ""), s["fails"], s["runs"])
            for label, s in by_label.items()
            if s["fails"] >= 3
        )
        for label, fails, total in chronic:
            body_lines.append(f"⚠ {label}: {fails}/{total} failed")

    today_report = pathlib.Path(cfg["audit_report_dir"]) / f"cron-audit-{now:%Y-%m-%d}.md"
    if today_report.exists():
        text = today_report.read_text()
        m = re.search(r"(\d+) stale lock\(s\) cleaned", text)
        if m and int(m.group(1)) > 0:
            body_lines.append(f"🔧 {m.group(1)} stale locks cleaned today")

    body = "\n".join(body_lines)
    res = subprocess.run(
        [IMESSAGE_SEND, "--to", phone, "--text", body],
        capture_output=True, text=True, timeout=30,
    )
    if res.returncode != 0:
        sys.stderr.write(f"[digest] iMessage send failed: {res.stderr}\n")
        sys.exit(1)
    print(f"[digest] sent · runs={len(runs)}")


if __name__ == "__main__":
    main()
