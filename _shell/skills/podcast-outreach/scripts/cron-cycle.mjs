#!/usr/bin/env node
// Launchd cron entrypoint. Wraps `daily-cycle --send` so the scheduler never
// has to know skill verbs. Pass `DRY_RUN=1` env to force dry-run from the
// plist if you want a no-mutate cron pass.

import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RUN_MJS = path.join(__dirname, "run.mjs");

const args = ["daily-cycle"];
if (process.env.DRY_RUN !== "1") args.push("--send");

const child = spawn(process.execPath, [RUN_MJS, ...args], {
  stdio: "inherit",
  env: process.env,
});
child.on("exit", (code) => process.exit(code ?? 1));
child.on("error", (e) => {
  console.error(`cron-cycle: failed to spawn run.mjs: ${e.message}`);
  process.exit(1);
});
