// Daily-cap accounting. Stored at state/rate-state.json:
//   { date: "2026-05-07", sent_today: 137 }
// Rolls over at local midnight (per the LOCAL date string).

import fs from "node:fs/promises";
import path from "node:path";
import { CAPS_FILE, RATE_STATE_FILE, STATE_DIR } from "./paths.mjs";

let capsCache = null;
export async function loadCaps() {
  if (capsCache) return capsCache;
  capsCache = JSON.parse(await fs.readFile(CAPS_FILE, "utf8"));
  return capsCache;
}

function localDateStr(d = new Date()) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

async function readState() {
  try {
    const raw = await fs.readFile(RATE_STATE_FILE, "utf8");
    return JSON.parse(raw);
  } catch {
    return { date: localDateStr(), sent_today: 0 };
  }
}

async function writeState(state) {
  await fs.mkdir(STATE_DIR, { recursive: true });
  await fs.writeFile(RATE_STATE_FILE, JSON.stringify(state, null, 2), "utf8");
}

export async function getRateState() {
  const state = await readState();
  const today = localDateStr();
  if (state.date !== today) {
    return { date: today, sent_today: 0 };
  }
  return state;
}

export async function getSentToday() {
  const state = await getRateState();
  return state.sent_today;
}

export async function getRemainingToday() {
  const caps = await loadCaps();
  const sent = await getSentToday();
  return Math.max(0, caps.daily_send_cap - sent);
}

export async function recordSend(n = 1) {
  const today = localDateStr();
  const state = await readState();
  const next = state.date === today
    ? { date: today, sent_today: state.sent_today + n }
    : { date: today, sent_today: n };
  await writeState(next);
  return next;
}

export class CapExceededError extends Error {
  constructor(scope, limit, actual) {
    super(`cap exceeded: ${scope} limit=${limit} actual=${actual}`);
    this.code = "CAP_EXCEEDED";
    this.scope = scope;
    this.limit = limit;
    this.actual = actual;
  }
}

export async function assertDailyHeadroom(needed = 1) {
  const remaining = await getRemainingToday();
  if (remaining < needed) {
    const caps = await loadCaps();
    throw new CapExceededError("daily", caps.daily_send_cap, caps.daily_send_cap - remaining);
  }
}
