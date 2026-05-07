#!/usr/bin/env python3
"""
schedule.py — compile / load / unload / status / remove launchd plists from
the source-of-truth `_shell/config/global-schedule.yaml` plus every workspace's
`config/schedule.yaml`.

Usage:
    schedule.py compile [--dry-run]
    schedule.py load <plist-name | --all>
    schedule.py unload <plist-name | --all>
    schedule.py status
    schedule.py remove <plist-name>
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"
PLISTS_DIR = ULTRON_ROOT / "_shell" / "plists"

sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "skills" / "schedule" / "scripts"))
from cron_to_launchd import cron_to_intervals, render_intervals_xml  # noqa: E402


def load_yaml(path: Path) -> dict:
    """Minimal YAML loader sufficient for ULTRON's schedule.yaml shapes.

    Falls back to PyYAML if available; otherwise parses the small, regular
    structure manually.
    """
    if not path.exists():
        return {}
    text = path.read_text(errors="ignore")
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # Tiny fallback: handles 2-level indented dicts and "key: value" lines.
    out: dict = {}
    stack: list[tuple[int, dict]] = [(0, out)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.lstrip()
        # Pop deeper stack entries.
        while stack and indent < stack[-1][0]:
            stack.pop()
        if line.endswith(":"):
            key = line[:-1].strip()
            new_dict: dict = {}
            stack[-1][1][key] = new_dict
            stack.append((indent + 2, new_dict))
        elif ":" in line:
            k, _, v = line.partition(":")
            stack[-1][1][k.strip()] = v.strip().strip('"').strip("'")
    return out


# ---- compile ------------------------------------------------------------

import plistlib
import shlex


def _load_cron_env() -> dict[str, str]:
    """Read top-level `cron_env:` from global-schedule.yaml.

    Single source of truth for env vars that every cron+daemon plist should inherit.
    Tilde-expanded at compile time (launchd does not expand `~` in plist env values).
    Empty/None values are skipped so a key can be neutralized by setting it to "".
    Cached so workspace-yaml jobs don't re-parse global-schedule.yaml per call.
    """
    if hasattr(_load_cron_env, "_cache"):
        return _load_cron_env._cache  # type: ignore[attr-defined]
    cfg = load_yaml(ULTRON_ROOT / "_shell" / "config" / "global-schedule.yaml")
    raw = (cfg or {}).get("cron_env") or {}
    out: dict[str, str] = {}
    for k, v in raw.items():
        if v is None or v == "":
            continue
        s = str(v)
        if s.startswith("~"):
            s = os.path.expanduser(s)
        out[str(k)] = s
    _load_cron_env._cache = out  # type: ignore[attr-defined]
    return out


def render_plist_dict(job: dict) -> dict:
    """Build a plist dict ready for plistlib.dumps(). Args are shell-quoted.

    Every plist is wrapped with cron-runner.py — captures exit/duration/stderr,
    appends a JSONL row to the cron ledger, and posts a colored event to the
    ULTRON Crons calendar. Calendar/ledger failures never fail the inner job.
    """
    label = job["label"]
    args_str = job["args"]
    args_quoted = " ".join(shlex.quote(a) for a in args_str.split())
    cmd = (
        f"flock -n /tmp/{shlex.quote(label)}.lock "
        f"{shlex.quote(str(ULTRON_ROOT))}/_shell/bin/cron-runner.py "
        f"{shlex.quote(label)} -- "
        f"{shlex.quote(str(ULTRON_ROOT))}/_shell/bin/run-stage.sh "
        f"{args_quoted}"
    )
    intervals = cron_to_intervals(job["cron"])

    plist: dict = {
        "Label": label,
        "ProgramArguments": ["/bin/bash", "-c", cmd],
        "EnvironmentVariables": {
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "ULTRON_ROOT": str(ULTRON_ROOT),
            "HOME": str(Path.home()),
        },
        "StandardOutPath": f"{ULTRON_ROOT}/_logs/{label}.out.log",
        "StandardErrorPath": f"{ULTRON_ROOT}/_logs/{label}.err.log",
        "WorkingDirectory": str(ULTRON_ROOT),
        "RunAtLoad": False,
    }
    if len(intervals) == 1:
        plist["StartCalendarInterval"] = intervals[0]
    else:
        plist["StartCalendarInterval"] = list(intervals)
    return plist


def _account_slug(account: str) -> str:
    """foo.bar@baz.qux → foo-bar-baz. Replaces dots in local part with hyphens."""
    if "@" not in account:
        return re.sub(r"[^a-z0-9-]", "-", account.lower()).strip("-")
    local, _, domain = account.partition("@")
    domain_stem = domain.split(".", 1)[0]
    local_clean = re.sub(r"[^a-z0-9-]", "-", local.lower()).strip("-")
    return f"{local_clean}-{domain_stem.lower()}"


def collect_jobs() -> list[dict]:
    """Walk every workspace's schedule.yaml + global-schedule.yaml and emit job specs."""
    jobs: list[dict] = []

    # 1. Cross-workspace jobs from global-schedule.yaml.
    global_cfg = load_yaml(ULTRON_ROOT / "_shell" / "config" / "global-schedule.yaml")
    cross = (global_cfg or {}).get("cross_workspace") or {}
    for name, body in cross.items():
        cron = (body or {}).get("cron")
        if not cron:
            continue
        label = f"com.adithya.ultron.{name.replace('_', '-')}"
        jobs.append({
            "label": label,
            "cron": cron,
            "args": _global_args_for(name),
            "kind": "global",
        })

    # 2. Per-workspace jobs.
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if workspaces_dir.exists():
        for ws_dir in sorted(workspaces_dir.iterdir()):
            if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
                continue
            ws_cfg = load_yaml(ws_dir / "config" / "schedule.yaml")
            if not ws_cfg:
                continue

            # 2a. workspace_jobs (lint, graphify, etc.).
            workspace_jobs = ws_cfg.get("workspace_jobs") or {}
            for job_name, job_body in workspace_jobs.items():
                cron = (job_body or {}).get("cron")
                if not cron:
                    continue
                label = f"com.adithya.ultron.{job_name}-{ws_dir.name}"
                jobs.append({
                    "label": label,
                    "cron": cron,
                    "args": f"{job_name} {ws_dir.name}",
                    "kind": "workspace_job",
                    "workspace": ws_dir.name,
                })

            # 2b. sources (per-(source,account)).
            sources = ws_cfg.get("sources") or {}
            for source_name, source_body in sources.items():
                cron = (source_body or {}).get("cron")
                if not cron:
                    continue
                accounts = (source_body or {}).get("accounts") or []
                if not accounts:
                    accounts = ["default"]
                for acct in accounts:
                    acct_slug = _account_slug(acct) if acct != "default" else "default"
                    label = f"com.adithya.ultron.ingest-{source_name}-{acct_slug}"
                    jobs.append({
                        "label": label,
                        "cron": cron,
                        "args": f"ingest-source {source_name} {acct}",
                        "kind": "ingest",
                        "source": source_name,
                        "account": acct,
                        "workspace_origin": ws_dir.name,
                    })

    # 3. Resolve duplicate labels (multiple workspaces declaring the same
    # (source,account)). Same cron → silently OK. Different crons → most-frequent
    # wins AND we log the divergence so the user knows their less-frequent
    # workspace cron was overridden. The single resulting plist still fans to
    # ALL subscribing workspaces via route.py.
    by_label: dict[str, dict] = {}
    divergences: list[str] = []
    for j in jobs:
        existing = by_label.get(j["label"])
        if existing is None:
            by_label[j["label"]] = j
            continue
        if existing["cron"] == j["cron"]:
            continue
        winner_count = _slot_count(j["cron"])
        existing_count = _slot_count(existing["cron"])
        if winner_count > existing_count:
            divergences.append(
                f"{j['label']}: {existing.get('workspace_origin')!r} cron {existing['cron']!r} "
                f"superseded by {j.get('workspace_origin')!r} cron {j['cron']!r} (more frequent)"
            )
            by_label[j["label"]] = j
        elif winner_count < existing_count:
            divergences.append(
                f"{j['label']}: {j.get('workspace_origin')!r} cron {j['cron']!r} "
                f"ignored (less frequent than {existing.get('workspace_origin')!r} {existing['cron']!r})"
            )
    if divergences:
        sys.stderr.write("schedule: cron divergences resolved (most-frequent wins):\n")
        for d in divergences:
            sys.stderr.write(f"  {d}\n")
    return list(by_label.values())


