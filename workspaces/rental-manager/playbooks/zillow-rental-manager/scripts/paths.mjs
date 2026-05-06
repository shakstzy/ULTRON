// paths.mjs -- single source of truth for every path the playbook touches.
//
// Everything is computed from this file's own location, so the workspace is
// drop-anywhere. No env vars required for normal operation; ZRM_* env knobs
// override individual paths only when needed (tests, multi-profile setups).

import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// scripts/  ->  playbooks/zillow-rental-manager/  ->  workspaces/rental-manager/
export const SCRIPTS_DIR = __dirname;
export const PLAYBOOK_ROOT = resolve(SCRIPTS_DIR, '..');
export const WORKSPACE_ROOT = resolve(PLAYBOOK_ROOT, '..', '..');

// Operational state — survives restarts, gitignored except for a few markers.
export const STATE_DIR = process.env.ZRM_STATE_DIR || join(WORKSPACE_ROOT, 'state');
export const THREADS_DIR = join(STATE_DIR, 'threads');
export const AUDIT_DIR = join(STATE_DIR, 'audit');
export const NETWORK_DIR = join(STATE_DIR, 'network');
export const BATCH_FOLLOWUP_DIR = join(STATE_DIR, 'batch-followup');
export const TMP_SCREENSHOT_DIR = join(STATE_DIR, 'tmp-screenshots');
export const PACING_FILE = join(STATE_DIR, 'pacing.json');
export const BREAKER_FILE = join(STATE_DIR, 'breaker.json');
export const THREADS_JSONL = join(STATE_DIR, 'threads.jsonl');

// Chrome profile — machine-local, gitignored. ZRM_PROFILE_DIR env honored for
// multi-profile experimentation.
export const PROFILE_DIR = process.env.ZRM_PROFILE_DIR || join(STATE_DIR, 'chrome-profile');

// Knowledge artifacts — committed markdown.
export const LEADS_DIR = join(WORKSPACE_ROOT, 'raw', 'leads');
export const APPLICATIONS_DIR = join(WORKSPACE_ROOT, 'raw', 'applications');

// Static assets bundled with the playbook.
export const APPLICATION_TEMPLATE_PATH = join(SCRIPTS_DIR, 'application-template.md');
