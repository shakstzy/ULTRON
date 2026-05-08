#!/usr/bin/env python3
"""auditor-deadman — the watchdog that watches the watchdog.

cron-auditor.py is the only thing that pages Adithya when scheduled jobs go
stale. If the auditor itself crashes, the entire alerting chain goes silent.

This dead-man reads `_logs/cron-audit-state.json` mtime and pages directly via
iMessage if the auditor hasn't successfully completed in MAX_AUDITOR_LAG_HOURS.

It is intentionally tiny and stdlib-only to minimize surfaces of its own.

Self-state: `_logs/auditor-deadman-state.json` tracks last_alert_at to avoid
spamming during a multi-cycle outage. Re-pages every REPAGE_INTERVAL_HOURS.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import sys

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
SELF_STATE_PATH = "/Users/shakstzy/ULTRON/_logs/auditor-deadman-state.json"
IMESSAGE_SEND = "/Users/shakstzy/.claude/skills/imessage/send.sh"

# Auditor runs hourly at :15. Anything past 1.5h means it missed at least one cycle.
MAX_AUDITOR_LAG_HOURS = 1.5
# After alerting, don't re-page until the outage exceeds this window.
REPAGE_INTERVAL_HOURS = 6.0


def send_imessage(phone: str, body: str) -> bool:
    try:
        res = subprocess.run(
            [IMESSAGE_SEND, "--to", phone, "--text", body],
            capture_output=True, text=True, timeout=30,
        )
        if res.returncode != 0:
            sys.stderr.write(
                f"[deadman] iMessage send failed (rc={res.returncode}): {res.stderr.strip()}\n"
            )
        return res.returncode == 0
    except Exception as e:
        sys.stderr.write(f"[deadman] iMessage send raised: {e}\n")
        return False


def load_self_state() -> dict:
    p = pathlib.Path(SELF_STATE_PATH)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_self_state(state: dict) -> None:
    p = pathlib.Path(SELF_STATE_PATH)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, p)


def main() -> int:
    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    state_path = pathlib.Path(cfg["audit_state_path"])
    phone = cfg.get("operator_phone")
    now = datetime.datetime.now().astimezone()

    if not state_path.exists():
        # Auditor has never run successfully (cold install or state was deleted).
        # We can't distinguish those cases, but either way Adithya needs to know.
        msg = (
            f"⚠ auditor-deadman: cron-auditor state.json does not exist "
            f"({state_path}). Auditor may have never completed."
        )
        sys.stderr.write(msg + "\n")
        if phone:
            send_imessage(phone, msg)
        return 1

    mtime = datetime.datetime.fromtimestamp(state_path.stat().st_mtime).astimezone()
    age_hours = (now - mtime).total_seconds() / 3600.0

    self_state = load_self_state()
    last_alert_at = self_state.get("last_alert_at")
    last_alert_dt = (
        datetime.datetime.fromisoformat(last_alert_at).astimezone()
        if last_alert_at else None
    )

    healthy = age_hours <= MAX_AUDITOR_LAG_HOURS

    if healthy:
        if last_alert_dt is not None:
            # Auditor recovered.
            if phone:
                send_imessage(
                    phone,
                    f"✓ auditor-deadman: cron-auditor recovered "
                    f"(state.json {age_hours:.1f}h old).",
                )
            self_state.pop("last_alert_at", None)
            save_self_state(self_state)
        print(f"[deadman] healthy state.json={age_hours:.2f}h_old")
        return 0

    # Stale auditor. Page if we haven't paged in REPAGE_INTERVAL_HOURS.
    should_page = (
        last_alert_dt is None
        or (now - last_alert_dt).total_seconds() / 3600.0 >= REPAGE_INTERVAL_HOURS
    )
    print(f"[deadman] stale state.json={age_hours:.2f}h_old should_page={should_page}")

    if should_page and phone:
        msg = (
            f"⚠ auditor-deadman: cron-auditor has not run in {age_hours:.1f}h "
            f"(threshold {MAX_AUDITOR_LAG_HOURS}h). Cron alerting is BLIND. "
            f"Check _logs/com.adithya.ultron.cron-auditor.err.log."
        )
        if send_imessage(phone, msg):
            self_state["last_alert_at"] = now.isoformat()
            save_self_state(self_state)

    return 1  # always non-zero on stale so cron-ledger records the unhealthy state


if __name__ == "__main__":
    sys.exit(main())
