#!/usr/bin/env python3
"""Patch every ULTRON cron plist to wrap its inner command with cron-runner.py.

Idempotent — re-running is a no-op. Backs up originals to _shell/plists/.unpatched-backup/.

Usage:
    cron-patch-plists.py              # patch all plists in place
    cron-patch-plists.py --revert     # restore from backup
    cron-patch-plists.py --dry-run    # show planned transforms only
"""

import argparse
import glob
import pathlib
import plistlib
import shutil
import sys

PLIST_DIR = pathlib.Path("/Users/shakstzy/ULTRON/_shell/plists")
BACKUP_DIR = PLIST_DIR / ".unpatched-backup"
RUNNER = "/Users/shakstzy/ULTRON/_shell/bin/cron-runner.py"
MARKER = "cron-runner.py"


def patch_command(label, cmd):
    """Wrap a shell command with cron-runner.

    Common case: 'flock -n <lock> <inner>' → 'flock -n <lock> cron-runner.py <label> -- <inner>'.
    Fallback: '<cmd>' → 'cron-runner.py <label> -- <cmd>'.
    """
    if MARKER in cmd:
        return cmd, "already-patched"

    parts = cmd.split(None, 3)
    if len(parts) >= 4 and parts[0] == "flock" and parts[1] == "-n":
        lockfile = parts[2]
        inner = parts[3]
        new = f"flock -n {lockfile} {RUNNER} {label} -- {inner}"
        return new, "wrapped-flock"

    return f"{RUNNER} {label} -- {cmd}", "wrapped-bare"


def patch_plist(path: pathlib.Path, dry_run: bool):
    with open(path, "rb") as f:
        plist = plistlib.load(f)

    label = plist.get("Label")
    pa = plist.get("ProgramArguments")
    if not label or not pa:
        return ("skip", "no-label-or-program-args")

    if not (len(pa) >= 3 and pa[0] in ("/bin/bash", "/bin/sh", "/bin/zsh") and pa[1] in ("-c", "-lc", "-l")):
        return ("skip", f"unexpected-program-shape: {pa[:2]}")

    original_cmd = pa[2]
    new_cmd, action = patch_command(label, original_cmd)
    if action == "already-patched":
        return ("ok", action)

    if dry_run:
        return ("dry", f"{action}: {new_cmd[:100]}...")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / path.name
    if not backup_path.exists():
        shutil.copy2(path, backup_path)

    pa[2] = new_cmd
    plist["ProgramArguments"] = pa
    with open(path, "wb") as f:
        plistlib.dump(plist, f)

    return ("ok", action)


def revert_all():
    if not BACKUP_DIR.exists():
        print("no backup dir; nothing to revert")
        return
    n = 0
    for backup in BACKUP_DIR.glob("*.plist"):
        target = PLIST_DIR / backup.name
        shutil.copy2(backup, target)
        n += 1
    print(f"reverted {n} plists from backup")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()

    if args.revert:
        revert_all()
        return

    counts = {}
    for path in sorted(PLIST_DIR.glob("com.adithya.ultron.*.plist")):
        status, info = patch_plist(path, args.dry_run)
        counts[(status, info.split(":", 1)[0])] = counts.get((status, info.split(":", 1)[0]), 0) + 1
        print(f"{status:5s} {path.name}: {info}")

    print()
    print("Summary:")
    for (s, i), n in sorted(counts.items()):
        print(f"  {s:5s} {i}: {n}")


if __name__ == "__main__":
    main()
