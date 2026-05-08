#!/usr/bin/env python3
"""Project ULTRON cron schedules onto the ULTRON Crons Google Calendar.

Reads every ~/ULTRON/_shell/plists/com.adithya.ultron.*.plist, extracts the
StartCalendarInterval blocks, and ensures one gray recurring event per (label, slot)
exists on the calendar. Stable id = SHA1(label + slot-json)[:12], stored in the event's
private extended properties for idempotent diffing.

Run hourly to keep the calendar in sync with the plists.
"""

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
GOG = "/Users/shakstzy/.local/bin/gog"

WEEKDAY_TO_BYDAY = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]


def stable_id(label, slot):
    payload = label + "|" + json.dumps(slot, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def next_occurrence(slot, now):
    """Compute the next datetime in the future matching this launchd slot."""
    h = slot.get("Hour", 0)
    m = slot.get("Minute", 0)
    weekday = slot.get("Weekday")
    day = slot.get("Day")
    month = slot.get("Month")

    if weekday is not None:
        target_iso = (weekday - 1) % 7
        cur_iso = now.weekday()
        days_ahead = (target_iso - cur_iso) % 7
        candidate = (now + datetime.timedelta(days=days_ahead)).replace(hour=h, minute=m, second=0, microsecond=0)
        if candidate <= now:
            candidate += datetime.timedelta(days=7)
        return candidate

    if month is not None and day is not None:
        candidate = now.replace(month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
        if candidate <= now:
            candidate = candidate.replace(year=now.year + 1)
        return candidate

    if day is not None:
        candidate = now.replace(day=day, hour=h, minute=m, second=0, microsecond=0)
        if candidate <= now:
            if now.month == 12:
                candidate = candidate.replace(year=now.year + 1, month=1)
            else:
                candidate = candidate.replace(month=now.month + 1)
        return candidate

    candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if candidate <= now:
        candidate += datetime.timedelta(days=1)
    return candidate


def slot_to_rrule(slot):
    if "Weekday" in slot:
        byday = WEEKDAY_TO_BYDAY[slot["Weekday"]]
        return f"RRULE:FREQ=WEEKLY;BYDAY={byday}"
    if "Month" in slot and "Day" in slot:
        return "RRULE:FREQ=YEARLY"
    if "Day" in slot:
        return f"RRULE:FREQ=MONTHLY;BYMONTHDAY={slot['Day']}"
    return "RRULE:FREQ=DAILY"


def slot_to_summary(label, slot):
    short = label.replace("com.adithya.ultron.", "")
    h = slot.get("Hour", 0)
    m = slot.get("Minute", 0)
    if "Weekday" in slot:
        wd = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][slot["Weekday"]]
        when = f"{wd} {h:02d}:{m:02d}"
    elif "Month" in slot and "Day" in slot:
        when = f"M{slot['Month']:02d}-D{slot['Day']:02d} {h:02d}:{m:02d}"
    elif "Day" in slot:
        when = f"D{slot['Day']:02d} {h:02d}:{m:02d}"
    else:
        when = f"{h:02d}:{m:02d}"
    return f"⏱ {short} @ {when}"


def collect_desired(now):
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


def list_existing_schedule_events(cfg):
    """Return {stable_id: (event_id, htmlLink)} for events tagged ultron_kind=schedule."""
    args = [
        GOG, "-a", cfg["account"], "cal", "events", cfg["calendar_id"],
        "--private-prop-filter", "ultron_kind=schedule",
        "--from", "2020-01-01",
        "--to", "2099-12-31",
        "--max", "2500",
        "--all-pages",
        "--json", "--results-only",
    ]
    res = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if res.returncode != 0:
        sys.stderr.write(f"[projector] list events failed: {res.stderr}\n")
        return {}
    try:
        events = json.loads(res.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"[projector] list events: bad JSON\n")
        return {}
    out = {}
    for ev in events:
        if ev.get("recurringEventId"):
            continue
        priv = (ev.get("extendedProperties") or {}).get("private") or {}
        sid = priv.get("ultron_stable_id")
        if sid:
            out[sid] = ev["id"]
    return out


def create_event(cfg, sid, spec):
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
        return False
    return True


def delete_event(cfg, event_id):
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
    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    now = datetime.datetime.now().astimezone()

    desired = collect_desired(now)
    existing = list_existing_schedule_events(cfg)

    to_create = [(sid, spec) for sid, spec in desired.items() if sid not in existing]
    to_delete = [(sid, evid) for sid, evid in existing.items() if sid not in desired]

    print(f"[projector] desired={len(desired)} existing={len(existing)} create={len(to_create)} delete={len(to_delete)}")

    created = 0
    for sid, spec in to_create:
        if create_event(cfg, sid, spec):
            created += 1
    deleted = 0
    for sid, evid in to_delete:
        if delete_event(cfg, evid):
            deleted += 1

    print(f"[projector] done: created={created} deleted={deleted} unchanged={len(desired) - len(to_create)}")


if __name__ == "__main__":
    main()
