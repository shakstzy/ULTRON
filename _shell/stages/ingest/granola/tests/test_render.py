"""Body / frontmatter render tests — Lock 3, Lock 4."""
import json
import unittest

import conftest  # noqa: F401
from conftest import FIXTURES

from render import (
    build_attendees,
    duration_str,
    render_transcript,
    render_body,
    build_calendar_event,
)


def seg(text, source="microphone", is_final=True,
        start="2026-04-13T18:00:00Z", end="2026-04-13T18:00:01Z", idx=0):
    s = {"text": text, "source": source}
    if is_final is not None:
        s["is_final"] = is_final
    if start is not None:
        s["start_timestamp"] = start
    if end is not None:
        s["end_timestamp"] = end
    return s


class AttendeesTest(unittest.TestCase):
    def test_creator_excluded_from_attendees_by_email(self):
        people = {
            "creator": {"name": "Adithya", "email": "adithya@outerscope.xyz"},
            "attendees": [
                {"name": "Adithya", "email": "ADITHYA@outerscope.xyz"},  # case mismatch
                {"name": "Sydney", "email": "sydney@eclipse.audio"},
            ],
        }
        creator, attendees = build_attendees(people)
        self.assertEqual(creator["email"], "adithya@outerscope.xyz")
        self.assertEqual(len(attendees), 1)
        self.assertEqual(attendees[0]["email"], "sydney@eclipse.audio")

    def test_creator_dedup_falls_back_to_name_when_email_missing(self):
        people = {
            "creator": {"name": "Adithya", "email": None},
            "attendees": [
                {"name": "adithya", "email": None},
                {"name": "Sydney", "email": "s@x.com"},
            ],
        }
        _, attendees = build_attendees(people)
        self.assertEqual(len(attendees), 1)
        self.assertEqual(attendees[0]["name"], "Sydney")

    def test_no_creator(self):
        creator, attendees = build_attendees({"attendees": [{"name": "X", "email": "x@x"}]})
        self.assertIsNone(creator)
        self.assertEqual(len(attendees), 1)

    def test_strips_granola_details_from_creator(self):
        # Granola's API returns creator with a nested "details" object
        # (Affinity / HubSpot / company lookup state). We discard it.
        people = {
            "creator": {
                "name": "Adithya",
                "email": "adithya@outerscope.xyz",
                "details": {"person": {"name": {"fullName": "Adithya"}}},
            },
            "attendees": [],
        }
        creator, _ = build_attendees(people)
        self.assertEqual(set(creator.keys()), {"name", "email"})
        self.assertNotIn("details", creator)

    def test_strips_details_from_attendees_too(self):
        people = {
            "creator": None,
            "attendees": [{
                "name": "Sydney",
                "email": "sydney@eclipse.audio",
                "details": {"company": {"name": "Eclipse Labs"}},
            }],
        }
        _, attendees = build_attendees(people)
        self.assertEqual(set(attendees[0].keys()), {"name", "email"})


class AttendeeNameNullRenderTest(unittest.TestCase):
    """Live data: many calendar-pulled attendees have only emails. Don't
    render a `?` placeholder for missing names."""

    def test_attendee_no_name_renders_email_only(self):
        from render import render_body
        doc = {
            "id": "x",
            "title": "T",
            "created_at": "2026-04-13T18:00:00Z",
            "updated_at": "2026-04-13T18:00:00Z",
            "people": {
                "creator": {"name": "Adithya", "email": "adi@out.x"},
                "attendees": [{"email": "sydney@eclipse.builders"}],  # no name
            },
        }
        segs = [seg("hi")]
        md = render_body(doc, segs, ["ECLIPSE"])
        self.assertIn("- <sydney@eclipse.builders>", md)
        self.assertNotIn("- ? <", md)
        self.assertNotIn("- ?\n", md)

    def test_creator_with_only_email(self):
        from render import render_body
        doc = {
            "id": "x",
            "title": "T",
            "created_at": "2026-04-13T18:00:00Z",
            "updated_at": "2026-04-13T18:00:00Z",
            "people": {
                "creator": {"email": "adi@out.x"},  # no name
                "attendees": [],
            },
        }
        segs = [seg("hi")]
        md = render_body(doc, segs, ["ECLIPSE"])
        self.assertIn("- (creator) <adi@out.x>", md)
        self.assertNotIn("**?**", md)


class DurationStrTest(unittest.TestCase):
    def test_minutes_seconds(self):
        self.assertEqual(duration_str(125_000), "2m 5s")

    def test_seconds_only(self):
        self.assertEqual(duration_str(45_000), "45s")

    def test_zero(self):
        self.assertEqual(duration_str(0), "0s")

    def test_none(self):
        self.assertIsNone(duration_str(None))


