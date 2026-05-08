// Centralized path constants. Anything that touches the filesystem should
// import from here so renames are one-shot.

import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const SKILL_ROOT = path.resolve(__dirname, "..", "..");
export const ULTRON_ROOT = process.env.ULTRON_ROOT || path.resolve(os.homedir(), "ULTRON");

export const STATE_HOME = path.resolve(os.homedir(), ".ultron", "podcast-outreach");
export const STATE_DIR = path.join(STATE_HOME, "state");
export const HALT_FILE = path.join(STATE_HOME, ".halt");

export const QUEUE_FILE = path.join(STATE_HOME, "queue.jsonl");
export const SENT_FILE = path.join(STATE_HOME, "sent.jsonl");
export const REPLIES_FILE = path.join(STATE_HOME, "replies.jsonl");
export const LOW_QUALITY_FILE = path.join(STATE_HOME, "low-quality.jsonl");

export const RATE_STATE_FILE = path.join(STATE_DIR, "rate-state.json");
export const SEED_CURSOR_FILE = path.join(STATE_DIR, "seed-cursor.json");
export const ACTIONS_LOG = path.join(STATE_DIR, "actions.ndjson");

export const DISCOVER_DIR = path.join(STATE_HOME, "discover");
export const DRY_RUN_DIR = path.join(STATE_HOME, "dry-run");

export const BROWSER_PROFILE = path.join(
  ULTRON_ROOT,
  "_credentials",
  "browser-profiles",
  "podcast-outreach",
);

export const TEMPLATE_FILE = path.join(SKILL_ROOT, "templates", "initial-outreach.md");
export const SEEDS_FILE = path.join(SKILL_ROOT, "config", "seeds.yaml");
export const CAPS_FILE = path.join(SKILL_ROOT, "config", "caps.json");

export const RAW_DEPOSIT_ROOT = path.join(
  ULTRON_ROOT,
  "workspaces",
  "eclipse",
  "raw",
  "listennotes",
);

export const ACCOUNT_EMAIL = "adithya@eclipse.builders";
// Labels already exist in adithya@eclipse.builders Gmail — exact case, flat
// (not nested under a parent "Podcast/" folder). Verified 2026-05-07.
export const LABEL_ARCHIVED = "Podcast - Archived";
export const LABEL_PRIORITY = "Podcast - Priority";
