// contextual-send.mjs -- per-lead status-routed reply generation + send.
//
// Reads each lead's thread state, picks a "bucket" by status_label, generates
// a status-appropriate reply (claude -p sonnet), and either:
//   - dry-run (default): saves draft to state/drafts/<cid>.json for review
//   - --live:           also sends via the convo.zillow.com gmail relay
//
// Buckets (and goal):
//   INQUIRED        → propose 3 calendar slots, ask which works
//   TOUR_REQUESTED  → if lead picked a slot, hand off to auto-book; else
//                     re-propose 3 fresh slots
//   POST_TOUR       → push them to apply (Zillow application link)
//   APPLIED         → SKIP (application-notifier handles this bucket)
//   WITHDRAWN       → SKIP (no action, lead is gone)
//
// Skip rules across all buckets:
//   - Skip if last_outbound_at >= last_inbound_at (already replied since
//     they last spoke; nothing to do until they respond)
//   - Skip if no relay address (can't email)
//
// Virtual-tour reveal staging: the FaceTime / pin-code / on-site-tenant
// context lives in auto-book.mjs and is sent ONLY after a calendar event is
// created. This script never mentions it.
//
// Usage:
//   node scripts/contextual-send.mjs --dry [--limit N] [--only-bucket B] [--cids c1,c2]
//   node scripts/contextual-send.mjs --live [--limit N] [--cids c1,c2]

import { existsSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

import { STATE_DIR, THREADS_DIR } from './paths.mjs';
import { readThreadState } from './storage.mjs';
import { proposeTourSlots } from './calendar.mjs';

const DRAFTS_DIR = join(STATE_DIR, 'drafts');

const PROPERTY_FACTS = `
- 13245 Klein Ct, Sylmar, CA 91342
- 4 rooms still open. Pricing:
  * Two 3rd-floor rooms with walk-in closets, shared bath: $1,000/mo
  * 2nd-floor room with private bathroom: $1,200/mo
  * 1st-floor private suite (attached bath + walk-in closet): $1,250/mo
- Utilities: flat $100/mo per room (water, electric, gas, internet)
- W/D in unit, full Samsung kitchen, central AC/heat, private patio
- Dog park + community pool nearby
- Pets welcome, non-smoking
- Current roommate: John, 40 yo, quiet and chill
- Parking is an optional add-on
- Application link: https://www.zillow.com/renter-hub/applications/listing/258vhr7ge6q56/rental-application/?itc=rentalhdpapplynow ($25 fee, 2-3 references)
- Move-in: rooms are ready immediately
`.trim();

const VOICE_GUIDE = `
You are Adithya, a 30-year-old landlord. You're casual, direct, confident.
- Write like you're texting a friend who's interested in the place.
- No corporate-speak. No excessive politeness. No em dashes.
- Short sentences. Plain words.
- One ask per message. Move them forward.
- Don't repeat info they've already heard in this thread.
- Don't sign off with "Best," or "Thanks!" — just end the sentence.
`.trim();

// Per-bucket goal directives. The LLM gets these on top of voice + facts +
// history, so the same prompt machinery routes by status.
const BUCKET_GOALS = {
  INQUIRED: `
GOAL: Get them to commit to a tour. Propose 2-3 specific times (provided below) and ask which works. Tours are virtual — you'll FaceTime them. DO NOT mention FaceTime or virtual yet; just call it "a tour" or "swing by". Reveal happens later.
`.trim(),
  TOUR_REQUESTED: `
GOAL: Lock in a specific tour time. If their last message picked a slot, confirm it back to them. If they're still vague, re-propose the slots provided below and push for a pick.
`.trim(),
  POST_TOUR: `
GOAL: Get them to apply. Reference that the tour happened, ask if they're ready to apply. Mention the $25 fee and the 2-3 references upfront so there are no surprises. Drop the application link at the end.
`.trim()
};

function parseArgs(argv) {
  const out = { dry: true, limit: null, onlyBucket: null, cids: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--live') out.dry = false;
    else if (a === '--dry') out.dry = true;
    else if (a === '--limit') out.limit = parseInt(argv[++i], 10);
    else if (a === '--only-bucket') out.onlyBucket = argv[++i].toUpperCase();
    else if (a === '--cids') out.cids = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
  }
  return out;
}

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

// Map thread state to bucket. Multi-signal: status_label is the strongest
// hint when present, but we also infer POST_TOUR from tour_event_id +
// tour_slot_iso since Gmail-first ingest no longer surfaces Zillow's TOURED
// status (was portal-only).
//
// Null status treated as INQUIRED (initial inquiry, no movement yet).
export function chooseBucket(thread) {
  const sl = (thread.status_label || '').toUpperCase();
  if (sl.startsWith('APPLICATION')) return 'APPLIED'; // RECEIVED, WITHDRAWN, etc.
  // POST_TOUR signal: we booked a tour, the slot has passed, no app yet.
  if (thread.tour_event_id && thread.tour_slot_iso) {
    const slotMs = Date.parse(thread.tour_slot_iso);
    if (slotMs && slotMs < Date.now() - 30 * 60 * 1000) {
      // Tour was at least 30 min ago — they should have toured by now.
      return 'POST_TOUR';
    }
  }
  if (sl === 'TOUR REQUESTED' || sl === 'TOUR_REQUESTED') return 'TOUR_REQUESTED';
  if (sl === 'TOURED') return 'POST_TOUR';
  return 'INQUIRED';
}

// Should we even draft? Skip if we already replied since their last message.
function shouldDraft(thread) {
  const inboundMs = thread.last_inbound_at ? Date.parse(thread.last_inbound_at) : 0;
  const outboundMs = thread.last_outbound_at ? Date.parse(thread.last_outbound_at) : 0;
  // No inbound at all — nothing to reply to.
  if (!inboundMs) return false;
  // We already replied after their last message — wait for them.
  if (outboundMs >= inboundMs) return false;
  return true;
}

function renderConversation(messages) {
  if (!messages || !messages.length) return '(no messages yet — this is the initial inquiry)';
  return messages.map((m, i) => {
    const who = m.direction === 'inbound' ? `${m.sender_name || 'Lead'}` : 'Adithya';
    const when = m.ts_iso ? m.ts_iso.slice(0, 10) : '';
    return `[${i + 1}] ${who} (${when}): ${m.body}`;
  }).join('\n\n');
}

function summarizeRenterProfile(profile) {
  if (!profile || typeof profile !== 'object') return '(no renter profile data)';
  const lines = [];
  if (profile.credit) lines.push(`credit: ${profile.credit}`);
  if (profile.incomeYearlyRange) lines.push(`income: ${profile.incomeYearlyRange}`);
  if (profile.moveInDate) lines.push(`wants move-in: ${profile.moveInDate}`);
  if (profile.numOccupants) lines.push(`occupants: ${profile.numOccupants}`);
  if (profile.numBedrooms) lines.push(`bedrooms wanted: ${profile.numBedrooms}`);
  if (profile.leaseLengthMonths) lines.push(`lease length: ${profile.leaseLengthMonths} mo`);
  if (profile.desiredParking) lines.push(`parking: ${profile.desiredParking}`);
  if (Array.isArray(profile.petDetails) && profile.petDetails.length) {
    lines.push(`pets: ${profile.petDetails.length}`);
  }
  return lines.length ? lines.join(', ') : '(profile present but empty)';
}

function renderSlots(slots) {
  if (!slots || !slots.length) return '(no calendar slots available — leave a generic "let me know what works" ask)';
  return slots.map((s, i) => `  ${i + 1}. ${s.human}`).join('\n');
}

function buildPrompt(thread, bucket, slots) {
  const { lead_name, status_label, renter_profile, messages } = thread;
  const slotsBlock = (bucket === 'INQUIRED' || bucket === 'TOUR_REQUESTED')
    ? `\nAVAILABLE TIMES (your calendar is free in these windows — propose THESE specifically, not generic):\n${renderSlots(slots)}\n`
    : '';
  return `${VOICE_GUIDE}

PROPERTY FACTS (use only what's relevant — don't dump):
${PROPERTY_FACTS}

LEAD: ${lead_name || '(unknown)'}
CURRENT STATUS: ${status_label || 'INQUIRED'} (bucket: ${bucket})
RENTER PROFILE: ${summarizeRenterProfile(renter_profile)}
${slotsBlock}
${BUCKET_GOALS[bucket]}

CONVERSATION HISTORY:
${renderConversation(messages)}

YOUR TASK: Write the next reply from Adithya. Address the lead's last message directly. Drive toward the bucket goal above.

Length: 1-4 short sentences typically. Match the energy of their last message.

OUTPUT: just the reply body. No quotes around it. No "Hi <name>!" greeting required if the conversation is mid-stream.`;
}

function claudeAsk(prompt, { timeoutMs = 180_000 } = {}) {
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
  return { engine: 'claude-sonnet', text: r.stdout.trim() };
}

function loadAllThreads() {
  const out = [];
  const files = readdirSync(THREADS_DIR).filter(f => f.endsWith('.json'));
  for (const f of files) {
    const cid = f.replace(/\.json$/, '');
    const st = readThreadState(cid);
    if (!st) continue;
    out.push({ cid, ...st });
  }
  return out;
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  ensureDir(DRAFTS_DIR);

  let threads = loadAllThreads();
  if (opts.cids) {
    const set = new Set(opts.cids);
    threads = threads.filter(t => set.has(t.cid));
  }

  // Bucketize and apply skip rules.
  const tagged = threads.map(t => ({ ...t, bucket: chooseBucket(t) }));
  const skips = { no_relay: 0, already_replied: 0, applied_bucket: 0 };
  let work = tagged.filter(t => {
    if (!t.lead_reference_email) { skips.no_relay++; return false; }
    if (t.bucket === 'APPLIED') { skips.applied_bucket++; return false; }
    if (!shouldDraft(t)) { skips.already_replied++; return false; }
    return true;
  });
  if (opts.onlyBucket) work = work.filter(t => t.bucket === opts.onlyBucket);
  if (opts.limit) work = work.slice(0, opts.limit);

  const bucketCounts = {};
  for (const t of work) bucketCounts[t.bucket] = (bucketCounts[t.bucket] || 0) + 1;

  console.error(`[contextual-send] ${threads.length} threads total, ${work.length} need replies, dry=${opts.dry}`);
  console.error(`[contextual-send] skips: ${JSON.stringify(skips)}`);
  console.error(`[contextual-send] buckets: ${JSON.stringify(bucketCounts)}`);

  // Pull calendar slots ONCE (shared across all tour-bucket threads).
  let slots = [];
  if (work.some(t => t.bucket === 'INQUIRED' || t.bucket === 'TOUR_REQUESTED')) {
    try {
      slots = proposeTourSlots({ count: 3, daysOut: 7 });
      console.error(`[contextual-send] proposed ${slots.length} calendar slots: ${slots.map(s => s.human).join(' | ')}`);
    } catch (e) {
      console.error(`[contextual-send] WARN: calendar lookup failed (${e.message}); falling back to generic ask`);
    }
  }

  const indexPath = join(DRAFTS_DIR, `index-${new Date().toISOString().replace(/[:.]/g, '-')}.ndjson`);
  const summary = { generated: 0, sent: 0, failed: 0 };

  for (let i = 0; i < work.length; i++) {
    const t = work[i];
    console.error(`\n[${i + 1}/${work.length}] cid=${t.cid} bucket=${t.bucket} name="${t.lead_name}"`);
    let body, engine;
    try {
      const prompt = buildPrompt(t, t.bucket, slots);
      const res = claudeAsk(prompt, { timeoutMs: 180_000 });
      body = res.text;
      engine = res.engine;
      if (!body) throw new Error('claude returned empty body');
    } catch (e) {
      summary.failed++;
      writeFileSync(join(DRAFTS_DIR, `${t.cid}-error.json`), JSON.stringify({ cid: t.cid, error: e.message, bucket: t.bucket }, null, 2));
      console.error(`  LLM ERROR: ${e.message}`);
      continue;
    }
    summary.generated++;

    const draft = {
      cid: t.cid,
      lead_name: t.lead_name,
      status_label: t.status_label,
      bucket: t.bucket,
      relay: t.lead_reference_email,
      body,
      engine,
      generated_at: new Date().toISOString(),
      message_count: (t.messages || []).length,
      slots_used: (t.bucket === 'INQUIRED' || t.bucket === 'TOUR_REQUESTED') ? slots : []
    };
    writeFileSync(join(DRAFTS_DIR, `${t.cid}.json`), JSON.stringify(draft, null, 2));
    writeFileSync(indexPath, JSON.stringify(draft) + '\n', { flag: 'a' });
    console.error(`  draft saved (${body.length} chars): ${body.replace(/\s+/g, ' ').slice(0, 90)}...`);

    if (!opts.dry) {
      try {
        const { sendViaEmail } = await import('./email-send.mjs');
        const r = await sendViaEmail(t.cid, body, { dryRun: false });
        summary.sent++;
        console.error(`  SENT via email-relay gmail=${r.gmail_message_id || '?'}`);
      } catch (e) {
        summary.failed++;
        console.error(`  SEND FAILED: ${e.message}`);
      }
    }
  }

  console.error(`\n[contextual-send] done. generated=${summary.generated} sent=${summary.sent} failed=${summary.failed}`);
}

// Only run main when invoked directly, not on import (auto-book and
// application-notifier import chooseBucket).
const isMain = (() => {
  try { return process.argv[1] && import.meta.url === `file://${process.argv[1]}`; }
  catch (_) { return false; }
})();
if (isMain) {
  main().catch((e) => {
    console.error('[contextual-send] FATAL', e);
    process.exit(1);
  });
}
