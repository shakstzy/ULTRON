// browser.mjs -- patchright persistent-context launcher for Zillow Rental Manager.
// Exports launchContext() -> { context, page, close } plus pidfile + breaker helpers.
//
// Design notes:
// - No custom fingerprint/init-script layer. Patchright's defaults are battle-tested;
//   ad-hoc canvas/audio/webgl noise is more detectable than stock because it varies
//   across sessions reusing the same cookies (flagged by Codex adversarial review).
// - Pidfile is atomic (openSync 'wx'); stale locks are reaped then retried once.
// - Breaker trips only on top-level navigation 403s and debounces duplicate strikes.
// - SIGINT/SIGTERM are NOT auto-handled here; callers install their own graceful
//   shutdown so the browser context closes before the process exits.

import { chromium } from 'patchright';
// rebrowser-playwright patches the Runtime.enable CDP leak that stock Playwright
// exposes (Gemini diagnostic 2026-05-05: PerimeterX scores Runtime.enable
// instrumentation by triggering a synthetic JS error and reading the stack).
// Used for the daemon-attach path against real Chrome.
import { chromium as playwrightChromium } from 'rebrowser-playwright';
import { chmod, mkdir } from 'node:fs/promises';
import { existsSync, readFileSync, writeFileSync, unlinkSync, openSync, closeSync } from 'node:fs';
import { join } from 'node:path';
import { execSync } from 'node:child_process';
import { PROFILE_DIR, BREAKER_FILE } from './paths.mjs';

const PIDFILE = join(PROFILE_DIR, '.skill.pid');

const ZILLOW_HOSTS = new Set(['www.zillow.com', 'zillow.com', 'rentals.zillow.com']);
const STRIKE_DEBOUNCE_MS = 60 * 1000;
const HALT_COOLDOWN_MS = 24 * 3600 * 1000;
// Domains whose session cookies we forcibly upgrade to persistent before close.
// Required because Chrome drops session cookies on context teardown, even with
// launchPersistentContext, which kills the Zillow CIAM session between commands.
const ZILLOW_COOKIE_DOMAINS = ['.zillow.com', 'www.zillow.com', 'identity.zillow.com'];
const SESSION_COOKIE_TTL_DAYS = 30;

export function getProfileDir() { return PROFILE_DIR; }

export function sanitizeUrl(u) {
  try { const p = new URL(u); return p.origin + p.pathname; }
  catch (_) { return '(invalid-url)'; }
}

function isAlive(pid) {
  try { process.kill(pid, 0); return true; } catch (_) { return false; }
}

function releasePidfile() {
  try {
    if (existsSync(PIDFILE) && readFileSync(PIDFILE, 'utf8').trim() === String(process.pid)) {
      unlinkSync(PIDFILE);
    }
  } catch (_) {}
}

/**
 * Defensive: scan for stragglers bound to our profile dir and kill them.
 * The profile is dedicated to this skill -- nothing else should bind to it.
 * If something does (e.g. orphan chrome-devtools-mcp processes from prior
 * Claude Code sessions, dead daemons), it'll hold SingletonLock and our
 * launchPersistentContext will silently fail with "context closed".
 *
 * Skips our own daemon (managed via daemon-start/daemon-stop, has its own pidfile).
 */
function killOrphanProfileProcesses() {
  try {
    const daemonPidfile = join(PROFILE_DIR, '.daemon.pid');
    let daemonPid = 0;
    if (existsSync(daemonPidfile)) {
      try { daemonPid = parseInt(readFileSync(daemonPidfile, 'utf8').trim(), 10); } catch (_) {}
    }
    // ps -A -o pid=,command= for portability across mac/linux.
    const out = execSync('ps -A -o pid=,command=', { encoding: 'utf8', timeout: 5000 });
    const lines = out.split('\n');
    const victims = [];
    for (const line of lines) {
      const m = line.match(/^\s*(\d+)\s+(.*)$/);
      if (!m) continue;
      const pid = parseInt(m[1], 10);
      const cmd = m[2];
      if (pid === process.pid) continue;
      if (daemonPid && pid === daemonPid) continue;
      // Match anything binding our exact profile dir.
      if (!cmd.includes(`--user-data-dir=${PROFILE_DIR}`)) continue;
      victims.push({ pid, cmd: cmd.slice(0, 120) });
    }
    if (!victims.length) return;
    console.error(`[zrm] killing ${victims.length} orphan process(es) bound to ${PROFILE_DIR}:`);
    for (const v of victims) {
      console.error(`  pid=${v.pid} ${v.cmd}`);
      try { process.kill(v.pid, 'SIGKILL'); } catch (_) {}
    }
    // Best-effort: clear stale SingletonLock if no live owner remains.
    const lock = join(PROFILE_DIR, 'SingletonLock');
    if (existsSync(lock)) {
      try { unlinkSync(lock); } catch (_) {}
    }
  } catch (e) {
    console.error(`[zrm] killOrphanProfileProcesses failed (non-fatal): ${e.message}`);
  }
}

