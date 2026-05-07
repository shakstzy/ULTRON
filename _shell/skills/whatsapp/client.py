"""
client.py — Python consumer surface for ULTRON's whatsapp send skill.

Wraps `send.sh` so any Python or Node consumer can shell out to the Go bridge
without thinking about the REST endpoint, recipient resolution, or bridge
liveness checks.

Usage:
    import sys
    sys.path.insert(0, "/Users/shakstzy/ULTRON/_shell/skills/whatsapp")
    from client import send_whatsapp, WhatsAppError

    send_whatsapp("+15125551234", text="hi")
    send_whatsapp(group="kinetics-commercial-expansion-ai", text="gm")
    send_whatsapp("+15125551234", file="/abs/path/to/image.png")

Returns the parsed JSON dict from send.sh stdout. Raises WhatsAppError on any
non-zero exit (arg error / resolution miss / bridge unreachable / send rejected).
"""
from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

_SEND_SH = Path(__file__).parent / "send.sh"


class WhatsAppError(RuntimeError):
    def __init__(self, message: str, exit_code: int, stderr: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


def send_whatsapp(
    to: str | None = None,
    *,
    group: str | None = None,
    text: str | None = None,
    file: str | None = None,
) -> dict:
    """Send via send.sh. Mutually exclusive: `to` xor `group`. At least one of `text`/`file`."""
    if not _SEND_SH.exists():
        raise WhatsAppError(f"send.sh missing at {_SEND_SH}", exit_code=127, stderr="")
    if (to is None) == (group is None):
        raise WhatsAppError("exactly one of `to` or `group` required", exit_code=2, stderr="")
    if not text and not file:
        raise WhatsAppError("at least one of `text` or `file` required", exit_code=2, stderr="")

    cmd: list[str] = [str(_SEND_SH)]
    if to:
        cmd += ["--to", to]
    if group:
        cmd += ["--group", group]
    if text:
        cmd += ["--text", text]
    if file:
        cmd += ["--file", file]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise WhatsAppError(
            f"send.sh exit {proc.returncode}: {proc.stderr.strip() or 'no stderr'}",
            exit_code=proc.returncode,
            stderr=proc.stderr,
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise WhatsAppError(
            f"send.sh returned non-JSON stdout: {proc.stdout!r}",
            exit_code=proc.returncode,
            stderr=proc.stderr,
        )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="WhatsApp send (CLI entrypoint)")
    p.add_argument("--to")
    p.add_argument("--group")
    p.add_argument("--text")
    p.add_argument("--file")
    args = p.parse_args()
    print(json.dumps(send_whatsapp(to=args.to, group=args.group, text=args.text, file=args.file)))
