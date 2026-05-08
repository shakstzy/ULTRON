#!/usr/bin/env node
// run.mjs -- CLI dispatcher. First run auto-installs deps (patchright + chrome binary).
// Usage:
//   node scripts/run.mjs login
//   node scripts/run.mjs image --model nano-banana-pro --prompt "..."
//   node scripts/run.mjs video --model seedance_2_0_fast --prompt "..."
//   node scripts/run.mjs marketing --preset UGC --prompt "..."
//   node scripts/run.mjs cinema --mode video --scene "..."
//   node scripts/run.mjs resume <run-dir>
//   node scripts/run.mjs status
//   node scripts/run.mjs reset-breaker

import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = resolve(HERE, '..');
const NODE_MODULES = join(SKILL_ROOT, 'node_modules');

function ensureDeps() {
  if (existsSync(join(NODE_MODULES, 'patchright'))) return;
  console.log('[higgsfield] First run: installing dependencies (patchright + Chrome binary). This may take a few minutes.');
  const r1 = spawnSync('npm', ['install'], { cwd: SKILL_ROOT, stdio: 'inherit' });
  if (r1.status !== 0) {
    console.error('[higgsfield] npm install failed. Run `npm install` manually in', SKILL_ROOT);
    process.exit(r1.status || 1);
  }
  // patchright install chrome is run by postinstall script in package.json.
}

// Flags that may be repeated. Repeated values accumulate into an array.
const REPEATABLE_FLAGS = new Set(['ref']);

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const camelKey = toCamel(key);
      const next = argv[i + 1];
      const value = next && !next.startsWith('--') ? next : true;
      if (next && !next.startsWith('--')) i++;
      if (REPEATABLE_FLAGS.has(key) || REPEATABLE_FLAGS.has(camelKey)) {
        // Repeatable flags require a non-empty value; silent drop produces
        // "no refs" instead of a loud error, masking typos.
        if (value === true || value === '' || value === undefined || value === null) {
          throw new Error(`--${key} requires a value (got empty). Use --${key} <path>.`);
        }
        if (!Array.isArray(out[camelKey])) out[camelKey] = out[camelKey] ? [out[camelKey]] : [];
        out[camelKey].push(value);
      } else {
        out[camelKey] = value;
      }
    } else {
      out._.push(a);
    }
  }
  return out;
}
function toCamel(s) { return s.replace(/-([a-z])/g, (_, c) => c.toUpperCase()); }

function printHelp() {
  console.log(`higgsfield skill dispatcher

Commands:
  login                             One-time Clerk login (visible browser)
  image --model M --prompt "..."    Nano Banana Pro or Soul Cinematic
  video --model M --prompt "..."    AI Video (Kling / Seedance / Veo / Wan / Sora / Minimax slugs)
  marketing --preset P --prompt ".." Marketing Studio (--project-id or --new)
  cinema --mode image|video --scene "..."  Cinema Studio (--project-id or --new)
  batch --jobs <file.jsonl>         Submit N image jobs in parallel (shared browser)
  resume <run-dir>                  Resume a crashed run from its state.json
  status                            Show wallet balance + breaker state + active pidfile
  reset-breaker                     Reset the 403 circuit breaker (after you solve captcha manually)

Global flags:
  --output DIR                      Override default output dir
  --dry-run                         Print the POST body and exit; do not hit the network
  --debug                           On error, leave the browser open for inspection
  --force                           Bypass circuit-breaker halt (strongly discouraged)
  --unlim                           Use your subscription's unlim allowance
  --free-gens                       Use free daily gens if available

Picker flags (image + video + cinema + marketing, where supported):
  --aspect RATIO                    Aspect ratio pill: 3:4, 1:1, 16:9, 9:16, Auto, etc.
  --res LABEL                       Resolution/quality pill: 1K/2K/4K or 720p/1080p
  --batch N                         Batch size (image only, N out of 4 default)
  --duration Ns                     Video duration: 3s/5s/8s/10s (model-dependent)
  --ref PATH                        Reference file to attach. Repeat flag for multiple refs.

Batch flags:
  --jobs FILE.jsonl                 JSONL of image jobs, one per line. Keys: prompt, model, aspect, res, batch, ref.
  --concurrency N                   Max in-flight jobs (default 4, ceiling 8).

Env:
  HF_PROXY=http://user:pass@host:port   Residential proxy (DO NOT use a consumer VPN)
  HF_TYPING_WPM_MIN / HF_TYPING_WPM_MAX
  HF_JITTER_MS_MIN  / HF_JITTER_MS_MAX
  HF_BROWSE_PHASE=0                     Disable browse phase (discouraged)
  HF_DEBUG=1                            Verbose`);
}

