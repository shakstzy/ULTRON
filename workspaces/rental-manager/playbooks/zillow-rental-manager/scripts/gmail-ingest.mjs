// gmail-ingest.mjs — primary lead-discovery + thread-sync via Gmail.
//
// Replaces the PerimeterX-blocked Zillow portal scraper. Every renter
// message arrives in Adithya's Gmail from a per-conversation alias
// `<token>@convo.zillow.com`; replies sent via gog round-trip back through
// Zillow's relay to the renter AND mirror into the portal thread, so the
// renter still sees their conversation in Zillow's UI. The portal is no
// longer required for ingest.
//
// Pipeline:
//   1. Search Gmail for `from:convo.zillow.com` threads.
//   2. Group messages by Gmail threadId — each = one Zillow conversation.
//   3. Build relay->cid mapping from existing state/threads/*.json so new
//      Gmail threads attach to existing Zillow cids (no duplicates).
//   4. For each thread, write/update state/threads/<cid>.json + raw lead
//      markdown.
//   5. Detect APPLICATION RECEIVED via `from:no-reply@comet.zillow.com`
//      "rental application" notifications. Match back to threads by listing
//      address.
//
// What we drop (vs portal scraper):
//   - Zillow-side status_label (TOUR REQUESTED, TOURED) — we infer from
//     subject pattern + message content via downstream LLM routing.
//   - Structured renter profile (credit, income, move-in) — never used for
//     drafting anyway; LLM works fine without.
//   - Application PDF download — defer until the user asks for it.
//
// Idempotent. Cursor-less for v1 (Gmail is fast enough at 100-thread scale).
// Future: track historyId for incremental sync.
//
// Usage:
//   node scripts/gmail-ingest.mjs [--days 60] [--limit N] [--dry]

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

import { THREADS_DIR } from './paths.mjs';
import {
  readThreadState, writeThreadState, writeLeadMarkdown,
  appendObservation, toLowerEmail
} from './storage.mjs';

const OWNER_EMAIL = process.env.ZRM_OWNER_EMAIL || 'adithya.shak.kumar@gmail.com';
const LISTING_ADDRESS = '13245 Klein Ct, Sylmar, CA 91342';
const LISTING_ALIAS = '258vhr7ge6q56';

function parseArgs(argv) {
  const out = { days: 60, limit: null, dry: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--days') out.days = parseInt(argv[++i], 10);
    else if (a === '--limit') out.limit = parseInt(argv[++i], 10);
    else if (a === '--dry') out.dry = true;
  }
  return out;
}

function gogJson(args, { allowEmpty = false } = {}) {
  const r = spawnSync('gog', ['-a', OWNER_EMAIL, '-j', '--results-only', ...args], {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024  // some thread payloads are large
  });
  if (r.status !== 0) {
    const detail = (r.stderr || r.stdout || '').trim().slice(0, 500);
    throw new Error(`gog ${args.slice(0,4).join(' ')}... failed (exit=${r.status}): ${detail}`);
  }
  const out = (r.stdout || '').trim();
  if (!out) {
    if (allowEmpty) return null;
    throw new Error(`gog ${args.slice(0,4).join(' ')}... returned empty stdout`);
  }
  try { return JSON.parse(out); }
  catch (e) { throw new Error(`gog non-JSON: ${out.slice(0, 200)}`); }
}

// Parse "Display Name <email@host>" → { name, email }. Falls back when bare.
function parseAddress(raw) {
  if (!raw) return { name: null, email: null };
  const m = raw.match(/^\s*"?([^"<]*?)"?\s*<([^>]+)>\s*$/);
  if (m) return { name: m[1].trim() || null, email: m[2].trim().toLowerCase() };
  return { name: null, email: raw.trim().toLowerCase() };
}

function headersToMap(headers) {
  const out = {};
  for (const h of headers || []) out[h.name.toLowerCase()] = h.value;
  return out;
}

