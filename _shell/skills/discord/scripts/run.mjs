#!/usr/bin/env node
// run.mjs -- ULTRON Discord skill CLI dispatcher.
// Verbs run through a patchright-driven Chrome session on discord.com,
// executing Discord REST via page.evaluate(fetch). Authenticated by session
// cookies in the profile dir.

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import {
  die,
  ensureDeps,
  openSession,
  listFriends,
  resolveUser,
  openDmChannel
} from './session.mjs';

const ARG_OPTIONS = {
  force: { type: 'boolean' },
  workspace: { type: 'string' },
  ws: { type: 'string' },
  'dry-run': { type: 'boolean' },
  'no-describe': { type: 'boolean' },
  'max-pages': { type: 'string' },
  help: { type: 'boolean', short: 'h' }
};

// Verbs.

async function whoami() {
  const sess = await openSession();
  try {
    const me = await sess.call('GET', '/api/v9/users/@me');
    console.log(JSON.stringify({
      ok: true,
      id: me.id,
      username: me.username,
      global_name: me.global_name,
      verified: me.verified,
      mfa_enabled: me.mfa_enabled
    }, null, 2));
  } finally { await sess.close(); }
}

async function friends(argv) {
  const q = (argv.positional[0] || '').toLowerCase();
  const sess = await openSession();
  try {
    const list = await listFriends(sess);
    const filtered = q
      ? list.filter(u => u.username?.toLowerCase().includes(q) || u.global_name?.toLowerCase().includes(q))
      : list;
    const out = filtered.map(u => ({
      id: u.id,
      username: u.username,
      global_name: u.global_name
    }));
    console.log(JSON.stringify({ query: q || null, count: out.length, friends: out }, null, 2));
  } finally { await sess.close(); }
}

async function login(argv) {
  ensureDeps();
  const { runLogin } = await import('./login.mjs');
  await runLogin({ force: !!argv.flags.force });
}

async function status() {
  const { readBreaker, getProfileDir } = await import('./browser.mjs');
  const dir = getProfileDir();
  const pidfilePath = join(dir, '.skill.pid');
  const pid = existsSync(pidfilePath) ? parseInt(readFileSync(pidfilePath, 'utf8').trim(), 10) : null;
  const b = readBreaker();
  const cookiesPath = join(dir, 'Default', 'Cookies');
  const cookies = existsSync(cookiesPath) ? 'present' : 'missing';
  console.log(JSON.stringify({
    profile_dir: dir,
    active_pid: pid,
    breaker: b,
    cookies
  }, null, 2));
}

async function resetBreaker() {
  const { writeBreaker } = await import('./browser.mjs');
  writeBreaker({ state: 'healthy', flagged_at: null, count_24h: 0, events: [] });
  console.error('[discord] breaker reset to healthy.');
}

async function ingest(argv) {
  ensureDeps();
  const { runIngest } = await import('./ingest.mjs');
  await runIngest(argv);
}

async function dm(argv) {
  const [target, ...rest] = argv.positional;
  if (!target) die('Usage: dm <name|id> <text...>');
  const text = rest.join(' ').trim();
  if (!text) die('text required');
  if (text.length > 2000) die(`message is ${text.length} chars; Discord limit is 2000`);
  const sess = await openSession();
  try {
    const recipient = await resolveUser(sess, target);
    const channelId = await openDmChannel(sess, recipient.id);
    const who = recipient.global_name || recipient.username || channelId;
    process.stderr.write(`[discord] DM -> ${who} (${recipient.username || recipient.id}) channel=${channelId}\n[discord] body: ${text}\n`);
    const msg = await sess.call('POST', `/api/v9/channels/${channelId}/messages`, {
      body: { content: text, allowed_mentions: { parse: [] } }
    });
    console.log(JSON.stringify({ ok: true, channel_id: channelId, message_id: msg.id, recipient: { id: recipient.id, username: recipient.username, global_name: recipient.global_name } }, null, 2));
  } finally { await sess.close(); }
}

const VERBS = {
  whoami,
  friends,
  login,
  status,
  'reset-breaker': resetBreaker,
  ingest,
  dm
};

function printHelp() {
  console.error(`ULTRON Discord skill CLI

Usage:
  node scripts/run.mjs <verb> [args...]

Verbs:
  login                                 one-time visible browser login
  whoami                                confirm session via /users/@me
  friends [query]                       list friends, optional name filter
  status                                profile + cookies + breaker state
  reset-breaker                         reset 24h breaker
  ingest <name|id> --workspace <ws> [options]
                                        pull entire DM history with a friend
                                        and write per-month .md files under
                                        workspaces/<ws>/raw/discord/individuals/

Ingest options:
  --no-describe       skip cloud-llm image descriptions
  --dry-run           print what would land, write nothing
  --max-pages N       cap pagination pages (debug; default unlimited)

Env:
  DISCORD_PROFILE_DIR     override profile dir (default: ~/ULTRON/_credentials/browser-profiles/discord)
  DISCORD_DEBUG=1         log request URLs
`);
}

const { values: flags, positionals } = parseArgs({
  args: process.argv.slice(2),
  options: ARG_OPTIONS,
  allowPositionals: true,
  strict: false
});
const [verb, ...positional] = positionals;

if (!verb || flags.help || verb === 'help') {
  printHelp();
  process.exit(verb ? 0 : 2);
}
if (!VERBS[verb]) {
  console.error(`Unknown verb: ${verb}`);
  printHelp();
  process.exit(2);
}

try {
  await VERBS[verb]({ flags, positional });
} catch (e) {
  die(`[error] ${e.message}`);
}
