// pacing.mjs -- velocity governor for the Zillow skill.
//
// PerimeterX's press-and-hold challenge fires on burst patterns (>10 calls in
// 30s confirmed empirically). We pace EVERY user-driven action (page nav,
// thread click, send) to a minimum 45-90s jittered gap. Hard caps prevent
// any sustained-burst regression.
//
// State lives at ~/.shakos/playbook-output/zillow-rental-manager/state/pacing.json
// and survives process restarts. Atomic writes (tmp+rename).

import { existsSync, readFileSync, writeFileSync, renameSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const STATE_DIR = process.env.ZRM_STATE_DIR || `${process.env.HOME}/.shakos/playbook-output/zillow-rental-manager/state`;
const PACING_FILE = join(STATE_DIR, 'pacing.json');

// HARD CEILINGS — env CANNOT exceed these. Re-calibrated 2026-05-04 after
// observing Adithya's manual browse fires 60+/hr without flagging. The
// 2026-04-30 PX 403 was on busted automation fingerprints; with patchright
// stealth + a real logged-in profile, sustained 60/hr is fine. We keep
// generous ceilings as the ultimate safety net.
//
// Old caps (15/80, 45-90s gap) treated each scroll wheel tick as a new
// "user action," which is silly: a human reads through 100 leads in 5
// minutes, firing dozens of GraphQL calls per minute. The pacing layer is
// for THREAD CLICKS (each is a discrete user action), not for list-scroll
// pagination bursts.
// Re-tuned 2026-05-04 round 2: Adithya confirmed the v3 run (40 calls/hr)
// looked natural to Zillow with zero PX flags. Pushing further to match
// human-browse velocity (5-10s between thread clicks).
const HARD_HOURLY_CEILING = 150;
const HARD_DAILY_CEILING = 600;
const HARD_MIN_GAP_FLOOR_MS = 4000;

// Defaults. Env can lower hourly/daily or raise gap, but not the other way.
const HOURLY_CAP = Math.min(parseInt(process.env.ZRM_HOURLY_CAP || '120', 10), HARD_HOURLY_CEILING);
const DAILY_CAP = Math.min(parseInt(process.env.ZRM_DAILY_CAP || '400', 10), HARD_DAILY_CEILING);
const MIN_GAP_MS = Math.max(parseInt(process.env.ZRM_MIN_GAP_MS || '5000', 10), HARD_MIN_GAP_FLOOR_MS);
const MAX_GAP_MS = Math.max(parseInt(process.env.ZRM_MAX_GAP_MS || '10000', 10), MIN_GAP_MS + 2000);

// Post-flag cooldown: when the circuit breaker hits 'flagged' (one 403/captcha
// in the last 24h), every paced call refuses for 4 hours after the strike.
// This prevents the "second strike -> halted = 24h block" failure mode.
// Applied unconditionally regardless of env. Breaker state lives in
// browser.mjs's BREAKER_FILE; we read it lazily to avoid a circular import.
const POST_FLAG_COOLDOWN_MS = 4 * 3600 * 1000;
const BREAKER_FILE = `${process.env.HOME}/.shakos/chrome-profiles/zillow-rental-manager/.breaker.json`;

function ensureDir() {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
}

function readState() {
  ensureDir();
  if (!existsSync(PACING_FILE)) return { last_call_at: 0, calls: [] };
  try { return JSON.parse(readFileSync(PACING_FILE, 'utf8')); }
  catch (_) { return { last_call_at: 0, calls: [] }; }
}

function writeState(s) {
  ensureDir();
  const tmp = PACING_FILE + '.tmp';
  writeFileSync(tmp, JSON.stringify(s, null, 2));
  renameSync(tmp, PACING_FILE);
}

function pruneCalls(calls, now) {
  const dayAgo = now - 24 * 3600 * 1000;
  return calls.filter(t => t > dayAgo);
}

function jitterMs() {
  return MIN_GAP_MS + Math.floor(Math.random() * (MAX_GAP_MS - MIN_GAP_MS));
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function readBreakerSafe() {
  try {
    if (!existsSync(BREAKER_FILE)) return { state: 'healthy' };
    return JSON.parse(readFileSync(BREAKER_FILE, 'utf8'));
  } catch (_) { return { state: 'healthy' }; }
}

/**
 * Block until the next call is allowed under all pacing rules.
 * Throws if hourly/daily caps would be exceeded -- caller decides whether to
 * abort the whole run or skip the next batch.
 *
 * Also throws if the circuit breaker is 'flagged' (one 403/captcha in the
 * last 24h) and the 4-hour post-flag cooldown hasn't elapsed yet. This is
 * the most important new safety: after a flag, refusing all calls for 4h
 * gives PerimeterX time to forget us, and prevents the second-strike halt.
 *
 * intentLabel is logged but doesn't affect rate decisions. Single global queue.
 */
export async function enforceMinPacing(intentLabel = 'op') {
  // Post-flag cooldown gate -- check before anything else.
  const b = readBreakerSafe();
  if (b.state === 'flagged' && b.last_strike_at) {
    const sinceStrike = Date.now() - b.last_strike_at;
    if (sinceStrike < POST_FLAG_COOLDOWN_MS) {
      const remaining = POST_FLAG_COOLDOWN_MS - sinceStrike;
      const err = new Error(`PerimeterX flagged us ${Math.floor(sinceStrike/60000)}min ago. Mandatory ${Math.ceil(POST_FLAG_COOLDOWN_MS/3600000)}h cooldown active. ${Math.ceil(remaining/60000)}min remaining. Refusing "${intentLabel}".`);
      err.code = 'POST_FLAG_COOLDOWN';
      err.waitMs = remaining;
      throw err;
    }
  }

  const now = Date.now();
  const s = readState();
  s.calls = pruneCalls(s.calls || [], now);

  // Hard caps -- refuse, don't sleep through.
  const hourAgo = now - 3600 * 1000;
  const callsLastHour = s.calls.filter(t => t > hourAgo).length;
  const callsLastDay = s.calls.length;
  if (callsLastHour >= HOURLY_CAP) {
    const oldestInWindow = s.calls.find(t => t > hourAgo);
    const waitMs = oldestInWindow ? (oldestInWindow + 3600 * 1000) - now : 3600 * 1000;
    const err = new Error(`Hourly cap (${HOURLY_CAP}) hit. ${callsLastHour} calls in last hour. Wait ${Math.ceil(waitMs/1000)}s.`);
    err.code = 'PACING_HOURLY_CAP';
    err.waitMs = waitMs;
    throw err;
  }
  if (callsLastDay >= DAILY_CAP) {
    const err = new Error(`Daily cap (${DAILY_CAP}) hit. ${callsLastDay} calls in last 24h. Wait until tomorrow.`);
    err.code = 'PACING_DAILY_CAP';
    throw err;
  }

  // Min-gap.
  const lastAt = s.last_call_at || 0;
  const gap = jitterMs();
  const elapsed = now - lastAt;
  if (lastAt > 0 && elapsed < gap) {
    const wait = gap - elapsed;
    console.error(`[zrm pacing] sleeping ${(wait/1000).toFixed(1)}s before "${intentLabel}" (last=${(elapsed/1000).toFixed(1)}s ago, jitter target=${(gap/1000).toFixed(1)}s)`);
    await sleep(wait);
  } else if (lastAt === 0) {
    console.error(`[zrm pacing] first call this run, no wait needed before "${intentLabel}"`);
  } else {
    console.error(`[zrm pacing] last call was ${(elapsed/1000).toFixed(1)}s ago, threshold met for "${intentLabel}"`);
  }

  // Record.
  const now2 = Date.now();
  s.last_call_at = now2;
  s.calls.push(now2);
  writeState(s);
}

/**
 * Behavioral mimicry between API-relevant actions. Cheap, idempotent.
 * Random scroll + small mouse jitter. Best-effort -- exceptions swallowed.
 */
export async function humanBeat(page) {
  try {
    const x = 200 + Math.floor(Math.random() * 600);
    const y = 200 + Math.floor(Math.random() * 400);
    await page.mouse.move(x, y, { steps: 3 + Math.floor(Math.random() * 5) });
    await sleep(200 + Math.floor(Math.random() * 600));
    const dy = 200 + Math.floor(Math.random() * 400);
    await page.mouse.wheel(0, dy);
    await sleep(300 + Math.floor(Math.random() * 700));
  } catch (_) { /* swallow */ }
}

export function pacingStatus() {
  const now = Date.now();
  const s = readState();
  s.calls = pruneCalls(s.calls || [], now);
  const hourAgo = now - 3600 * 1000;
  return {
    file: PACING_FILE,
    last_call_at: s.last_call_at ? new Date(s.last_call_at).toISOString() : null,
    seconds_since_last: s.last_call_at ? Math.floor((now - s.last_call_at) / 1000) : null,
    calls_last_hour: s.calls.filter(t => t > hourAgo).length,
    calls_last_24h: s.calls.length,
    hourly_cap: HOURLY_CAP,
    daily_cap: DAILY_CAP,
    min_gap_ms: MIN_GAP_MS,
    max_gap_ms: MAX_GAP_MS
  };
}

export function resetPacing() {
  writeState({ last_call_at: 0, calls: [] });
}

/**
 * Record an externally-fired GraphQL call (e.g. a lazy-load triggered by a
 * single scroll that fires multiple requests in a burst). Just appends a
 * timestamp; does not sleep. Used by the inbox paginator to retroactively
 * account for burst-loaded pages so the hourly/daily cap stays honest.
 *
 * Throws nothing -- the call already left the wire by the time this runs.
 * Caller checks countCallsLastHour() BEFORE scrolling to decide if it's safe.
 */
export function recordExternalCall(reason = 'external') {
  const now = Date.now();
  const s = readState();
  s.calls = pruneCalls(s.calls || [], now);
  s.last_call_at = now;
  s.calls.push(now);
  writeState(s);
  console.error(`[zrm pacing] recorded external call "${reason}"; ${s.calls.filter(t => t > now - 3600*1000).length}/${HOURLY_CAP} in last hour`);
}

/**
 * Returns { callsLastHour, callsLastDay, hourlyCap, dailyCap } without
 * throwing. Used to peek at the budget before scrolling.
 */
export function peekPacing() {
  const now = Date.now();
  const s = readState();
  const calls = pruneCalls(s.calls || [], now);
  const hourAgo = now - 3600 * 1000;
  return {
    callsLastHour: calls.filter(t => t > hourAgo).length,
    callsLastDay: calls.length,
    hourlyCap: HOURLY_CAP,
    dailyCap: DAILY_CAP
  };
}
