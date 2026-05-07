// calendar.mjs — Adithya's calendar lookup + free-slot proposer.
//
// Two surfaces:
//   1. proposeTourSlots() → 3 free 30-min windows in the next ~7 days, in
//      Adithya's working hours (Austin, CT). Used by contextual-send to
//      embed concrete time options in tour-ask emails.
//   2. createTourEvent() → drop a calendar event on his primary calendar
//      when a lead confirms a slot. Used by auto-book on tour confirmation.
//
// Backed by `gog` (Adithya's Google CLI wrapper). FreeBusy API is used for
// availability (faster + respects "transparent" events vs enumerating).
//
// Eclipse account currently has a revoked OAuth token; we silently skip it
// when probing busy slots so the script keeps working off the personal
// calendar alone. Adithya refreshes tokens in his own session.

import { spawnSync } from 'node:child_process';

const PRIMARY_ACCOUNT = 'adithya.shak.kumar@gmail.com';
const SECONDARY_ACCOUNT = 'adithya@eclipse.builders';
const TZ = 'America/Chicago';
const WORK_START_HOUR = 10;   // 10am CT
const WORK_END_HOUR = 18;     // 6pm CT (last slot starts 5:30pm)
const SLOT_MIN = 30;
const BUFFER_HOURS = 18;      // first slot must be ≥18h from now (gives lead time to reply)

function gogJson(account, args, { allowEmpty = false } = {}) {
  const r = spawnSync('gog', ['-a', account, '-j', '--results-only', ...args], {
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024
  });
  if (r.status !== 0) {
    const detail = (r.stderr || r.stdout || '').trim().slice(0, 500);
    throw new Error(`gog ${args.join(' ')} (acct=${account}) failed (exit=${r.status}): ${detail}`);
  }
  const out = (r.stdout || '').trim();
  if (!out) {
    if (allowEmpty) return null;
    throw new Error(`gog ${args.join(' ')} returned empty stdout`);
  }
  try { return JSON.parse(out); }
  catch (e) { throw new Error(`gog ${args.join(' ')} returned non-JSON: ${out.slice(0, 200)}`); }
}

// Pull busy intervals for one account. Returns [] on auth failure (so the
// secondary account's revoked token doesn't kill the whole proposer).
function pullBusy(account, fromIso, toIso) {
  try {
    const resp = gogJson(account, [
      'calendar', 'freebusy',
      '--cal', 'primary',
      '--from', fromIso,
      '--to', toIso
    ]);
    return (resp?.primary?.busy || []).map(b => ({
      start: new Date(b.start).getTime(),
      end: new Date(b.end).getTime()
    }));
  } catch (e) {
    if (/invalid_grant|revoked|expired/i.test(e.message)) return [];
    throw e;
  }
}

// Given a CT (America/Chicago) anchor day, return the [startMs, endMs] of
// each 30-min slot inside [WORK_START_HOUR, WORK_END_HOUR). Quick and dirty:
// we use date math on the local server (assumes server is in CT or UTC; we
// adjust via Intl). Safer: build slot starts via Intl.DateTimeFormat with
// timeZone=TZ and reverse-lookup the UTC offset for that day.
function slotsForDay(year, month, day) {
  const slots = [];
  for (let h = WORK_START_HOUR; h < WORK_END_HOUR; h++) {
    for (let m = 0; m < 60; m += SLOT_MIN) {
      // Build a UTC timestamp that, when rendered in TZ, equals h:m on year-month-day.
      // Trick: construct a Date for the wall time at UTC, then offset by TZ's UTC offset for that local day.
      const wallUtc = Date.UTC(year, month - 1, day, h, m, 0);
      // Get TZ offset for that date by formatting and re-parsing.
      const fmt = new Intl.DateTimeFormat('en-US', {
        timeZone: TZ, hour12: false,
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        timeZoneName: 'shortOffset'
      });
      const parts = fmt.formatToParts(new Date(wallUtc));
      const offsetPart = parts.find(p => p.type === 'timeZoneName')?.value || 'GMT-5';
      const m2 = offsetPart.match(/GMT([+-])(\d{1,2}):?(\d{0,2})/);
      const sign = m2 && m2[1] === '-' ? -1 : 1;
      const oh = m2 ? parseInt(m2[2], 10) : 5;
      const om = m2 && m2[3] ? parseInt(m2[3], 10) : 0;
      const offsetMin = sign * (oh * 60 + om);
      // wallUtc represents "h:m in UTC", but we wanted "h:m in CT".
      // CT is UTC + offsetMin (negative for -5/-6), so the actual UTC instant is wallUtc - offsetMin.
      const startMs = wallUtc - offsetMin * 60 * 1000;
      slots.push({ startMs, endMs: startMs + SLOT_MIN * 60 * 1000, h, m });
    }
  }
  return slots;
}

function isBusy(slot, busy) {
  for (const b of busy) {
    if (slot.startMs < b.end && slot.endMs > b.start) return true;
  }
  return false;
}

// Format a slot for human display in CT.
function formatSlot(startMs, endMs) {
  const opts = { timeZone: TZ, weekday: 'short', month: 'short', day: 'numeric' };
  const date = new Intl.DateTimeFormat('en-US', opts).format(new Date(startMs));
  const t1 = new Intl.DateTimeFormat('en-US', { timeZone: TZ, hour: 'numeric', minute: '2-digit' }).format(new Date(startMs));
  const t2 = new Intl.DateTimeFormat('en-US', { timeZone: TZ, hour: 'numeric', minute: '2-digit' }).format(new Date(endMs));
  return `${date} ${t1}–${t2} CT`;
}

