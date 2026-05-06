// daemon.mjs -- long-lived Chrome process with --remote-debugging-port=9222.
// All skill commands (login, snapshot, pull-inbox, follow-up) attach via CDP
// instead of launching their own Chrome. Reasons:
//
// 1. PerimeterX flags back-to-back-warmup pattern from per-command launches.
//    A long-lived browser keeps the same _px3, same TLS/JA4, same fingerprint
//    across all jobs. Confirmed pattern per 2026 research (chrome-cdp-skill,
//    chrome-devtools-mcp, browser-use).
// 2. Eliminates the "fresh px3 token every command" red flag.
// 3. Auth cookies live in the daemon's runtime, not just on disk -> no
//    session-cookie-drop-on-close failure mode.
//
// Daemon spawns the system Chrome binary directly (NOT through patchright)
// so its stealth patches aren't needed -- a real Chrome process is the goal.

import { spawn } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { mkdir } from 'node:fs/promises';
import { PROFILE_DIR } from './paths.mjs';

const CHROME_BIN = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const DAEMON_PIDFILE = join(PROFILE_DIR, '.daemon.pid');
const DEBUG_PORT = parseInt(process.env.ZRM_DEBUG_PORT || '9222', 10);

export function getDebugPort() { return DEBUG_PORT; }
export function getCdpUrl() { return `http://127.0.0.1:${DEBUG_PORT}`; }
export function getProfileDir() { return PROFILE_DIR; }

function isAlive(pid) {
  if (!pid) return false;
  try { process.kill(pid, 0); return true; } catch (_) { return false; }
}

export function readDaemonPid() {
  if (!existsSync(DAEMON_PIDFILE)) return null;
  try { return parseInt(readFileSync(DAEMON_PIDFILE, 'utf8').trim(), 10); } catch (_) { return null; }
}

export function isDaemonAlive() {
  const pid = readDaemonPid();
  return isAlive(pid) ? pid : null;
}

async function isCdpReachable() {
  try {
    const r = await fetch(`${getCdpUrl()}/json/version`, { signal: AbortSignal.timeout(2000) });
    return r.ok;
  } catch (_) { return false; }
}

export async function waitForCdpReady(timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await isCdpReachable()) return true;
    await new Promise(r => setTimeout(r, 500));
  }
  return false;
}

export async function startDaemon({ visible = true } = {}) {
  const existing = isDaemonAlive();
  if (existing) {
    if (await isCdpReachable()) {
      return { ok: true, pid: existing, alreadyRunning: true };
    }
    // Stale pidfile or Chrome died. Clean up.
    try { unlinkSync(DAEMON_PIDFILE); } catch (_) {}
  }

  // Reject if a non-daemon Chrome is already using this profile (prevents
  // the "profile is already in use" SingletonLock error).
  const lockfile = join(PROFILE_DIR, 'SingletonLock');
  if (existsSync(lockfile)) {
    // Check if the lock is stale (target process dead).
    try {
      const link = await import('node:fs').then(m => m.readlinkSync(lockfile));
      const m = link.match(/-(\d+)$/);
      const lockPid = m ? parseInt(m[1], 10) : 0;
      if (!isAlive(lockPid)) {
        unlinkSync(lockfile);
      } else {
        return { ok: false, error: `profile in use by pid ${lockPid} (not our daemon). Close that Chrome window first.` };
      }
    } catch (_) {}
  }

  await mkdir(PROFILE_DIR, { recursive: true });

  const args = [
    `--remote-debugging-port=${DEBUG_PORT}`,
    `--user-data-dir=${PROFILE_DIR}`,
    '--no-default-browser-check',
    '--no-first-run',
    '--restore-last-session=false',
    // Open a blank starter tab so we don't auto-hit any URL on launch.
    'about:blank'
  ];

  if (!visible) {
    args.push('--headless=new');
  }

  const child = spawn(CHROME_BIN, args, {
    detached: true,
    stdio: 'ignore'
  });
  child.unref();

  if (!child.pid) {
    return { ok: false, error: 'spawn returned no pid' };
  }
  writeFileSync(DAEMON_PIDFILE, String(child.pid));

  const ready = await waitForCdpReady(15000);
  if (!ready) {
    try { process.kill(child.pid); } catch (_) {}
    try { unlinkSync(DAEMON_PIDFILE); } catch (_) {}
    return { ok: false, error: `CDP at ${getCdpUrl()} did not become reachable within 15s` };
  }

  return { ok: true, pid: child.pid, port: DEBUG_PORT, cdpUrl: getCdpUrl() };
}

export async function stopDaemon() {
  const pid = readDaemonPid();
  if (!pid) return { ok: true, msg: 'no daemon pidfile' };
  if (!isAlive(pid)) {
    try { unlinkSync(DAEMON_PIDFILE); } catch (_) {}
    return { ok: true, msg: 'pidfile stale, cleaned up' };
  }
  // Polite SIGTERM, then SIGKILL after 3s if still alive.
  try { process.kill(pid, 'SIGTERM'); } catch (_) {}
  for (let i = 0; i < 6; i++) {
    if (!isAlive(pid)) break;
    await new Promise(r => setTimeout(r, 500));
  }
  if (isAlive(pid)) {
    try { process.kill(pid, 'SIGKILL'); } catch (_) {}
  }
  try { unlinkSync(DAEMON_PIDFILE); } catch (_) {}
  return { ok: true, msg: `stopped pid ${pid}` };
}

export async function daemonStatus() {
  const pid = readDaemonPid();
  const alive = isAlive(pid);
  const cdpReachable = alive ? await isCdpReachable() : false;
  let version = null;
  if (cdpReachable) {
    try {
      const r = await fetch(`${getCdpUrl()}/json/version`, { signal: AbortSignal.timeout(1500) });
      version = await r.json();
    } catch (_) {}
  }
  return {
    pidfile: DAEMON_PIDFILE,
    pid,
    alive,
    cdpUrl: getCdpUrl(),
    cdpReachable,
    chromeVersion: version?.Browser || null,
    profileDir: PROFILE_DIR
  };
}