// Extract the lead's actual message text from a Zillow relay email body.
// Zillow puts the message as preview chrome in a hidden <span>:
//   <span style="display: none ...">{message}</span>
// That span is the cleanest source. Falls back to gmail snippet if not found.
function extractRenterBody(htmlBody, snippet) {
  if (htmlBody) {
    const spanRe = /<span[^>]*display\s*:\s*none[^>]*>([\s\S]*?)<\/span>/i;
    const m = htmlBody.match(spanRe);
    if (m) {
      const stripped = m[1]
        .replace(/<[^>]+>/g, ' ')
        .replace(/&nbsp;/gi, ' ')
        .replace(/&amp;/gi, '&')
        .replace(/&lt;/gi, '<')
        .replace(/&gt;/gi, '>')
        .replace(/&quot;/gi, '"')
        .replace(/&#39;/gi, "'")
        .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCharCode(parseInt(h, 16)))
        .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(parseInt(d, 10)))
        .replace(/\s+/g, ' ')
        .trim();
      if (stripped.length > 0) return stripped;
    }
  }
  // Fallback: gmail snippet (already plaintext, ~200 char). Strip Zillow chrome
  // "New message from a renter / Regarding your listing at: ..." that bleeds in.
  if (snippet) {
    let s = String(snippet);
    s = s.replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, '&');
    s = s.split(/New message from a renter|Regarding your listing at/i)[0].trim();
    return s || null;
  }
  return null;
}

// First-name extractor from the convo subject template:
//   "<Name> is requesting (information|an application) about <listing>"
//   "Re: <Name> is requesting ..."
function leadNameFromSubject(subject) {
  if (!subject) return null;
  const m = subject.match(/^(?:Re:\s*)*([A-Za-z][^]*?)\s+is\s+requesting/i);
  return m ? m[1].trim() : null;
}

// Subject hints at status. NB: "requesting an application" = lead pursued the
// app link from the listing — they're warmer than initial-INQUIRED.
function statusHintFromSubject(subject) {
  if (!subject) return 'INQUIRED';
  const s = subject.toLowerCase();
  if (/requesting an application/.test(s)) return 'TOUR REQUESTED';
  if (/requesting information/.test(s)) return 'INQUIRED';
  return 'INQUIRED';
}

// Normalize timestamp (RFC2822 Date header) to ms + iso.
function parseGmailDate(d) {
  if (!d) return { ts_ms: 0, ts_iso: null };
  const t = Date.parse(d);
  if (!t) return { ts_ms: 0, ts_iso: null };
  return { ts_ms: t, ts_iso: new Date(t).toISOString() };
}

function sha256Hex(s) {
  return createHash('sha256').update(s).digest('hex');
}

// Build relay -> cid map from existing state (for continuity with the 68
// portal-ingested threads). New Gmail threads with no matching relay get a
// synthetic cid `gmail-<threadId>`.
function buildRelayToCidMap() {
  const map = new Map();
  if (!existsSync(THREADS_DIR)) return map;
  for (const f of readdirSync(THREADS_DIR).filter(f => f.endsWith('.json'))) {
    const cid = f.replace(/\.json$/, '');
    const st = readThreadState(cid);
    if (st?.lead_reference_email) {
      map.set(st.lead_reference_email.toLowerCase(), cid);
    }
  }
  return map;
}

// Pull recent applications-received notifications. Returns Set<lead-name-lc>
// — best we can do without portal — and Set<relay-email> for thread-keyed.
function pullApplicationReceivedSignals(days) {
  const since = `newer_than:${days}d`;
  const search = `from:no-reply@comet.zillow.com (subject:"new rental application" OR subject:"rental application waiting") ${since}`;
  let list;
  try { list = gogJson(['gmail', 'messages', 'list', search, '--max', '100'], { allowEmpty: true }) || []; }
  catch (e) {
    appendObservation({ kind: 'gmail-ingest-comet-search-failed', error: e.message });
    return { byName: new Set() };
  }
  const byName = new Set();
  for (const m of list) {
    const subj = m.subject || '';
    // The subject is "Rental application waiting for <addr>" or "You have a
    // new rental application for <addr>" — the lead name isn't in the subject
    // for these. We need the body. Skip if not the right listing.
    if (!subj.toLowerCase().includes(LISTING_ADDRESS.split(',')[0].toLowerCase().trim())) continue;
    // Best-effort: parse the body to extract the renter name.
    try {
      const full = gogJson(['gmail', 'get', m.id], { allowEmpty: true });
      const body = full?.body || '';
      // Comet emails have "Hi Adithya, <Name> has applied" or similar.
      const nm = body.match(/applied for\s+[^.]*?\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/) ||
                 body.match(/<strong>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)<\/strong>\s*has\s+applied/i) ||
                 body.match(/applied to rent your property[^A-Z]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/);
      if (nm) byName.add(nm[1].toLowerCase());
    } catch (_) { /* swallow, best-effort */ }
  }
  return { byName };
}

