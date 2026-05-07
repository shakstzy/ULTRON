#!/usr/bin/env python3
"""Hourly health auditor for ULTRON crons.

Reads the cron-ledger.jsonl, parses each currently-loaded plist's
StartCalendarInterval, and classifies every job as HEALTHY / STALE / BROKEN.

Self-heals:
  - Deletes /tmp/com.adithya.ultron.*.lock files older than 2h with no live
    process holding them (fixes the bumble "profile_locked" pattern).

Notifies (iMessage to operator_phone):
  - Sends a compact status digest only when at least one job's state changed
    since the last audit, debounced by _logs/cron-audit-state.json.

Writes:
  - _logs/cron-audit-<YYYY-MM-DD>.md — daily markdown report (overwritten per
    day, so each day has one rolling report).
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import pathlib
import plistlib
import subprocess
import sys

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
PLIST_DIR = "/Users/shakstzy/ULTRON/_shell/plists"
LEDGER = "/Users/shakstzy/ULTRON/_logs/cron-ledger.jsonl"
LOCK_GLOB = "/tmp/com.adithya.ultron.*.lock"
IMESSAGE_SEND = "/Users/shakstzy/.claude/skills/imessage/send.sh"

LOCK_STALE_HOURS = 2.0
BROKEN_CONSECUTIVE = 3
GRACE_HOURS = 1.0


def load_ledger(cutoff: datetime.datetime) -> tuple[dict, datetime.datetime | None]:
    """Returns (runs_by_label, oldest_ledger_start). The latter establishes the
    'cron-runner has been live since X' boundary used for cold-start grace."""
    runs_by_label: dict[str, list[dict]] = {}
    oldest: datetime.datetime | None = None
    if not pathlib.Path(LEDGER).exists():
        return runs_by_label, None
    with open(LEDGER) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                start = datetime.datetime.fromisoformat(r["start"])
            except Exception:
                continue
            if oldest is None or start < oldest:
                oldest = start
            if start < cutoff:
                continue
            runs_by_label.setdefault(r["label"], []).append(r)
    for runs in runs_by_label.values():
        runs.sort(key=lambda r: r["start"], reverse=True)
    return runs_by_label, oldest


def loaded_labels() -> set[str]:
    out = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    labels = set()
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2].startswith("com.adithya.ultron."):
            labels.add(parts[2])
    return labels


def parse_plist_jobs(loaded: set[str]) -> dict:
    jobs = {}
    for path in glob.glob(f"{PLIST_DIR}/com.adithya.ultron.*.plist"):
        with open(path, "rb") as f:
            p = plistlib.load(f)
        label = p.get("Label")
        if not label or label not in loaded:
            continue
        sci = p.get("StartCalendarInterval")
        if not sci:
            continue
        slots = sci if isinstance(sci, list) else [sci]
        jobs[label] = {"slots": [dict(s) for s in slots]}
    return jobs


def prev_occurrence(slot: dict, now: datetime.datetime) -> datetime.datetime:
    h = slot.get("Hour", 0)
    m = slot.get("Minute", 0)
    weekday = slot.get("Weekday")
    day = slot.get("Day")
    month = slot.get("Month")

    if weekday is not None:
        target_iso = (weekday - 1) % 7
        cur_iso = now.weekday()
        days_back = (cur_iso - target_iso) % 7
        candidate = (now - datetime.timedelta(days=days_back)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        if candidate > now:
            candidate -= datetime.timedelta(days=7)
        return candidate

    if month is not None and day is not None:
        try:
            candidate = now.replace(month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
        except ValueError:
            return now - datetime.timedelta(days=365)
        if candidate > now:
            candidate = candidate.replace(year=now.year - 1)
        return candidate

    if day is not None:
        try:
            candidate = now.replace(day=day, hour=h, minute=m, second=0, microsecond=0)
        except ValueError:
            return now - datetime.timedelta(days=30)
        if candidate > now:
            if now.month == 1:
                candidate = candidate.replace(year=now.year - 1, month=12)
            else:
                candidate = candidate.replace(month=now.month - 1)
        return candidate

    candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if candidate > now:
        candidate -= datetime.timedelta(days=1)
    return candidate


def classify(label: str, info: dict, runs: list[dict], now: datetime.datetime,
             ledger_start: datetime.datetime | None) -> dict:
    expected = max(prev_occurrence(s, now) for s in info["slots"])
    grace = datetime.timedelta(hours=GRACE_HOURS)
    hours_since_expected = (now - expected).total_seconds() / 3600.0

    last_run_start = None
    last_run_success = None
    if runs:
        last_run_start = datetime.datetime.fromisoformat(runs[0]["start"])
        last_run_success = runs[0].get("success", runs[0].get("exit_code") == 0)

    if last_run_start is not None and last_run_start >= expected - grace:
        last_n = runs[: BROKEN_CONSECUTIVE]
        if len(last_n) >= BROKEN_CONSECUTIVE and all(
            not r.get("success", r.get("exit_code") == 0) for r in last_n
        ):
            status = "BROKEN"
        else:
            status = "HEALTHY"
    elif ledger_start is not None and expected < ledger_start:
        status = "PRE_INSTALL"
    else:
        if hours_since_expected > GRACE_HOURS:
            status = "STALE"
        else:
            status = "WAITING"

    fail_count_24h = sum(
        1 for r in runs
        if datetime.datetime.fromisoformat(r["start"]) >= now - datetime.timedelta(hours=24)
        and not r.get("success", r.get("exit_code") == 0)
    )
    run_count_24h = sum(
        1 for r in runs
        if datetime.datetime.fromisoformat(r["start"]) >= now - datetime.timedelta(hours=24)
    )

    return {
        "status": status,
        "expected_last_fire": expected.isoformat(),
        "hours_since_expected": round(hours_since_expected, 1),
        "last_run_start": last_run_start.isoformat() if last_run_start else None,
        "last_run_success": last_run_success,
        "runs_24h": run_count_24h,
        "fails_24h": fail_count_24h,
    }


def cleanup_stale_locks(now: datetime.datetime) -> list[dict]:
    cleaned = []
    for lock in glob.glob(LOCK_GLOB):
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(lock)).astimezone()
        except OSError:
            continue
        age_hours = (now - mtime).total_seconds() / 3600.0
        if age_hours < LOCK_STALE_HOURS:
            continue
        try:
            res = subprocess.run(["lsof", lock], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                continue
        except Exception:
            pass
        try:
            os.unlink(lock)
            cleaned.append({"lock": os.path.basename(lock), "age_hours": round(age_hours, 1)})
        except OSError:
            pass
    return cleaned


def build_report(statuses: dict, cleaned_locks: list, now: datetime.datetime) -> str:
    counts = {"HEALTHY": 0, "WAITING": 0, "STALE": 0, "BROKEN": 0, "PRE_INSTALL": 0}
    for s in statuses.values():
        counts[s["status"]] = counts.get(s["status"], 0) + 1

    lines = [f"# ULTRON cron audit · {now.isoformat()}", ""]
    lines.append(f"**{counts['HEALTHY']} healthy** · {counts['WAITING']} waiting · "
                 f"{counts['PRE_INSTALL']} pre-install · "
                 f"**{counts['STALE']} stale** · **{counts['BROKEN']} broken** "
                 f"· {len(cleaned_locks)} stale lock(s) cleaned")
    lines.append("")

    flagged = sorted(
        ((label, s) for label, s in statuses.items() if s["status"] in ("STALE", "BROKEN")),
        key=lambda x: (x[1]["status"], -x[1]["hours_since_expected"]),
    )
    if flagged:
        lines.append("## Needs attention")
        lines.append("")
        lines.append("| Status | Job | Last fire expected | Last run | 24h runs (fails) |")
        lines.append("|---|---|---|---|---|")
        for label, s in flagged:
            short = label.replace("com.adithya.ultron.", "")
            last_run = s["last_run_start"] or "never"
            if last_run != "never":
                last_run = last_run[:19]
            lines.append(
                f"| **{s['status']}** | `{short}` | "
                f"{s['expected_last_fire'][:16]} ({s['hours_since_expected']}h ago) | "
                f"{last_run[:19]} | {s['runs_24h']} ({s['fails_24h']}) |"
            )
        lines.append("")

    if cleaned_locks:
        lines.append("## Self-heal: stale locks cleaned")
        lines.append("")
        for c in cleaned_locks:
            lines.append(f"- `{c['lock']}` (age {c['age_hours']}h, no live holder)")
        lines.append("")

    healthy_jobs = sorted(label for label, s in statuses.items() if s["status"] == "HEALTHY")
    if healthy_jobs:
        lines.append("## Healthy")
        lines.append("")
        for label in healthy_jobs:
            short = label.replace("com.adithya.ultron.", "")
            s = statuses[label]
            lines.append(f"- `{short}` · last run {s['last_run_start'][:19]} · {s['runs_24h']} runs/24h")
        lines.append("")

    return "\n".join(lines)


def state_path_exists(cfg: dict) -> bool:
    return pathlib.Path(cfg["audit_state_path"]).exists()


def state_diff(prior: dict, current: dict) -> list[dict]:
    diffs = []
    for label, s in current.items():
        prev_status = (prior.get(label) or {}).get("status")
        if prev_status != s["status"]:
            diffs.append({"label": label, "from": prev_status, "to": s["status"], "info": s})
    return diffs


def send_imessage(cfg: dict, body: str) -> bool:
    phone = cfg.get("operator_phone")
    if not phone:
        return False
    try:
        res = subprocess.run(
            [IMESSAGE_SEND, "--to", phone, "--text", body],
            capture_output=True, text=True, timeout=30,
        )
        return res.returncode == 0
    except Exception as e:
        sys.stderr.write(f"[auditor] iMessage send failed: {e}\n")
        return False


def main():
    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    now = datetime.datetime.now().astimezone()
    cutoff = now - datetime.timedelta(days=7)

    runs, ledger_start = load_ledger(cutoff)
    loaded = loaded_labels()
    jobs = parse_plist_jobs(loaded)

    statuses = {
        label: classify(label, info, runs.get(label, []), now, ledger_start)
        for label, info in jobs.items()
    }
    cleaned = cleanup_stale_locks(now)
    cold_start = not state_path_exists(cfg)

    report = build_report(statuses, cleaned, now)
    report_path = pathlib.Path(cfg["audit_report_dir"]) / f"cron-audit-{now:%Y-%m-%d}.md"
    report_path.write_text(report)

    state_path = pathlib.Path(cfg["audit_state_path"])
    prior = {}
    if state_path.exists():
        try:
            prior = json.loads(state_path.read_text())
        except Exception:
            pass

    diffs = state_diff(prior, statuses)
    alert_diffs = [d for d in diffs if d["to"] in ("STALE", "BROKEN")]
    recovered = [d for d in diffs if d["to"] == "HEALTHY" and d["from"] in ("STALE", "BROKEN")]

    if cold_start:
        alert_diffs = []
        recovered = []

    if alert_diffs or recovered:
        lines = [f"ULTRON cron audit @ {now:%H:%M}"]
        for d in alert_diffs:
            short = d["label"].replace("com.adithya.ultron.", "")
            lines.append(f"⚠ {short}: {d['from'] or 'NEW'} → {d['to']} ({d['info']['hours_since_expected']}h overdue)")
        for d in recovered:
            short = d["label"].replace("com.adithya.ultron.", "")
            lines.append(f"✓ {short}: {d['from']} → HEALTHY")
        if cleaned:
            lines.append(f"Cleaned {len(cleaned)} stale lock(s)")
        send_imessage(cfg, "\n".join(lines))

    state_path.write_text(json.dumps(statuses, indent=2))

    counts = {}
    for s in statuses.values():
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(f"[auditor] {dict(sorted(counts.items()))} cleaned_locks={len(cleaned)} alerts={len(alert_diffs)} recovered={len(recovered)}")


if __name__ == "__main__":
    main()