function acquirePidfile() {
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const fd = openSync(PIDFILE, 'wx');
      writeFileSync(fd, String(process.pid));
      closeSync(fd);
      process.on('exit', releasePidfile);
      return;
    } catch (e) {
      if (e.code !== 'EEXIST') throw e;
      let old = 0;
      try { old = parseInt(readFileSync(PIDFILE, 'utf8').trim(), 10); } catch (_) {}
      if (old && isAlive(old)) {
        throw new Error(`Profile locked by pid ${old}. Wait for it to finish or kill it.`);
      }
      try { unlinkSync(PIDFILE); } catch (_) {}
    }
  }
  throw new Error('Could not acquire pidfile after stale cleanup');
}

export function readBreaker() {
  if (!existsSync(BREAKER_FILE)) return { state: 'healthy', flagged_at: null, count_24h: 0, events: [] };
  try { return JSON.parse(readFileSync(BREAKER_FILE, 'utf8')); }
  catch (_) { return { state: 'healthy', flagged_at: null, count_24h: 0, events: [] }; }
}

export function writeBreaker(next) {
  writeFileSync(BREAKER_FILE, JSON.stringify(next, null, 2));
}

export function triggerBreaker(reason = '403') {
  const now = Date.now();
  const b = readBreaker();
  if (b.last_strike_at && (now - b.last_strike_at) < STRIKE_DEBOUNCE_MS) {
    return b;
  }
  const events = (b.events || []).filter(t => now - t < HALT_COOLDOWN_MS);
  events.push(now);
  const next = {
    state: events.length >= 2 ? 'halted' : 'flagged',
    flagged_at: new Date(now).toISOString(),
    last_strike_at: now,
    last_reason: reason,
    count_24h: events.length,
    events
  };
  writeBreaker(next);
  return next;
}

export function breakerAllowsLaunch(force = false) {
  if (force) return { ok: true, forced: true };
  const b = readBreaker();
  if (b.state === 'halted') {
    const elapsed = Date.now() - new Date(b.flagged_at).getTime();
    if (elapsed < HALT_COOLDOWN_MS) {
      return { ok: false, reason: 'breaker-halted', breaker: b };
    }
    writeBreaker({ state: 'healthy', flagged_at: null, last_strike_at: null, count_24h: 0, events: [] });
  }
  return { ok: true, forced: false };
}

// 403-on-top-level-nav listener that trips the breaker. Hoisted so both the
// fresh-launch path AND the CDP-attach path install it. Earlier this was
// inline in launchContext only, so daemon-attached runs ran blind: every
// thread URL could 403 without ever flipping the breaker. Found via smoke
// probe 2026-05-05 (102-lead batch silently absorbed every 403).
//
// Idempotent via WeakSet: the same process can call connectOrLaunch() more
// than once on the same context (e.g. reconnect after a transient CDP drop)
// without registering duplicate response handlers, which would duplicate
// breaker strikes per response.
const _watchedContexts = new WeakSet();
function installBreakerWatcher(context) {
  if (_watchedContexts.has(context)) return;
  _watchedContexts.add(context);
  context.on('response', (resp) => {
    try {
      const u = new URL(resp.url());
      if (!ZILLOW_HOSTS.has(u.hostname)) return;
      if (resp.status() !== 403) return;
      const req = resp.request();
      if (!req.isNavigationRequest()) return;
      const b = triggerBreaker('403');
      console.error(`[zrm] 403 on top-level nav to ${sanitizeUrl(resp.url())} -> breaker state=${b.state} count_24h=${b.count_24h}`);
    } catch (_) {}
  });
}

