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


def main():
    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    now = datetime.datetime.now().astimezone()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    ledger_path = pathlib.Path(cfg["ledger_path"])
    runs = []
    if ledger_path.exists():
        with open(ledger_path) as f:
            for line in f:
                line = line.strip()
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
        successes = sum(1 for r in runs if r.get("success"))
        failures = len(runs) - successes
        total_runtime_h = sum(r.get("duration_ms", 0) for r in runs) / 1000.0 / 3600.0
        by_label: dict[str, dict] = {}
        for r in runs:
            slot = by_label.setdefault(r["label"], {"runs": 0, "fails": 0})
            slot["runs"] += 1
            if not r.get("success"):
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
        [IMESSAGE_SEND, "--to", cfg["operator_phone"], "--text", body],
        capture_output=True, text=True, timeout=30,
    )
    if res.returncode != 0:
        sys.stderr.write(f"[digest] iMessage send failed: {res.stderr}\n")
        sys.exit(1)
    print(f"[digest] sent · runs={len(runs)}")


if __name__ == "__main__":
    main()
