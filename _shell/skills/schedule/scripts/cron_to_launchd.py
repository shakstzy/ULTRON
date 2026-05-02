#!/usr/bin/env python3
"""
cron_to_launchd.py — translate a 5-field cron string into a list of launchd
StartCalendarInterval dicts (each dict = one matching slot per period).

Supports common patterns used by ULTRON's schedule.yaml files:
    "M H * * *"           daily at H:M
    "M H-H2 * * *"        hourly within range, all minute=M
    "M */N * * *"         every N hours, minute=M
    "M H * * <dow>"       weekly at H:M on weekday (0=Sun)
    "M H D * *"           monthly at H:M on day-of-month
    "M H D */N *"         every N months, day=D, time H:M (multiple intervals)
    "M H * * 1-5"         weekdays Mon-Fri

Returns [{"Hour": ..., "Minute": ...}, ...]. Each dict represents ONE slot;
launchd fires once per slot per period.
"""
from __future__ import annotations

import sys
from typing import Iterable


def _expand_field(field: str, lo: int, hi: int) -> list[int]:
    """Expand a cron field over the allowed integer range [lo, hi]."""
    out: list[int] = []
    for part in field.split(","):
        part = part.strip()
        if part == "*":
            return list(range(lo, hi + 1))
        if part.startswith("*/"):
            step = int(part[2:])
            return list(range(lo, hi + 1, step))
        if "-" in part:
            range_part, _, step_str = part.partition("/")
            step = int(step_str) if step_str else 1
            a, b = range_part.split("-", 1)
            out.extend(range(int(a), int(b) + 1, step))
            continue
        out.append(int(part))
    return sorted(set(out))


def cron_to_intervals(cron: str) -> list[dict]:
    parts = cron.split()
    if len(parts) != 5:
        raise ValueError(f"cron must have 5 fields: {cron!r}")
    minute_f, hour_f, dom_f, month_f, dow_f = parts

    minutes = _expand_field(minute_f, 0, 59)
    hours = _expand_field(hour_f, 0, 23)
    doms = _expand_field(dom_f, 1, 31) if dom_f != "*" else None
    months = _expand_field(month_f, 1, 12) if month_f != "*" else None
    dows = _expand_field(dow_f, 0, 6) if dow_f != "*" else None

    out: list[dict] = []

    # Cron's day-of-month / day-of-week semantics are OR by default; launchd's
    # are AND. We approximate: if both DOM and DOW are restricted, we emit DOW
    # slots and let DOM be advisory (rare edge case for our usage).
    base_slots: list[dict] = []
    for h in hours:
        for m in minutes:
            base_slots.append({"Hour": h, "Minute": m})

    if dows is not None:
        for slot in base_slots:
            for d in dows:
                out.append({**slot, "Weekday": d})
    elif doms is not None and months is not None:
        for slot in base_slots:
            for d in doms:
                for mo in months:
                    out.append({**slot, "Day": d, "Month": mo})
    elif doms is not None:
        for slot in base_slots:
            for d in doms:
                out.append({**slot, "Day": d})
    elif months is not None:
        for slot in base_slots:
            for mo in months:
                out.append({**slot, "Month": mo})
    else:
        out = base_slots

    return out


def render_intervals_xml(intervals: Iterable[dict]) -> str:
    """Return the <key>StartCalendarInterval</key>... XML block."""
    intervals = list(intervals)
    if not intervals:
        return ""
    out = ["<key>StartCalendarInterval</key>"]
    if len(intervals) == 1:
        out.append("<dict>")
        for k, v in intervals[0].items():
            out.append(f"  <key>{k}</key><integer>{v}</integer>")
        out.append("</dict>")
    else:
        out.append("<array>")
        for entry in intervals:
            out.append("  <dict>")
            for k, v in entry.items():
                out.append(f"    <key>{k}</key><integer>{v}</integer>")
            out.append("  </dict>")
        out.append("</array>")
    return "\n".join(out)


if __name__ == "__main__":
    cron = " ".join(sys.argv[1:])
    if not cron:
        sys.stderr.write("usage: cron_to_launchd.py <cron-string>\n")
        sys.exit(2)
    intervals = cron_to_intervals(cron)
    print(render_intervals_xml(intervals))