def _global_args_for(name: str) -> str:
    """Translate a global-schedule.yaml key to run-stage.sh args."""
    overrides = {
        "graphify_supermerge": "graphify-supermerge",
        "audit": "audit",
        "weekly_review": "weekly-review",
        "apple_contacts_sync": "apple-contacts-sync",
        "ledger_compact": "ledger-compact",
    }
    return overrides.get(name, name.replace("_", "-"))


def _slot_count(cron: str) -> int:
    try:
        return len(cron_to_intervals(cron))
    except Exception:
        return 0


def render_daemon_plist_dict(daemon: dict) -> dict:
    """Build a plist for a long-running daemon (KeepAlive=true, no cron).

    Daemons differ from scheduled jobs:
      • RunAtLoad: True  → start as soon as launchctl loads the agent
      • KeepAlive: True  → restart on crash / unexpected exit
      • No StartCalendarInterval (not a cron)
      • No cron-runner.py wrap (a daemon's "exit" is failure, not a discrete run)
    """
    label = daemon["label"]
    program_args: list[str] = list(daemon.get("program_args") or [])
    if not program_args:
        cmd = daemon.get("command")
        if not cmd:
            raise ValueError(f"daemon {label!r}: missing 'command' or 'program_args'")
        program_args = shlex.split(cmd)

    env: dict[str, str] = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "ULTRON_ROOT": str(ULTRON_ROOT),
        "HOME": str(Path.home()),
    }
    env.update(daemon.get("env") or {})

    plist: dict = {
        "Label": label,
        "ProgramArguments": program_args,
        "EnvironmentVariables": env,
        "StandardOutPath": f"{ULTRON_ROOT}/_logs/{label}.out.log",
        "StandardErrorPath": f"{ULTRON_ROOT}/_logs/{label}.err.log",
        "WorkingDirectory": daemon.get("working_dir") or str(ULTRON_ROOT),
        "RunAtLoad": True,
        # `KeepAlive: {SuccessfulExit: false}` restarts ONLY on non-zero exits, so
        # if the daemon exits cleanly (e.g., to release a port for a manual rebuild)
        # launchd respects that. With bare `KeepAlive: true` even clean exits would
        # re-spawn, masking real shutdowns.
        "KeepAlive": (
            {"SuccessfulExit": False}
            if bool(daemon.get("keep_alive", True))
            else False
        ),
    }
    # ThrottleInterval (seconds) caps restart frequency. Auth-loss / config error
    # crashes can otherwise spin at the launchd default 10s, hammering logs and
    # potentially network endpoints. Default to 60s if not specified; raise for
    # daemons that talk to rate-limited services.
    plist["ThrottleInterval"] = int(daemon.get("throttle_interval", 60))
    return plist


