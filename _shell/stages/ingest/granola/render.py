"""Body markdown + frontmatter helpers. Locks 3 + 4 of format.md.

Pure functions. No I/O. Imports prosemirror.render_prosemirror for the
AI Notes section.
"""
from __future__ import annotations

from prosemirror import render_prosemirror

_SOURCE_LABEL = {
    "microphone": "Me",
    "system": "Other",
}


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------

def _trim_person(p: dict | None) -> dict | None:
    """Keep only {name, email} — strip Granola's nested `details` blob."""
    if not isinstance(p, dict):
        return None
    email = (p.get("email") or "").strip().lower() or None
    return {"name": p.get("name"), "email": email}


def build_attendees(people: dict | None) -> tuple[dict | None, list[dict]]:
    """Return (creator, attendees) with the creator de-duped from attendees.

    Both creator and attendees are trimmed to {name, email} only —
    Granola's API returns a nested `details` object with company /
    Affinity / HubSpot lookup state that we deliberately discard at the
    raw layer. Wiki agents can re-enrich downstream.

    Dedup key: lowercased email. If creator.email is missing, fall back
    to lowercased-stripped name.
    """
    if not isinstance(people, dict):
        return None, []
    creator_raw = people.get("creator") if isinstance(people.get("creator"), dict) else None
    creator = _trim_person(creator_raw)
    raw_attendees = people.get("attendees") or []

    if creator:
        ckey_email = (creator.get("email") or "").strip().lower()
        ckey_name = (creator.get("name") or "").strip().lower()
    else:
        ckey_email = ckey_name = ""

    out: list[dict] = []
    for a in raw_attendees:
        a_trim = _trim_person(a)
        if not a_trim:
            continue
        a_email = (a_trim.get("email") or "").strip().lower()
        a_name = (a_trim.get("name") or "").strip().lower()
        if ckey_email and a_email == ckey_email:
            continue
        if not ckey_email and ckey_name and a_name == ckey_name:
            continue
        out.append(a_trim)
    return creator, out


# ---------------------------------------------------------------------------
# Calendar event
# ---------------------------------------------------------------------------

def build_calendar_event(google_calendar_event: dict | None) -> dict | None:
    """Extract Lock 3 calendar_event from Granola's google_calendar_event."""
    if not google_calendar_event:
        return None
    ge = google_calendar_event
    title = ge.get("summary") or None
    url = ge.get("htmlLink") or None

    def _ts(d):
        if not isinstance(d, dict):
            return None
        return d.get("dateTime") or d.get("date") or None

    start = _ts(ge.get("start"))
    end = _ts(ge.get("end"))

    conferencing_url = ge.get("hangoutLink") or None
    conferencing_type = None
    cd = ge.get("conferenceData")
    if isinstance(cd, dict):
        sol = cd.get("conferenceSolution") or {}
        if isinstance(sol, dict):
            conferencing_type = sol.get("name") or None
        if not conferencing_url:
            for ep in cd.get("entryPoints") or []:
                if isinstance(ep, dict) and ep.get("entryPointType") == "video":
                    conferencing_url = ep.get("uri")
                    break

    return {
        "title": title,
        "start": start,
        "end": end,
        "url": url,
        "conferencing_url": conferencing_url,
        "conferencing_type": conferencing_type,
    }


# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------

