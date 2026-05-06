#!/usr/bin/env node
// run.mjs -- CLI dispatcher for the Zillow Rental Manager skill.
// First run auto-installs deps (patchright + chrome binary).
//
// Commands:
//   node scripts/run.mjs login            One-time visible-browser Zillow login
//   node scripts/run.mjs status           Show profile + breaker + pidfile state
//   node scripts/run.mjs reset-breaker    Clear the 24h captcha halt
//   node scripts/run.mjs explore [url]    Open visible Chrome on URL, leave it open
//   node scripts/run.mjs snapshot <url> <out-dir>   Navigate + dump HTML + screenshot

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = resolve(HERE, '..');
const NODE_MODULES = join(SKILL_ROOT, 'node_modules');

function ensureDeps() {
  if (existsSync(join(NODE_MODULES, 'patchright'))) return;
  console.log('[zrm] First run: installing dependencies (patchright + Chrome binary). This may take a few minutes.');
  const r1 = spawnSync('npm', ['install'], { cwd: SKILL_ROOT, stdio: 'inherit' });
  if (r1.status !== 0) {
    console.error('[zrm] npm install failed. Run `npm install` manually in', SKILL_ROOT);
    process.exit(r1.status || 1);
  }
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      // Support both --key=value and --key value forms.
      const eq = a.indexOf('=');
      if (eq > 2) {
        out[toCamel(a.slice(2, eq))] = a.slice(eq + 1);
      } else {
        const key = a.slice(2);
        const next = argv[i + 1];
        if (next && !next.startsWith('--')) { out[toCamel(key)] = next; i++; }
        else out[toCamel(key)] = true;
      }
    } else {
      out._.push(a);
    }
  }
  return out;
}
function toCamel(s) { return s.replace(/-([a-z])/g, (_, c) => c.toUpperCase()); }

function printHelp() {
  console.log(`zillow-rental-manager skill dispatcher

Commands (daemon-first; recommended flow):
  daemon-start                      Spawn long-lived Chrome with --remote-debugging-port=9222.
                                    Required by CDP-attach commands. Avoids per-command warmups
                                    that trip PerimeterX. One Chrome, many attaches.
  daemon-stop                       Stop the daemon Chrome.
  daemon-status                     Show daemon pid, CDP reachability, Chrome version.

Commands (auth + work):
  login [--force]                   One-time Zillow login (auto-attaches to daemon if running,
                                    else launches a one-off Chrome). Polls server-side
                                    /users/get loggedIn:true. Visible Chrome required.
  status                            Show profile dir + breaker + daemon + pacing state
  reset-breaker                     Reset the 24h 403/captcha circuit breaker
  reset-pacing                      Clear the pacing call log (use after long downtime)
  explore [url] [--force]           Open Chrome on [url]. Ctrl-C to close cleanly.
  snapshot <url> <out-dir>          Navigate, wait for network idle, dump HTML + PNG + meta

Inbox + lead operations (drive UI, capture GraphQL responses):
  pull-inbox [--max=N] [--all] [--force-fetch]
                                    Pull conversation list, then for each unread (default) open the
                                    thread, capture full message + renter profile, and persist to
                                    ~/QUANTUM/raw/rental-property/leads/<slug>.md
                                    --all: include read leads too (still skips archived + spam).
                                    --force-fetch: ignore checkpoint, re-fetch every targeted thread.
                                    Paced 45-90s between thread fetches. Hard caps: 20/hour, 100/day.
  pull-thread <conversation_id>     Pull a single thread by id. Persists per-lead markdown +
                                    per-thread state. Requires inbox to have been opened first.
  send-reply <conversation_id> <body> [--live]
                                    Type body into the conversation. Default is dry-run (types
                                    then clears). Pass --live to actually click Send. Saves an
                                    immutable audit bundle either way.
  pacing-status                     Show last call timestamp, hourly/daily counts, caps.

Global flags:
  --headless                        (legacy launch mode only) run headless. Daemon mode follows
                                    the daemon's visibility setting at start time.
  --force                           Bypass circuit-breaker halt (discouraged)
  --live                            (send-reply only) actually click Send instead of dry-run

Env:
  ZRM_PROFILE_DIR                   Override profile dir (default ~/.shakos/chrome-profiles/zillow-rental-manager)
  ZRM_DEBUG_PORT                    CDP debug port (default 9222)
  ZRM_PROXY=http://user:pass@host:port   Residential proxy (legacy launch mode only). Consumer VPNs refused.
  ZRM_MIN_GAP_MS                    Min gap between paced ops (default 45000)
  ZRM_MAX_GAP_MS                    Max gap (jitter ceiling, default 90000)
  ZRM_HOURLY_CAP                    Max paced ops per hour (default 20)
  ZRM_DAILY_CAP                     Max paced ops per 24h (default 100)
  ZRM_DEBUG=1                       Print stack on error.`);
}