async function cmdStatus() {
  const { readBreaker, getProfileDir } = await import('./browser.mjs');
  const PROFILE_DIR = getProfileDir();
  const pidfile = join(PROFILE_DIR, '.skill.pid');
  const alivePid = existsSync(pidfile) ? parseInt(readFileSync(pidfile, 'utf8').trim(), 10) : null;
  const b = readBreaker();
  console.log('higgsfield status');
  console.log('  profile dir:', PROFILE_DIR);
  console.log('  pidfile:', alivePid ? `pid ${alivePid}` : '(none)');
  console.log('  breaker:', JSON.stringify(b));
}

async function cmdResetBreaker() {
  const { writeBreaker, getProfileDir } = await import('./browser.mjs');
  writeBreaker({ state: 'healthy', flagged_at: null, count_24h: 0, events: [] });
  console.log('[higgsfield] breaker reset to healthy. Next run will launch normally.');
}

// Download-only resume. Reads state.json's job_uuid, opens History panel, finds
// the matching completed asset, downloads. Never re-submits — protects against
// the "I paid for a 30-min video, the CLI timed out, where's my output?" case.
async function cmdResume(runDir) {
  const { readState } = await import('./state.mjs');
  const s = await readState(runDir);
  if (!s) { console.error('No state.json at', runDir); process.exit(2); }
  console.log(`[higgsfield] resume (download-only): status=${s.status} cmd=${s.cmd} job_uuid=${s.job_uuid || '(none)'} prompt=${s.prompt?.slice(0, 80)}`);
  if (s.status === 'saved') { console.log('Already saved. Files in', runDir); return; }
  if (!s.job_uuid) {
    console.error('No job_uuid in state.json — this run never reached the submitted phase. Resume cannot recover. Re-run the original command instead.');
    process.exit(2);
  }
  if (s.cmd === 'batch') {
    console.error('Resume for batch runs is not supported in v1. Each per-job state.json under the batch run dir can be resumed individually.');
    process.exit(2);
  }

  const { launchContext } = await import('./browser.mjs');
  const { waitForCapturedJwt } = await import('./jwt.mjs');
  const { openHistoryPanel, scrapeUserAssets, userIdFromJwtCapture, bestDownloadUrl } = await import('./ui-submit.mjs');
  const { downloadAll, finalize, getWallet, walletTotal } = await import('./job.mjs');
  const { transition } = await import('./state.mjs');
  const { browsePhase } = await import('./behavior.mjs');

  const ctx = await launchContext({ force: true, headless: false });
  try {
    const url = s.tool_url || (s.cmd === 'video' ? 'https://higgsfield.ai/ai/video' : 'https://higgsfield.ai/ai/image');
    await ctx.page.goto(url, { waitUntil: 'load', timeout: 45000 });
    const wait = await waitForCapturedJwt(ctx.jwtCapture, { timeoutMs: 30000 });
    if (!wait.ok) throw new Error(`No Clerk JWT observed: ${wait.reason}. Run 'login' to refresh session.`);
    const userSub = userIdFromJwtCapture(ctx.jwtCapture);
    if (!userSub) throw new Error('Could not extract user_id from captured JWT.');
    const userSubstr = userSub.replace(/^user_/, '');

    await openHistoryPanel(ctx.page);
    await browsePhase(ctx.page);

    const isVideo = s.cmd === 'video' || (s.cmd === 'cinema' && /video/i.test(s.params?.mode || ''));
    const timeoutMs = (isVideo ? 30 : 5) * 60 * 1000;
    console.log(`[higgsfield] scanning History panel for completed asset (up to ${Math.round(timeoutMs/60000)} min)...`);
    const start = Date.now();
    let fresh = [];
    while (Date.now() - start < timeoutMs) {
      const all = await scrapeUserAssets(ctx.page, userSubstr);
      if (isVideo) fresh = all.filter(a => a.kind === 'video' || a.kind === 'video_thumbnail');
      else fresh = all.filter(a => a.kind === 'image');
      if (fresh.length > 0) break;
      await new Promise(r => setTimeout(r, 5000));
    }
    if (fresh.length === 0) {
      throw new Error('Resume found no completed asset in History within timeout. Job may still be processing; rerun resume later.');
    }
    const newest = fresh[0];
    console.log(`[higgsfield] newest matching asset: ${newest.cdn}`);
    console.log('[higgsfield] WARNING: resume matches by newest, not by job_uuid. Verify the file matches the run before relying on it.');

    const dlUrl = bestDownloadUrl(newest);
    await transition(runDir, 'downloading', { resumed: true });
    const records = await downloadAll(runDir, [dlUrl]);
    const walletAfter = await getWallet(ctx.page, ctx.jwtCapture);
    const meta = await finalize(runDir, {
      wallet_before: null, wallet_after: walletTotal(walletAfter),
      job_uuid: s.job_uuid, job: null, records,
      cmd: s.cmd, model_frontend: s.model_frontend, model_backend: s.model_backend,
      prompt: s.prompt, params: s.params || {}
    });
    console.log(`[higgsfield] resume SAVED ${records.length} file(s) to ${runDir}`);
    for (const r of records) console.log(`  ${r.local_path} (${r.bytes} bytes, ${r.content_type})`);
    return { runDir, metadata: meta, resumed: true };
  } finally {
    await ctx.close();
  }
}

