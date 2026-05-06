// storage.mjs -- two-tier storage for the Zillow rental-manager playbook.
//
// Tier 1: per-lead markdown committed under workspaces/rental-manager/raw/leads/.
//   - phone E.164, email lowercase, kebab-case slug
//   - body holds messages timeline + observed renter profile attributes
//
// Tier 2: operational state under workspaces/rental-manager/state/.
//   - threads/<conversationId>.json   per-thread canonical state
//   - audit/<yyyy-mm-dd>/<intent>/    immutable send bundles
//   - network/<yyyy-mm-dd>/...        redacted GraphQL captures
//   - threads.jsonl                   append-only observation log

import { existsSync, readFileSync, writeFileSync, mkdirSync, renameSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { LEADS_DIR, STATE_DIR, NETWORK_DIR, AUDIT_DIR, THREADS_DIR, THREADS_JSONL } from './paths.mjs';

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

function atomicWrite(path, data) {
  ensureDir(path.replace(/\/[^/]+$/, ''));
  const tmp = path + '.tmp';
  writeFileSync(tmp, data);
  renameSync(tmp, path);
}

function sha256(s) {
  return 'sha256:' + createHash('sha256').update(s).digest('hex');
}

// -----------------------------
// canonicalization (graph rules)
// -----------------------------

export function toE164(raw) {
  if (!raw) return null;
  const digits = String(raw).replace(/\D+/g, '');
  if (!digits) return null;
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`;
  if (digits.length >= 10) return `+${digits}`;
  return null;
}

export function toLowerEmail(raw) {
  if (!raw) return null;
  const e = String(raw).trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e) ? e : null;
}

export function toSlug(s) {
  return String(s || '')
    .normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function leadSlug({ name, listingAlias, phone, conversationId }) {
  // Disambiguate: first+last name when available, else first+phone-suffix,
  // else first+cid-suffix. Pure first-name-only collides on common names
  // (Jennifer Cuevas vs Jennifer Jukes both wrote to jennifer-zillow-... and
  // the second silently clobbered the first on 2026-05-04).
  const tokens = (name || '').trim().split(/\s+/).filter(Boolean);
  const first = toSlug(tokens[0] || 'lead') || 'lead';
  const last = tokens.length > 1 ? toSlug(tokens[tokens.length - 1]) : '';
  const alias = toSlug(listingAlias) || 'unknown';

  if (last) {
    return `${first}-${last}-zillow-${alias}`;
  }
  // No last name. Disambiguate with phone last-4 or cid last-4.
  const e164 = phone ? toE164(phone) : null;
  const phoneSuffix = e164 ? e164.slice(-4) : '';
  if (phoneSuffix) {
    return `${first}-${phoneSuffix}-zillow-${alias}`;
  }
  const cidSuffix = conversationId ? String(conversationId).slice(-4) : '';
  if (cidSuffix) {
    return `${first}-${cidSuffix}-zillow-${alias}`;
  }
  return `${first}-zillow-${alias}`;
}

// -----------------------------
// Tier 1: per-lead markdown
// -----------------------------

function frontmatter(obj) {
  // Minimal YAML. We're conservative: any string that COULD trip YAML 1.1/1.2
  // (colon, hash, quote, hyphen-prefix, leading whitespace, indicators, multiline)
  // gets JSON-quoted. Names like "Adithya: Lord of Bots" or addresses with
  // commas (which YAML treats as flow-context separators) must be quoted.
  // Adversary path: a renter posts a name like `evil\n---\nstatus: SPAM` —
  // JSON.stringify renders \n as a literal `\n` escape, keeping YAML 1-line.
  const SAFE_BARE = /^[A-Za-z0-9_][A-Za-z0-9_./+ -]*[A-Za-z0-9_./+ -]$|^[A-Za-z0-9_]$/;
  const yamlValue = (v) => {
    if (v === null || v === undefined) return 'null';
    if (Array.isArray(v)) return '[' + v.map(x => JSON.stringify(String(x))).join(', ') + ']';
    if (typeof v === 'object') return JSON.stringify(v);
    if (typeof v === 'number' || typeof v === 'boolean') return String(v);
    const s = String(v);
    // Reject anything containing YAML special chars or whitespace-edge cases.
    if (!SAFE_BARE.test(s) || /[:#\n\r\t"'`{}[\],&*!|>%@?]/.test(s)) return JSON.stringify(s);
    return s;
  };
  const lines = ['---'];
  for (const [k, v] of Object.entries(obj)) {
    if (v === null || v === undefined || v === '') continue;
    lines.push(`${k}: ${yamlValue(v)}`);
  }
  lines.push('---');
  return lines.join('\n');
}

