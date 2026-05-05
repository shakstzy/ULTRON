"""Pre-filter tests — Lock 5."""
import unittest

import conftest  # noqa: F401

from filter import should_skip


# Helpers
def doc(**overrides):
    base = {
        "id": "test-id",
        "was_trashed": None,
        "valid_meeting": None,
        "transcript_deleted_at": None,
        "folder_titles": ["ECLIPSE"],
    }
    base.update(overrides)
    return base


def seg(text, is_final=True, source="microphone"):
    return {"text": text, "is_final": is_final, "source": source,
            "start_timestamp": "2026-04-13T18:00:00Z",
            "end_timestamp":   "2026-04-13T18:00:01Z"}


SUBS = ["ECLIPSE"]


class FilterTest(unittest.TestCase):
    # was_trashed
    def test_trashed_true_skips(self):
        skip, reason = should_skip(doc(was_trashed=True), [seg("hi")], SUBS)
        self.assertTrue(skip)
        self.assertIn("trashed", reason)

    def test_trashed_none_does_not_skip(self):
        skip, _ = should_skip(doc(was_trashed=None), [seg("hi")], SUBS)
        self.assertFalse(skip)

    def test_trashed_false_does_not_skip(self):
        skip, _ = should_skip(doc(was_trashed=False), [seg("hi")], SUBS)
        self.assertFalse(skip)

    # valid_meeting
    def test_valid_false_skips(self):
        skip, reason = should_skip(doc(valid_meeting=False), [seg("hi")], SUBS)
        self.assertTrue(skip)
        self.assertIn("valid_meeting", reason)

    def test_valid_none_does_not_skip(self):
        # Live-probe: many real Eclipse docs have valid_meeting=None.
        skip, _ = should_skip(doc(valid_meeting=None), [seg("hi")], SUBS)
        self.assertFalse(skip)

    def test_valid_true_does_not_skip(self):
        skip, _ = should_skip(doc(valid_meeting=True), [seg("hi")], SUBS)
        self.assertFalse(skip)

    # transcript_deleted_at
    def test_transcript_deleted_skips(self):
        skip, reason = should_skip(
            doc(transcript_deleted_at="2026-04-14T00:00:00Z"),
            [seg("hi")],
            SUBS,
        )
        self.assertTrue(skip)
        self.assertIn("transcript_deleted", reason)

    def test_transcript_not_deleted_does_not_skip(self):
        skip, _ = should_skip(doc(transcript_deleted_at=None), [seg("hi")], SUBS)
        self.assertFalse(skip)

    # folder intersection
    def test_no_folder_match_skips(self):
        skip, reason = should_skip(doc(folder_titles=["RANDOM"]), [seg("hi")], SUBS)
        self.assertTrue(skip)
        self.assertIn("folder", reason)

    def test_no_folders_at_all_skips(self):
        skip, reason = should_skip(doc(folder_titles=[]), [seg("hi")], SUBS)
        self.assertTrue(skip)

    # transcript
    def test_zero_segments_skips(self):
        skip, reason = should_skip(doc(), [], SUBS)
        self.assertTrue(skip)
        self.assertIn("transcript", reason)

    def test_only_interim_segments_skips(self):
        # is_final=False on every segment.
        skip, _ = should_skip(doc(), [seg("hi", is_final=False)], SUBS)
        self.assertTrue(skip)

    def test_missing_is_final_treated_as_final(self):
        s = seg("hi")
        del s["is_final"]
        skip, _ = should_skip(doc(), [s], SUBS)
        self.assertFalse(skip)


if __name__ == "__main__":
    unittest.main()
