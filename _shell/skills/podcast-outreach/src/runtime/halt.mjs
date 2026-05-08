// Kill switch. Touching ~/.ultron/podcast-outreach/.halt makes every verb
// abort fast. The cron entrypoint checks this first; manual verbs check
// before any send. Mirrors the linkedin halt pattern.

import fs from "node:fs/promises";
import { HALT_FILE } from "./paths.mjs";

export async function isHalted() {
  try {
    await fs.access(HALT_FILE);
    return true;
  } catch {
    return false;
  }
}

export async function abortIfHalted() {
  if (await isHalted()) {
    const reason = await fs.readFile(HALT_FILE, "utf8").catch(() => "no reason recorded");
    const e = new Error(`HALT: ${reason.trim() || "halt file present"}`);
    e.code = "HALT";
    throw e;
  }
}

export async function setHalt(reason = "manual halt") {
  const fs2 = await import("node:fs/promises");
  const path = await import("node:path");
  await fs2.mkdir(path.dirname(HALT_FILE), { recursive: true });
  await fs2.writeFile(HALT_FILE, `${reason}\n${new Date().toISOString()}\n`, "utf8");
}

export async function clearHalt() {
  await fs.unlink(HALT_FILE).catch(() => {});
}
