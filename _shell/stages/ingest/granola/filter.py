"""Pre-filter: deterministic skip rules. Lock 5 of format.md.

Pure logic, no I/O.
"""
from __future__ import annotations

from typing import Iterable


def should_skip(
    doc: dict,
    transcript_segments: list[dict],
    subscribed_folders: Iterable[str],
) -> tuple[bool, str]:
    """Return (skip?, reason).

    Reason is empty when not skipping. Lock 5 conditions:

    1. doc.was_trashed is True
    2. doc.transcript_deleted_at is not None
    3. doc.valid_meeting is False
    4. doc.folder_titles ∩ subscribed_folders is empty
    5. transcript has zero segments where is_final is True (or missing,
       treated as final)
    """
    if doc.get("was_trashed") is True:
        return True, "was_trashed=True"
    if doc.get("transcript_deleted_at") is not None:
        return True, "transcript_deleted_at set"
    if doc.get("valid_meeting") is False:
        return True, "valid_meeting=False"

    folder_titles = set(doc.get("folder_titles") or [])
    subscribed = set(subscribed_folders)
    if not folder_titles or folder_titles.isdisjoint(subscribed):
        return True, "no folder match"

    # Treat missing is_final as True (older Granola records lack the flag).
    final_segs = [s for s in (transcript_segments or [])
                  if s.get("is_final", True) is not False]
    if not final_segs:
        return True, "transcript has 0 final segments"

    return False, ""