// List all Gmail threads tied to this listing's relay aliases.
function listConvoThreads(days, limit) {
  const search = `from:convo.zillow.com newer_than:${days}d`;
  const max = limit ? String(Math.min(limit * 3, 500)) : '500';
  const messages = gogJson(['gmail', 'messages', 'list', search, '--max', max], { allowEmpty: true }) || [];
  // Group by threadId.
  const byThread = new Map();
  for (const m of messages) {
    const tid = m.threadId;
    if (!tid) continue;
    if (!byThread.has(tid)) byThread.set(tid, []);
    byThread.get(tid).push(m);
  }
  return Array.from(byThread.keys());
}

// Pull the full thread + parse out conversation messages + metadata.
function syncThread(threadId, relayToCid, applicationNamesLc, opts) {
  const tdata = gogJson(['gmail', 'thread', 'get', threadId], { allowEmpty: true });
  const thr = tdata?.thread || tdata;
  const msgs = thr?.messages || [];
  if (!msgs.length) return { skipped: 'empty-thread' };

  // Pass 1: derive conversation key (relay) + lead name from FIRST message
  // (which is the lead's initial inquiry; their display name is correct here
  // even if later messages use a derived username).
  let relay = null, leadName = null, listingHit = false, statusHint = 'INQUIRED';
  for (const m of msgs) {
    const headers = headersToMap(m.payload?.headers);
    const fromAddr = parseAddress(headers.from || '');
    if (fromAddr.email && /@convo\.zillow\.com$/.test(fromAddr.email)) {
      relay = fromAddr.email;
      const subj = headers.subject || '';
      if (!leadName) leadName = leadNameFromSubject(subj) || fromAddr.name;
      if (subj.toLowerCase().includes(LISTING_ADDRESS.split(',')[0].toLowerCase().trim())) listingHit = true;
      const newHint = statusHintFromSubject(subj);
      // Highest-warmth wins (TOUR REQUESTED beats INQUIRED).
      if (newHint === 'TOUR REQUESTED') statusHint = 'TOUR REQUESTED';
      break; // first inbound = canonical lead identity
    }
  }
  if (!relay) return { skipped: 'no-relay' };
  if (!listingHit) return { skipped: 'wrong-listing' };

  // Pass 2: build messages timeline.
  const messages = [];
  for (const m of msgs) {
    const headers = headersToMap(m.payload?.headers);
    const fromAddr = parseAddress(headers.from || '');
    const isInbound = !!fromAddr.email && /@convo\.zillow\.com$/.test(fromAddr.email);
    const isOutbound = !!fromAddr.email && fromAddr.email === OWNER_EMAIL.toLowerCase();
    if (!isInbound && !isOutbound) continue;
    const { ts_ms, ts_iso } = parseGmailDate(headers.date);
    const subject = headers.subject || '';
    const renterBody = isInbound
      ? extractRenterBody(tdata?.body /* not present per-msg here */, m.snippet || '')
      : null;
    // For inbound, prefer renterBody; for outbound, the snippet is the reply
    // (we sent it, it's our text with Zillow chrome appended sometimes).
    const body = isInbound
      ? (renterBody || m.snippet || '')
      : (m.snippet || '').split(/On\s+\w+,?\s+\w+\s+\d+,?\s+\d{4}/i)[0].trim();
    if (!body) continue;
    messages.push({
      direction: isInbound ? 'inbound' : 'outbound',
      sender_name: isInbound ? (fromAddr.name || leadName || 'Lead') : 'Adithya Shak Kumar',
      body,
      ts_ms,
      ts_iso,
      message_id: `gmail:${m.id}`,
      message_type: isInbound ? 'gmail:relay-inbound' : 'gmail:relay-outbound',
      hash: 'sha256:' + sha256Hex(body)
    });
  }
  if (!messages.length) return { skipped: 'no-extractable-messages', relay };

  // Sort oldest-first.
  messages.sort((a, b) => a.ts_ms - b.ts_ms);

  // Resolve cid: existing state's cid if relay already known; else synthetic.
  const cid = relayToCid.get(relay.toLowerCase()) || `gmail-${threadId}`;

  // Last in/out timestamps + hashes.
  const lastInbound = [...messages].reverse().find(m => m.direction === 'inbound');
  const lastOutbound = [...messages].reverse().find(m => m.direction === 'outbound');

  // Application status override.
  let statusLabel = statusHint;
  if (leadName && applicationNamesLc.has(leadName.toLowerCase())) statusLabel = 'APPLICATION RECEIVED';

  // Merge with existing state (preserve fields the portal set: tour_event_id,
  // renter_profile, etc.) — Gmail-derived fields override their counterparts.
  const prior = readThreadState(cid) || {};
  const merged = {
    ...prior,
    listing_alias: prior.listing_alias || LISTING_ALIAS,
    listing_address: prior.listing_address || LISTING_ADDRESS,
    lead_name: leadName || prior.lead_name,
    lead_phone: prior.lead_phone || null,
    lead_reference_email: relay,
    inquiry_id: prior.inquiry_id || null,
    status_label: statusLabel,
    renter_us_state: prior.renter_us_state || null,
    has_unread: false,
    is_archived: prior.is_archived || false,
    is_spam: prior.is_spam || false,
    is_active: true,
    last_pulled_at: new Date().toISOString(),
    last_inbound_at: lastInbound?.ts_iso || prior.last_inbound_at || null,
    last_inbound_hash: lastInbound?.hash || prior.last_inbound_hash || null,
    last_outbound_at: lastOutbound?.ts_iso || prior.last_outbound_at || null,
    last_outbound_hash: lastOutbound?.hash || prior.last_outbound_hash || null,
    messages,
    renter_profile: prior.renter_profile || null,
    gmail_thread_id: threadId,
    ingest_source: 'gmail-v1'
  };

  if (opts.dry) {
    return { ok: true, dry: true, cid, relay, status: statusLabel, msgs: messages.length };
  }

  writeThreadState(cid, merged);
  try {
    writeLeadMarkdown({
      conversation_id: cid,
      listing_alias: merged.listing_alias,
      listing_address: merged.listing_address,
      name: merged.lead_name,
      phone: merged.lead_phone,
      email: null,
      reference_email: merged.lead_reference_email,
      status_label: merged.status_label,
      renter_us_state: merged.renter_us_state,
      pulled_at_iso: merged.last_pulled_at,
      messages,
      renter_profile: merged.renter_profile
    });
  } catch (e) {
    appendObservation({ kind: 'gmail-ingest-md-failed', cid, error: e.message });
  }
  return { ok: true, dry: false, cid, relay, status: statusLabel, msgs: messages.length, isNew: !prior.thread_id };
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  console.error(`[gmail-ingest] starting (days=${opts.days}, limit=${opts.limit ?? 'none'}, dry=${opts.dry})`);

  // 1. Application-received signals (best-effort).
  const appSig = pullApplicationReceivedSignals(opts.days);
  console.error(`[gmail-ingest] application notifications: ${appSig.byName.size} names matched`);

  // 2. Discover all conversation threads.
  const threadIds = listConvoThreads(opts.days, opts.limit);
  console.error(`[gmail-ingest] ${threadIds.length} convo threads found in Gmail`);

  // 3. Build relay->cid map for continuity.
  const relayToCid = buildRelayToCidMap();
  console.error(`[gmail-ingest] ${relayToCid.size} existing thread states (for relay-keyed continuity)`);

  // 4. Sync each thread.
  const summary = { synced: 0, new: 0, skipped: {}, errors: 0 };
  let processed = 0;
  for (const tid of threadIds) {
    if (opts.limit && processed >= opts.limit) break;
    processed++;
    try {
      const r = syncThread(tid, relayToCid, appSig.byName, opts);
      if (r.skipped) {
        summary.skipped[r.skipped] = (summary.skipped[r.skipped] || 0) + 1;
        continue;
      }
      if (r.ok) {
        summary.synced++;
        if (r.isNew) summary.new++;
        process.stderr.write(`  ${r.isNew ? 'NEW ' : 'upd '} cid=${r.cid} status=${r.status} msgs=${r.msgs}\n`);
      }
    } catch (e) {
      summary.errors++;
      appendObservation({ kind: 'gmail-ingest-thread-failed', thread_id: tid, error: e.message });
      console.error(`  ERROR thread=${tid}: ${e.message}`);
    }
  }

  console.error(`\n[gmail-ingest] done. synced=${summary.synced} new=${summary.new} errors=${summary.errors} skipped=${JSON.stringify(summary.skipped)}`);
}

main().catch((e) => { console.error('[gmail-ingest] FATAL', e); process.exit(1); });
