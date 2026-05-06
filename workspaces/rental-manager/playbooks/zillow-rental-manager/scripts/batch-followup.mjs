// batch-followup.mjs -- one-shot blast across all 102 leads at 13245 Klein Ct.
//
// Per-lead pipeline:
//   1. Mirror to Apple Contacts as "<First> Renter Showing26"
//      (collision: <FirstLast> as the first-name field, no spaces).
//      Skip if a contact with the same E.164 phone already exists.
//   2. Navigate to the Zillow thread URL.
//   3. sendReply LIVE with a body templated per status_label.
//   4. Send an iMessage casual variant if phone is present.
//
// Pacing: sendReply's internal enforceMinPacing is the only paced gate per
// lead, so 102 sends = 102 paced calls = fits inside the 120/hr cap.
//
// Run log lives at ~/.shakos/playbook-output/zillow-rental-manager/state/
// batch-followup/<runId>.json so the run is resumable. Pass --resume <runId>
// to pick up where an interrupted run left off.
//
// Flags:
//   --dry           Don't send Zillow OR iMessage, don't mutate Contacts.
//                   Just preview body + decisions per lead.
//   --live          Required to actually fire (default is dry-run).
//   --limit N       Stop after N leads.
//   --only-status S Process only leads with status_label=S.
//   --resume R      Resume a prior run by id (skips cids in that log).
//   --skip-contacts Skip the Apple Contacts mirror pass.
//   --skip-imessage Skip the iMessage send pass.
//   --skip-zillow   Skip the Zillow send pass.

