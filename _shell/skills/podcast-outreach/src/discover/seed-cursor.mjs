// Walk through config/seeds.yaml deterministically across cron runs.
// State at state/seed-cursor.json:
//   { idx: 17, cycle: 3, shuffle_seed: 42, order: [12, 7, 33, ...] }
//
// We snapshot a shuffled order on the first run (deterministic per
// shuffle_seed). When we exhaust it, increment cycle and re-shuffle.

import fs from "node:fs/promises";
import path from "node:path";
import yaml from "yaml";
import { SEED_CURSOR_FILE, SEEDS_FILE, STATE_DIR } from "../runtime/paths.mjs";

let cachedSeeds = null;

async function loadSeeds() {
  if (cachedSeeds) return cachedSeeds;
  const raw = await fs.readFile(SEEDS_FILE, "utf8");
  const parsed = yaml.parse(raw);
  if (!parsed?.seeds || !Array.isArray(parsed.seeds)) {
    throw new Error(`seeds.yaml malformed; expected top-level seeds: list`);
  }
  cachedSeeds = parsed.seeds;
  return cachedSeeds;
}

// Mulberry32 — deterministic RNG seeded by an int.
function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6D2B79F5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle(arr, seed) {
  const rng = mulberry32(seed);
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

async function readState() {
  try {
    const raw = await fs.readFile(SEED_CURSOR_FILE, "utf8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function writeState(state) {
  await fs.mkdir(STATE_DIR, { recursive: true });
  const tmp = SEED_CURSOR_FILE + ".tmp";
  await fs.writeFile(tmp, JSON.stringify(state, null, 2), "utf8");
  await fs.rename(tmp, SEED_CURSOR_FILE);
}

async function ensureState() {
  const seeds = await loadSeeds();
  let state = await readState();
  if (!state || !state.order || state.order.length !== seeds.length) {
    const shuffleSeed = Math.floor(Math.random() * 1_000_000) + 1;
    state = {
      idx: 0,
      cycle: 1,
      shuffle_seed: shuffleSeed,
      order: shuffle(seeds.map((_, i) => i), shuffleSeed),
    };
    await writeState(state);
  }
  return { seeds, state };
}

export async function nextN(n) {
  const { seeds, state } = await ensureState();
  const out = [];
  let idx = state.idx;
  let cycle = state.cycle;
  let order = state.order;
  let shuffleSeed = state.shuffle_seed;

  for (let i = 0; i < n; i++) {
    if (idx >= order.length) {
      cycle += 1;
      shuffleSeed = (shuffleSeed * 31 + 7) | 0;
      if (shuffleSeed <= 0) shuffleSeed = 1;
      order = shuffle(seeds.map((_, j) => j), shuffleSeed);
      idx = 0;
    }
    const seed = seeds[order[idx]];
    out.push({ ...seed, _cursor: { cycle, idx } });
    idx += 1;
  }

  await writeState({ idx, cycle, shuffle_seed: shuffleSeed, order });
  return out;
}

export async function status() {
  const { seeds, state } = await ensureState();
  return {
    total: seeds.length,
    idx: state.idx,
    cycle: state.cycle,
    seeds_remaining_in_cycle: seeds.length - state.idx,
  };
}
