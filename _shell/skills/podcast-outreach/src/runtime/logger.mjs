// Two-channel logger: human-readable colored stdout + structured ndjson at
// ~/.ultron/podcast-outreach/state/actions.ndjson. Every meaningful action
// (discover, send, dry-run, label-apply, reply-promote, halt) gets one row.

import fs from "node:fs/promises";
import path from "node:path";
import { ACTIONS_LOG, STATE_DIR } from "./paths.mjs";

const COLORS = {
  reset: "\x1b[0m",
  dim: "\x1b[2m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  cyan: "\x1b[36m",
  magenta: "\x1b[35m",
};
const tty = process.stdout.isTTY;
const c = (col, s) => (tty ? `${COLORS[col]}${s}${COLORS.reset}` : s);

let initialized = false;
async function ensureDir() {
  if (initialized) return;
  await fs.mkdir(STATE_DIR, { recursive: true });
  initialized = true;
}

export async function audit(verb, payload = {}) {
  await ensureDir();
  const row = {
    ts: new Date().toISOString(),
    verb,
    pid: process.pid,
    ...payload,
  };
  await fs.appendFile(ACTIONS_LOG, JSON.stringify(row) + "\n", "utf8");
  return row;
}

export function info(msg, ...rest) {
  console.log(c("cyan", "[info]"), msg, ...rest);
}
export function ok(msg, ...rest) {
  console.log(c("green", "[ok]  "), msg, ...rest);
}
export function warn(msg, ...rest) {
  console.warn(c("yellow", "[warn]"), msg, ...rest);
}
export function err(msg, ...rest) {
  console.error(c("red", "[err] "), msg, ...rest);
}
export function dim(msg, ...rest) {
  if (tty) console.log(c("dim", msg), ...rest);
  else console.log(msg, ...rest);
}
export function step(msg, ...rest) {
  console.log(c("magenta", "[step]"), msg, ...rest);
}
