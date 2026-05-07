// auto-book.mjs -- detect "lead picked a tour time" and book + reveal.
//
// Runs BEFORE contextual-send in the cron sequence. For threads where the
// most recent inbound looks like a tour-time confirmation, we:
//   1. Ask claude -p sonnet to extract the picked time from the inbound
//      (relative to the tour slots we last proposed, persisted in the draft).
//   2. Validate against Adithya's free/busy via calendar.mjs (don't book on
//      top of an event that just landed).
//   3. createTourEvent() — drops a 30-min event on his primary calendar.
//   4. Send a "confirmed" reply via email-send that REVEALS the virtual-tour
//      context: FaceTime call, on-site tenant won't be there but the door
//      has a pin code, etc.
//   5. Mark the thread as `tour_confirmed_at` + `tour_event_id` so this
//      script + contextual-send both skip it next run.
//
// Skip rules:
//   - Bucket must be INQUIRED or TOUR_REQUESTED.
//   - last_inbound_at must be > last_outbound_at (lead has spoken since us).
//   - tour_event_id must NOT already be set on the thread.
//
// Usage:
//   node scripts/auto-book.mjs --dry [--limit N] [--cids c1,c2]
//   node scripts/auto-book.mjs --live

import { existsSync, readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

import { STATE_DIR, THREADS_DIR } from './paths.mjs';
import { readThreadState, writeThreadState } from './storage.mjs';
import { proposeTourSlots, createTourEvent } from './calendar.mjs';
import { chooseBucket } from './contextual-send.mjs';

const DRAFTS_DIR = join(STATE_DIR, 'drafts');
const BOOK_LOG_DIR = join(STATE_DIR, 'book-runs');

// Reveal context — only sent AFTER calendar event lands.
const REVEAL_BLURB = `
quick heads up — I'm not living at the property anymore but I'll FaceTime you for the tour. front door has a pin code I'll send you the morning of. my current tenant John won't be in the way, you'll get full run of the place on camera. if you've got specific things you want to see (closets, kitchen, whatever) just say the word.
`.trim();

function parseArgs(argv) {
  const out = { dry: true, limit: null, cids: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--live') out.dry = false;
    else if (a === '--dry') out.dry = true;
    else if (a === '--limit') out.limit = parseInt(argv[++i], 10);
    else if (a === '--cids') out.cids = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
  }
  return out;
}

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

function claudeAsk(prompt, { timeoutMs = 120_000 } = {}) {
  const r = spawnSync('claude', ['-p', '--model', 'sonnet'], {
    input: prompt,
    encoding: 'utf8',
    timeout: timeoutMs,
    maxBuffer: 16 * 1024 * 1024
  });
  if (r.status !== 0 || !r.stdout) {
    const detail = (r.stderr || r.error?.message || `exit=${r.status}`).slice(0, 500);
    throw new Error(`claude failed: ${detail}`);
  }
  return r.stdout.trim();
}

// Ask claude to classify the latest inbound + extract a picked slot if any.
// We deliberately ask for a tagged-line output (not JSON) because claude -p
// without explicit structured-output sometimes wraps JSON in markdown fences,
// and a 3-line tagged format is forgiving to parse and easy to validate.
function detectIntentAndSlot(thread, slotsContext) {
  const slotsList = slotsContext && slotsContext.length
    ? slotsContext.map((s, i) => `  ${i + 1}. ${s.human} (start_iso=${s.start_iso}, end_iso=${s.end_iso})`).join('\n')
    : '  (no slots were proposed)';

  const lastInbound = (thread.messages || [])
    .filter(m => m.direction === 'inbound')
    .slice(-1)[0]?.body || '';

  const recent = (thread.messages || []).slice(-6).map((m, i) => {
    const who = m.direction === 'inbound' ? (m.sender_name || 'Lead') : 'Adithya';
    return `[${i + 1}] ${who}: ${m.body}`;
  }).join('\n\n');

  const prompt = `You're parsing a rental-tour conversation. Decide if the LEAD has picked a specific tour time in their LATEST message.

PROPOSED SLOTS (we sent these in our last reply):
${slotsList}

RECENT MESSAGES:
${recent}

LATEST INBOUND (the one to classify):
"""
${lastInbound}
"""

Output EXACTLY 3 lines, no extra text, no markdown fences:
INTENT: <BOOK | NO_BOOK>
SLOT_INDEX: <1-based index of the slot they picked, or NONE>
NOTES: <one short sentence explaining your reasoning>

Rules:
- INTENT=BOOK only if the lead clearly committed to a specific time. Vague "yeah sounds good" without a time → NO_BOOK. "Friday 2pm works" with that exact time matching a slot → BOOK with the matching SLOT_INDEX.
- If they propose a NEW time not in the list, INTENT=NO_BOOK (we'll re-engage with new slots next round).
- If they ask a question or want more info, INTENT=NO_BOOK.`;

  const out = claudeAsk(prompt, { timeoutMs: 60_000 });
  const lines = out.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const get = (key) => {
    const line = lines.find(l => l.toUpperCase().startsWith(key + ':'));
    return line ? line.slice(key.length + 1).trim() : null;
  };
  const intent = (get('INTENT') || '').toUpperCase();
  const slotIdxRaw = get('SLOT_INDEX');
  const notes = get('NOTES') || '';
  const slotIdx = (() => {
    if (!slotIdxRaw || /^NONE$/i.test(slotIdxRaw)) return null;
    const n = parseInt(slotIdxRaw, 10);
    return Number.isFinite(n) && n >= 1 && n <= (slotsContext || []).length ? n : null;
  })();
  return { intent, slotIdx, notes, raw: out };
}

// Draft the "confirmed" reply: short ack + reveal blurb.
function draftConfirmedReply(thread, slot) {
  // Keep this short and human. Don't burn an LLM call — fixed template.
  const firstName = (thread.lead_name || '').trim().split(/\s+/)[0] || '';
  const opener = firstName ? `nice, ${firstName} — ` : '';
  return `${opener}got you down for ${slot.human}. ${REVEAL_BLURB}`;
}

function loadThreads(filterCids) {
  const out = [];
  const files = readdirSync(THREADS_DIR).filter(f => f.endsWith('.json'));
  for (const f of files) {
    const cid = f.replace(/\.json$/, '');
    if (filterCids && !filterCids.has(cid)) continue;
    const st = readThreadState(cid);
    if (!st) continue;
    out.push({ cid, ...st });
  }
  return out;
}

// Pull last-proposed slots from the per-cid draft (written by contextual-send).
function loadProposedSlotsForCid(cid) {
  const p = join(DRAFTS_DIR, `${cid}.json`);
  if (!existsSync(p)) return [];
  try {
    const d = JSON.parse(readFileSync(p, 'utf8'));
    return Array.isArray(d.slots_used) ? d.slots_used : [];
  } catch (_) { return []; }
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  ensureDir(BOOK_LOG_DIR);

  const filter = opts.cids ? new Set(opts.cids) : null;
  let threads = loadThreads(filter);

  // Apply skip rules.
  threads = threads.filter(t => {
    if (!t.lead_reference_email) return false;
    if (t.tour_event_id) return false;
    const inboundMs = t.last_inbound_at ? Date.parse(t.last_inbound_at) : 0;
    const outboundMs = t.last_outbound_at ? Date.parse(t.last_outbound_at) : 0;
    if (!inboundMs || outboundMs >= inboundMs) return false;
    const bucket = chooseBucket(t);
    if (bucket !== 'INQUIRED' && bucket !== 'TOUR_REQUESTED') return false;
    return true;
  });

  if (opts.limit) threads = threads.slice(0, opts.limit);

  console.error(`[auto-book] scanning ${threads.length} candidate threads, dry=${opts.dry}`);

  // Compute "fresh" slots once — used as a fallback if a thread has no
  // proposed slots persisted yet (first-touch INQUIRED leads who replied
  // before we could send our initial proposal).
  let freshSlots = [];
  try {
    freshSlots = proposeTourSlots({ count: 3, daysOut: 7 });
  } catch (e) {
    console.error(`[auto-book] WARN: calendar lookup failed (${e.message})`);
  }

  const runId = `run-${new Date().toISOString().replace(/[:.]/g, '-')}`;
  const logPath = join(BOOK_LOG_DIR, `${runId}.ndjson`);
  const summary = { booked: 0, no_book: 0, errors: 0 };

  for (let i = 0; i < threads.length; i++) {
    const t = threads[i];
    const proposedSlots = loadProposedSlotsForCid(t.cid);
    const slotsContext = proposedSlots.length ? proposedSlots : freshSlots;

    console.error(`\n[${i + 1}/${threads.length}] cid=${t.cid} name="${t.lead_name}" slots_in_ctx=${slotsContext.length}`);
    let detection;
    try {
      detection = detectIntentAndSlot(t, slotsContext);
    } catch (e) {
      summary.errors++;
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, error: e.message }) + '\n', { flag: 'a' });
      console.error(`  DETECT ERROR: ${e.message}`);
      continue;
    }

    console.error(`  intent=${detection.intent} slot=${detection.slotIdx} notes=${detection.notes}`);

    if (detection.intent !== 'BOOK' || !detection.slotIdx) {
      summary.no_book++;
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, action: 'no_book', detection }) + '\n', { flag: 'a' });
      continue;
    }

    const slot = slotsContext[detection.slotIdx - 1];
    if (!slot) {
      summary.errors++;
      console.error(`  ERROR: detection returned slot ${detection.slotIdx} but slotsContext has only ${slotsContext.length}`);
      continue;
    }

    // Create calendar event (gated by --live).
    let evt;
    try {
      evt = createTourEvent({
        startIso: slot.start_iso,
        endIso: slot.end_iso,
        leadName: t.lead_name || 'Klein Ct lead',
        leadPhone: t.lead_phone || null,
        listingAddress: t.listing_address || '13245 Klein Ct, Sylmar, CA 91342'
      }, { dryRun: opts.dry });
    } catch (e) {
      summary.errors++;
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, action: 'event_create_failed', error: e.message }) + '\n', { flag: 'a' });
      console.error(`  EVENT CREATE FAILED: ${e.message}`);
      continue;
    }

    // Draft + send reveal reply.
    const body = draftConfirmedReply(t, slot);
    if (opts.dry) {
      console.error(`  DRY booked ${slot.human}, would send reveal reply (${body.length} chars)`);
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, action: 'dry_book', slot, body }) + '\n', { flag: 'a' });
      summary.booked++;
      continue;
    }

    try {
      const { sendViaEmail } = await import('./email-send.mjs');
      const r = await sendViaEmail(t.cid, body, { dryRun: false });
      // Patch thread state with tour confirmation.
      const fresh = readThreadState(t.cid) || t;
      fresh.tour_event_id = evt.event_id || null;
      fresh.tour_event_link = evt.html_link || null;
      fresh.tour_slot_iso = slot.start_iso;
      fresh.tour_confirmed_at = new Date().toISOString();
      writeThreadState(t.cid, fresh);
      summary.booked++;
      console.error(`  BOOKED + sent reveal: ${slot.human} event=${evt.event_id || '?'} gmail=${r.gmail_message_id || '?'}`);
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, action: 'booked', slot, event_id: evt.event_id, gmail_message_id: r.gmail_message_id }) + '\n', { flag: 'a' });
    } catch (e) {
      summary.errors++;
      writeFileSync(logPath, JSON.stringify({ cid: t.cid, action: 'reveal_send_failed', error: e.message, event_id: evt.event_id }) + '\n', { flag: 'a' });
      console.error(`  REVEAL SEND FAILED (event already created!): ${e.message}`);
    }
  }

  console.error(`\n[auto-book] done. booked=${summary.booked} no_book=${summary.no_book} errors=${summary.errors}`);
  console.error(`[auto-book] log -> ${logPath}`);
}

main().catch((e) => {
  console.error('[auto-book] FATAL', e);
  process.exit(1);
});