class TranscriptTest(unittest.TestCase):
    def test_groups_consecutive_same_source(self):
        segs = [seg("hi"), seg("there"), seg("ok", source="system")]
        out = render_transcript(segs)
        self.assertIn("**Me:** hi there", out)
        self.assertIn("**Other:** ok", out)

    def test_skips_non_final(self):
        segs = [seg("interim", is_final=False), seg("real")]
        out = render_transcript(segs)
        self.assertNotIn("interim", out)
        self.assertIn("real", out)

    def test_treats_missing_is_final_as_final(self):
        segs = [seg("hi", is_final=None)]  # is_final not in dict
        out = render_transcript(segs)
        self.assertIn("hi", out)

    def test_orders_by_start_timestamp(self):
        segs = [
            seg("second", start="2026-04-13T18:00:01Z"),
            seg("first",  start="2026-04-13T18:00:00Z"),
        ]
        out = render_transcript(segs)
        first_pos = out.index("first")
        second_pos = out.index("second")
        self.assertLess(first_pos, second_pos)

    def test_null_safe_sort_with_missing_timestamps(self):
        # Should not crash on missing timestamps. Spec: missing-timestamp
        # segments preserve their original order via secondary sort key.
        segs = [
            seg("a", start=None),
            seg("b", start="2026-04-13T18:00:00Z"),
            seg("c", start=None),
        ]
        # Just assert no crash; render still produces text.
        out = render_transcript(segs)
        self.assertIn("a", out)
        self.assertIn("b", out)
        self.assertIn("c", out)

    def test_unknown_source_label(self):
        segs = [seg("test", source="phone_in")]
        out = render_transcript(segs)
        self.assertIn("**phone_in:**", out)


class CalendarEventTest(unittest.TestCase):
    def test_null_input_returns_none(self):
        self.assertIsNone(build_calendar_event(None))
        self.assertIsNone(build_calendar_event({}))

    def test_extracts_fields(self):
        ge = {
            "summary": "Sync",
            "htmlLink": "https://cal/x",
            "start": {"dateTime": "2026-04-13T18:30:00-05:00"},
            "end":   {"dateTime": "2026-04-13T19:00:00-05:00"},
            "hangoutLink": "https://meet.google.com/abc",
            "conferenceData": {
                "conferenceSolution": {"name": "Google Meet"},
                "entryPoints": [{"entryPointType": "video", "uri": "https://meet.google.com/abc"}],
            },
        }
        ce = build_calendar_event(ge)
        self.assertEqual(ce["title"], "Sync")
        self.assertEqual(ce["url"], "https://cal/x")
        self.assertEqual(ce["start"], "2026-04-13T18:30:00-05:00")
        self.assertEqual(ce["end"], "2026-04-13T19:00:00-05:00")
        self.assertEqual(ce["conferencing_url"], "https://meet.google.com/abc")


class RenderBodyFixtureTest(unittest.TestCase):
    """Use captured real fixture to confirm body assembly."""

    def setUp(self):
        self.doc = json.loads((FIXTURES / "doc-with-notes.json").read_text())
        # Synthesize a small final-only transcript for body test.
        self.segs = [
            seg("Hello there", start="2026-04-13T18:00:00Z"),
            seg("Hi back",    source="system",     start="2026-04-13T18:00:01Z"),
        ]

    def test_body_has_h1_title(self):
        md = render_body(self.doc, self.segs, ["ECLIPSE"])
        self.assertIn("# " + self.doc["title"], md)

    def test_body_includes_attendees_section(self):
        md = render_body(self.doc, self.segs, ["ECLIPSE"])
        self.assertIn("## Attendees", md)

    def test_body_includes_ai_notes_section_when_lvp_has_content(self):
        md = render_body(self.doc, self.segs, ["ECLIPSE"])
        self.assertIn("## AI Notes", md)

    def test_body_omits_ai_notes_when_empty(self):
        d = dict(self.doc)
        d["last_viewed_panel"] = "panel-id-only-string"
        d["notes_markdown"] = ""
        md = render_body(d, self.segs, ["ECLIPSE"])
        self.assertNotIn("## AI Notes", md)

    def test_body_omits_calendar_event_when_null(self):
        d = dict(self.doc)
        d["google_calendar_event"] = None
        md = render_body(d, self.segs, ["ECLIPSE"])
        self.assertNotIn("## Calendar Event", md)

    def test_body_includes_transcript(self):
        md = render_body(self.doc, self.segs, ["ECLIPSE"])
        self.assertIn("## Transcript", md)
        self.assertIn("**Me:**", md)
        self.assertIn("**Other:**", md)


if __name__ == "__main__":
    unittest.main()