export async function launchContext({ force = false, headless = false } = {}) {
  const check = breakerAllowsLaunch(force);
  if (!check.ok) {
    const err = new Error(`Circuit breaker HALT active since ${check.breaker.flagged_at} (reason: ${check.breaker.last_reason || 'unknown'}). 24h cooldown. Solve captcha on zillow.com from your normal browser, then \`node scripts/run.mjs reset-breaker\`. Override with --force only if you know what you're doing.`);
    err.code = 'BREAKER_HALTED';
    throw err;
  }

  await mkdir(PROFILE_DIR, { recursive: true });
  try { await chmod(PROFILE_DIR, 0o700); } catch (_) {}
  killOrphanProfileProcesses();
  acquirePidfile();

  try {
    const proxy = process.env.ZRM_PROXY ? parseProxy(process.env.ZRM_PROXY) : undefined;
    if (proxy && /\.(nordvpn|expressvpn|mullvad|surfshark|protonvpn|privateinternetaccess|cyberghost|ipvanish|vyprvpn|torguard)\b/i.test(proxy.server || '')) {
      throw new Error('ZRM_PROXY points at a consumer VPN domain. Zillow blocks datacenter VPN IPs aggressively. Use a residential proxy or tether.');
    }

    let context;
    try {
      // Simplified config per Codex adversarial review (2026-04-28). Earlier we
      // had --disable-blink-features=AutomationControlled, custom viewport, etc.
      // Empirically: stripping all stealth args + adding a warmUp() sequence is
      // what unblocked /rental-manager-api/... 403s from PerimeterX.
      //
      // 2026-04-30: dropped `channel: 'chrome'` -- system Chrome 147 disabled
      // CDP browser-context-management (Browser.setDownloadBehavior errors), and
      // patchright's launchPersistentContext spawns Chrome 147 then immediately
      // sees the context die. Patchright's bundled Chromium (~/Library/Caches/
      // ms-playwright/chromium-1217) doesn't have that restriction. The bundled
      // build is also what patchright's stealth patches were tested against, so
      // fingerprint surface is more predictable.
      context = await chromium.launchPersistentContext(PROFILE_DIR, {
        headless,
        viewport: null,
        locale: 'en-US',
        timezoneId: 'America/Chicago',
        proxy
      });
    } catch (e) {
      if (/executable|browser|chrome|not found|doesn't exist|missing/i.test(e.message)) {
        throw new Error(`Chrome binary missing for patchright. In the skill dir run: npx patchright install chrome\nOriginal: ${e.message}`);
      }
      throw e;
    }

    installBreakerWatcher(context);

    // launchPersistentContext re-opens any tabs the prior run left behind.
    // Close stragglers on launch so we don't accumulate clutter across runs.
    const existing = context.pages();
    let page = existing[0] || await context.newPage();
    for (const p of existing.slice(1)) {
      try { await p.close({ runBeforeUnload: false }); } catch (_) {}
    }

    return {
      context,
      page,
      async close() {
        try { await persistZillowSessionCookies(context); } catch (_) {}
        try {
          for (const p of context.pages()) {
            try { await p.close({ runBeforeUnload: false }); } catch (_) {}
          }
        } catch (_) {}
        try { await context.close(); } finally { releasePidfile(); }
      }
    };
  } catch (e) {
    releasePidfile();
    throw e;
  }
}

