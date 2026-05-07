#!/usr/bin/env node
// Drains 04-outbound/approved/ via patchright. Up to 15 messages per invocation by default
// (cron schedules ~15 invocations across the day, ~225/day target). Pass --all to drain everything
// in one session, or pass a numeric arg to override the per-fire cap.

import { launchPersistent } from "../src/runtime/profile.mjs";
import { sendMessage } from "../src/tinder/send.mjs";
import { listQueue, moveQueueItem, extractDraftedReply, readQueueItem } from "../src/runtime/queue.mjs";
import { abortIfHalted } from "../src/runtime/halt.mjs";
import { logSession } from "../src/runtime/logger.mjs";
import { sleep, jitter } from "../src/runtime/humanize.mjs";
import { recordRedirect, clearRedirects } from "../src/runtime/entity-store.mjs";

const drainAll = process.argv.includes("--all");
const dryRun = process.argv.includes("--dry-run");
const explicitLimit = parseInt(process.argv.find(a => /^\d+$/.test(a)) || "0", 10);
const DEFAULT_PER_FIRE = 15;
await abortIfHalted();

const queue = await listQueue("approved");
if (queue.length === 0) {
  console.log("approved_queue:empty");
  process.exit(0);
}

const limit = drainAll ? queue.length : (explicitLimit > 0 ? explicitLimit : DEFAULT_PER_FIRE);
const todo = queue.slice(0, limit);

const { ctx, page } = await launchPersistent({ headless: false });
let sent = 0;       // truly delivered
let dryRunCount = 0; // typed-but-not-sent (dry-run only)
let failed = 0;
try {
  await page.goto("https://tinder.com/app/matches", { waitUntil: "domcontentloaded" });
  // Wait for matches list to render (cheap proxy for "session is alive + selectors healthy")
  try { await page.waitForSelector("a[href^='/app/messages/']", { timeout: 15000 }); }
  catch { console.error("matches list never rendered; halting"); process.exit(1); }

  for (const item of todo) {
    const text = extractDraftedReply(item.body);
    try {
      const result = await sendMessage(page, {
        matchId: item.meta.match_id,
        text,
        mode: item.meta.mode,
        draftId: item.meta.draft_id,
        lintScore: item.meta.lint_pass ? 1 : 0,
        dryRun,
      });
      // CODEX-R3-3: only count + move queue when truly sent. dry-run leaves
      // queue items in place for inspection and tracks count separately.
      if (result?.sent) {
        await moveQueueItem(item.id, "approved", item.meta.mode === "auto" ? "auto-sent" : "sent");
        if (item.meta.slug) await clearRedirects(item.meta.slug);
        sent += 1;
        // CODEX-R3-4: only sleep between REAL sends — dry-run validation should be fast.
        if (drainAll && todo.length > 1) await sleep(jitter(45000, 180000));
      } else if (result?.dryRun) {
        dryRunCount += 1;
      }
    } catch (e) {
      failed += 1;
      console.error(`send_failed ${item.id}: ${e.message}`);
      // Two-strike auto-archive on thread redirect. Other failures don't increment.
      if (/thread_redirect/.test(e.message) && item.meta.slug) {
        try {
          const r = await recordRedirect(item.meta.slug);
          // If the entity got archived (this redirect or any prior brought count >= 2),
          // move the orphaned queue item out of approved/ so we don't retry it forever.
          if (r?.archived || r?.redirect_count >= 2) {
            await moveQueueItem(item.id, "approved", "expired").catch(me => console.error(`expire-on-redirect failed: ${me.message}`));
          }
        } catch (re) {
          console.error(`recordRedirect failed: ${re.message}`);
        }
      }
      if (/HALTED/.test(e.message)) break;
    }
  }
  await logSession({ event: "send", sent, dryRun: dryRunCount, failed, queue_remaining: queue.length - sent });
  console.log(JSON.stringify({ sent, dryRunCount, failed, queue_remaining: queue.length - sent, dryRun }));
} finally {
  await ctx.close();
}