async function cmdStatus() {
  const { readBreaker, getProfileDir } = await import('./browser.mjs');
  const { daemonStatus } = await import('./daemon.mjs');
  const { pacingStatus } = await import('./pacing.mjs');
  const PROFILE_DIR = getProfileDir();
  const pidfile = join(PROFILE_DIR, '.skill.pid');
  const alivePid = existsSync(pidfile) ? parseInt(readFileSync(pidfile, 'utf8').trim(), 10) : null;
  const b = readBreaker();
  const ds = await daemonStatus();
  const pacing = pacingStatus();
  console.log('zillow-rental-manager status');
  console.log('  profile dir:', PROFILE_DIR);
  console.log('  profile exists:', existsSync(PROFILE_DIR));
  console.log('  legacy pidfile:', alivePid ? `pid ${alivePid}` : '(none)');
  console.log('  breaker:', JSON.stringify(b));
  console.log('  daemon pid:', ds.pid ?? '(none)', '| alive:', ds.alive, '| cdp:', ds.cdpReachable, ds.chromeVersion ? `(${ds.chromeVersion})` : '');
  console.log('  pacing:', `last_call=${pacing.last_call_at || '(never)'} (${pacing.seconds_since_last ?? '-'}s ago) | last_hour=${pacing.calls_last_hour}/${pacing.hourly_cap} | last_24h=${pacing.calls_last_24h}/${pacing.daily_cap} | gap=${pacing.min_gap_ms/1000}-${pacing.max_gap_ms/1000}s`);
}

async function cmdDaemonStart(argv) {
  const { startDaemon } = await import('./daemon.mjs');
  const visible = !argv.headless;
  const result = await startDaemon({ visible });
  if (!result.ok) {
    console.error('[zrm] daemon-start failed:', result.error);
    process.exit(1);
  }
  if (result.alreadyRunning) {
    console.log(`[zrm] daemon already running pid=${result.pid}`);
  } else {
    console.log(`[zrm] daemon started pid=${result.pid} cdp=${result.cdpUrl}`);
  }
}

async function cmdDaemonStop() {
  const { stopDaemon } = await import('./daemon.mjs');
  const result = await stopDaemon();
  console.log(`[zrm] ${result.msg}`);
}

async function cmdDaemonStatus() {
  const { daemonStatus } = await import('./daemon.mjs');
  const ds = await daemonStatus();
  console.log(JSON.stringify(ds, null, 2));
}

async function cmdResetBreaker() {
  const { writeBreaker } = await import('./browser.mjs');
  writeBreaker({ state: 'healthy', flagged_at: null, last_strike_at: null, count_24h: 0, events: [] });
  console.log('[zrm] breaker reset to healthy.');
}

async function cmdResetPacing() {
  const { resetPacing } = await import('./pacing.mjs');
  resetPacing();
  console.log('[zrm] pacing call log cleared.');
}

async function cmdPacingStatus() {
  const { pacingStatus } = await import('./pacing.mjs');
  console.log(JSON.stringify(pacingStatus(), null, 2));
}

