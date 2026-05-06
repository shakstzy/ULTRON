#!/usr/bin/env python3
"""
add-gemini-account.py — drive ONE Gemini OAuth flow.

Per memory: user only clicks the browser. Claude does everything else.

Strategy (no Terminal.app, no TUI, no pty):
  1. Make a temp HOME dir with a copy of ~/.gemini/settings.json
     (so oauth-personal auth mode is selected).
  2. Run `gemini -p "ping"` headless with HOME set to the temp dir.
     Gemini prints "Opening authentication page in your browser.
     Do you want to continue? [Y/n]:" — we feed "Y\\n" to stdin.
     Gemini auto-opens a browser to the OAuth URL.
  3. User clicks through Google login. Gemini receives the callback,
     writes <tmp>/.gemini/oauth_creds.json.
  4. Poll for new creds. Decode JWT id_token to get email. Copy creds
     to ~/.gemini/accounts/<email>.json.
  5. Kill subprocess. Clean up.

Returns 0 on success and prints the new account email; non-zero on failure.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import signal
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


def main():
    ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_SETTINGS.exists():
        sys.exit("ERROR: ~/.gemini/settings.json missing")

    tmp_home = Path(tempfile.mkdtemp(prefix="gemini-auth-"))
    tmp_gemini = tmp_home / ".gemini"
    tmp_gemini.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GLOBAL_SETTINGS, tmp_gemini / "settings.json")
    new_oauth = tmp_gemini / "oauth_creds.json"

    print(f"=== isolated HOME: {tmp_home} ===")
    print("=== launching gemini headless; sending 'Y' to bootstrap OAuth ===")
    print(">>> CLICK THROUGH the Google login when the browser pops <<<")
    print()

    env = os.environ.copy()
    env["HOME"] = str(tmp_home)

    proc = subprocess.Popen(
        ["gemini", "-p", "ping", "-o", "text"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        start_new_session=True,
    )
    # Send Y to confirm browser-auth prompt
    try:
        proc.stdin.write(b"Y\n")
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        pass

    new_email = None
    waited = 0.0
    try:
        while waited < MAX_WAIT_SEC:
            time.sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL
            if new_oauth.exists():
                time.sleep(0.5)
                email = decode_email(new_oauth)
                if email:
                    new_email = email
                    break
            if proc.poll() is not None and not new_oauth.exists():
                # gemini exited without producing creds
                stderr = proc.stderr.read().decode(errors="replace")[:500]
                print(f"!!! gemini exited (code {proc.returncode}); stderr: {stderr}")
                return 2

        if new_email is None:
            print(f"!!! timed out after {MAX_WAIT_SEC}s")
            return 2

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
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
        shutil.rmtree(tmp_home, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
