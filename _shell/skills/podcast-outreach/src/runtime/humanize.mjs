// Jittered sleep helpers. We want sends spaced out — 200/hr ≈ one every 18s,
// jittered ±4s to avoid even-cadence spam-detection heuristics.

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function jitter(minMs, maxMs) {
  const range = Math.max(0, maxMs - minMs);
  return Math.floor(minMs + Math.random() * range);
}

export async function jitteredSleep(minMs, maxMs) {
  return sleep(jitter(minMs, maxMs));
}