async function cmdPullInbox(argv) {
  const { connectOrLaunch, installGracefulShutdown } = await import('./browser.mjs');
  const { pullInboxList, pullThread, persistThread } = await import('./inbox.mjs');
  const { readThreadState } = await import('./storage.mjs');
  const { enforceMinPacing } = await import('./pacing.mjs');
  const max = parseInt(argv.max || '0', 10);
  const force = !!argv.forceFetch;
  const includeAll = !!argv.all;

  // Pace BEFORE launch. Chrome's initial about:blank tab can auto-quit if it
  // sits idle while we sleep, leaving us with a closed page when we navigate.
  await enforceMinPacing('pull-inbox-list');

  const ctx = await connectOrLaunch({ headless: !!argv.headless, force: !!argv.force });
  installGracefulShutdown(() => ctx.close());
  console.log(`[zrm] pull-inbox starting (mode=${ctx.mode}${max ? `, max=${max}` : ''}${force ? ', force-fetch' : ''})`);

  try {
    const list = await pullInboxList(ctx.page);
    console.log(`[zrm] inbox list: ${list.length} conversations`);
    if (!list.length) return;

    // Triage: --all -> every non-archived, non-spam lead. Default -> unread only.
    const candidates = includeAll
      ? list.filter(l => !l.is_archived && !l.is_spam)
      : list.filter(l => l.has_unread && !l.is_archived && !l.is_spam);
    if (includeAll) {
      console.log(`[zrm] --all flag set: targeting ${candidates.length} non-archived/non-spam conversations (read + unread)`);
    }

    // Lead-checkpoint dedupe (per Gemini 2026-05-02 bypass strategy):
    // skip threads where the inbox-list timestamp matches what we recorded
    // on the last successful pull. Saves ~80% of paced calls in steady state.
    // --force-fetch bypasses this for full re-pulls.
    const fresh = [];
    let skipped = 0;
    for (const item of candidates) {
      if (force) { fresh.push(item); continue; }
      const prior = readThreadState(item.conversation_id);
      const priorTs = prior?.last_observed_list_message_at_ms;
      if (priorTs && item.last_message_at_ms && priorTs >= item.last_message_at_ms) {
        skipped++;
        continue;
      }
      fresh.push(item);
    }
    if (skipped > 0) {
      console.log(`[zrm] checkpoint: skipping ${skipped} thread(s) with no new messages since last pull (use --force-fetch to override)`);
    }

    const targets = (max > 0 ? fresh.slice(0, max) : fresh);
    const triageBlurb = includeAll
      ? 'all non-archived/non-spam, new since last pull'
      : 'unread + new since last pull, non-archived, non-spam';
    console.log(`[zrm] target threads to fetch: ${targets.length} (${triageBlurb})`);

    const persisted = [];
    for (let i = 0; i < targets.length; i++) {
      const item = targets[i];
      const statusBlurb = item.status_label || item.inquiry_state || (item.is_archived ? 'ARCHIVED' : '?');
      console.log(`[zrm] [${i+1}/${targets.length}] thread cid=${item.conversation_id} alias=${item.listing_alias} name="${item.name||'?'}" status=${statusBlurb}`);
      try {
        await enforceMinPacing(`pull-thread:${item.conversation_id}`);
        const thread = await pullThread(ctx.page, item.conversation_id, item.listing_alias);
        const r = persistThread(thread, { listItem: item });
        console.log(`[zrm]   persisted -> ${r.md_path}`);
        persisted.push(r);
      } catch (e) {
        console.error(`[zrm]   FAILED thread ${item.conversation_id}: ${e.message}`);
        if (e.code === 'PX_CHALLENGE' || e.code === 'PACING_HOURLY_CAP' || e.code === 'PACING_DAILY_CAP' || e.code === 'POST_FLAG_COOLDOWN') {
          console.error(`[zrm] aborting pull; ${e.code} hit. Resume after cooldown.`);
          break;
        }
      }
    }

    console.log(`[zrm] pull-inbox done. ${persisted.length}/${targets.length} threads persisted${skipped ? ` (${skipped} skipped via checkpoint)` : ''}.`);
  } finally {
    await ctx.close();
  }
}

