#!/usr/bin/env node
// podcast-outreach skill dispatcher. Single entrypoint for every verb.
//
//   node scripts/run.mjs <verb> [flags]
//
// Verbs:
//   status, ensure-labels, discover, enqueue, send, scan-replies,
//   daily-cycle, dump-queue, halt
//
// Write verbs (send, daily-cycle, ensure-labels, scan-replies promote)
// default to DRY-RUN. Pass --send to execute. Per the new-send-skill
// agent-learning: smoke tests must use --dry-run, never real sends.

import fs from "node:fs/promises";
import path from "node:path";
import { audit, dim, err, info, ok, step, warn } from "../src/runtime/logger.mjs";
import { abortIfHalted, clearHalt, isHalted, setHalt } from "../src/runtime/halt.mjs";
import { jitteredSleep } from "../src/runtime/humanize.mjs";
import {
  assertDailyHeadroom,
  CapExceededError,
  getRemainingToday,
  getSentToday,
  loadCaps,
  recordSend,
} from "../src/runtime/caps.mjs";
import {
  ACCOUNT_EMAIL,
  DRY_RUN_DIR,
  LABEL_ARCHIVED,
  LABEL_PRIORITY,
  LOW_QUALITY_FILE,
  RAW_DEPOSIT_ROOT,
  STATE_HOME,
} from "../src/runtime/paths.mjs";
import * as Queue from "../src/pipeline/queue.mjs";
import * as Sent from "../src/pipeline/sent-log.mjs";
import {
  applyLabelToThread,
  ensureLabels,
  findLabel,
} from "../src/pipeline/labels.mjs";
import { renderEmail } from "../src/sender/template.mjs";
import { searchSentToEmail, sendEmail } from "../src/sender/gmail-send.mjs";
import { scanReplies } from "../src/replies/scanner.mjs";
import * as SeedCursor from "../src/discover/seed-cursor.mjs";
import { discoverFromSeeds } from "../src/discover/listennotes.mjs";
import { isLowQualityEmail, isValidEmail } from "../src/discover/rss-extractor.mjs";

const argv = process.argv.slice(2);
const verb = argv[0];
const rest = argv.slice(1);

if (!verb || verb === "--help" || verb === "-h") {
  printHelp();
  process.exit(verb ? 0 : 1);
}

const verbs = {
  status: vStatus,
  "ensure-labels": vEnsureLabels,
  discover: vDiscover,
  enqueue: vEnqueue,
  send: vSend,
  "scan-replies": vScanReplies,
  "daily-cycle": vDailyCycle,
  "dump-queue": vDumpQueue,
  halt: vHalt,
};

const handler = verbs[verb];
if (!handler) {
  err(`Unknown verb: ${verb}`);
  printHelp();
  process.exit(1);
}