function renderMessages(messages) {
  if (!messages || !messages.length) return '_no messages yet_';
  const lines = ['## Messages\n'];
  // Oldest first.
  const sorted = [...messages].sort((a, b) => (a.ts_ms || 0) - (b.ts_ms || 0));
  for (const m of sorted) {
    const who = m.direction === 'outbound' ? 'Owner (Adithya)' : (m.sender_name || 'Lead');
    const when = m.ts_iso || (m.ts_ms ? new Date(m.ts_ms).toISOString() : 'unknown');
    lines.push(`### ${when} - ${who}`);
    lines.push('');
    lines.push((m.body || '').trim() || '_(empty)_');
    lines.push('');
  }
  return lines.join('\n');
}

function renderRenterProfile(rp) {
  if (!rp || !Object.keys(rp).length) return '';
  const lines = ['## Renter profile\n'];
  for (const [k, v] of Object.entries(rp)) {
    if (v === null || v === undefined || v === '') continue;
    if (Array.isArray(v) && !v.length) continue;
    if (typeof v === 'object') {
      lines.push(`- **${k}**: \`${JSON.stringify(v)}\``);
    } else {
      lines.push(`- **${k}**: ${v}`);
    }
  }
  lines.push('');
  return lines.join('\n');
}

/**
 * Write or update the per-lead markdown file in workspaces/rental-manager/raw/leads/.
 * Idempotent: rewrites the entire file each call from observed state.
 *
 * lead shape:
 *   {
 *     conversation_id: string,
 *     listing_alias: string,
 *     listing_address: string,
 *     name: string,
 *     phone: string?,        // raw input; we canonicalize
 *     email: string?,        // raw input; we canonicalize
 *     reference_email: string?,  // convo.zillow.com forwarding addr
 *     status_label: string?, // INQUIRED / TOUR_REQUESTED / APPLICATION_STARTED / ...
 *     pulled_at_iso: string,
 *     messages: [{direction, body, ts_ms, ts_iso, sender_name, hash}],
 *     renter_profile: {credit, incomeYearlyRange, ...}?,
 *     raw_inquiry_state: string?
 *   }
 */
export function writeLeadMarkdown(lead) {
  ensureDir(LEADS_DIR);
  const slug = leadSlug({
    name: lead.name,
    listingAlias: lead.listing_alias,
    phone: lead.phone,
    conversationId: lead.conversation_id
  });
  const path = join(LEADS_DIR, `${slug}.md`);

  const phone = toE164(lead.phone);
  const email = toLowerEmail(lead.email);
  const refEmail = toLowerEmail(lead.reference_email);

  const fm = frontmatter({
    slug,
    source: 'zillow-rental-manager',
    workspace: 'rental-manager',
    name: lead.name,
    phone,
    email,
    reference_email: refEmail,
    listing_alias: lead.listing_alias,
    listing_address: lead.listing_address,
    conversation_id: lead.conversation_id,
    status_label: lead.status_label,
    renter_us_state: lead.renter_us_state,
    last_pulled_at: lead.pulled_at_iso
  });

  const sections = [
    fm,
    '',
    `# ${lead.name || slug}`,
    '',
    `Lead from Zillow Rental Manager for **${lead.listing_address || lead.listing_alias}**.`,
    '',
    `- Status: \`${lead.status_label || 'unknown'}\``,
    phone ? `- Phone: \`${phone}\`` : null,
    email ? `- Email: \`${email}\`` : null,
    refEmail ? `- Zillow forwarding email: \`${refEmail}\`` : null,
    `- Conversation ID: \`${lead.conversation_id}\``,
    `- Listing alias: \`${lead.listing_alias}\``,
    '',
    renderRenterProfile(lead.renter_profile || {}),
    renderMessages(lead.messages || [])
  ].filter(x => x !== null).join('\n');

  atomicWrite(path, sections);
  return { path, slug };
}