async function cmdPullThread(argv) {
  const conversationId = argv._[1];
  if (!conversationId) {
    console.error('Usage: run.mjs pull-thread <conversation_id>');
    process.exit(2);
  }
  const { connectOrLaunch, installGracefulShutdown } = await import('./browser.mjs');
  const { pullInboxList, pullThread, persistThread } = await import('./inbox.mjs');
  const { enforceMinPacing } = await import('./pacing.mjs');
  await enforceMinPacing('pull-thread-cmd');
  const ctx = await connectOrLaunch({ headless: !!argv.headless, force: !!argv.force });
  installGracefulShutdown(() => ctx.close());
  try {
    const list = await pullInboxList(ctx.page);
    const item = list.find(x => x.conversation_id === conversationId);
    if (!item) {
      console.error(`[zrm] conversation ${conversationId} not visible in current inbox folder.`);
      process.exit(3);
    }
    await enforceMinPacing(`pull-thread:${conversationId}`);
    const thread = await pullThread(ctx.page, conversationId, item.listing_alias);
    const r = persistThread(thread, { listItem: item });
    console.log(`[zrm] persisted ${r.md_path}`);
  } finally {
    await ctx.close();
  }
}

async function cmdSendReply(argv) {
  const conversationId = argv._[1];
  const body = argv._.slice(2).join(' ');
  if (!conversationId || !body) {
    console.error('Usage: run.mjs send-reply <conversation_id> "<body>" [--live]');
    process.exit(2);
  }
  const dryRun = !argv.live;
  const { connectOrLaunch, installGracefulShutdown } = await import('./browser.mjs');
  const { pullInboxList, pullThread, sendReply, persistThread } = await import('./inbox.mjs');
  const { enforceMinPacing } = await import('./pacing.mjs');
  await enforceMinPacing('send-reply-cmd');
  const ctx = await connectOrLaunch({ headless: !!argv.headless, force: !!argv.force });
  installGracefulShutdown(() => ctx.close());
  try {
    const list = await pullInboxList(ctx.page);
    const item = list.find(x => x.conversation_id === conversationId);
    if (!item) {
      console.error(`[zrm] conversation ${conversationId} not visible in current inbox folder.`);
      process.exit(3);
    }
    await enforceMinPacing(`pull-thread:${conversationId}`);
    const thread = await pullThread(ctx.page, conversationId, item.listing_alias);
    persistThread(thread, { listItem: item });

    console.log(`[zrm] ${dryRun ? 'DRY-RUN' : 'LIVE'} sending to cid=${conversationId} (${body.length} chars)`);
    const result = await sendReply(ctx.page, conversationId, body, { dryRun });
    console.log(`[zrm] result: ok=${result.ok} dry_run=${result.dry_run} audit=${result.audit_dir}`);
    if (!dryRun && result.mutation_response) {
      console.log(`[zrm] mutation status=${result.mutation_response.status} op=${result.mutation_response.parsed?.operationName}`);
    }
  } finally {
    await ctx.close();
  }
}

