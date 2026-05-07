#!/usr/bin/env node
// run.mjs -- ULTRON Discord skill CLI dispatcher.
// Verbs run through a patchright-driven Chrome session on discord.com,
// executing Discord REST via page.evaluate(fetch). Authenticated by session
// cookies in the profile dir.

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  die,
  ensureDeps,
  openSession,
  listFriends,
  resolveUser,
  openDmChannel
} from './session.mjs';

const PROFILE_DIR = process.env.DISCORD_PROFILE_DIR || `${process.env.HOME}/ULTRON/_credentials/browser-profiles/discord`;

function parseArgs(argv) {
  const positional = [];
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const eq = a.indexOf('=');
      if (eq > -1) {
        flags[a.slice(2, eq)] = a.slice(eq + 1);
      } else {
        const key = a.slice(2);
        const next = argv[i + 1];
        if (next !== undefined && !next.startsWith('--')) {
          flags[key] = next;
          i++;
        } else {
          flags[key] = true;
        }
      }
    } else {
      positional.push(a);
    }
  }
  return { positional, flags };
}

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

const [, , verb, ...argvRaw] = process.argv;
if (!verb || verb === 'help' || verb === '--help' || verb === '-h') {
  printHelp();
  process.exit(verb ? 0 : 2);
}
if (!VERBS[verb]) {
  console.error(`Unknown verb: ${verb}`);
  printHelp();
  process.exit(2);
}

const argv = parseArgs(argvRaw);

try {
  await VERBS[verb](argv);
} catch (e) {
  die(`[error] ${e.message}`);
}