def duration_str(ms: int | None) -> str | None:
    if ms is None:
        return None
    secs = max(0, int(ms) // 1000)
    if secs >= 60:
        m, s = divmod(secs, 60)
        return f"{m}m {s}s"
    return f"{secs}s"


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

def render_transcript(segments: list[dict]) -> str:
    """Render a transcript segment array to grouped-by-source markdown.

    Lock 4 rules:
    - Use only segments where is_final is True (or missing).
    - Sort by (start_timestamp or "", original index) — null-safe.
    - Group consecutive same-source runs into single blocks.
    - microphone → "Me", system → "Other", anything else → raw source.
    """
    if not segments:
        return ""

    indexed = list(enumerate(segments))
    finals = [(i, s) for i, s in indexed
              if s.get("is_final", True) is not False]
    if not finals:
        return ""

    # Null-safe sort: missing start_timestamp goes last but stable by idx.
    finals.sort(key=lambda pair: (pair[1].get("start_timestamp") or "￿", pair[0]))

    blocks: list[tuple[str, list[str]]] = []
    for _, seg in finals:
        src = seg.get("source") or "unknown"
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        if blocks and blocks[-1][0] == src:
            blocks[-1][1].append(text)
        else:
            blocks.append((src, [text]))

    lines: list[str] = []
    for src, texts in blocks:
        label = _SOURCE_LABEL.get(src, src)
        lines.append(f"**{label}:** " + " ".join(texts))
    return "\n\n".join(lines)


def transcript_duration_ms(segments: list[dict]) -> int | None:
    """Compute duration in ms from final segments. Null-safe.

    Uses only segments where BOTH start_timestamp and end_timestamp are
    present and parseable as ISO-8601. Returns None if none qualify.
    """
    from datetime import datetime
    starts: list[float] = []
    ends: list[float] = []
    for s in segments or []:
        if s.get("is_final", True) is False:
            continue
        st = s.get("start_timestamp")
        en = s.get("end_timestamp")
        for raw, bucket in ((st, starts), (en, ends)):
            if not raw:
                continue
            try:
                # Granola uses ISO 8601 with `Z` suffix.
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                bucket.append(dt.timestamp() * 1000)
            except (ValueError, AttributeError):
                continue
    if not starts or not ends:
        return None
    span = max(ends) - min(starts)
    return int(span) if span > 0 else None


# ---------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------

def render_body(
    doc: dict,
    transcript_segments: list[dict],
    subscribed_folders_for_workspace: list[str] | None = None,
) -> str:
    """Assemble the full markdown body (Lock 4)."""
    title = (doc.get("title") or "").strip() or "Untitled meeting"
    creator, attendees = build_attendees(doc.get("people"))
    cal = build_calendar_event(doc.get("google_calendar_event"))
    dur_ms = transcript_duration_ms(transcript_segments)
    dur = duration_str(dur_ms)

    n_attendees = len(attendees) + (1 if creator else 0)
    quote_bits = []
    if doc.get("created_at"):
        quote_bits.append(doc["created_at"])
    if dur:
        quote_bits.append(f"duration {dur}")
    quote_bits.append(f"{n_attendees} attendees")
    quote = "> " + " · ".join(quote_bits)

    lines: list[str] = [f"# {title}", "", quote, ""]

    # Attendees section
    if creator or attendees:
        lines.append("## Attendees")
        lines.append("")
        if creator:
            cn = creator.get("name") or "?"
            ce = creator.get("email") or ""
            email_part = f" <{ce}>" if ce else ""
            lines.append(f"- **{cn}** (creator){email_part}")
        for a in attendees:
            an = a.get("name") or "?"
            ae = a.get("email") or ""
            email_part = f" <{ae}>" if ae else ""
            lines.append(f"- {an}{email_part}")
        lines.append("")

    # Calendar event section (omit if null)
    if cal:
        lines.append("## Calendar Event")
        lines.append("")
        if cal.get("title"):
            lines.append(f"- Title: {cal['title']}")
        if cal.get("start"):
            lines.append(f"- Start: {cal['start']}")
        if cal.get("end"):
            lines.append(f"- End: {cal['end']}")
        if cal.get("url"):
            lines.append(f"- URL: {cal['url']}")
        if cal.get("conferencing_url"):
            ct = cal.get("conferencing_type") or "video"
            lines.append(f"- Conferencing: {ct} {cal['conferencing_url']}")
        lines.append("")

    # AI Notes section: notes_markdown wins, else last_viewed_panel.content
    ai_notes = (doc.get("notes_markdown") or "").strip()
    if not ai_notes:
        lvp = doc.get("last_viewed_panel")
        if isinstance(lvp, dict):
            ai_notes = render_prosemirror(lvp.get("content"))
    if ai_notes:
        lines.append("## AI Notes")
        lines.append("")
        lines.append(ai_notes)
        lines.append("")

    # Transcript section
    tx = render_transcript(transcript_segments)
    if tx:
        lines.append("## Transcript")
        lines.append("")
        lines.append(tx)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
