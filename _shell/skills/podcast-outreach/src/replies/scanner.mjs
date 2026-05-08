// Scan threads under `Podcast/podcast - archived` for inbound replies.
// For each thread that has at least one message NOT from
// adithya@eclipse.builders, demote `archived` and add `priority`, mark
// unread, log to replies.jsonl, and ping Adithya via imessage.

import fs from "node:fs/promises";
import { spawn } from "node:child_process";
import {
  ACCOUNT_EMAIL,
  LABEL_ARCHIVED,
  LABEL_PRIORITY,
  REPLIES_FILE,
  STATE_HOME,
} from "../runtime/paths.mjs";
import { audit, dim, info, ok, warn } from "../runtime/logger.mjs";
import {
  applyLabelToThread,
  findLabel,
  markThreadUnread,
  removeLabelFromThread,
} from "../pipeline/labels.mjs";
import { searchThreadsByQuery, getThread } from "../sender/gmail-send.mjs";

async function readPromoted() {
  try {
    const raw = await fs.readFile(REPLIES_FILE, "utf8");
    if (!raw.trim()) return new Set();
    const set = new Set();
    for (const line of raw.split("\n")) {
      if (!line.trim()) continue;
      try {
        const r = JSON.parse(line);
        if (r.thread_id) set.add(r.thread_id);
      } catch { /* skip */ }
    }
    return set;
  } catch {
    return new Set();
  }
}

async function appendPromotion(row) {
  await fs.mkdir(STATE_HOME, { recursive: true });
  await fs.appendFile(REPLIES_FILE, JSON.stringify(row) + "\n", "utf8");
}

function getHeader(headers, name) {
  if (!headers) return null;
  const arr = Array.isArray(headers) ? headers : Object.entries(headers).map(([k, v]) => ({ name: k, value: v }));
  const found = arr.find((h) => (h.name || "").toLowerCase() === name.toLowerCase());
  return found ? found.value : null;
}

function isInboundFromCounterparty(message, selfEmail) {
  // Trust gmail's labelIds: SENT means we sent it. Inbox/Inbox-like = inbound.
  const labels = message.labelIds || [];
  if (labels.includes("SENT")) return false;
  // Backup heuristic: parse From header.
  const from = getHeader(message.payload?.headers, "From") || "";
  if (!from) return false;
  return !from.toLowerCase().includes(selfEmail.toLowerCase());
}

function snippetOf(message) {
  return (message.snippet || "").slice(0, 80).replace(/\s+/g, " ");
}

async function pingAdithya(text) {
  // We use imessage skill via shell invocation — the skill writes its own audit log.
  const cmd = process.env.HOME + "/.claude/skills/imessage/scripts/send.sh";
  try {
    await fs.access(cmd);
  } catch {
    dim(`[scan-replies] imessage skill missing at ${cmd}; logging only`);
    return;
  }
  return new Promise((resolve) => {
    const child = spawn(cmd, ["--to-self", "--text", text], { stdio: "ignore" });
    child.on("close", () => resolve());
    child.on("error", () => resolve());
  });
}

export async function scanReplies({ lookbackDays, send, maxThreads }) {
  const archived = await findLabel(LABEL_ARCHIVED);
  const priority = await findLabel(LABEL_PRIORITY);
  if (!archived || !priority) {
    warn(`labels not found: archived=${!!archived} priority=${!!priority}. Run ensure-labels first.`);
    return { promoted: 0, scanned: 0 };
  }

  const promoted = await readPromoted();
  const query = `label:"${LABEL_ARCHIVED}" newer_than:${lookbackDays}d`;
  info(`[scan-replies] query: ${query}`);
  const threads = await searchThreadsByQuery(query, { limit: maxThreads });
  info(`[scan-replies] candidate threads: ${threads.length}`);

  let promotedCount = 0;
  for (const t of threads) {
    const tid = t.id || t.threadId;
    if (!tid) continue;
    if (promoted.has(tid)) {
      dim(`[scan-replies] already promoted: ${tid}`);
      continue;
    }
    let full;
    try {
      full = await getThread(tid);
    } catch (e) {
      warn(`[scan-replies] thread fetch failed ${tid}: ${e.message}`);
      continue;
    }
    const messages = full.messages || [];
    const inbound = messages.find((m) => isInboundFromCounterparty(m, ACCOUNT_EMAIL));
    if (!inbound) {
      dim(`[scan-replies] no inbound message in ${tid}`);
      continue;
    }
    const fromHeader = getHeader(inbound.payload?.headers, "From") || "";
    const subjectHeader = getHeader(inbound.payload?.headers, "Subject") || "";
    const fromEmail = (fromHeader.match(/<([^>]+)>/) || [, fromHeader])[1].trim();
    const podcastSnippet = snippetOf(inbound);

    info(`[scan-replies] reply from ${fromEmail}: "${podcastSnippet}"`);

    await removeLabelFromThread(tid, archived.id, { send });
    await applyLabelToThread(tid, priority.id, { send });
    await markThreadUnread(tid, { send });
    const row = {
      thread_id: tid,
      promoted_at: new Date().toISOString(),
      from: fromEmail,
      subject: subjectHeader,
      snippet: podcastSnippet,
      dry_run: !send,
    };
    if (send) {
      await appendPromotion(row);
      await pingAdithya(`[podcast-outreach] reply from ${fromEmail}: "${podcastSnippet}"`);
    } else {
      dim(`[dry-run] would promote thread ${tid} from ${fromEmail}`);
    }
    await audit("reply-promoted", row);
    promotedCount += 1;
  }
  ok(`[scan-replies] promoted ${promotedCount}/${threads.length}`);
  return { promoted: promotedCount, scanned: threads.length };
}
