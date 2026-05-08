// Append-only sent log. The canonical dedup index. We also build an
// in-memory Set<email> on first read for O(1) lookup during a discover
// batch.
//
// Row schema:
//   { email, podcast_name, sent_at, gmail_thread_id, gmail_message_id, dry_run? }

import fs from "node:fs/promises";
import { SENT_FILE, STATE_HOME } from "../runtime/paths.mjs";

async function ensureFile() {
  await fs.mkdir(STATE_HOME, { recursive: true });
  await fs.appendFile(SENT_FILE, "", "utf8");
}

export async function readAll() {
  await ensureFile();
  const raw = await fs.readFile(SENT_FILE, "utf8");
  if (!raw.trim()) return [];
  return raw
    .split("\n")
    .filter((l) => l.trim())
    .map((l) => {
      try {
        return JSON.parse(l);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

export async function append(row) {
  await ensureFile();
  await fs.appendFile(SENT_FILE, JSON.stringify(row) + "\n", "utf8");
}

export async function emailSet({ excludeDryRun = false } = {}) {
  const rows = await readAll();
  const set = new Set();
  for (const r of rows) {
    if (excludeDryRun && r.dry_run) continue;
    if (r.email) set.add(r.email.toLowerCase());
  }
  return set;
}

export async function countToday() {
  const rows = await readAll();
  const today = new Date().toISOString().slice(0, 10);
  return rows.filter((r) => !r.dry_run && (r.sent_at || "").startsWith(today)).length;
}
