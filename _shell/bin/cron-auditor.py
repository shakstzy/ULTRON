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
import fcntl
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


LEDGER_TAIL_BYTES = 5 * 1024 * 1024  # only read last 5MB; anything older isn't relevant


def load_ledger(cutoff: datetime.datetime) -> tuple[dict, datetime.datetime | None]:
    """Returns (runs_by_label, oldest_ledger_start). Reads only the tail of the ledger
    (LEDGER_TAIL_BYTES) so memory stays bounded as the file grows; oldest_ledger_start
    is the earliest start in the read window. Cold-start grace requires it to be older
    than expected_last_fire, so the bound only matters once the ledger is huge."""
    runs_by_label: dict[str, list[dict]] = {}
    oldest: datetime.datetime | None = None
    p = pathlib.Path(LEDGER)
    if not p.exists():
        return runs_by_label, None
    try:
        size = p.stat().st_size
    except OSError:
        return runs_by_label, None
    seek_to = max(0, size - LEDGER_TAIL_BYTES)
    with open(p, "rb") as fb:
        fb.seek(seek_to)
        if seek_to > 0:
            fb.readline()  # skip partial line
        for raw in fb:
            line = raw.decode("utf-8", errors="replace").strip()
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


def _safe_replace(dt: datetime.datetime, **kwargs) -> datetime.datetime | None:
    try:
        return dt.replace(**kwargs)
    except ValueError:
        return None


def _last_day_of_month(year: int, month: int) -> int:
    if month == 12:
        nxt = datetime.date(year + 1, 1, 1)
    else:
        nxt = datetime.date(year, month + 1, 1)
    return (nxt - datetime.timedelta(days=1)).day


def prev_occurrence(slot: dict, now: datetime.datetime) -> datetime.datetime:
    """Latest datetime <= now that matches this launchd slot.

    Handles weekday=7 (Sun alias for 0), Feb 29 in non-leap years,
    Day=31 in months with <31 days (clamps to last day of month)."""
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
        for year_offset in range(0, 4):
            year = now.year - year_offset
            cand = _safe_replace(now, year=year, month=month, day=day,
                                 hour=h, minute=m, second=0, microsecond=0)
            if cand is not None and cand <= now:
                return cand
        return now - datetime.timedelta(days=365)

    if day is not None:
        # launchd skips months whose last day < requested Day. Match that, else
        # we'd compute a phantom "expected last fire" for Feb when Day=31.
        for month_offset in range(0, 13):
            year = now.year + (now.month - 1 - month_offset) // 12
            mo = ((now.month - 1 - month_offset) % 12) + 1
            if day > _last_day_of_month(year, mo):
                continue
            cand = _safe_replace(now, year=year, month=mo, day=day,
                                 hour=h, minute=m, second=0, microsecond=0)
            if cand is not None and cand <= now:
                return cand
        return now - datetime.timedelta(days=30)

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
            # Don't flag STALE if the job is currently running — long-running
            # jobs (e.g., dating-bumble-send taking 25 min, ingest jobs taking
            # an hour+) wouldn't have written their ledger row yet.
            if is_lock_held(f"/tmp/{label}.lock"):
                status = "HEALTHY"
            else:
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


def is_lock_held(lock_path: str) -> bool:
    """True iff some process currently holds an exclusive flock on the file.

    We try to acquire the lock non-blocking; success means nobody else has it
    (and we release immediately by closing the file). BlockingIOError = held."""
    try:
        with open(lock_path, "a") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            except BlockingIOError:
                return True
    except OSError:
        return False


def cleanup_stale_locks(now: datetime.datetime) -> list[dict]:
    """Delete /tmp/com.adithya.ultron.*.lock files whose holder has died.

    Probe via fcntl.flock (not lsof — `lsof` can be missing from launchd's PATH
    or time out under load, in which case the previous lsof-based check would
    fall through and unlink a live lock). The flock probe atomically tells us
    whether any process holds an exclusive lock on the inode."""
    cleaned = []
    for lock in glob.glob(LOCK_GLOB):
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(lock)).astimezone()
        except OSError:
            continue
        age_hours = (now - mtime).total_seconds() / 3600.0
        if age_hours < LOCK_STALE_HOURS:
            continue
        if is_lock_held(lock):
            continue
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
    state_corrupt = False
    if state_path.exists():
        try:
            prior = json.loads(state_path.read_text())
        except Exception:
            # Zero-byte or partial JSON (e.g., interrupted write before the
            # atomic-rename fix landed). Treating prior={} would re-fire alerts
            # for every currently-flagged job. Suppress instead and rewrite.
            state_corrupt = True
            sys.stderr.write("[auditor] audit-state.json unreadable; suppressing alerts and rewriting\n")

    diffs = state_diff(prior, statuses)
    alert_diffs = [d for d in diffs if d["to"] in ("STALE", "BROKEN")]
    recovered = [d for d in diffs if d["to"] == "HEALTHY" and d["from"] in ("STALE", "BROKEN")]

    if cold_start or state_corrupt:
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

    # Atomic write: a crash mid-write previously left a zero-byte state.json,
    # which the next run silently swallows (parse fail → prior={}) and re-fires
    # alerts for every job as if it were brand new.
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(statuses, indent=2))
    os.replace(tmp_path, state_path)

    counts = {}
    for s in statuses.values():
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(f"[auditor] {dict(sorted(counts.items()))} cleaned_locks={len(cleaned)} alerts={len(alert_diffs)} recovered={len(recovered)}")


if __name__ == "__main__":
    main()
