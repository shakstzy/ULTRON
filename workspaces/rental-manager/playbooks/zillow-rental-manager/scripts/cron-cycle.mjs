// cron-cycle.mjs -- one full rental-manager pass.
//
// Sequence (each step short-circuits cleanly on its own; downstream steps
// continue):
//   1. gmail-ingest                    (Gmail-first lead + reply discovery —
//                                       replaces PerimeterX-blocked portal
//                                       scraper, see 2026-05-07 pivot)
//   2. auto-book --live                (book leads who picked a tour time)
//   3. contextual-send --live          (status-routed reply to anyone who
//                                       spoke since our last outbound)
//   4. application-notifier --live     (iMessage Adithya on new APPLIED)
//
// Designed to be the single launchd entry point; runs 3x daily.
//
// Env knobs:
//   ZRM_HOURLY_CAP / ZRM_DAILY_CAP   pacing override (default 9999/9999;
//                                     the in-script ceilings remain the
//                                     real safety net, see pacing.mjs)
//   ZRM_DRY_RUN=1                    force dry-run on send + notifier
//                                     (calendar lookups still happen)

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

import { STATE_DIR } from './paths.mjs';

const SCRIPTS_DIR = dirname(fileURLToPath(import.meta.url));
const CRON_LOG_DIR = join(STATE_DIR, 'cron-runs');

function ensureDir(p) { if (!existsSync(p)) mkdirSync(p, { recursive: true }); }

function runStep(label, args, { timeoutMs = 30 * 60 * 1000 } = {}) {
  console.error(`\n========== ${label} ==========`);
  const t0 = Date.now();
  const r = spawnSync('node', args, {
    cwd: SCRIPTS_DIR,
    encoding: 'utf8',
    stdio: ['ignore', 'inherit', 'inherit'],
    timeout: timeoutMs,
    env: {
      ...process.env,
      // Defaults — if caller already set, keep their value.
      ZRM_HOURLY_CAP: process.env.ZRM_HOURLY_CAP || '9999',
      ZRM_DAILY_CAP: process.env.ZRM_DAILY_CAP || '9999'
    }
  });
  const dur = Date.now() - t0;
  return { ok: r.status === 0, exit: r.status, dur_ms: dur };
}

function main() {
  ensureDir(CRON_LOG_DIR);
  const runId = `cycle-${new Date().toISOString().replace(/[:.]/g, '-')}`;
  const logPath = join(CRON_LOG_DIR, `${runId}.json`);

  const dry = process.env.ZRM_DRY_RUN === '1';
  const liveFlag = dry ? '--dry' : '--live';

  console.error(`[cron-cycle] start ${runId} (dry=${dry})`);

  const steps = [];

  // 1. INGEST — Gmail-first. The legacy portal scraper (run.mjs pull-inbox)
  // is no longer in this pipeline; PerimeterX 403'd it consistently.
  steps.push({
    name: 'gmail-ingest',
    ...runStep('gmail-ingest', ['gmail-ingest.mjs', '--days', '90'], { timeoutMs: 15 * 60_000 })
  });

  // 2. AUTO-BOOK (always live unless ZRM_DRY_RUN=1)
  steps.push({
    name: 'auto-book',
    ...runStep('auto-book', ['auto-book.mjs', liveFlag], { timeoutMs: 25 * 60_000 })
  });

  // 3. CONTEXTUAL-SEND
  steps.push({
    name: 'contextual-send',
    ...runStep('contextual-send', ['contextual-send.mjs', liveFlag], { timeoutMs: 30 * 60_000 })
  });

  // 4. APPLICATION-NOTIFIER
  steps.push({
    name: 'application-notifier',
    ...runStep('application-notifier', ['application-notifier.mjs', liveFlag], { timeoutMs: 60_000 })
  });

  const result = {
    run_id: runId,
    started_at: new Date().toISOString(),
    dry_run: dry,
    steps
  };
  writeFileSync(logPath, JSON.stringify(result, null, 2));

  const failed = steps.filter(s => !s.ok);
  console.error(`\n[cron-cycle] done ${runId}. ${steps.length - failed.length}/${steps.length} steps ok.`);
  console.error(`[cron-cycle] log -> ${logPath}`);

  // Exit non-zero if ingest itself failed (downstream may still have done
  // useful work; we surface the most-critical failure for launchd).
  if (failed.find(s => s.name === 'gmail-ingest')) process.exit(2);
  if (failed.length) process.exit(1);
}

main();
