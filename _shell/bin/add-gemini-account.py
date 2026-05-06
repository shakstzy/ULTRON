#!/usr/bin/env python3
"""
add-gemini-account.py — drive ONE Gemini OAuth flow.

Per memory: user only clicks the browser. Claude does everything else.

Strategy:
  1. Backup current ~/.gemini/oauth_creds.json (if any) to /tmp/.
  2. Delete it.
  3. Spawn `gemini` (interactive). With oauth-personal selectedType set in
     settings.json, the CLI launches an OAuth browser flow and writes new
     credentials to ~/.gemini/oauth_creds.json when complete.
  4. Poll for the new file. When seen + parseable, decode the JWT id_token
     to extract the email, copy creds into ~/.gemini/accounts/<email>.json.
  5. Kill the gemini subprocess.
  6. Restore the original oauth_creds.json from backup.

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
import time
from pathlib import Path

GEMINI_DIR = Path.home() / ".gemini"
OAUTH = GEMINI_DIR / "oauth_creds.json"
ACCOUNTS_DIR = GEMINI_DIR / "accounts"
BACKUP = Path("/tmp/oauth_creds.bak.json")

POLL_INTERVAL = 1.0
MAX_WAIT_SEC = 300


def backup_creds():
    if OAUTH.exists():
        shutil.copy2(OAUTH, BACKUP)
        OAUTH.unlink()


def restore_creds():
    if BACKUP.exists():
        shutil.copy2(BACKUP, OAUTH)
        BACKUP.unlink()


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

    print("=== backing up current oauth_creds.json (if any) ===")
    backup_creds()

    print("=== launching gemini interactive — browser will open ===")
    print(">>> CLICK THROUGH the Google login in the browser when it appears <<<")
    print()
    proc = subprocess.Popen(
        ["gemini"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    new_email = None
    waited = 0.0
    try:
        while waited < MAX_WAIT_SEC:
            time.sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL
            if OAUTH.exists():
                # Wait a beat for write to settle, then try to decode
                time.sleep(0.5)
                email = decode_email(OAUTH)
                if email:
                    new_email = email
                    break
            if proc.poll() is not None:
                # gemini exited unexpectedly
                print(f"!!! gemini subprocess exited early (code {proc.returncode})")
                break

        if new_email is None:
            print("!!! timed out waiting for browser auth (or unparseable creds)")
            return 2
    finally:
        # Kill gemini subprocess
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass

    # Save the new account
    dest = ACCOUNTS_DIR / f"{new_email}.json"
    shutil.copy2(OAUTH, dest)
    print(f"=== authed: {new_email} ===")
    print(f"    saved to {dest}")

    # Restore the old creds for the active session
    restore_creds()

    # Show pool state
    accounts = sorted(ACCOUNTS_DIR.glob("*.json"))
    print()
    print(f"pool now has {len(accounts)} account(s):")
    for a in accounts:
        print(f"  {a.stem}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
