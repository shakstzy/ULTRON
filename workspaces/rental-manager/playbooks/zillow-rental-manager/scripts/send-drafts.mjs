// send-drafts.mjs -- read pre-written drafts from state/drafts/<cid>.json and
// send each one through the convo.zillow.com gmail relay via sendViaEmail.
//
// Drafts are produced upstream (by contextual-send.mjs, by subagents, or by
// hand). This script is just the dispatcher.
//
// Usage:
//   node scripts/send-drafts.mjs --dry           # preview only
//   node scripts/send-drafts.mjs --live          # actually send
//   node scripts/send-drafts.mjs --live --cids c1,c2  # subset

import { existsSync, readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';

import { STATE_DIR } from './paths.mjs';
import { sendViaEmail } from './email-send.mjs';

const DRAFTS_DIR = join(STATE_DIR, 'drafts');
const RUN_LOG_DIR = join(STATE_DIR, 'send-runs');

function parseArgs(argv) {
  const out = { dry: true, cids: null, gapMs: 1500 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--live') out.dry = false;
    else if (a === '--dry') out.dry = true;
    else if (a === '--cids') out.cids = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
    else if (a === '--gap') out.gapMs = parseInt(argv[++i], 10);
  }
  return out;
}

function loadDrafts(filter) {
  if (!existsSync(DRAFTS_DIR)) return [];
  const files = readdirSync(DRAFTS_DIR).filter(f => /^\d+\.json$/.test(f));
  const drafts = [];
  for (const f of files) {
    const cid = f.replace(/\.json$/, '');
    if (filter && !filter.has(cid)) continue;
    try {
      const d = JSON.parse(readFileSync(join(DRAFTS_DIR, f), 'utf8'));
      if (!d.body || !d.body.trim()) {
        console.error(`[skip ${cid}] empty body`);
        continue;
      }
      if (!d.relay || !/@convo\.zillow\.com$/i.test(d.relay)) {
        console.error(`[skip ${cid}] invalid relay: ${d.relay}`);
        continue;
      }
      drafts.push({ cid, ...d });
    } catch (e) {
      console.error(`[skip ${cid}] parse error: ${e.message}`);
    }
  }
  return drafts;
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const filter = opts.cids ? new Set(opts.cids) : null;
  const drafts = loadDrafts(filter);

  console.error(`[send-drafts] ${drafts.length} drafts found, dry=${opts.dry}, gap=${opts.gapMs}ms`);

  if (!existsSync(RUN_LOG_DIR)) mkdirSync(RUN_LOG_DIR, { recursive: true });
  const runId = `run-${new Date().toISOString().replace(/[:.]/g, '-')}`;
  const logPath = join(RUN_LOG_DIR, `${runId}.ndjson`);

  const summary = { sent: 0, failed: 0, dry: 0 };

  for (let i = 0; i < drafts.length; i++) {
    const d = drafts[i];
    const t0 = Date.now();
    const rec = { idx: i, cid: d.cid, lead_name: d.lead_name, status: d.status_label, relay: d.relay, body_len: d.body.length };
    console.error(`\n[${i + 1}/${drafts.length}] cid=${d.cid} name="${d.lead_name}" status=${d.status_label} -> ${d.relay}`);

    try {
      const r = await sendViaEmail(d.cid, d.body, { dryRun: opts.dry });
      Object.assign(rec, { ok: r.ok, dry_run: r.dry_run, audit_dir: r.audit_dir, gmail_message_id: r.gmail_message_id, subject: r.subject, dur_ms: Date.now() - t0 });
      if (r.dry_run) { summary.dry++; console.error(`  DRY (${r.subject})`); }
      else { summary.sent++; console.error(`  SENT gmail_id=${r.gmail_message_id || '?'} (${rec.dur_ms}ms)`); }
    } catch (e) {
      summary.failed++;
      Object.assign(rec, { ok: false, error: e.message, error_code: e.code || null, dur_ms: Date.now() - t0 });
      console.error(`  FAILED: ${e.message}`);
    }

    writeFileSync(logPath, JSON.stringify(rec) + '\n', { flag: 'a' });

    // Light gap between sends — Gmail's own throttle is generous but no need
    // to hammer at thousands per second.
    if (i < drafts.length - 1 && opts.gapMs > 0) await sleep(opts.gapMs);
  }

  console.error(`\n[send-drafts] done. sent=${summary.sent} dry=${summary.dry} failed=${summary.failed}`);
  console.error(`[send-drafts] log -> ${logPath}`);
}

main().catch((e) => { console.error('[send-drafts] FATAL', e); process.exit(1); });