/**
 * Propose N free tour slots in Adithya's calendar.
 *
 * @param {object} [opts]
 * @param {number} [opts.count=3]   How many slots to return.
 * @param {number} [opts.daysOut=7] How far ahead to scan.
 * @returns {Array<{start_iso, end_iso, human}>}
 */
export function proposeTourSlots({ count = 3, daysOut = 7 } = {}) {
  const now = Date.now();
  const earliestMs = now + BUFFER_HOURS * 3600 * 1000;
  const fromIso = new Date(now).toISOString();
  const toIso = new Date(now + daysOut * 24 * 3600 * 1000).toISOString();

  // Pull busy from BOTH accounts (eclipse may be empty if token revoked).
  const busyPersonal = pullBusy(PRIMARY_ACCOUNT, fromIso, toIso);
  const busySecondary = pullBusy(SECONDARY_ACCOUNT, fromIso, toIso);
  const busy = [...busyPersonal, ...busySecondary];

  // Walk days; pick AT MOST one slot per day so the proposed times are
  // spread across the week (better than three slots back-to-back on day 1).
  // For variety, alternate target hours: morning, afternoon, evening.
  const targetHours = [10, 14, 17]; // try 10am, 2pm, 5pm-ish first
  const out = [];
  for (let dayOffset = 0; dayOffset < daysOut && out.length < count; dayOffset++) {
    const d = new Date(now + dayOffset * 24 * 3600 * 1000);
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' })
      .formatToParts(d);
    const y = parseInt(parts.find(p => p.type === 'year').value, 10);
    const mo = parseInt(parts.find(p => p.type === 'month').value, 10);
    const dy = parseInt(parts.find(p => p.type === 'day').value, 10);

    const slots = slotsForDay(y, mo, dy);
    // Prefer the target-hour slot for THIS pick (rotate by out.length).
    const preferredHour = targetHours[out.length % targetHours.length];
    let picked = null;
    // First try: slot at or just-after preferredHour, free, ≥buffer.
    for (const s of slots) {
      if (s.startMs < earliestMs) continue;
      if (isBusy(s, busy)) continue;
      if (s.h < preferredHour) continue;
      picked = s;
      break;
    }
    // Fallback: first free slot of the day (any hour).
    if (!picked) {
      for (const s of slots) {
        if (s.startMs < earliestMs) continue;
        if (isBusy(s, busy)) continue;
        picked = s; break;
      }
    }
    if (picked) {
      out.push({
        start_iso: new Date(picked.startMs).toISOString(),
        end_iso: new Date(picked.endMs).toISOString(),
        human: formatSlot(picked.startMs, picked.endMs)
      });
    }
  }
  return out;
}

/**
 * Create a tour calendar event on Adithya's primary calendar.
 *
 * @param {object} input
 * @param {string} input.startIso       Slot start (RFC3339).
 * @param {string} input.endIso         Slot end (RFC3339).
 * @param {string} input.leadName       For the event title.
 * @param {string} input.leadPhone      Stored on the event for FaceTime.
 * @param {string} input.listingAddress Property address.
 * @param {object} [opts]
 * @param {boolean} [opts.dryRun=false]
 * @returns {{ok, dry_run, event_id?, html_link?}}
 */
export function createTourEvent({ startIso, endIso, leadName, leadPhone, listingAddress }, { dryRun = false } = {}) {
  const summary = `Klein Ct virtual tour — ${leadName}`;
  const description = [
    `Virtual FaceTime walkthrough of ${listingAddress}.`,
    `Lead: ${leadName}`,
    leadPhone ? `Phone: ${leadPhone}` : null,
    '',
    `Plan: FaceTime the lead at the start time. Tenant on-site walks the camera; you narrate.`,
    `Front door pin code: (give to lead day-of, or pre-share if they're confident).`
  ].filter(Boolean).join('\n');

  if (dryRun) {
    return { ok: true, dry_run: true, summary, description, startIso, endIso };
  }

  const args = [
    'calendar', 'create', 'primary',
    '--summary', summary,
    '--description', description,
    '--start', startIso,
    '--end', endIso
  ];
  const resp = gogJson(PRIMARY_ACCOUNT, args);
  return {
    ok: true,
    dry_run: false,
    event_id: resp?.id || null,
    html_link: resp?.htmlLink || null,
    summary,
    startIso,
    endIso
  };
}

// --- CLI smoke test ---
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2];
  if (cmd === 'propose') {
    const slots = proposeTourSlots({ count: 3, daysOut: 7 });
    console.log(JSON.stringify(slots, null, 2));
  } else if (cmd === 'create') {
    const startIso = process.argv[3];
    const endIso = process.argv[4];
    const leadName = process.argv[5] || 'Test Lead';
    const dry = process.argv.includes('--dry');
    console.log(JSON.stringify(createTourEvent({
      startIso, endIso, leadName, leadPhone: '+15555550100',
      listingAddress: '13245 Klein Ct, Sylmar, CA 91342'
    }, { dryRun: dry }), null, 2));
  } else {
    console.error('usage: calendar.mjs propose | create <startIso> <endIso> <leadName> [--dry]');
    process.exit(2);
  }
}