def collect_daemons() -> list[dict]:
    """Read top-level `daemons:` from global-schedule.yaml. Each daemon → one plist.

    YAML shape:
        daemons:
          whatsapp_bridge:
            command: /abs/path/to/binary
            working_dir: /abs/working/dir
            keep_alive: true
            throttle_interval: 30
            env:
              SOMEVAR: "value"
    """
    out: list[dict] = []
    global_cfg = load_yaml(ULTRON_ROOT / "_shell" / "config" / "global-schedule.yaml")
    daemons = (global_cfg or {}).get("daemons") or {}
    for name, body in daemons.items():
        body = body or {}
        slug = name.replace("_", "-")
        out.append({
            "label": f"com.adithya.ultron.daemon-{slug}",
            "kind": "daemon",
            **body,
        })
    return out


def render_plist(job: dict) -> bytes:
    if job.get("kind") == "daemon":
        return plistlib.dumps(render_daemon_plist_dict(job))
    return plistlib.dumps(render_plist_dict(job))


def cmd_compile(args: argparse.Namespace) -> int:
    jobs = collect_jobs() + collect_daemons()
    PLISTS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    skipped: list[tuple[str, str]] = []
    for job in jobs:
        try:
            content = render_plist(job)
        except ValueError as e:
            skipped.append((job["label"], str(e)))
            continue
        out = PLISTS_DIR / f"{job['label']}.plist"
        if not args.dry_run:
            out.write_bytes(content)
        written.append(out)

    print(f"{'would write' if args.dry_run else 'wrote'} {len(written)} plist(s):")
    for p in written:
        print(f"  {p.relative_to(ULTRON_ROOT)}")

    if skipped:
        print("\nSKIPPED (cron pattern not yet supported by compiler):")
        for label, err in skipped:
            print(f"  {label}: {err}")

    # Orphan detection: existing plists that don't match any current job.
    existing = sorted(PLISTS_DIR.glob("com.adithya.ultron.*.plist"))
    intended = {p.name for p in written}
    orphans = [p for p in existing if p.name not in intended]
    if orphans:
        print("\nORPHAN plists (no matching schedule.yaml entry):")
        for p in orphans:
            print(f"  {p.name}  →  run /schedule remove to retire")

    return 0