async function cmdRebuildLeads(argv) {
  // Reads every thread state file in ~/.shakos/.../state/threads/<cid>.json
  // and writes the per-lead markdown using the CURRENT leadSlug schema. Lets
  // us migrate to a disambiguated slug (e.g. first+last) and clean up orphans
  // from the old schema -- without firing any paced GraphQL calls. Pure
  // local file-to-file transform.
  const { readdirSync, readFileSync, unlinkSync, statSync } = await import('node:fs');
  const { join } = await import('node:path');
  const { writeLeadMarkdown, leadSlug } = await import('./storage.mjs');
  const STATE_DIR = process.env.ZRM_STATE_DIR || `${process.env.HOME}/.shakos/playbook-output/zillow-rental-manager/state`;
  const threadsDir = join(STATE_DIR, 'threads');
  const QUANTUM_RAW = `${process.env.HOME}/QUANTUM/raw/rental-property/leads`;
  const dryRun = !argv.apply;

  let stateFiles = [];
  try { stateFiles = readdirSync(threadsDir).filter(f => f.endsWith('.json')); }
  catch (e) { console.error(`[zrm rebuild] no threads dir at ${threadsDir}`); return; }

  console.error(`[zrm rebuild] ${stateFiles.length} state files; ${dryRun ? 'DRY RUN (pass --apply to write)' : 'APPLYING'}`);
  const writtenSlugs = new Set();
  let collisions = 0;
  for (const fname of stateFiles) {
    const cid = fname.replace(/\.json$/, '');
    let st;
    try { st = JSON.parse(readFileSync(join(threadsDir, fname), 'utf8')); }
    catch (e) { console.error(`[zrm rebuild] skip ${fname}: ${e.message}`); continue; }

    const lead = {
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
      messages: st.messages || [],
      renter_profile: st.renter_profile || null,
      has_unread: !!st.has_unread,
      is_archived: !!st.is_archived,
      is_spam: !!st.is_spam,
      is_active: !!st.is_active
    };
    const slug = leadSlug({ name: lead.name, listingAlias: lead.listing_alias, phone: lead.phone, conversationId: lead.conversation_id });
    if (writtenSlugs.has(slug)) {
      collisions++;
      console.error(`[zrm rebuild] COLLISION: ${slug} already written; cid=${cid} name="${lead.name}"`);
    }
    writtenSlugs.add(slug);
    if (!dryRun) {
      try { writeLeadMarkdown(lead); console.error(`[zrm rebuild]   wrote ${slug}`); }
      catch (e) { console.error(`[zrm rebuild]   FAILED ${slug}: ${e.message}`); }
    } else {
      console.error(`[zrm rebuild]   would write ${slug} (cid=${cid}, name="${lead.name}")`);
    }
  }

  // Orphan cleanup pass: any *.md in QUANTUM_RAW whose slug is not in
  // writtenSlugs is from the old schema. Delete (always with --apply).
  let mdFiles = [];
  try { mdFiles = readdirSync(QUANTUM_RAW).filter(f => f.endsWith('.md')); } catch (_) {}
  let orphans = 0;
  for (const f of mdFiles) {
    const slug = f.replace(/\.md$/, '');
    if (writtenSlugs.has(slug)) continue;
    orphans++;
    if (!dryRun) {
      try { unlinkSync(join(QUANTUM_RAW, f)); console.error(`[zrm rebuild]   deleted orphan ${f}`); }
      catch (e) { console.error(`[zrm rebuild]   FAILED to delete orphan ${f}: ${e.message}`); }
    } else {
      console.error(`[zrm rebuild]   would delete orphan ${f}`);
    }
  }
  console.error(`[zrm rebuild] done. wrote=${writtenSlugs.size} collisions=${collisions} orphans=${orphans} (${dryRun ? 'DRY' : 'APPLIED'})`);
}

async function cmdExplore(argv) {
  const { launchContext, installGracefulShutdown, sanitizeUrl, warmUpZillow } = await import('./browser.mjs');
  const { installGlobalGraphqlTap } = await import('./inbox.mjs');
  const url = argv._[1] || 'https://www.zillow.com/rental-manager/';
  const ctx = await launchContext({ headless: !!argv.headless, force: !!argv.force });
  installGracefulShutdown(() => ctx.close());
  try {
    // Tap every inbox/graphql POST while Adithya browses. Records to
    // ~/.shakos/playbook-output/zillow-rental-manager/network/<date>/. No
    // pacing -- pacing only fires before scripted ops, not page-driven calls.
    installGlobalGraphqlTap(ctx.page);
    if (!argv.skipWarmup) await warmUpZillow(ctx.page);
    await ctx.page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    console.log(`[zrm] Opened ${sanitizeUrl(url)}. Global GraphQL tap is recording every inbox/graphql POST.`);
    console.log(`[zrm] Captures landing at ~/.shakos/playbook-output/zillow-rental-manager/network/`);
    console.log(`[zrm] Browse normally (click leads, send replies, view profiles). Ctrl-C to close.`);
    await new Promise((resolve) => {
      process.once('SIGINT', resolve);
      process.once('SIGTERM', resolve);
    });
  } finally {
    await ctx.close();
  }
}