// Connect-or-launch: prefer attaching to a running daemon Chrome via CDP.
// Falls back to launching a fresh patchright persistent context only if the
// daemon isn't running. CDP attach is dramatically less likely to trip
// PerimeterX because the daemon's _px3/TLS/fingerprint stay continuous.
//
// Returns the same shape as launchContext(): { context, page, close, mode }.
// `close` is conservative: it does NOT close the daemon's browser when in
// CDP mode -- only the connection. The daemon keeps running for the next
// command. In launch mode, close behaves like before (closes the context
// and persists session cookies).
export async function connectOrLaunch({ force = false, headless = false } = {}) {
  // CDP attach path was previously bypassing breakerAllowsLaunch entirely:
  // a halted breaker only blocked the fresh-launch path while the daemon
  // remained reachable, so production batches kept running through a halt.
  // Gate both paths on the same check.
  const check = breakerAllowsLaunch(force);
  if (!check.ok) {
    const err = new Error(`Circuit breaker HALT active since ${check.breaker.flagged_at} (reason: ${check.breaker.last_reason || 'unknown'}). 24h cooldown. Solve captcha on zillow.com from your normal browser, then \`node scripts/run.mjs reset-breaker\`. Override with --force.`);
    err.code = 'BREAKER_HALTED';
    throw err;
  }

  const { getCdpUrl } = await import('./daemon.mjs');
  const cdpUrl = getCdpUrl();
  // Try CDP first.
  let cdpReachable = false;
  try {
    const r = await fetch(`${cdpUrl}/json/version`, { signal: AbortSignal.timeout(1500) });
    cdpReachable = r.ok;
  } catch (_) {}

  if (cdpReachable) {
    // Use stock playwright (NOT patchright) for the CDP attach path.
    // Patchright's CDP connect fails with "Browser.setDownloadBehavior:
    // Browser context management is not supported" against stock Chrome.
    // The daemon spawns real Chrome anyway, so patchright's stealth patches
    // don't apply -- stock Chrome IS the correct fingerprint.
    const browser = await playwrightChromium.connectOverCDP(cdpUrl);
    const contexts = browser.contexts();
    if (!contexts.length) {
      // newContext() over CDP creates an incognito-like context NOT tied to the
      // daemon's persistent profile, so cookies/storage/breaker state would
      // diverge silently. Treat this as fatal (Codex adversarial review).
      try { await browser.close(); } catch (_) {}
      const err = new Error('CDP daemon has no default context (likely a stale or non-persistent Chrome). Restart with `node scripts/run.mjs daemon-stop && node scripts/run.mjs daemon-start`.');
      err.code = 'CDP_NO_DEFAULT_CONTEXT';
      throw err;
    }
    const context = contexts[0];
    installBreakerWatcher(context);
    // Tab hygiene: close everything except the first usable tab so we operate
    // on a known surface. about:blank or zillow.com is preferred. We MUST skip
    // chrome:// / devtools:// / chrome-extension:// pages -- closing those
    // hangs forever in Playwright (they're privileged surfaces, not normal
    // pages). Wrap close() in a 2s timeout race so a single misbehaving tab
    // can't deadlock the launcher. (Bug observed live 2026-05-05: Chrome
    // spawns chrome://omnibox-popup tabs that hang p.close() indefinitely.)
    const isInternalUrl = (u) => u.startsWith('chrome://') || u.startsWith('devtools://') || u.startsWith('chrome-extension://') || u.startsWith('chrome-untrusted://');
    const pages = context.pages();
    let keep = pages.find(p => {
      const u = p.url();
      return u === 'about:blank' || u.startsWith('https://www.zillow.com');
    });
    if (!keep) keep = pages.find(p => !isInternalUrl(p.url()));
    if (!keep) keep = await context.newPage();
    for (const p of pages) {
      if (p === keep) continue;
      if (isInternalUrl(p.url())) continue;
      try {
        await Promise.race([
          p.close({ runBeforeUnload: false }),
          new Promise((_, reject) => setTimeout(() => reject(new Error('close timeout')), 2000))
        ]);
      } catch (_) { /* don't let one bad tab block startup */ }
    }
    return {
      context,
      page: keep,
      mode: 'cdp',
      async close() {
        // Disconnect only -- don't kill the daemon.
        try { await persistZillowSessionCookies(context); } catch (_) {}
        try { await browser.close(); } catch (_) {}
      }
    };
  }

  // Fallback: legacy fresh launch.
  const ctx = await launchContext({ force, headless });
  return { ...ctx, mode: 'launch' };
}