# ---- load / unload ------------------------------------------------------

def _label_from_arg(arg: str) -> str:
    return arg.replace(".plist", "")


def cmd_load(args: argparse.Namespace) -> int:
    targets: list[Path]
    if args.target == "--all":
        targets = sorted(PLISTS_DIR.glob("com.adithya.ultron.*.plist"))
    else:
        label = _label_from_arg(args.target)
        targets = [PLISTS_DIR / f"{label}.plist"]
    rc_total = 0
    LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
    for plist in targets:
        if not plist.exists():
            print(f"  missing: {plist}")
            rc_total = 1
            continue
        link = LAUNCH_AGENTS / plist.name
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(plist)
        # bootout-before-bootstrap: launchctl bootstrap returns rc=5 ("already
        # loaded") and silently keeps the OLD plist contents. After a recompile,
        # we need to evict the stale agent first so launchd reloads from the new
        # symlinked file. bootout rc != 0 is OK if the agent wasn't loaded.
        label = plist.stem
        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"],
            check=False, capture_output=True,
        )
        rc = subprocess.run(
            ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(link)],
            check=False,
        ).returncode
        # rc=5 should now only fire on truly-stuck agents; we still treat as success
        # so the loop doesn't abort the rest of --all.
        if rc not in (0, 5):
            rc_total = rc
        print(f"  loaded: {plist.name} (launchctl rc={rc})")
    subprocess.run(
        "launchctl list | grep com.adithya.ultron || true",
        shell=True, check=False,
    )
    return rc_total


def cmd_unload(args: argparse.Namespace) -> int:
    if args.target == "--all":
        labels = [p.stem for p in sorted(LAUNCH_AGENTS.glob("com.adithya.ultron.*.plist"))]
    else:
        labels = [_label_from_arg(args.target)]
    for label in labels:
        rc = subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"],
            check=False,
        ).returncode
        link = LAUNCH_AGENTS / f"{label}.plist"
        if link.exists() or link.is_symlink():
            link.unlink()
        print(f"  unloaded: {label} (launchctl rc={rc})")
    return 0


# ---- status -------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> int:
    plists = sorted(PLISTS_DIR.glob("com.adithya.ultron.*.plist"))
    loaded = subprocess.run(
        "launchctl list | grep com.adithya.ultron || true",
        shell=True, check=False, capture_output=True, text=True,
    ).stdout
    loaded_labels = {line.split()[-1] for line in loaded.splitlines() if line.strip()}

    print(f"plists at {PLISTS_DIR.relative_to(ULTRON_ROOT)}:")
    for p in plists:
        label = p.stem
        is_loaded = label in loaded_labels
        out_log = ULTRON_ROOT / "_logs" / f"{label}.out.log"
        last_run = "never"
        if out_log.exists():
            try:
                stat = out_log.stat()
                from datetime import datetime, timezone
                last_run = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            except OSError:
                pass
        print(f"  {label}  loaded={is_loaded}  last_run={last_run}")
    return 0


# ---- remove -------------------------------------------------------------

def cmd_remove(args: argparse.Namespace) -> int:
    label = _label_from_arg(args.target)
    plist = PLISTS_DIR / f"{label}.plist"
    link = LAUNCH_AGENTS / f"{label}.plist"
    subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"],
        check=False,
    )
    if link.exists() or link.is_symlink():
        link.unlink()
    if plist.exists():
        plist.unlink()
        print(f"  removed: {plist.relative_to(ULTRON_ROOT)}")
    else:
        print(f"  not found: {plist.relative_to(ULTRON_ROOT)}")
    return 0


# ---- main ---------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compile")
    c.add_argument("--dry-run", action="store_true")

    l = sub.add_parser("load")
    l.add_argument("target")

    u = sub.add_parser("unload")
    u.add_argument("target")

    sub.add_parser("status")

    r = sub.add_parser("remove")
    r.add_argument("target")

    args = ap.parse_args()

    if args.cmd == "compile":
        return cmd_compile(args)
    if args.cmd == "load":
        return cmd_load(args)
    if args.cmd == "unload":
        return cmd_unload(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "remove":
        return cmd_remove(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
