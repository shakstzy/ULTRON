// Append-only JSONL queue. One row per pending podcast outreach.
// Schema (per row):
//   {
//     email, podcast_name, host_name?, host_first?,
//     recent_episode?, listennotes_id?, rss_url?, website?, genre?,
//     discovered_at, source_seed, source_url
//   }

import fs from "node:fs/promises";
import path from "node:path";
import { QUEUE_FILE, STATE_HOME } from "../runtime/paths.mjs";

async function ensureFile() {
  await fs.mkdir(STATE_HOME, { recursive: true });
  await fs.appendFile(QUEUE_FILE, "", "utf8");
}

export async function readAll() {
  await ensureFile();
  const raw = await fs.readFile(QUEUE_FILE, "utf8");
  if (!raw.trim()) return [];
  return raw
    .split("\n")
    .filter((l) => l.trim())
    .map((l) => JSON.parse(l));
}

export async function append(rows) {
  await ensureFile();
  if (!rows.length) return 0;
  const lines = rows.map((r) => JSON.stringify(r)).join("\n") + "\n";
  await fs.appendFile(QUEUE_FILE, lines, "utf8");
  return rows.length;
}

export async function size() {
  const rows = await readAll();
  return rows.length;
}

// Pop N rows from the head, atomic-ish: we read all, slice, rewrite the
// remainder. Single-writer assumption (cron + manual must not race; flock
// guard lives in run-stage.sh).
export async function popN(n) {
  const rows = await readAll();
  if (rows.length === 0) return [];
  const popped = rows.slice(0, n);
  const remaining = rows.slice(n);
  const tmp = QUEUE_FILE + ".tmp";
  const out = remaining.map((r) => JSON.stringify(r)).join("\n");
  await fs.writeFile(tmp, out ? out + "\n" : "", "utf8");
  await fs.rename(tmp, QUEUE_FILE);
  return popped;
}

export async function peekN(n) {
  const rows = await readAll();
  return rows.slice(0, n);
}

// Remove rows whose `email` matches any in the given set. Used by
// dedup pass to scrub a fresh discover batch against sent.jsonl.
export async function removeEmails(emailSet) {
  const rows = await readAll();
  const kept = rows.filter((r) => !emailSet.has((r.email || "").toLowerCase()));
  if (kept.length === rows.length) return 0;
  const tmp = QUEUE_FILE + ".tmp";
  const out = kept.map((r) => JSON.stringify(r)).join("\n");
  await fs.writeFile(tmp, out ? out + "\n" : "", "utf8");
  await fs.rename(tmp, QUEUE_FILE);
  return rows.length - kept.length;
}
