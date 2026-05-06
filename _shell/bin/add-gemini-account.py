#!/usr/bin/env python3
"""
add-gemini-account.py — drive ONE Gemini OAuth flow without touching the
user's active gemini session.

Per memory: user only clicks the browser. Claude does everything else.

Strategy (Terminal.app + isolated HOME):
  1. Make a temp HOME dir with a copy of ~/.gemini/settings.json.
  2. Open a Terminal.app window running `HOME=<tmp> gemini` interactive.
     Gemini sees no oauth_creds.json there, opens a browser for OAuth,
     and writes new credentials to <tmp>/.gemini/oauth_creds.json once
     the user clicks through.
  3. Poll <tmp>/.gemini/oauth_creds.json. When seen + parseable, decode
     the JWT id_token, copy the creds into ~/.gemini/accounts/<email>.json.
  4. Close the Terminal window. Clean up the temp dir.

Returns 0 on success and prints the new account email; non-zero on failure.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GEMINI_DIR = Path.home() / ".gemini"
GLOBAL_SETTINGS = GEMINI_DIR / "settings.json"
ACCOUNTS_DIR = GEMINI_DIR / "accounts"

POLL_INTERVAL = 1.0
MAX_WAIT_SEC = 300


def decode_email(creds_path):
    try:
        d = json.loads(creds_path.read_text())
        idtok = d.get("id_token")
        if not idtok:
            return None
        parts = idtok.split(".")
        if len(parts) < 2:
            return None
        pad = "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad).decode())
        return payload.get("email")
    except Exception:
        return None


def open_terminal_with_command(cmd):
    """Open Terminal.app and run `cmd` inside a new window. Returns the
    window's id so we can close it later."""
    # Escape double quotes for AppleScript
    cmd_escaped = cmd.replace("\\", "\\\\").replace('"', '\\"')
    script = (
        f'tell application "Terminal"\n'
        f'  activate\n'
        f'  set newTab to do script "{cmd_escaped}"\n'
        f'  return id of window 1\n'
        f'end tell'
    )
    out = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.stderr.write(f"osascript error: {out.stderr}\n")
        return None
    try:
        return int(out.stdout.strip())
    except ValueError:
        return None


def close_terminal_window(window_id):
    if window_id is None:
        return
    script = f'tell application "Terminal" to close (every window whose id is {window_id})'
    subprocess.run(["osascript", "-e", script], capture_output=True)


def main():
    ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_SETTINGS.exists():
        sys.exit("ERROR: ~/.gemini/settings.json missing — bootstrap an initial gemini auth first")

    # Set up isolated HOME with the same auth-method config as global
    tmp_home = Path(tempfile.mkdtemp(prefix="gemini-auth-"))
    tmp_gemini = tmp_home / ".gemini"
    tmp_gemini.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GLOBAL_SETTINGS, tmp_gemini / "settings.json")
    new_oauth = tmp_gemini / "oauth_creds.json"

    print(f"=== isolated HOME: {tmp_home} ===")
    print(f"=== opening Terminal.app with `HOME={tmp_home} gemini` ===")
    print(">>> CLICK THROUGH the Google login when the browser pops <<<")
    print()

    # Build the command run inside Terminal.app
    inner = f'export HOME={tmp_home}; gemini; exit'
    window_id = open_terminal_with_command(inner)
    if window_id is None:
        sys.stderr.write("could not open Terminal window\n")
        shutil.rmtree(tmp_home, ignore_errors=True)
        return 2

    new_email = None
    waited = 0.0
    try:
        while waited < MAX_WAIT_SEC:
            time.sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL
            if new_oauth.exists():
                time.sleep(0.5)  # let write settle
                email = decode_email(new_oauth)
                if email:
                    new_email = email
                    break

        if new_email is None:
            print(f"!!! timed out after {MAX_WAIT_SEC}s waiting for new creds")
            return 2

        # Save the new account
        dest = ACCOUNTS_DIR / f"{new_email}.json"
        shutil.copy2(new_oauth, dest)
        print(f"=== authed: {new_email} ===")
        print(f"    saved to {dest}")

        accounts = sorted(ACCOUNTS_DIR.glob("*.json"))
        print()
        print(f"pool now has {len(accounts)} account(s):")
        for a in accounts:
            print(f"  {a.stem}")
        return 0
    finally:
        close_terminal_window(window_id)
        shutil.rmtree(tmp_home, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
