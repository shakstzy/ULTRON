#!/usr/bin/env python3
"""Project ULTRON cron schedules onto the ULTRON Crons Google Calendar.

Reads every ~/ULTRON/_shell/plists/com.adithya.ultron.*.plist, extracts the
StartCalendarInterval blocks, and ensures one gray recurring event per (label, slot)
exists on the calendar. Stable id = SHA1(label + slot-json)[:12], stored in the event's
private extended properties for idempotent diffing.

Idempotency uses a local state file (`_logs/cron-projector-state.json`) mapping
stable_id → master_event_id. This avoids depending on a calendar list-with-date-window
(which would miss yearly/quarterly recurrences). On `--reconcile`, the projector also
queries the calendar with a wide window to detect drift between state and reality.

Run hourly to keep the calendar in sync with the plists.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import pathlib
import plistlib
import subprocess
import sys

CONFIG_PATH = "/Users/shakstzy/ULTRON/_shell/config/cron-calendar.json"
PLIST_DIR = "/Users/shakstzy/ULTRON/_shell/plists"
STATE_PATH = pathlib.Path("/Users/shakstzy/ULTRON/_logs/cron-projector-state.json")
GOG = "/Users/shakstzy/.local/bin/gog"

WEEKDAY_TO_BYDAY = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
WEEKDAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def stable_id(label: str, slot: dict) -> str:
    payload = label + "|" + json.dumps(slot, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def _safe_replace(now: datetime.datetime, **kwargs) -> datetime.datetime | None:
    """Return now.replace(**kwargs), or None if the result is an invalid date
    (e.g. Feb 29 in a non-leap year, Day=31 in April)."""
    try:
        return now.replace(**kwargs)
    except ValueError:
        return None


def _last_day_of_month(year: int, month: int) -> int:
    if month == 12:
        nxt = datetime.date(year + 1, 1, 1)
    else:
        nxt = datetime.date(year, month + 1, 1)
    return (nxt - datetime.timedelta(days=1)).day


def next_occurrence(slot: dict, now: datetime.datetime) -> datetime.datetime:
    """Compute the next datetime in the future matching this launchd slot.

    Handles edge cases: weekday=7 (Sun alias for 0), Feb 29 in non-leap years,
    Day=31 in months with <31 days (clamps to last day of month)."""
    h = slot.get("Hour", 0)
    m = slot.get("Minute", 0)
    weekday = slot.get("Weekday")
    day = slot.get("Day")
    month = slot.get("Month")

    if weekday is not None:
        # launchd Weekday: 0 or 7 = Sun. Convert to ISO (0=Mon..6=Sun).
        target_iso = (weekday - 1) % 7
        cur_iso = now.weekday()
        days_ahead = (target_iso - cur_iso) % 7
        candidate = (now + datetime.timedelta(days=days_ahead)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        if candidate <= now:
            candidate += datetime.timedelta(days=7)
        return candidate

    if month is not None and day is not None:
        for year_offset in range(0, 4):
            year = now.year + year_offset
            cand = _safe_replace(now, year=year, month=month, day=day,
                                 hour=h, minute=m, second=0, microsecond=0)
            if cand is not None and cand > now:
                return cand
        return now + datetime.timedelta(days=365)

    if day is not None:
        for month_offset in range(0, 13):
            year = now.year + (now.month - 1 + month_offset) // 12
            mo = ((now.month - 1 + month_offset) % 12) + 1
            actual_day = min(day, _last_day_of_month(year, mo))
            cand = _safe_replace(now, year=year, month=mo, day=actual_day,
                                 hour=h, minute=m, second=0, microsecond=0)
            if cand is not None and cand > now:
                return cand
        return now + datetime.timedelta(days=30)

    candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if candidate <= now:
        candidate += datetime.timedelta(days=1)
    return candidate


def slot_to_rrule(slot: dict) -> str:
    if "Weekday" in slot:
        byday = WEEKDAY_TO_BYDAY[slot["Weekday"] % 7]
        return f"RRULE:FREQ=WEEKLY;BYDAY={byday}"
    if "Month" in slot and "Day" in slot:
        return "RRULE:FREQ=YEARLY"
    if "Day" in slot:
        return f"RRULE:FREQ=MONTHLY;BYMONTHDAY={slot['Day']}"
    return "RRULE:FREQ=DAILY"


def slot_to_summary(label: str, slot: dict) -> str:
    short = label.replace("com.adithya.ultron.", "")
    h = slot.get("Hour", 0)
    m = slot.get("Minute", 0)
    if "Weekday" in slot:
        wd = WEEKDAY_NAMES[slot["Weekday"] % 7]
        when = f"{wd} {h:02d}:{m:02d}"
    elif "Month" in slot and "Day" in slot:
        when = f"M{slot['Month']:02d}-D{slot['Day']:02d} {h:02d}:{m:02d}"
    elif "Day" in slot:
        when = f"D{slot['Day']:02d} {h:02d}:{m:02d}"
    else:
        when = f"{h:02d}:{m:02d}"
    return f"⏱ {short} @ {when}"


def collect_desired(now: datetime.datetime) -> dict:
    desired = {}
    for path in sorted(glob.glob(f"{PLIST_DIR}/com.adithya.ultron.*.plist")):
        with open(path, "rb") as f:
            plist = plistlib.load(f)
        label = plist.get("Label")
        if not label:
            continue
        sci = plist.get("StartCalendarInterval")
        if sci is None:
            continue
        slots = sci if isinstance(sci, list) else [sci]
        for slot in slots:
            sid = stable_id(label, dict(slot))
            dtstart = next_occurrence(dict(slot), now)
            desired[sid] = {
                "label": label,
                "slot": dict(slot),
                "dtstart": dtstart,
                "rrule": slot_to_rrule(dict(slot)),
                "summary": slot_to_summary(label, dict(slot)),
            }
    return desired


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_PATH)


def reconcile_with_calendar(cfg: dict, window_days: int = 90) -> dict:
    """Rebuild state map from calendar contents. Use on first run to seed state, or
    periodically to recover from drift. Returns a fresh state dict; existing local
    state is replaced. Window covers daily/weekly/monthly cleanly; quarterly/yearly
    slots will be missed when not in window — re-run reconcile near their fire time
    if needed."""
    now = datetime.datetime.now().astimezone()
    args = [
        GOG, "-a", cfg["account"], "cal", "events", cfg["calendar_id"],
        "--private-prop-filter", "ultron_kind=schedule",
        "--from", (now - datetime.timedelta(days=window_days)).strftime("%Y-%m-%d"),
        "--to", (now + datetime.timedelta(days=window_days)).strftime("%Y-%m-%d"),
        "--max", "2500",
        "--all-pages",
        "--json", "--results-only",
    ]
    res = subprocess.run(args, capture_output=True, text=True, timeout=300)
    if res.returncode != 0:
        sys.stderr.write(f"[projector] reconcile list failed: {res.stderr[:400]}\n")
        return {}
    try:
        events = json.loads(res.stdout)
    except json.JSONDecodeError:
        sys.stderr.write("[projector] reconcile list: bad JSON\n")
        return {}

    state: dict[str, str] = {}
    for ev in events:
        priv = (ev.get("extendedProperties") or {}).get("private") or {}
        sid = priv.get("ultron_stable_id")
        if not sid:
            continue
        master_id = ev.get("recurringEventId") or ev["id"]
        state[sid] = master_id  # last writer wins; all instances share same master
    sys.stderr.write(f"[projector] reconcile: rebuilt state from {len(events)} events → {len(state)} stable_ids\n")
    return state


def create_event(cfg: dict, sid: str, spec: dict) -> str | None:
    """Create a recurring schedule event. Returns the master event id, or None on failure."""
    dtstart = spec["dtstart"]
    dtend = dtstart + datetime.timedelta(minutes=1)
    args = [
        GOG, "-a", cfg["account"], "cal", "create", cfg["calendar_id"],
        "--summary", spec["summary"],
        "--from", dtstart.isoformat(),
        "--to", dtend.isoformat(),
        "--rrule", spec["rrule"],
        "--event-color", cfg["color_scheduled"],
        "--transparency", "transparent",
        "--description", f"Scheduled run: {spec['label']}\nSlot: {json.dumps(spec['slot'], sort_keys=True)}\nRRULE: {spec['rrule']}",
        "--private-prop", f"ultron_label={spec['label']}",
        "--private-prop", "ultron_kind=schedule",
        "--private-prop", f"ultron_stable_id={sid}",
        "--no-input",
        "--json",
    ]
    res = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if res.returncode != 0:
        sys.stderr.write(f"[projector] create failed for {sid} ({spec['label']}): {res.stderr[:400]}\n")
        return None
    try:
        payload = json.loads(res.stdout)
        return payload.get("id") or (payload.get("event") or {}).get("id")
    except json.JSONDecodeError:
        sys.stderr.write(f"[projector] create returned bad JSON for {sid}\n")
        return None


def delete_event(cfg: dict, event_id: str) -> bool:
    args = [
        GOG, "-a", cfg["account"], "cal", "delete", cfg["calendar_id"], event_id,
        "--force", "--no-input",
    ]
    res = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if res.returncode != 0:
        sys.stderr.write(f"[projector] delete failed for {event_id}: {res.stderr[:400]}\n")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reconcile", action="store_true",
                    help="Cross-check state file against calendar before diffing")
    args = ap.parse_args()

    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    now = datetime.datetime.now().astimezone()

    desired = collect_desired(now)
    state = load_state()

    if args.reconcile:
        state = reconcile_with_calendar(cfg)

    to_create = [(sid, spec) for sid, spec in desired.items() if sid not in state]
    to_delete = [(sid, mid) for sid, mid in state.items() if sid not in desired]

    print(f"[projector] desired={len(desired)} state={len(state)} create={len(to_create)} delete={len(to_delete)}")

    created = 0
    for sid, spec in to_create:
        eid = create_event(cfg, sid, spec)
        if eid:
            state[sid] = eid
            created += 1
    deleted = 0
    for sid, mid in to_delete:
        if delete_event(cfg, mid):
            state.pop(sid, None)
            deleted += 1

    save_state(state)
    print(f"[projector] done: created={created} deleted={deleted} state_size={len(state)}")


if __name__ == "__main__":
    main()