import { existsSync, readFileSync, readdirSync, writeFileSync, mkdirSync, appendFileSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { readThreadState, writeThreadState } from './storage.mjs';

const HOME = process.env.HOME;
const STATE_DIR = process.env.ZRM_STATE_DIR || `${HOME}/.shakos/playbook-output/zillow-rental-manager/state`;
const THREADS_DIR = join(STATE_DIR, 'threads');
const RUN_LOG_DIR = join(STATE_DIR, 'batch-followup');
const APP_LINK = 'https://www.zillow.com/renter-hub/applications/listing/258vhr7ge6q56/rental-application/?itc=rentalhdpapplynow';
const ADDRESS = '13245 Klein Ct';
const CITY = 'Sylmar';

const STATUS_PRIORITY = {
  'APPLICATION RECEIVED': 1,
  'TOURED': 2,
  'INVITED TO APPLY': 3,
  'TOUR REQUESTED': 4,
  'TOUR CANCELED': 5,
  'APPLICATION WITHDRAWN': 6,
  'INQUIRED': 7
};

function parseArgv(argv) {
  const out = { dry: true, limit: null, only: null, resume: null, skipContacts: false, skipIMessage: false, skipZillow: false, skipApplications: false, slowRampLeads: 5, slowRampExtraMs: 25000 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--live') { out.dry = false; }
    else if (a === '--dry') { out.dry = true; }
    else if (a === '--limit') { out.limit = parseInt(argv[++i], 10); }
    else if (a === '--only-status') { out.only = argv[++i]; }
    else if (a === '--resume') { out.resume = argv[++i]; }
    else if (a === '--skip-contacts') { out.skipContacts = true; }
    else if (a === '--skip-imessage') { out.skipIMessage = true; }
    else if (a === '--skip-zillow') { out.skipZillow = true; }
    else if (a === '--skip-applications') { out.skipApplications = true; }
    else if (a === '--no-slow-ramp') { out.slowRampLeads = 0; }
  }
  return out;
}

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

function loadAllLeads() {
  const files = readdirSync(THREADS_DIR).filter(f => f.endsWith('.json'));
  const leads = [];
  for (const f of files) {
    const cid = f.replace(/\.json$/, '');
    let st;
    try { st = JSON.parse(readFileSync(join(THREADS_DIR, f), 'utf8')); }
    catch (e) { console.error(`[skip ${cid}] parse error: ${e.message}`); continue; }
    leads.push({
      conversation_id: cid,
      listing_alias: st.listing_alias,
      name: (st.lead_name || '').trim(),
      phone: st.lead_phone || null,
      status_label: st.status_label || 'INQUIRED',
      messages: st.messages || []
    });
  }
  return leads;
}

function firstNameOf(name) {
  return (name || '').trim().split(/\s+/)[0] || 'there';
}

function lastNameOf(name) {
  const parts = (name || '').trim().split(/\s+/);
  return parts.length > 1 ? parts.slice(1).join(' ') : '';
}

// --- bodies per status ---
function zillowBody(first, status) {
  switch (status) {
    case 'INQUIRED':
      return `Hey ${first}! Following up on my Sylmar listing at ${ADDRESS}. I've got 4 rooms still open, all available immediately: $1,000 (two 3rd-floor rooms with walk-in closets, shared bath), $1,200 (2nd floor with private bath), $1,250 (1st-floor private suite, attached bath + walk-in closet). Utilities are a flat $100/mo per room. Washer/dryer in unit, full Samsung kitchen, AC/heat, patio, dog park + community pool nearby. Parking is an optional add-on. Pets welcome, non-smoking. Current roommate is John, 40, super quiet and chill. Want to set up a tour or jump straight to the application? ${APP_LINK}`;
    case 'TOUR REQUESTED':
      return `Hey ${first}! Wanted to follow up on the tour you asked about for ${ADDRESS} in ${CITY}. Are you still interested in coming by? I'm pretty flexible on timing. 4 rooms still open ($1,000-$1,250 + $100 flat utilities), all move-in ready. Let me know what day works and I'll set it up.`;
    case 'TOURED':
      return `Hey ${first}! Thanks again for touring ${ADDRESS}. Are you still considering the place? Happy to answer any questions you have. If you're ready to move forward, the application is here: ${APP_LINK} ($25 fee, asks for 2-3 references). Rooms are still open.`;
    case 'INVITED TO APPLY':
      return `Hey ${first}! Following up on the application invite I sent for ${ADDRESS}. Still interested? Link is here when you're ready: ${APP_LINK} ($25 fee, asks for 2-3 references). Rooms still open.`;
    case 'APPLICATION RECEIVED':
      return `Hey ${first}! Wanted to circle back since it's been a minute on your application for ${ADDRESS}. How's your living situation looking right now, still searching or has anything shifted? If you're still interested I'd love to keep things moving. Let me know.`;
    case 'TOUR CANCELED':
      return `Hey ${first}! Saw you canceled the tour for ${ADDRESS}. Totally fine, just wanted to check if you'd want to reschedule or if you're no longer looking. 4 rooms still open ($1,000-$1,250 + $100 utilities) if so. No pressure.`;
    case 'APPLICATION WITHDRAWN':
      return `Hey ${first}! Wanted to circle back. Saw your application got pulled, totally understand. If your situation shifts and you're still curious about ${ADDRESS}, the rooms are still open. No pressure either way.`;
    default:
      return `Hey ${first}! Following up on ${ADDRESS} in ${CITY}. Are you still interested? 4 rooms still open ($1,000-$1,250 + $100 utilities). Let me know.`;
  }
}

function imessageBody(first, status) {
  switch (status) {
    case 'INQUIRED':
      return `Hey ${first}, Adithya here from the Klein Ct rental in ${CITY} (Zillow). Circling back since you'd reached out. 4 rooms still open, move-in immediate. $1k-$1,250 + $100 flat utilities. Roommate's chill (40 yo, quiet). Pets ok, non-smoking. W/D in unit, full Samsung kitchen, dog park + pool nearby. Want a tour or want to apply? ${APP_LINK}`;
    case 'TOUR REQUESTED':
      return `Hey ${first}, Adithya from the Klein Ct rental in ${CITY}. You'd asked about a tour a bit back. Still want to check it out? Pretty flexible on timing. 4 rooms still open, $1k-$1,250 + $100 utilities.`;
    case 'TOURED':
      return `Hey ${first}, Adithya from Klein Ct in ${CITY}. Thanks again for coming by. Still thinking about the place? Any questions I can answer? If you're ready: ${APP_LINK} ($25, 2-3 refs).`;
    case 'INVITED TO APPLY':
      return `Hey ${first}, Adithya from Klein Ct in ${CITY}. Wanted to bump the app invite. Still interested? ${APP_LINK} ($25, 2-3 refs).`;
    case 'APPLICATION RECEIVED':
      return `Hey ${first}, Adithya from the Klein Ct app you submitted. Realized it's been a while, wanted to check in. Still in the market or did your situation change? If still interested, want to keep things moving on your end?`;
    case 'TOUR CANCELED':
      return `Hey ${first}, Adithya from Klein Ct in ${CITY}. Saw you canceled the tour, all good. Want to reschedule or no longer looking? Rooms still open if so.`;
    case 'APPLICATION WITHDRAWN':
      return `Hey ${first}, Adithya from Klein Ct in ${CITY}. Saw your app got pulled, all good. If things shift and you want back in, rooms are still open. No pressure.`;
    default:
      return `Hey ${first}, Adithya from Klein Ct in ${CITY}. Following up on the listing. Still looking? 4 rooms open, $1k-$1,250 + $100 utilities.`;
  }
}

// --- Apple Contacts via osascript (JXA-flavored AppleScript) ---
function osascriptRun(script) {
  const r = spawnSync('osascript', ['-e', script], { encoding: 'utf8' });
  if (r.status !== 0) {
    const stderr = (r.stderr || '').trim();
    throw new Error(`osascript failed: ${stderr || 'unknown'}`);
  }
  return (r.stdout || '').trim();
}

// One-shot cache load: dump all existing "Renter Showing" contacts with their
// phone tails (last 10 digits). Replaces per-lead osascript scans (which were
// O(existing-contacts * phones-per-contact) per lead = pathological at 102 leads).
let _contactCache = null;
function loadContactCache() {
  if (_contactCache) return _contactCache;
  const script = `
    tell application "Contacts"
      set output to ""
      repeat with p in (every person whose name contains "Renter Showing")
        set nm to name of p
        set phoneList to ""
        try
          repeat with ph in phones of p
            set v to value of ph
            set vd to ""
            repeat with c in (characters of v)
              if c is in {"0","1","2","3","4","5","6","7","8","9"} then set vd to vd & c
            end repeat
            set phoneList to phoneList & vd & ","
          end repeat
        end try
        set output to output & nm & "|" & phoneList & linefeed
      end repeat
      return output
    end tell
  `;
  let raw = '';
  try { raw = osascriptRun(script); }
  catch (e) {
    console.error(`[contact-cache] load failed: ${e.message}`);
    _contactCache = { byPhoneTail10: new Map(), byName: new Set() };
    return _contactCache;
  }
  const byPhoneTail10 = new Map();
  const byName = new Set();
  for (const line of raw.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const sep = line.indexOf('|');
    if (sep === -1) continue;
    const nm = line.slice(0, sep).trim();
    const phones = line.slice(sep + 1).split(',').filter(Boolean);
    byName.add(nm);
    for (const p of phones) {
      const tail = p.slice(-10);
      if (tail.length === 10 && !byPhoneTail10.has(tail)) byPhoneTail10.set(tail, nm);
    }
  }
  console.error(`[contact-cache] loaded ${byName.size} renter contacts, ${byPhoneTail10.size} unique phones`);
  _contactCache = { byPhoneTail10, byName };
  return _contactCache;
}

function findContactByPhone(phoneE164) {
  if (!phoneE164) return null;
  const cache = loadContactCache();
  const tail = phoneE164.replace(/\D/g, '').slice(-10);
  return cache.byPhoneTail10.get(tail) || null;
}

function findContactByName(fullName) {
  const cache = loadContactCache();
  return cache.byName.has(fullName) ? fullName : null;
}

function createContact(firstField, lastField, phoneE164) {
  const f = firstField.replace(/"/g, '\\"');
  const l = lastField.replace(/"/g, '\\"');
  const p = (phoneE164 || '').replace(/"/g, '\\"');
  const script = `
    tell application "Contacts"
      set newP to make new person with properties {first name:"${f}", last name:"${l}"}
      ${p ? `make new phone at end of phones of newP with properties {label:"mobile", value:"${p}"}` : ''}
      save
      return id of newP
    end tell
  `;
  return osascriptRun(script);
}

function mirrorContact(lead, leadIdx, allLeads, opts) {
  if (opts.skipContacts) return { skipped: true, reason: 'skip-flag' };
  const first = firstNameOf(lead.name);
  if (!first || first === 'there') return { skipped: true, reason: 'no-first-name' };

  const lastField = 'Renter Showing26';

  // Stable name resolution: if a prior run already chose a contact_full_name
  // for this conversation, reuse it. Without this, a --limit 1 run that sees
  // no collisions creates "Jennifer Renter Showing26" while a full-batch run
  // that sees JenniferCuevas+JenniferJukes creates "JenniferCuevas Renter
  // Showing26", and re-runs duplicate the contact because the name-match
  // dedupe looks for an exact string. Hit on 2026-05-04/05.
  const prior = readThreadState(lead.conversation_id);
  let firstField;
  let fullName;
  if (prior?.contact_first_field && prior?.contact_full_name) {
    firstField = prior.contact_first_field;
    fullName = prior.contact_full_name;
  } else {
    // Fresh resolution: use disambiguated form whenever a last name exists.
    // Falling back to bare first name only when last is genuinely empty (and
    // even then phone/cid suffix would be safer if needed).
    const last = lastNameOf(lead.name);
    if (last) {
      firstField = `${first}${last.replace(/\s+/g, '')}`;
    } else {
      firstField = first;
    }
    fullName = `${firstField} ${lastField}`;
  }

  // Dry runs are read-only — never persist contact decisions. Otherwise a
  // dry preview can lock in a name that a later live run inherits.
  const persist = (extra) => {
    if (opts.dry) return;
    try { writeThreadState(lead.conversation_id, { ...(prior || {}), contact_first_field: firstField, contact_full_name: fullName, ...extra }); } catch (_) {}
  };

  // Phone-first dedupe.
  if (lead.phone) {
    const existingByPhone = findContactByPhone(lead.phone);
    if (existingByPhone) {
      // Persist whichever name actually matched so future runs don't drift.
      persist({ contact_full_name: existingByPhone });
      return { skipped: true, reason: `phone-match:${existingByPhone}`, fullName: existingByPhone };
    }
  }
  // Name-second dedupe.
  const existingByName = findContactByName(fullName);
  if (existingByName) {
    persist({});
    return { skipped: true, reason: `name-match:${existingByName}`, fullName };
  }

  if (opts.dry) return { skipped: false, dry: true, action: 'WOULD-CREATE', fullName };

  const id = createContact(firstField, lastField, lead.phone);
  // Update the in-memory cache so subsequent leads in this run see this contact.
  if (_contactCache) {
    _contactCache.byName.add(fullName);
    if (lead.phone) {
      const tail = lead.phone.replace(/\D/g, '').slice(-10);
      if (tail.length === 10) _contactCache.byPhoneTail10.set(tail, fullName);
    }
  }
  persist({ contact_apple_id: id });
  return { skipped: false, action: 'CREATED', fullName, id };
}

// --- iMessage send via osascript ---
function sendImessage(phone, body, dry) {
  if (!phone) return { skipped: true, reason: 'no-phone' };
  if (dry) return { skipped: false, dry: true, action: 'WOULD-SEND' };
  const safeBody = body.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  // Try iMessage first; fall back to SMS if the buddy isn't on iMessage.
  const script = `
    tell application "Messages"
      try
        set targetService to first service whose service type = iMessage
        set targetBuddy to buddy "${phone}" of targetService
        send "${safeBody}" to targetBuddy
      on error
        set targetService to first service whose service type = SMS
        set targetBuddy to buddy "${phone}" of targetService
        send "${safeBody}" to targetBuddy
      end try
    end tell
  `;
  osascriptRun(script);
  return { skipped: false, action: 'SENT' };
}

// --- after-send: append outbound to thread state + regenerate .md ---
async function appendOutboundAndRegenerate(lead, body) {
  const { readThreadState, writeThreadState, writeLeadMarkdown, sha256 } = await import('./storage.mjs');
  const cid = lead.conversation_id;
  const st = readThreadState(cid);
  if (!st) return { ok: false, reason: 'no-state-file' };
  st.messages = st.messages || [];
  const nowMs = Date.now();
  st.messages.push({
    direction: 'outbound',
    sender_name: 'Adithya',
    body,
    ts_ms: nowMs,
    ts_iso: new Date(nowMs).toISOString(),
    message_id: `batch-followup-${nowMs}`,
    message_type: 'manual_followup',
    hash: 'sha256:' + (await import('node:crypto')).createHash('sha256').update(body).digest('hex')
  });
  st.last_outbound_at = new Date(nowMs).toISOString();
  writeThreadState(cid, st);
  const leadObj = {
    conversation_id: cid,
    listing_alias: st.listing_alias,
    listing_address: st.listing_address,
    name: st.lead_name,
    phone: st.lead_phone,
    email: null,
    reference_email: st.lead_reference_email,
    status_label: st.status_label,
    renter_us_state: st.renter_us_state,
    pulled_at_iso: st.last_pulled_at,
    messages: st.messages,
    renter_profile: st.renter_profile || null,
    has_unread: !!st.has_unread,
    is_archived: !!st.is_archived,
    is_spam: !!st.is_spam,
    is_active: !!st.is_active
  };
  writeLeadMarkdown(leadObj);
  return { ok: true, messages: st.messages.length };
}

// --- application packet: download PDF + Gemini parse + append to .md ---
async function maybeDownloadApplication(page, lead, opts) {
  if (lead.status_label !== 'APPLICATION RECEIVED') return { skipped: true, reason: 'wrong-status' };
  if (opts.skipApplications) return { skipped: true, reason: 'skip-flag' };

  const { leadSlug } = await import('./storage.mjs');
  const slug = leadSlug({ name: lead.name, listingAlias: lead.listing_alias, phone: lead.phone, conversationId: lead.conversation_id });
  const outDir = join(process.env.HOME, 'QUANTUM/raw/rental-property/applications', slug);
  if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });
  const pdfPath = join(outDir, 'source.pdf');

  // Look for a "View application" link/button on the thread page.
  const candidates = [
    'a:has-text("View application")',
    'a:has-text("View Application")',
    'button:has-text("View application")',
    'button:has-text("View Application")',
    'a:has-text("View renter profile")',
    'a[href*="/rental-manager/applications/"]',
    'a[href*="/renter-hub/applications/"]'
  ];
  let clicked = false;
  for (const sel of candidates) {
    try {
      const loc = page.locator(sel).first();
      if (await loc.count() === 0) continue;
      if (!(await loc.isVisible().catch(() => false))) continue;
      await loc.click({ timeout: 5000 });
      clicked = true;
      break;
    } catch (_) { /* try next */ }
  }
  if (!clicked) return { skipped: true, reason: 'no-view-application-link', pdf_path: null };

  // Wait for application page to settle.
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(2000);

  // page.pdf() is Chromium-only via Page.printToPDF. Should work in CDP-attached
  // headed Chrome (real Chrome supports it). If it fails, fall back to a
  // full-page screenshot.
  let pdfOk = false;
  let pdfErr = null;
  try {
    await page.pdf({ path: pdfPath, format: 'Letter', printBackground: true });
    pdfOk = true;
  } catch (e) {
    pdfErr = e.message;
    // Fallback: full-page screenshot.
    try {
      const pngPath = pdfPath.replace(/\.pdf$/, '.png');
      await page.screenshot({ path: pngPath, fullPage: true });
      return { skipped: false, action: 'SCREENSHOT_FALLBACK', png_path: pngPath, pdf_error: pdfErr };
    } catch (e2) {
      return { skipped: false, action: 'CAPTURE_FAILED', pdf_error: pdfErr, screenshot_error: e2.message };
    }
  }

  // Run Gemini parse with the standardized template.
  const TPL_PATH = '/Users/shakstzy/SHAKOS/workspaces/rental-property/playbooks/zillow-rental-manager/scripts/application-template.md';
  let templateContent;
  try { templateContent = readFileSync(TPL_PATH, 'utf8'); }
  catch (e) { return { skipped: false, action: 'TEMPLATE_MISSING', error: e.message, pdf_path: pdfPath }; }

  const promptBody = `You are parsing a Zillow rental application PDF for a landlord. The PDF is at @raw/rental-property/applications/${slug}/source.pdf

Fill out the template below using ONLY data present in the PDF. For any field you cannot determine, write "_(not provided)_". Skip SSN, full bank-account numbers, full credit-card numbers, and any government-ID full numbers — write "(redacted by Claude policy)" instead. The "last 4" fields are OK if visible.

TEMPLATE TO FILL:

${templateContent}

OUTPUT: just the filled-in markdown, no preamble, no closing remarks.`;

  const r = spawnSync('gemini', ['-m', 'gemini-3-pro-preview', '--approval-mode', 'plan', '-o', 'text', '-p', promptBody], {
    encoding: 'utf8',
    cwd: join(process.env.HOME, 'QUANTUM'),
    timeout: 180000
  });
  if (r.status !== 0) {
    const stderr = (r.stderr || '').slice(0, 400);
    return { skipped: false, action: 'GEMINI_FAILED', pdf_path: pdfPath, error: stderr };
  }
  const parsedMd = (r.stdout || '').trim();
  if (!parsedMd) return { skipped: false, action: 'GEMINI_EMPTY', pdf_path: pdfPath };

  // Append to lead .md.
  const mdPath = join(process.env.HOME, 'QUANTUM/raw/rental-property/leads', `${slug}.md`);
  if (!existsSync(mdPath)) return { skipped: false, action: 'LEAD_MD_MISSING', pdf_path: pdfPath };
  const stamp = new Date().toISOString();
  appendFileSync(mdPath, `\n\n## Application packet (parsed via Gemini ${stamp})\n\n${parsedMd}\n`);
  return { skipped: false, action: 'PARSED_AND_APPENDED', pdf_path: pdfPath, md_path: mdPath };
}

// --- main ---
async function main() {
  const opts = parseArgv(process.argv.slice(2));
  ensureDir(RUN_LOG_DIR);
  const runId = opts.resume || `run-${new Date().toISOString().replace(/[:.]/g, '-')}`;
  const runLogPath = join(RUN_LOG_DIR, `${runId}.ndjson`);
  console.error(`[batch] runId=${runId} log=${runLogPath} dry=${opts.dry}`);

  // Run markers — silent process death used to leave us guessing whether a
  // run finished or got SIGKILLed mid-lead. Three explicit markers:
  //   <runId>.start   written immediately
  //   <runId>.done    written on clean main() exit
  //   <runId>.crashed written on uncaughtException / unhandledRejection
  // Plus a `pid` field so future runs can tell whether the writing process is
  // still alive (helps diagnose stale lockfiles).
  const writeMarker = (suffix, extra = {}) => {
    try {
      writeFileSync(
        join(RUN_LOG_DIR, `${runId}.${suffix}`),
        JSON.stringify({ ts: new Date().toISOString(), pid: process.pid, runId, ...extra }, null, 2)
      );
    } catch (_) { /* don't let marker writes mask real errors */ }
  };
  writeMarker('start', { argv: process.argv.slice(2) });
  // Re-throwing inside an uncaughtException handler short-circuits later
  // listeners and produces messy exits. Per Codex adversarial review: write
  // the marker, log, set process.exitCode, then process.exit on next tick.
  process.once('uncaughtException', (e) => {
    writeMarker('crashed', { error: e.message, stack: e.stack?.slice(0, 2000), kind: 'uncaughtException' });
    console.error('[batch] FATAL uncaughtException:', e);
    process.exitCode = 1;
    setImmediate(() => process.exit(1));
  });
  process.once('unhandledRejection', (e) => {
    writeMarker('crashed', { error: String(e?.message || e), stack: e?.stack?.slice(0, 2000), kind: 'unhandledRejection' });
    console.error('[batch] FATAL unhandledRejection:', e);
    process.exitCode = 1;
    setImmediate(() => process.exit(1));
  });

  // Load and sort leads. Keep an unfiltered copy for collision detection so
  // --limit/--only doesn't break the JenniferCuevas/JenniferJukes split.
  const allLeads = loadAllLeads();
  let leads = [...allLeads];
  leads.sort((a, b) => (STATUS_PRIORITY[a.status_label] || 99) - (STATUS_PRIORITY[b.status_label] || 99));
  if (opts.only) leads = leads.filter(l => l.status_label === opts.only);
  if (opts.limit) leads = leads.slice(0, opts.limit);

  // Resume: skip cids already in this log.
  const done = new Set();
  if (opts.resume && existsSync(runLogPath)) {
    for (const line of readFileSync(runLogPath, 'utf8').split('\n')) {
      if (!line.trim()) continue;
      try { const r = JSON.parse(line); if (r.zillow?.action === 'SENT' || r.zillow?.dry) done.add(r.cid); }
      catch (_) {}
    }
    console.error(`[batch resume] skipping ${done.size} cids already done`);
  }
  leads = leads.filter(l => !done.has(l.conversation_id));
  console.error(`[batch] processing ${leads.length} leads`);

  // Connect once, send all. CRITICAL: ensure the daemon (long-lived chromium
  // with --remote-debugging-port=9222) is running BEFORE connectOrLaunch, so
  // we attach via CDP instead of cold-starting a fresh patchright Chromium.
  // Cold-start = no human warm-up state in the JS runtime = PerimeterX 403.
  // The daemon survives our script restarts; only restarts when daemon-stop is
  // called explicitly or the host reboots.
  const { connectOrLaunch, installGracefulShutdown, warmUpZillow } = await import('./browser.mjs');
  const { sendReply, pullThread } = await import('./inbox.mjs');
  const { startDaemon, isDaemonAlive } = await import('./daemon.mjs');
  let ctx = null;
  if (!opts.skipZillow) {
    if (!isDaemonAlive()) {
      console.error('[batch] daemon not running, starting it...');
      const r = await startDaemon({ visible: true });
      if (!r.ok) throw new Error(`daemon-start failed: ${r.error}`);
      console.error(`[batch] daemon started pid=${r.pid} cdp=${r.cdpUrl}`);
    } else {
      console.error('[batch] daemon already alive, attaching via CDP');
    }
    ctx = await connectOrLaunch({ headless: false, force: false });
    installGracefulShutdown(() => ctx.close());
    console.error(`[batch] connected mode=${ctx.mode}`);
    // Warm-up: PerimeterX scores the JS runtime state heavily. Hitting the
    // homepage with a real wheel + idle BEFORE any /rental-manager API call
    // establishes the px collector token. Without this, the first call gets
    // 403'd. ~12s. Throws WARMUP_403 if the homepage itself rejects us (IP/
    // profile flagged) -- we abort cleanly in that case.
    //
    // Recover from "Target page... closed" by creating a fresh tab and
    // retrying once. Happens when the daemon's tabs were churned by a prior
    // CDP client (e.g. our pre-fire navigation helper).
    let warmedUp = false;
    for (let attempt = 0; attempt < 2 && !warmedUp; attempt++) {
      try {
        await warmUpZillow(ctx.page);
        warmedUp = true;
        console.error('[batch] warm-up complete');
      } catch (e) {
        if (e.code === 'WARMUP_403') {
          console.error('[batch] WARMUP_403: IP/profile flagged at homepage. Aborting.');
          throw e;
        }
        const closed = /closed|disconnected|browser has been closed/i.test(e.message);
        if (closed && attempt === 0) {
          console.error(`[batch] warm-up page-closed, creating fresh tab and retrying: ${e.message}`);
          try { ctx.page = await ctx.context.newPage(); }
          catch (e2) { console.error(`[batch] new page failed: ${e2.message}`); throw e; }
          continue;
        }
        console.error(`[batch] warm-up error after ${attempt + 1} attempt(s), aborting: ${e.message}`);
        throw e;
      }
    }
  }

  const summary = { created: 0, skipped_contact: 0, zillow_sent: 0, zillow_failed: 0, imessage_sent: 0, imessage_failed: 0, imessage_skipped: 0 };

  try {
    for (let i = 0; i < leads.length; i++) {
      const lead = leads[i];
      const first = firstNameOf(lead.name);
      const zBody = zillowBody(first, lead.status_label);
      const iBody = imessageBody(first, lead.status_label);
      const result = { ts: new Date().toISOString(), idx: i, cid: lead.conversation_id, name: lead.name, status: lead.status_label, phone: lead.phone };

      console.error(`\n[batch ${i + 1}/${leads.length}] cid=${lead.conversation_id} status=${lead.status_label} name="${lead.name}"`);

      // Slow ramp: leads 2..N (1-indexed) where N=slowRampLeads (default 5).
      // Adds humanlike pause on top of the existing pacing.mjs gap so PX has
      // time to score the first few sends as paced human activity, not bursts.
      if (i > 0 && i < opts.slowRampLeads && !opts.dry && !opts.skipZillow) {
        const ms = opts.slowRampExtraMs;
        console.error(`  [slow-ramp] sleeping ${(ms/1000).toFixed(0)}s extra (first ${opts.slowRampLeads} leads)`);
        await sleep(ms);
      }

      // 1. Mirror contact. Pass allLeads (full 102) for collision detection.
      try {
        const c = mirrorContact(lead, i, allLeads, opts);
        result.contact = c;
        if (c.skipped) summary.skipped_contact++; else if (c.action === 'CREATED') summary.created++;
        console.error(`  contact: ${c.skipped ? 'SKIP ' + c.reason : c.action} -> "${c.fullName || ''}"`);
      } catch (e) {
        result.contact = { error: e.message };
        console.error(`  contact: ERROR ${e.message}`);
      }

      // 2. Zillow send.
      if (!opts.skipZillow) {
        try {
          if (opts.dry) {
            result.zillow = { dry: true, body_len: zBody.length };
            console.error(`  zillow: DRY (${zBody.length} chars)`);
          } else {
            // Direct nav + wait for textarea. Avoids pullThread's dependency on
            // the MessageList_GetConversation GraphQL op (name appears to have
            // shifted server-side ~2026-05; both APPLICATION RECEIVED leads
            // timed out at 35s on that op even though the page rendered fine).
            // The compose textarea attaching is the only signal we actually
            // need before sendReply.
            const targetUrl = `https://www.zillow.com/rental-manager/inbox/${lead.listing_alias}/${lead.conversation_id}`;
            // If we're already on this thread URL, bounce to inbox first so the
            // SPA re-renders the compose surface.
            if (ctx.page.url().includes(lead.conversation_id)) {
              await ctx.page.goto('https://www.zillow.com/rental-manager/inbox', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
              await ctx.page.waitForTimeout(500);
            }
            const navResp = await ctx.page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
            if (navResp && navResp.status() === 403) {
              const err = new Error(`Thread nav returned 403 (auth lapsed or PerimeterX flagged). URL=${ctx.page.url()}`);
              err.code = 'AUTH_OR_PX';
              throw err;
            }
            // Check auth BEFORE the textarea wait — saves 15s when we're
            // already logged out. Use context.cookies() not document.cookie
            // because zjs_user_id may be HttpOnly (Gemini adversarial review:
            // document.cookie can't read HttpOnly, would silently false-null).
            {
              const cookies = await ctx.context.cookies('https://www.zillow.com/').catch(() => []);
              const userIdCookie = cookies.find(c => c.name === 'zjs_user_id');
              const userId = userIdCookie?.value;
              if (!userId || userId === 'null') {
                const err = new Error(`zjs_user_id missing or null after nav (cookie ${userIdCookie ? 'present but value=null' : 'absent'}). URL=${ctx.page.url()}`);
                err.code = 'AUTH_LAPSED';
                throw err;
              }
            }
            try {
              await ctx.page.waitForSelector('[data-testid="textarea-autosize"]', { state: 'attached', timeout: 15000 });
            } catch (_) {
              // Auth checked good above; textarea miss is a genuine SPA edge case.
              throw new Error(`textarea not present after nav (url=${ctx.page.url()})`);
            }
            // Settle a moment so React state populates (avoids typing into stale textarea).
            await ctx.page.waitForTimeout(1500);
            const r = await sendReply(ctx.page, lead.conversation_id, zBody, { dryRun: false });
            result.zillow = { action: 'SENT', ok: r.ok, audit: r.audit_dir };
            summary.zillow_sent++;
            console.error(`  zillow: SENT ok=${r.ok}`);

            // 2a. Update lead state + .md immediately after successful send.
            try {
              const upd = await appendOutboundAndRegenerate(lead, zBody);
              result.md_update = upd;
              console.error(`  md: ${upd.ok ? `regenerated (${upd.messages} messages)` : 'FAILED ' + upd.reason}`);
            } catch (e) {
              result.md_update = { ok: false, error: e.message };
              console.error(`  md: ERROR ${e.message}`);
            }

            // 2b. Application packet (APPLICATION RECEIVED only): try to find
            // a "View application" link on the thread, click, page.pdf(), run
            // Gemini parse with the standardized template, append to the
            // lead's .md as `## Application packet`.
            if (lead.status_label === 'APPLICATION RECEIVED') {
              try {
                const ap = await maybeDownloadApplication(ctx.page, lead, opts);
                result.application = ap;
                if (ap.skipped) console.error(`  application: SKIP ${ap.reason}`);
                else console.error(`  application: ${ap.action} ${ap.pdf_path || ''}`);
              } catch (e) {
                result.application = { error: e.message };
                console.error(`  application: ERROR ${e.message}`);
              }
            }
          }
        } catch (e) {
          result.zillow = { error: e.message, code: e.code || null };
          summary.zillow_failed++;
          console.error(`  zillow: ERROR [${e.code || 'no-code'}] ${e.message}`);
          // Abort the whole batch on auth-lapsed: every subsequent lead would
          // fail identically until cookies are restored. Match by err.code,
          // not by regex on e.message (Codex adversarial review: brittle).
          if (e.code === 'AUTH_LAPSED' || e.code === 'AUTH_OR_PX' || e.code === 'BREAKER_HALTED') {
            appendFileSync(runLogPath, JSON.stringify(result) + '\n');
            console.error(`[batch] ${e.code} after lead ${i+1}/${leads.length}. Aborting.`);
            console.error(`[batch] To resume: \`node scripts/run.mjs login\` then \`node scripts/batch-followup.mjs --live --resume ${runId}\``);
            writeMarker('aborted', { code: e.code, lead_idx: i, lead_cid: lead.conversation_id, summary });
            return;
          }
        }
      } else {
        result.zillow = { skipped: true, reason: 'skip-flag' };
      }

      // 3. iMessage.
      if (!opts.skipIMessage) {
        try {
          const im = sendImessage(lead.phone, iBody, opts.dry);
          result.imessage = im;
          if (im.skipped) summary.imessage_skipped++;
          else if (im.action === 'SENT') summary.imessage_sent++;
          else if (im.dry) {} // no counter
          console.error(`  imessage: ${im.skipped ? 'SKIP ' + im.reason : im.action || (im.dry ? 'DRY' : '?')}`);
        } catch (e) {
          result.imessage = { error: e.message };
          summary.imessage_failed++;
          console.error(`  imessage: ERROR ${e.message}`);
        }
      } else {
        result.imessage = { skipped: true, reason: 'skip-flag' };
      }

      appendFileSync(runLogPath, JSON.stringify(result) + '\n');
    }
  } finally {
    if (ctx) await ctx.close();
  }

  console.error('\n[batch] DONE');
  console.error(JSON.stringify(summary, null, 2));
  console.error(`[batch] log: ${runLogPath}`);
  writeMarker('done', { summary });
}

main().catch(e => {
  console.error('[batch] FATAL', e);
  process.exit(1);
});