// -----------------------------
// Tier 2: operational state
// -----------------------------

function threadStatePath(conversationId) {
  return join(THREADS_DIR, `${conversationId}.json`);
}

export function readThreadState(conversationId) {
  const p = threadStatePath(conversationId);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, 'utf8')); } catch (_) { return null; }
}

export function writeThreadState(conversationId, state) {
  ensureDir(THREADS_DIR);
  state.version = 1;
  state.thread_id = conversationId;
  state.updated_at = new Date().toISOString();
  atomicWrite(threadStatePath(conversationId), JSON.stringify(state, null, 2));
}

export function appendObservation(record) {
  ensureDir(STATE_DIR);
  const line = JSON.stringify({ ts: new Date().toISOString(), ...record }) + '\n';
  // append (not atomic but log-shaped, ok)
  writeFileSync(THREADS_JSONL, (existsSync(THREADS_JSONL) ? readFileSync(THREADS_JSONL, 'utf8') : '') + line);
}

/**
 * Save a redacted GraphQL capture for offline inspection. Drops cookies,
 * authorization headers, and known PII top-level fields if a `redact` map is
 * passed.
 */
export function saveNetworkCapture({ operationName, requestBody, responseBody, status }) {
  const today = new Date().toISOString().slice(0, 10);
  const dir = join(NETWORK_DIR, today);
  ensureDir(dir);
  const ts = Date.now();
  const path = join(dir, `${ts}-${operationName || 'unknown'}.json`);
  const payload = {
    ts_iso: new Date(ts).toISOString(),
    operationName: operationName || null,
    status: status ?? null,
    requestBody: requestBody ?? null,
    responseBody: responseBody ?? null
  };
  atomicWrite(path, JSON.stringify(payload, null, 2));
  return path;
}

export function saveSendBundle({ conversationId, intent, body, preScreenshot, postScreenshot, threadBefore, threadAfter, mutationResp }) {
  const today = new Date().toISOString().slice(0, 10);
  const id = `${Date.now()}-${conversationId}`;
  const dir = join(AUDIT_DIR, today, id);
  ensureDir(dir);
  atomicWrite(join(dir, 'send_intent.json'), JSON.stringify({ conversationId, intent, ts: new Date().toISOString() }, null, 2));
  atomicWrite(join(dir, 'rendered_body.txt'), body || '');
  if (threadBefore) atomicWrite(join(dir, 'thread_before.json'), JSON.stringify(threadBefore, null, 2));
  if (threadAfter) atomicWrite(join(dir, 'thread_after.json'), JSON.stringify(threadAfter, null, 2));
  if (mutationResp) atomicWrite(join(dir, 'mutation_response.json'), JSON.stringify(mutationResp, null, 2));
  if (preScreenshot && existsSync(preScreenshot)) {
    try { renameSync(preScreenshot, join(dir, 'pre_send.png')); } catch (_) {}
  }
  if (postScreenshot && existsSync(postScreenshot)) {
    try { renameSync(postScreenshot, join(dir, 'post_send.png')); } catch (_) {}
  }
  return dir;
}

export { sha256 };
