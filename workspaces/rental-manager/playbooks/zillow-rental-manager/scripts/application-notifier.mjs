// application-notifier.mjs -- iMessage Adithya when new applications land.
//
// Sweeps thread state for APPLICATION_RECEIVED leads we haven't notified
// about yet. Groups them into a single iMessage so a daily ingest with 4
// new apps becomes one ping, not four.
//
// Bucket detail (mirrors contextual-send.chooseBucket):
//   - "APPLICATION RECEIVED" → notify
//   - "APPLICATION WITHDRAWN" → ignore (lead pulled it)
//   - everything else → ignore
//
// Idempotency state lives at state/application-notifier.json:
//   { notified: { <cid>: { last_status: <label>, notified_at: <iso> } } }
//
// We re-notify a cid only if the status_label changed (e.g. WITHDRAWN
// → RECEIVED, the lead resubmitted). Fresh APPLIED stays silent on
// subsequent runs.
//
// iMessage uses the imessage skill via send.sh. Recipient is hardcoded to
// Adithya's primary cell (his contact phone in the global entity stub).
//
// Usage:
//   node scripts/application-notifier.mjs --dry
//   node scripts/application-notifier.mjs --live

import { existsSync, readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

import { STATE_DIR, THREADS_DIR } from './paths.mjs';
import { readThreadState } from './storage.mjs';

const STATE_FILE = join(STATE_DIR, 'application-notifier.json');
const ADITHYA_PHONE = '+15126601911';
const SEND_SH = '/Users/shakstzy/ULTRON/_shell/skills/imessage/send.sh';

function parseArgs(argv) {
  const out = { dry: true };
  for (const a of argv) {
    if (a === '--live') out.dry = false;
    else if (a === '--dry') out.dry = true;
  }
  return out;
}

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

function loadState() {
  if (!existsSync(STATE_FILE)) return { notified: {} };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); }
  catch (_) { return { notified: {} }; }
}

function saveState(state) {
  ensureDir(STATE_DIR);
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function loadAppliedThreads() {
  const out = [];
  const files = readdirSync(THREADS_DIR).filter(f => f.endsWith('.json'));
  for (const f of files) {
    const cid = f.replace(/\.json$/, '');
    const st = readThreadState(cid);
    if (!st) continue;
    const label = (st.status_label || '').toUpperCase();
    if (label === 'APPLICATION RECEIVED') {
      out.push({ cid, ...st });
    }
  }
  return out;
}

function sendImessage(text, { dry }) {
  if (dry) {
    console.error(`[application-notifier] DRY iMessage to ${ADITHYA_PHONE}:\n---\n${text}\n---`);
    return { ok: true, dry: true };
  }
  const r = spawnSync(SEND_SH, ['--to', ADITHYA_PHONE, '--text', text], {
    encoding: 'utf8',
    timeout: 30_000
  });
  if (r.status !== 0) {
    const detail = (r.stderr || r.stdout || '').trim().slice(0, 500);
    throw new Error(`send.sh failed (exit=${r.status}): ${detail}`);
  }
  return { ok: true, dry: false, raw: r.stdout.trim() };
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const state = loadState();
  const applied = loadAppliedThreads();

  // Pick threads that are NEW since our last notification: not in state, or
  // status changed (e.g. WITHDRAWN → RECEIVED resubmission).
  const fresh = [];
  for (const t of applied) {
    const prior = state.notified[t.cid];
    if (!prior || prior.last_status !== t.status_label) fresh.push(t);
  }

  console.error(`[application-notifier] ${applied.length} APPLICATION RECEIVED total, ${fresh.length} new since last ping`);

  if (!fresh.length) return;

  // Build the message. Keep it short; one line per applicant.
  const lines = [
    `🏠 ${fresh.length} new Klein Ct application${fresh.length === 1 ? '' : 's'} to review:`,
    ...fresh.map(t => `• ${t.lead_name || '(unknown)'}${t.lead_phone ? ` (${t.lead_phone})` : ''}`),
    '',
    'Review at: https://www.zillow.com/rental-manager/applications'
  ];
  const text = lines.join('\n');

  try {
    const r = sendImessage(text, { dry: opts.dry });
    console.error(`[application-notifier] ${r.dry ? 'dry-run' : 'sent'} ok`);
  } catch (e) {
    console.error(`[application-notifier] ERROR sending: ${e.message}`);
    process.exit(1);
  }

  // Mark them all notified (only if not dry).
  if (!opts.dry) {
    const now = new Date().toISOString();
    for (const t of fresh) {
      state.notified[t.cid] = { last_status: t.status_label, notified_at: now };
    }
    saveState(state);
  }
}

main();