// Warm-up sequence for PerimeterX. Without this, /rental-manager-api/api/...
// returns 403 px-captcha even with valid auth cookies. Hitting the homepage
// first lets the px collector establish a healthy runtime token before we
// touch the protected API tier. Costs ~20s but flips API responses 403 -> 200.
//
// Hard breaker: if the homepage warmup itself returns 403 (i.e. PerimeterX
// rejects us before we even reach the auth tier), throw with code WARMUP_403.
// Caller MUST close the context immediately. Continuing would burn more
// requests against an already-flagged IP/profile, harden the flag, and risk
// tripping the 24h breaker halt. This is the cheapest abort point.
export async function warmUpZillow(page, { homepageWaitMs = 12000 } = {}) {
  const resp = await page.goto('https://www.zillow.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (resp && resp.status() === 403) {
    // Stop the daemon proactively — leaving a flagged Chrome running means
    // the next CDP attach inherits the poisoned state and re-trips on first
    // request (Gemini adversarial review 2026-05-06). Operator workflow:
    // wipe state/chrome-profile/, re-login from a clean network.
    try {
      const { stopDaemon } = await import('./daemon.mjs');
      await stopDaemon();
      console.error('[zrm] warmup 403 -> daemon stopped to prevent attach loop. Wipe state/chrome-profile/ and re-login.');
    } catch (e) {
      console.error(`[zrm] warmup 403 but daemon-stop failed: ${e.message}`);
    }
    const err = new Error('Homepage warmup returned 403 (PerimeterX). IP or Chrome profile is flagged. Daemon stopped. Wipe state/chrome-profile/ and re-login from a clean network.');
    err.code = 'WARMUP_403';
    throw err;
  }
  try { await page.mouse.move(240, 180); await page.mouse.wheel(0, 500); } catch (_) {}
  await page.waitForTimeout(homepageWaitMs);
}

async function persistZillowSessionCookies(context) {
  // Pass an explicit URL list so we get cookies regardless of which tabs are
  // currently open. Gemini adversarial review 2026-05-06: bare cookies()
  // returns only cookies for currently-loaded domains in some Playwright
  // builds, which silently dropped Zillow session cookies on close.
  const all = await context.cookies(['https://www.zillow.com', 'https://identity.zillow.com']);
  const ttl = Math.floor(Date.now() / 1000) + SESSION_COOKIE_TTL_DAYS * 24 * 3600;
  const upgraded = [];
  for (const c of all) {
    const isZillow = ZILLOW_COOKIE_DOMAINS.some(d => c.domain === d || c.domain === d.replace(/^\./, ''));
    if (!isZillow) continue;
    if (c.expires && c.expires > 0) continue;
    upgraded.push({ ...c, expires: ttl });
  }
  if (upgraded.length) {
    await context.addCookies(upgraded);
    console.error(`[zrm] persisted ${upgraded.length} zillow session cookies for ${SESSION_COOKIE_TTL_DAYS}d`);
  }
}

function parseProxy(urlStr) {
  const u = new URL(urlStr);
  return {
    server: `${u.protocol}//${u.hostname}${u.port ? ':' + u.port : ''}`,
    username: u.username ? decodeURIComponent(u.username) : undefined,
    password: u.password ? decodeURIComponent(u.password) : undefined
  };
}

export async function hasCaptchaInDom(page) {
  try {
    return !!(await page.evaluate(() => {
      const sel = [
        'iframe[src*="captcha"]',
        'iframe[src*="perimeterx"]',
        'iframe[src*="human.com"]',
        'div[class*="px-captcha"]',
        'div[id*="px-captcha"]',
        'iframe[src*="hcaptcha"]',
        'iframe[src*="recaptcha"]'
      ];
      return sel.some(s => { try { return !!document.querySelector(s); } catch (_) { return false; } });
    }));
  } catch (_) {
    return false;
  }
}

export async function escalateOnCaptcha(page, reason = 'captcha-dom') {
  if (await hasCaptchaInDom(page)) {
    const b = triggerBreaker(reason);
    console.error(`[zrm] captcha detected -> breaker state=${b.state}`);
    return true;
  }
  return false;
}

export function installGracefulShutdown(closeFn) {
  let shuttingDown = false;
  const handler = async (signal, code) => {
    if (shuttingDown) return;
    shuttingDown = true;
    console.error(`[zrm] received ${signal}, closing browser...`);
    try { await closeFn(); } catch (_) {}
    process.exit(code);
  };
  process.on('SIGINT', () => handler('SIGINT', 130));
  process.on('SIGTERM', () => handler('SIGTERM', 143));
}
