// session.mjs -- shared Discord session helpers used by both run.mjs and ingest.mjs.
// Lives in its own module so that ingest.mjs can statically import from here
// without creating a top-level-await cycle through run.mjs.

import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = resolve(HERE, '..');
const NODE_MODULES = join(SKILL_ROOT, 'node_modules');
const DEBUG = process.env.DISCORD_DEBUG === '1';

export function die(msg, code = 1) {
  process.stderr.write(msg.endsWith('\n') ? msg : msg + '\n');
  process.exit(code);
}

export function ensureDeps() {
  if (existsSync(join(NODE_MODULES, 'patchright'))) return;
  console.error('[discord] First run: installing patchright + Chrome. This may take 2-3 minutes.');
  const r = spawnSync('npm', ['install'], { cwd: SKILL_ROOT, stdio: 'inherit' });
  if (r.status !== 0) die('npm install failed');
}

const MAX_429_RETRIES = 4;

class DiscordSession {
  constructor(ctx, pageApi, token) {
    this.ctx = ctx;
    this.pageApi = pageApi;
    this.token = token;
  }
  async call(method, path, opts = {}) {
    if (DEBUG) process.stderr.write(`[discord] ${method} ${path}\n`);
    let retries = 0;
    while (true) {
      const tok = this.ctx.getCapturedToken() || this.token;
      const res = await this.pageApi(this.ctx.page, method, path, { ...opts, token: tok });
      if (res.status === 429) {
        if (++retries > MAX_429_RETRIES) die(`[discord] ${method} ${path}: rate limited repeatedly, giving up`);
        const retry = (res.body && res.body.retry_after) || 2;
        process.stderr.write(`[discord] 429; sleeping ${retry}s\n`);
        await new Promise(r => setTimeout(r, retry * 1000));
        continue;
      }
      if (res.status === 401) {
        die('[discord] 401 unauthorized. Token may be invalidated. Run: node scripts/run.mjs login', 3);
      }
      if (!res.ok) {
        const code = res.body && typeof res.body === 'object' ? res.body.code : undefined;
        const message = res.body && typeof res.body === 'object' ? res.body.message : res.body;
        const e = new Error(`${method} ${path} -> ${res.status}${code ? ` code=${code}` : ''}${message ? ` ${message}` : ''}`);
        e.status = res.status;
        e.code = code;
        throw e;
      }
      return res.body;
    }
  }
  async close() { await this.ctx.close(); }
}

export async function openSession() {
  ensureDeps();
  const { launchContext, pageApi, waitForCapturedToken } = await import('./browser.mjs');
  const ctx = await launchContext({ visible: false });
  try {
    await ctx.page.goto('https://discord.com/channels/@me', { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (e) {
    await ctx.close();
    throw e;
  }
  const tok = await waitForCapturedToken(ctx, { timeoutMs: 60000, probeEveryMs: 500 });
  if (!tok) {
    const finalUrl = ctx.page.url();
    await ctx.close();
    if (finalUrl.includes('/login')) {
      die(`[discord] Session expired (page redirected to ${finalUrl}). Run: node scripts/run.mjs login`, 3);
    }
    die(`[discord] No Authorization header captured within 60s (page at ${finalUrl}). Run: node scripts/run.mjs login`, 3);
  }
  const sess = new DiscordSession(ctx, pageApi, tok);
  try {
    const probe = await pageApi(ctx.page, 'GET', '/api/v9/users/@me', { token: tok });
    if (probe.status === 401) {
      await ctx.close();
      die('[discord] 401 from /users/@me with captured token. Run: node scripts/run.mjs login', 3);
    }
    if (!probe.ok) {
      await ctx.close();
      die(`[discord] Session probe failed: /users/@me returned ${probe.status}`);
    }
  } catch (e) {
    await ctx.close();
    throw e;
  }
  return sess;
}

export async function listFriends(sess) {
  const rels = await sess.call('GET', '/api/v9/users/@me/relationships');
  return rels.filter(r => r.type === 1).map(r => r.user);
}

export async function listDmRecipients(sess) {
  const channels = await sess.call('GET', '/api/v9/users/@me/channels');
  return (channels || [])
    .filter(c => c.type === 1 && Array.isArray(c.recipients) && c.recipients.length === 1)
    .map(c => c.recipients[0]);
}

function matchUser(users, needle) {
  const n = needle.toLowerCase();
  const exact = users.filter(u =>
    u.username?.toLowerCase() === n ||
    u.global_name?.toLowerCase() === n
  );
  if (exact.length === 1) return { match: exact[0], candidates: exact };
  const partial = users.filter(u =>
    u.username?.toLowerCase().includes(n) ||
    u.global_name?.toLowerCase().includes(n)
  );
  if (partial.length === 1) return { match: partial[0], candidates: partial };
  return { match: null, candidates: partial };
}

export async function resolveUser(sess, nameOrId) {
  if (/^\d{17,20}$/.test(nameOrId)) return { id: nameOrId, username: null, global_name: null };
  // Pass 1: friends list.
  const friends = await listFriends(sess);
  const fr = matchUser(friends, nameOrId);
  if (fr.match) return fr.match;
  if (fr.candidates.length > 1) {
    die(`Ambiguous in friends: "${nameOrId}" matches ${fr.candidates.length}: ${fr.candidates.map(c => `${c.global_name || c.username} (${c.username})`).join(', ')}`);
  }
  // Pass 2: open DM channels (covers people you DM but never friended).
  const dmRecipients = await listDmRecipients(sess);
  const dm = matchUser(dmRecipients, nameOrId);
  if (dm.match) return dm.match;
  if (dm.candidates.length > 1) {
    die(`Ambiguous in DMs: "${nameOrId}" matches ${dm.candidates.length}: ${dm.candidates.map(c => `${c.global_name || c.username} (${c.username})`).join(', ')}`);
  }
  die(`Not found: "${nameOrId}". Not in friends list and no open DM channel. Pass a numeric user ID instead.`);
}

export async function openDmChannel(sess, userId) {
  const ch = await sess.call('POST', '/api/v9/users/@me/channels', { body: { recipient_id: userId } });
  return ch.id;
}