try {
  const code = await handler(parseArgs(rest));
  process.exit(code ?? 0);
} catch (e) {
  err(`[${verb}] ${e.code || "ERR"} ${e.message}`);
  if (process.env.DEBUG) console.error(e.stack);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Verbs
// ---------------------------------------------------------------------------

async function vStatus(args) {
  const halted = await isHalted();
  const queueSize = await Queue.size();
  const sentToday = await getSentToday();
  const remaining = await getRemainingToday();
  const seedStatus = await SeedCursor.status();
  const caps = await loadCaps();
  const out = {
    account: ACCOUNT_EMAIL,
    halted,
    queue_size: queueSize,
    sent_today: sentToday,
    remaining_today: remaining,
    daily_cap: caps.daily_send_cap,
    target_queue_size: caps.target_queue_size,
    seed_cursor: seedStatus,
  };
  if (args.json) {
    console.log(JSON.stringify(out, null, 2));
  } else {
    console.log(`account:        ${out.account}`);
    console.log(`halted:         ${out.halted}`);
    console.log(`queue size:     ${out.queue_size}`);
    console.log(`sent today:     ${out.sent_today} / ${out.daily_cap}`);
    console.log(`remaining:      ${out.remaining_today}`);
    console.log(`target queue:   ${out.target_queue_size}`);
    console.log(`seed cursor:    cycle=${seedStatus.cycle} idx=${seedStatus.idx}/${seedStatus.total}`);
  }
  return 0;
}

async function vEnsureLabels(args) {
  await abortIfHalted();
  const labels = await ensureLabels({ send: !!args.send });
  if (!args.send) {
    info("dry-run: no labels actually created. Pass --send to execute.");
  }
  ok("labels ensured");
  await audit("ensure-labels", { send: !!args.send, labels: Object.keys(labels) });
  return 0;
}

async function vDiscover(args) {
  await abortIfHalted();
  const caps = await loadCaps();
  const seedCount = parseInt(args.seeds || caps.discover_seed_default, 10);
  const targetQueue = parseInt(args["target-queue"] || caps.target_queue_size, 10);
  const concurrency = parseInt(args.concurrency || caps.discover_concurrency, 10);
  const perSeedMax = parseInt(args["per-seed-max"] || caps.discover_per_seed_max, 10);
  const headful = !args.headless;

  const currentSize = await Queue.size();
  if (currentSize >= targetQueue && !args.force) {
    info(`queue size ${currentSize} >= target ${targetQueue}; skipping discover (use --force to override)`);
    return 0;
  }

  const seeds = await SeedCursor.nextN(seedCount);
  step(`discover: ${seeds.length} seeds, concurrency=${concurrency}, per-seed-max=${perSeedMax}, headful=${headful}`);

  const { launchPersistent } = await import("../src/discover/launcher.mjs");
  const { ctx } = await launchPersistent({ headless: !headful });
  let candidates = [];
  try {
    candidates = await discoverFromSeeds({ ctx, seeds, concurrency, perSeedMax, capsCfg: caps });
  } finally {
    try { await ctx.close(); } catch { /* ignore */ }
  }

  step(`discover: ${candidates.length} raw candidates`);

  // Dedup vs queue + sent log
  const sentSet = await Sent.emailSet({ excludeDryRun: true });
  const queued = await Queue.readAll();
  const queuedSet = new Set(queued.map((r) => (r.email || "").toLowerCase()).filter(Boolean));

  const fresh = [];
  const lowQuality = [];
  const seenEmail = new Set();
  for (const c of candidates) {
    const email = (c.email || "").trim().toLowerCase();
    if (!email || !isValidEmail(email)) continue;
    if (sentSet.has(email)) continue;
    if (queuedSet.has(email)) continue;
    if (seenEmail.has(email)) continue;

    if (isLowQualityEmail(email, caps.low_quality_email_prefixes)) {
      lowQuality.push({ ...c, email, _reason: "low-quality-prefix" });
      seenEmail.add(email);
      continue;
    }

    seenEmail.add(email);
    fresh.push({
      email,
      podcast_name: c.podcast_name || null,
      host_name: c.host_name || null,
      recent_episode: c.recent_episode || null,
      website: c.website || null,
      rss_url: c.rss_url || null,
      description: (c.description || "").slice(0, 280),
      source_seed: c._source_seed || null,
      source_url: c.url || null,
      discovered_at: new Date().toISOString(),
    });
  }

  await Queue.append(fresh);
  if (lowQuality.length) {
    await fs.appendFile(
      LOW_QUALITY_FILE,
      lowQuality.map((r) => JSON.stringify(r)).join("\n") + "\n",
      "utf8",
    );
  }

  // Deposit raw markdown digests for traceability
  if (fresh.length) {
    await depositRaw(fresh, seeds);
  }

  ok(`discover: appended ${fresh.length} fresh, low-quality ${lowQuality.length}, dups ${candidates.length - fresh.length - lowQuality.length}`);
  await audit("discover", {
    seed_count: seeds.length,
    raw: candidates.length,
    fresh: fresh.length,
    low_quality: lowQuality.length,
    queue_size_after: await Queue.size(),
  });
  return 0;
}

async function depositRaw(rows, seeds) {
  const now = new Date();
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const dir = path.join(RAW_DEPOSIT_ROOT, ym);
  await fs.mkdir(dir, { recursive: true });
  const ts = now.toISOString().replace(/[:.]/g, "-");
  const file = path.join(dir, `discover-${ts}.md`);
  const seedSummary = seeds.map((s) => s.kind === "genre" ? `genre:${s.slug}` : `q:${s.q}`).join(", ");
  const lines = [
    "---",
    `source: listennotes`,
    `workspace: eclipse`,
    `ingested_at: ${now.toISOString()}`,
    `ingest_version: 1`,
    `seed_count: ${seeds.length}`,
    `candidate_count: ${rows.length}`,
    `seeds: "${seedSummary.replace(/"/g, '\\"')}"`,
    "---",
    ``,
    `# Listennotes discover — ${ts}`,
    ``,
    `Seeds: ${seedSummary}`,
    ``,
    `## Candidates (${rows.length})`,
    ``,
  ];
  for (const r of rows) {
    lines.push(`### ${r.podcast_name || "(unnamed)"}`);
    lines.push(`- email: \`${r.email}\``);
    if (r.host_name) lines.push(`- host: ${r.host_name}`);
    if (r.recent_episode) lines.push(`- recent ep: ${r.recent_episode}`);
    if (r.website) lines.push(`- website: ${r.website}`);
    if (r.rss_url) lines.push(`- rss: ${r.rss_url}`);
    if (r.source_url) lines.push(`- listennotes: ${r.source_url}`);
    if (r.source_seed) lines.push(`- seed: ${r.source_seed}`);
    lines.push("");
  }
  await fs.writeFile(file, lines.join("\n"), "utf8");
  dim(`raw deposit: ${file}`);
}

async function vEnqueue(args) {
  const file = args._[0];
  if (!file) throw new Error("usage: enqueue <jsonl-file>");
  const raw = await fs.readFile(file, "utf8");
  const rows = raw.split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const sentSet = await Sent.emailSet({ excludeDryRun: true });
  const queued = await Queue.readAll();
  const queuedSet = new Set(queued.map((r) => (r.email || "").toLowerCase()).filter(Boolean));
  const fresh = rows.filter((r) => {
    const e = (r.email || "").toLowerCase();
    if (!e || !isValidEmail(e)) return false;
    if (sentSet.has(e)) return false;
    if (queuedSet.has(e)) return false;
    return true;
  });
  await Queue.append(fresh);
  ok(`enqueue: ${fresh.length}/${rows.length} appended`);
  return 0;
}

async function vSend(args) {
  await abortIfHalted();
  const send = !!args.send;
  const limit = parseInt(args.limit || 200, 10);
  const caps = await loadCaps();

  if (send) {
    try {
      await assertDailyHeadroom(1);
    } catch (e) {
      if (e instanceof CapExceededError) {
        warn(`daily cap reached: sent_today=${(await getSentToday())}/${caps.daily_send_cap}`);
        return 0;
      }
      throw e;
    }
  }

  const remaining = send ? await getRemainingToday() : limit;
  const toPop = Math.min(limit, remaining || limit);
  const batch = await Queue.popN(toPop);
  if (!batch.length) {
    info(`queue empty; nothing to send`);
    return 0;
  }
  step(`send: ${batch.length} message(s) (mode=${send ? "LIVE" : "dry-run"})`);

  // Dry-run never touches gmail — no label lookup, no auth dependency.
  let archivedLabel = null;
  if (send) {
    try {
      archivedLabel = await findLabel(LABEL_ARCHIVED);
    } catch (e) {
      warn(`label lookup failed (likely gog auth): ${e.message}`);
      warn(`re-queueing ${batch.length} popped rows; run: gog auth login ${ACCOUNT_EMAIL}`);
      await Queue.append(batch);
      return 1;
    }
    if (!archivedLabel) {
      warn(`label "${LABEL_ARCHIVED}" missing; run ensure-labels --send first`);
      await Queue.append(batch);
      return 1;
    }
  }

  let okCount = 0, failCount = 0, dupCount = 0;
  for (const row of batch) {
    if (send) {
      try {
        await assertDailyHeadroom(1);
      } catch (e) {
        warn(`daily cap reached mid-loop; deferring remainder back to queue`);
        const idx = batch.indexOf(row);
        const remainder = batch.slice(idx);
        await Queue.append(remainder);
        break;
      }
      // Live duplicate guard — gmail search by `to:<email>`. If we ever sent
      // anything, skip + log.
      try {
        const prior = await searchSentToEmail(row.email);
        if (prior && prior.length) {
          dim(`skip duplicate (gmail history): ${row.email}`);
          dupCount += 1;
          continue;
        }
      } catch (e) {
        // gmail unreachable — fall through, sent.jsonl is still authoritative.
        dim(`gmail dup-check failed for ${row.email}: ${e.message}`);
      }
    }

    let rendered;
    try {
      rendered = await renderEmail(row);
    } catch (e) {
      warn(`render failed for ${row.email}: ${e.message}`);
      failCount += 1;
      continue;
    }

    let result;
    try {
      result = await sendEmail({
        to: row.email,
        subject: rendered.subject,
        body: rendered.body,
        send,
      });
    } catch (e) {
      err(`send failed for ${row.email}: ${e.message}`);
      failCount += 1;
      continue;
    }

    if (send && result.thread_id && archivedLabel) {
      try {
        await applyLabelToThread(result.thread_id, archivedLabel.id, { send: true });
      } catch (e) {
        warn(`label apply failed for thread ${result.thread_id}: ${e.message}`);
      }
    }

    await Sent.append({
      email: row.email,
      podcast_name: row.podcast_name || null,
      host_name: row.host_name || null,
      sent_at: new Date().toISOString(),
      gmail_thread_id: result.thread_id,
      gmail_message_id: result.message_id,
      dry_run: !send,
    });
    if (send) await recordSend(1);
    okCount += 1;

    if (send && okCount < batch.length) {
      const [lo, hi] = caps.send_jitter_ms;
      await jitteredSleep(lo, hi);
    }
  }

  ok(`send: ok=${okCount} fail=${failCount} dup=${dupCount} mode=${send ? "LIVE" : "dry-run"}`);
  await audit("send-batch", { ok: okCount, fail: failCount, dup: dupCount, send });
  return failCount > 0 ? 1 : 0;
}

async function vScanReplies(args) {
  const caps = await loadCaps();
  const lookback = parseInt((args.lookback || "").replace(/d$/, "") || caps.reply_lookback_days, 10);
  const send = !!args.send;
  const max = parseInt(args["max-threads"] || caps.reply_scan_max_threads, 10);
  await scanReplies({ lookbackDays: lookback, send, maxThreads: max });
  return 0;
}

async function vDailyCycle(args) {
  await abortIfHalted();
  const send = !!args.send;
  const caps = await loadCaps();

  step(`daily-cycle (mode=${send ? "LIVE" : "dry-run"})`);

  // 1. Scan replies first — promoting labels is non-destructive even live.
  try {
    await scanReplies({ lookbackDays: caps.reply_lookback_days, send, maxThreads: caps.reply_scan_max_threads });
  } catch (e) {
    warn(`scan-replies stage failed: ${e.message} — continuing to discover/send`);
  }

  // 2. Top up queue if below target.
  const queueBefore = await Queue.size();
  if (queueBefore < caps.target_queue_size) {
    info(`queue ${queueBefore} < target ${caps.target_queue_size}; running discover`);
    try {
      await vDiscover({ seeds: String(caps.discover_seed_default) });
    } catch (e) {
      warn(`discover stage failed: ${e.message}`);
    }
  } else {
    info(`queue ${queueBefore} >= target ${caps.target_queue_size}; skipping discover`);
  }

  // 3. Send up to remaining daily headroom.
  const remaining = send ? await getRemainingToday() : caps.daily_send_cap;
  if (remaining > 0) {
    await vSend({ send, limit: String(Math.min(remaining, caps.daily_send_cap)) });
  } else {
    info(`daily cap reached; no sends`);
  }

  ok("daily-cycle complete");
  return 0;
}

async function vDumpQueue(args) {
  const limit = args.limit ? parseInt(args.limit, 10) : Infinity;
  const rows = await Queue.peekN(limit);
  for (const r of rows) console.log(JSON.stringify(r));
  return 0;
}

async function vHalt(args) {
  if (args.clear) {
    await clearHalt();
    ok("halt cleared");
  } else {
    await setHalt(args._.join(" ") || "manual halt");
    ok("halt set");
  }
  return 0;
}

// ---------------------------------------------------------------------------
// Argv parser. Supports --flag, --flag=value, --flag value, and positional.
// ---------------------------------------------------------------------------

function parseArgs(rest) {
  const out = { _: [] };
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a.startsWith("--")) {
      const eq = a.indexOf("=");
      let key, val;
      if (eq >= 0) {
        key = a.slice(2, eq);
        val = a.slice(eq + 1);
      } else {
        key = a.slice(2);
        const next = rest[i + 1];
        if (next != null && !next.startsWith("--")) {
          val = next;
          i += 1;
        } else {
          val = true;
        }
      }
      out[key] = val;
    } else {
      out._.push(a);
    }
  }
  return out;
}

function printHelp() {
  console.log(`Usage: node scripts/run.mjs <verb> [flags]

Verbs:
  status                                Show queue size, sent-today, halt state, seed cursor.
  ensure-labels [--send]                Create podcast-archived + podcast-priority labels (idempotent).
  discover [--seeds N] [--concurrency N] [--per-seed-max N] [--target-queue N] [--headless] [--force]
                                        Scrape Listennotes via N seeds, dedup, append to queue.
  enqueue <jsonl-file>                  Bulk-append a hand-curated batch.
  send [--limit N=200] [--send]         Pop N from queue, render + send, label archived. DEFAULT DRY-RUN.
  scan-replies [--lookback Nd=14] [--send] [--max-threads N]
                                        Promote replied threads from archived → priority. DEFAULT DRY-RUN.
  daily-cycle [--send]                  Cron entry: scan-replies → discover (if low) → send. DEFAULT DRY-RUN.
  dump-queue [--limit N]                Emit queue contents as JSONL.
  halt [--clear] [reason...]            Toggle the kill switch.

Account: adithya@eclipse.builders (single).
Workspace: eclipse (single).
Daily cap: 2000.
`);
}
