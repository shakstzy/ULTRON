// contextual-send.mjs -- per-lead contextual reply generation + send.
//
// Reads each lead's .md (which carries the full conversation history + status
// + renter profile after pull-inbox), prompts gemini-3-pro-preview to write
// the next reply in Adithya's voice, then either:
//   - dry-run (default): saves the draft to state/drafts/<cid>.json for review
//   - --live:           also sends via the convo.zillow.com gmail relay
//
// Usage:
//   node scripts/contextual-send.mjs --dry [--limit N] [--only-status S]
//   node scripts/contextual-send.mjs --live [--limit N] [--cids c1,c2]
//
// One LLM call per lead. Sequential. Account-cycling via cloud-llm is
// premature at 100-call scale; revisit if quotas bite.

import { existsSync, readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

import {
  STATE_DIR,
  THREADS_DIR,
  LEADS_DIR
} from './paths.mjs';
import { readThreadState } from './storage.mjs';

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
- One ask per message. Move them forward (tour, application, decision).
- Don't repeat info they've already heard in this thread.
- Don't sign off with "Best," or "Thanks!" — just end the sentence.
`.trim();

function parseArgs(argv) {
  const out = { dry: true, limit: null, onlyStatus: null, cids: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--live') out.dry = false;
    else if (a === '--dry') out.dry = true;
    else if (a === '--limit') out.limit = parseInt(argv[++i], 10);
    else if (a === '--only-status') out.onlyStatus = argv[++i];
    else if (a === '--cids') out.cids = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
  }
  return out;
}

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

// Render the conversation history in a compact form for the LLM.
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

function buildPrompt(thread) {
  const { lead_name, status_label, renter_profile, messages } = thread;
  return `${VOICE_GUIDE}

PROPERTY FACTS (use only what's relevant to THIS lead — don't dump):
${PROPERTY_FACTS}

LEAD: ${lead_name || '(unknown)'}
CURRENT STATUS: ${status_label || 'INQUIRED'}
RENTER PROFILE: ${summarizeRenterProfile(renter_profile)}

CONVERSATION HISTORY:
${renderConversation(messages)}

YOUR TASK: Write the next reply from Adithya. Take into account the lead's status, what they've already said, and what makes sense to say next given where the conversation is. If the conversation has gone quiet, re-engage. If they asked a specific question, answer it. If they're ready to apply or tour, push that forward.

Length: 1-4 short sentences typically. Match the energy of their last message.

OUTPUT: just the reply body. No quotes around it. No "Hi <name>!" greeting required if the conversation is mid-stream.`;
}

// Direct claude -p sonnet for the drafting. Gemini is reserved for visual
// tasks per Adithya 2026-05-06 (claude is the better writer for voice +
// style; gemini was burning prompt routing on a task it's not best at).
// `claude -p` reads the prompt from argv or stdin and prints the response
// to stdout. Eats the Max weekly cap; revisit if we hit it.
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
  // Filter.
  if (opts.cids) {
    const set = new Set(opts.cids);
    threads = threads.filter(t => set.has(t.cid));
  }
  if (opts.onlyStatus) {
    threads = threads.filter(t => (t.status_label || '').toUpperCase() === opts.onlyStatus.toUpperCase());
  }
  // Skip threads with no relay (can't email-send).
  threads = threads.filter(t => {
    if (!t.lead_reference_email) {
      console.error(`[skip ${t.cid}] no convo.zillow.com relay captured`);
      return false;
    }
    return true;
  });

  if (opts.limit) threads = threads.slice(0, opts.limit);

  console.error(`[contextual-send] ${threads.length} threads, dry=${opts.dry}`);

  const indexPath = join(DRAFTS_DIR, `index-${new Date().toISOString().replace(/[:.]/g, '-')}.ndjson`);
  const summary = { generated: 0, sent: 0, failed: 0 };

  for (let i = 0; i < threads.length; i++) {
    const t = threads[i];
    console.error(`\n[${i + 1}/${threads.length}] cid=${t.cid} status=${t.status_label} name="${t.lead_name}"`);
    let body, engine;
    try {
      const prompt = buildPrompt(t);
      const res = claudeAsk(prompt, { timeoutMs: 180_000 });
      body = res.text;
      engine = res.engine;
      if (!body) throw new Error('claude returned empty body');
    } catch (e) {
      summary.failed++;
      writeFileSync(join(DRAFTS_DIR, `${t.cid}-error.json`), JSON.stringify({ cid: t.cid, error: e.message }, null, 2));
      console.error(`  LLM ERROR: ${e.message}`);
      continue;
    }
    summary.generated++;

    const draft = {
      cid: t.cid,
      lead_name: t.lead_name,
      status_label: t.status_label,
      relay: t.lead_reference_email,
      body,
      engine,
      generated_at: new Date().toISOString(),
      message_count: (t.messages || []).length
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
  console.error(`[contextual-send] drafts -> ${DRAFTS_DIR}`);
  console.error(`[contextual-send] index -> ${indexPath}`);
}

main().catch((e) => {
  console.error('[contextual-send] FATAL', e);
  process.exit(1);
});
