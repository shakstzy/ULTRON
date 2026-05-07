// Path resolution for the LinkedIn skill. ULTRON-rooted.
//
// State (counters, halt, action log, alerts, quarantine, diag) lives at
// ~/.ultron/linkedin/. Persistent Chrome profile lives at
// _credentials/browser-profiles/linkedin/ to match the discord/grok-web/etc
// pattern. Raw markdown deposits land in a workspace's raw/linkedin/ — default
// "personal", overridable per-call via LINKEDIN_WORKSPACE env (set by
// run.mjs --workspace flag).

import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { homedir } from "node:os";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// _shell/skills/linkedin/src/runtime/paths.mjs -> _shell/skills/linkedin/
export const SKILL_ROOT = resolve(__dirname, "../..");
// _shell/skills/linkedin/ -> ULTRON root
export const ULTRON_ROOT = resolve(SKILL_ROOT, "../../..");

export const CONFIG_DIR = resolve(SKILL_ROOT, "config");
export const CAPS_FILE = resolve(CONFIG_DIR, "caps.json");

export const PROFILE_DIR = resolve(ULTRON_ROOT, "_credentials/browser-profiles/linkedin");

const WS = process.env.LINKEDIN_WORKSPACE || "personal";
export const WORKSPACE = WS;
export const RAW_DIR = resolve(ULTRON_ROOT, "workspaces", WS, "raw/linkedin");

export const STATE_HOME = resolve(homedir(), ".ultron/linkedin");
export const STATE_DIR = resolve(STATE_HOME, "state");
export const HALT_FILE = resolve(STATE_HOME, ".halt");
export const RATE_STATE_FILE = resolve(STATE_DIR, "rate-state.json");
export const ACTIONS_LOG = resolve(STATE_DIR, "actions.ndjson");
export const LAUNCH_TS_FILE = resolve(STATE_DIR, "last-launch.ts");
export const QUARANTINE_DIR = resolve(STATE_HOME, "quarantine");
export const ALERTS_DIR = resolve(STATE_HOME, "alerts");
export const DIAG_DIR = resolve(STATE_HOME, "diag");