async function cmdSnapshot(argv) {
  const url = argv._[1];
  const outDir = argv._[2];
  if (!url || !outDir) {
    console.error('Usage: run.mjs snapshot <url> <out-dir>');
    process.exit(2);
  }
  mkdirSync(outDir, { recursive: true });
  const { launchContext, installGracefulShutdown, sanitizeUrl, escalateOnCaptcha, warmUpZillow } = await import('./browser.mjs');
  const ctx = await launchContext({ headless: !!argv.headless, force: !!argv.force });
  installGracefulShutdown(() => ctx.close());
  try {
    if (!argv.skipWarmup) await warmUpZillow(ctx.page);
    await ctx.page.goto(url, { waitUntil: 'load', timeout: 60000 });
    await new Promise(r => setTimeout(r, 3500));
    if (await escalateOnCaptcha(ctx.page, 'snapshot')) {
      console.error('[zrm] Captcha blocked snapshot. Breaker tripped.');
      process.exitCode = 3;
      return;
    }
    const html = await ctx.page.content();
    writeFileSync(join(outDir, 'page.html'), html);
    await ctx.page.screenshot({ path: join(outDir, 'page.png'), fullPage: true });
    const meta = {
      requestedUrl: sanitizeUrl(url),
      finalUrl: sanitizeUrl(ctx.page.url()),
      ts: new Date().toISOString()
    };
    writeFileSync(join(outDir, 'meta.json'), JSON.stringify(meta, null, 2));
    console.log(`[zrm] snapshot saved to ${outDir} (finalUrl: ${meta.finalUrl})`);
  } finally {
    await ctx.close();
  }
}

(async () => {
  const argv = parseArgs(process.argv.slice(2));
  const cmd = argv._[0];
  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') { printHelp(); return; }

  if (cmd === 'status') { await cmdStatus(); return; }
  if (cmd === 'reset-breaker') { await cmdResetBreaker(); return; }
  if (cmd === 'reset-pacing') { await cmdResetPacing(); return; }
  if (cmd === 'pacing-status') { await cmdPacingStatus(); return; }
  if (cmd === 'daemon-start') { await cmdDaemonStart(argv); return; }
  if (cmd === 'daemon-stop') { await cmdDaemonStop(); return; }
  if (cmd === 'daemon-status') { await cmdDaemonStatus(); return; }

  ensureDeps();

  try {
    if (cmd === 'login') {
      const { runLogin } = await import('./login.mjs');
      await runLogin({ force: !!argv.force });
      return;
    }
    if (cmd === 'explore') { await cmdExplore(argv); return; }
    if (cmd === 'snapshot') { await cmdSnapshot(argv); return; }
    if (cmd === 'pull-inbox') { await cmdPullInbox(argv); return; }
    if (cmd === 'rebuild-leads') { await cmdRebuildLeads(argv); return; }
    if (cmd === 'pull-thread') { await cmdPullThread(argv); return; }
    if (cmd === 'send-reply') { await cmdSendReply(argv); return; }
    console.error('Unknown command:', cmd);
    printHelp();
    process.exit(2);
  } catch (e) {
    console.error('[zrm] ERROR:', e.message);
    if (e.code) console.error('  code:', e.code);
    if (process.env.ZRM_DEBUG === '1' && e.stack) console.error(e.stack);
    process.exit(1);
  }
})();
