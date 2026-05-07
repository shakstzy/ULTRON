"""iMessage skill client. Wraps send.sh for ergonomic Python use.

Usage:
    import sys
    sys.path.insert(0, "/Users/shakstzy/ULTRON/_shell/skills/imessage")
    from client import send_imessage, IMessageError

    result = send_imessage("+15125551234", "halt: turnstile detected")
    # → {"handoff": "ok", "path": "chat"}

Mirrors cloud-llm's interface: throws on hard failure, returns dict on success.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent
SEND_SH = SKILL_ROOT / "send.sh"


class IMessageError(RuntimeError):
    """send.sh exited non-zero (osascript or arg error)."""


def send_imessage(to: str, text: str | None = None, file: str | None = None) -> dict:
    """Send an iMessage. Provide either `text` or `file`, not both.

    `to` can be a phone number (E.164 preferred, but +1 / no-plus / punctuation
    variants are tolerated) or an Apple ID email.

    Returns the parsed JSON from send.sh: {"handoff": "ok", "path": "chat|buddy"}.
    Raises IMessageError on non-zero exit.
    """
    if (text is None) == (file is None):
        raise ValueError("provide exactly one of `text` or `file`")
    args = [str(SEND_SH), "--to", to]
    if text is not None:
        args += ["--text", text]
    else:
        args += ["--file", file]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise IMessageError(
            f"send.sh exit={proc.returncode}: stderr={proc.stderr.strip()[:300]}; stdout={proc.stdout.strip()[:300]}"
        )
    last_line = proc.stdout.strip().splitlines()[-1]
    return json.loads(last_line)