async function handlerFor(cmd) {
  if (cmd === 'login') return (await import('./login.mjs')).runLogin;
  if (cmd === 'image') return (await import('./image.mjs')).runImage;
  if (cmd === 'video') return (await import('./video.mjs')).runVideo;
  if (cmd === 'marketing') return (await import('./marketing.mjs')).runMarketing;
  if (cmd === 'cinema') return (await import('./cinema.mjs')).runCinema;
  if (cmd === 'batch') return (await import('./batch.mjs')).runBatch;
  throw new Error('Unknown command: ' + cmd);
}

(async () => {
  const argv = parseArgs(process.argv.slice(2));
  const cmd = argv._[0];
  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') { printHelp(); return; }

  if (cmd === 'status') { await cmdStatus(); return; }
  if (cmd === 'reset-breaker') { await cmdResetBreaker(); return; }

  ensureDeps();

  try {
    if (cmd === 'recon') {
      const { runRecon } = await import('./recon.mjs');
      await runRecon();
      return;
    }
    if (cmd === 'resume') {
      const runDir = argv._[1];
      if (!runDir) { console.error('Usage: run.mjs resume <run-dir>'); process.exit(2); }
      await cmdResume(runDir);
      return;
    }
    const fn = await handlerFor(cmd);
    await fn(argv);
  } catch (e) {
    console.error('[higgsfield] ERROR:', e.message);
    if (e.code) console.error('  code:', e.code);
    if (process.env.HF_DEBUG === '1' && e.stack) console.error(e.stack);
    process.exit(1);
  }
})();
