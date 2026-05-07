// ingest.mjs -- pull a friend's full DM history and write per-month .md
// under workspaces/<ws>/raw/discord/individuals/<slug>/<year>/.
//
// Format mirrors imessage individual files so lint/graphify don't fork:
//   * frontmatter parity (source, workspace, ingested_at, content_hash,
//     provider_modified_at, contact_*, counts, attachments list, etc.)
//   * body uses day headers + `**HH:MM — sender:** text` lines
//   * replies render as `↳ replying to <them> ("snippet"): reply text`
//   * images rendered as `↳ image: filename — "<description>" — <url>` with
//     descriptions generated via cloud-llm (Gemini Flash for vision)
//   * non-image attachments rendered as `↳ <kind>: filename — <url>`
//   * stripped: emoji-only filler, reactions, system messages (calls/pins/joins),
//     bot messages

import { existsSync, mkdirSync, writeFileSync, readFileSync, unlinkSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { openSession, resolveUser, openDmChannel } from './session.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ULTRON_ROOT = resolve(HERE, '..', '..', '..', '..');
const TZ = 'America/Chicago';

const PAGE_SIZE = 100;
const PAGE_JITTER_MIN_MS = 1500;
const PAGE_JITTER_MAX_MS = 4000;

function log(msg) { process.stderr.write(`[discord-ingest] ${msg}\n`); }
function jitter(minMs, maxMs) {
  const ms = minMs + Math.random() * (maxMs - minMs);
  return new Promise(r => setTimeout(r, ms));
}

function slugify(s) {
  return (s || 'unknown').toLowerCase().trim().replace(/[^a-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'unknown';
}

function workspaceExists(ws) {
  return existsSync(join(ULTRON_ROOT, 'workspaces', ws));
}

// Pull every message in the channel, newest -> oldest, paginating via `before=`.
// Returns array sorted oldest -> newest.
async function pullAllMessages(sess, channelId, { maxPages = Infinity } = {}) {
  const out = [];
  let before = null;
  let page = 0;
  while (page < maxPages) {
    const query = { limit: String(PAGE_SIZE) };
    if (before) query.before = before;
    const batch = await sess.call('GET', `/api/v9/channels/${channelId}/messages`, { query });
    if (!Array.isArray(batch) || batch.length === 0) break;
    out.push(...batch);
    log(`  page ${page + 1}: +${batch.length} (total ${out.length}; oldest in batch ${batch[batch.length - 1]?.id})`);
    if (batch.length < PAGE_SIZE) break;
    before = batch[batch.length - 1].id;
    page++;
    await jitter(PAGE_JITTER_MIN_MS, PAGE_JITTER_MAX_MS);
  }
  // Discord returns newest first per page. Sort ascending by snowflake.
  out.sort((a, b) => (BigInt(a.id) < BigInt(b.id) ? -1 : 1));
  return out;
}

// Cheap pre-filter: drop bot authors, system messages (non type 0/19), pure-empty.
function shouldKeep(m) {
  if (m.author?.bot) return { keep: false, reason: 'bot_author' };
  if (m.type !== 0 && m.type !== 19) return { keep: false, reason: `system_type_${m.type}` };
  const hasContent = (m.content && m.content.trim().length > 0);
  const hasAttach = (m.attachments?.length || 0) > 0;
  if (!hasContent && !hasAttach) return { keep: false, reason: 'empty' };
  return { keep: true };
}

const TZ_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'long'
});

function tzParts(iso) {
  const parts = Object.fromEntries(TZ_FMT.formatToParts(new Date(iso)).map(p => [p.type, p.value]));
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    month: `${parts.year}-${parts.month}`,
    year: parts.year,
    hm: `${parts.hour}:${parts.minute}`,
    weekday: parts.weekday
  };
}

function bucketByMonth(messages) {
  const buckets = new Map();
  for (const m of messages) {
    const t = tzParts(m.timestamp);
    if (!buckets.has(t.month)) buckets.set(t.month, []);
    buckets.get(t.month).push(m);
  }
  return buckets;
}

function clipSnippet(s, max = 80) {
  if (!s) return '';
  const oneLine = s.replace(/\s+/g, ' ').trim();
  return oneLine.length > max ? oneLine.slice(0, max - 1) + '…' : oneLine;
}

function attachmentKind(a) {
  const ct = (a.content_type || '').toLowerCase();
  if (ct.startsWith('image/')) return 'image';
  if (ct.startsWith('video/')) return 'video';
  if (ct.startsWith('audio/')) return 'audio';
  // Discord voice messages
  if ((a.filename || '').toLowerCase().endsWith('.ogg')) return 'audio';
  return 'file';
}

const DESCRIBE_SCRIPT = join(HERE, 'describe-image.py');

// cloud-llm forbids concurrent calls (rotates ~/.gemini/oauth_creds.json mid-flight),
// so describes are always serial. Returns null on any failure — caller renders the
// image without a description rather than aborting the ingest.
async function describeImage(absPath) {
  return await new Promise((resolveP) => {
    const py = spawn('python3', [DESCRIBE_SCRIPT, absPath], { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = ''; let stderr = '';
    py.stdout.on('data', d => stdout += d);
    py.stderr.on('data', d => stderr += d);
    py.on('close', () => {
      try {
        const j = JSON.parse(stdout.trim().split('\n').pop() || '{}');
        if (j.ok && j.output) resolveP(j.output);
        else { log(`  describe failed: ${j.error || 'no output'} ${stderr.slice(0, 200)}`); resolveP(null); }
      } catch (e) {
        log(`  describe parse error: ${e.message}; stdout=${stdout.slice(0, 200)}`);
        resolveP(null);
      }
    });
    py.on('error', e => { log(`  describe spawn error: ${e.message}`); resolveP(null); });
  });
}

async function downloadToTmp(url, filename) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch ${url} -> ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const safeName = filename.replace(/[^a-zA-Z0-9._-]/g, '_').slice(0, 80);
  const path = join(tmpdir(), `discord-img-${Date.now()}-${Math.random().toString(36).slice(2, 8)}-${safeName}`);
  writeFileSync(path, buf);
  return path;
}

// Discord puts the parent in `referenced_message` only when it's still resolvable.
// If `message_reference` exists but `referenced_message` doesn't, the parent is
// either deleted or just not inlined by the API — distinguish both honestly.
function renderReplyContext(m, mySelfId, recipientName) {
  if (m.referenced_message) {
    const author = m.referenced_message.author;
    const who = author?.id === mySelfId ? 'me' : (author?.global_name || author?.username || recipientName);
    const snippet = clipSnippet(m.referenced_message.content || '(no text)', 80);
    return `↳ replying to ${who} ("${snippet}"): `;
  }
  if (m.message_reference?.message_id) return '↳ replying to (unavailable): ';
  return '↳ replying to (deleted): ';
}

async function describeImagesForMonth(monthMessages) {
  // Phase 1: download all images for this month in parallel (Discord CDN tolerates fan-out).
  // Phase 2: describe sequentially (cloud-llm clobbers oauth_creds.json on concurrent calls).
  const imageRefs = [];
  for (const m of monthMessages) {
    for (const a of (m.attachments || [])) {
      if (attachmentKind(a) === 'image') imageRefs.push({ msgId: m.id, attId: a.id, url: a.url, filename: a.filename || 'image' });
    }
  }
  if (imageRefs.length === 0) return new Map();

  const downloads = await Promise.all(imageRefs.map(async ref => {
    try { return { ...ref, path: await downloadToTmp(ref.url, ref.filename) }; }
    catch (e) { log(`  download failed for ${ref.filename}: ${e.message}`); return { ...ref, path: null }; }
  }));

  const descByAttId = new Map();
  for (const d of downloads) {
    if (!d.path) continue;
    try {
      const desc = await describeImage(d.path);
      if (desc) descByAttId.set(d.attId, desc);
    } finally {
      try { unlinkSync(d.path); } catch (_) {}
    }
  }
  return descByAttId;
}

async function renderMonth({ ws, friendSlug, recipient, channelId, monthKey, monthMessages, mySelfId, recipientName, describe }) {
  const descByAttId = describe ? await describeImagesForMonth(monthMessages) : new Map();

  const lines = [];
  let myCount = 0, theirCount = 0;
  const attachmentsManifest = [];

  const byDay = new Map();
  for (const m of monthMessages) {
    const t = tzParts(m.timestamp);
    if (!byDay.has(t.date)) byDay.set(t.date, []);
    byDay.get(t.date).push(m);
  }
  const sortedDays = [...byDay.keys()].sort();

  const [year, monthNum] = monthKey.split('-');
  const monthLabel = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', month: 'long', year: 'numeric' })
    .format(new Date(Date.UTC(Number(year), Number(monthNum) - 1, 1)));

  lines.push(`# ${recipientName} — ${monthLabel}`);
  lines.push('');

  let firstDate = null, lastDate = null;
  let lastTimestamp = null;

  for (const date of sortedDays) {
    const dayMsgs = byDay.get(date);
    lines.push(`## ${date} (${tzParts(dayMsgs[0].timestamp).weekday})`);
    lines.push('');

    if (!firstDate) firstDate = date;
    lastDate = date;

    for (const m of dayMsgs) {
      const time = tzParts(m.timestamp).hm;
      const isMe = m.author?.id === mySelfId;
      if (isMe) myCount++; else theirCount++;
      const senderLabel = isMe ? 'me' : recipientName;
      const editedSuffix = m.edited_timestamp ? ' (edited)' : '';

      const replyPrefix = (m.type === 19 || m.referenced_message || m.message_reference)
        ? renderReplyContext(m, mySelfId, recipientName)
        : '';

      const text = (m.content || '').trim();
      lines.push(`**${time} — ${senderLabel}${editedSuffix}:** ${replyPrefix}${text}`);

      for (const a of (m.attachments || [])) {
        const kind = attachmentKind(a);
        const sizeKb = a.size ? ` (${Math.round(a.size / 1024)} KB)` : '';
        const desc = (kind === 'image' && describe) ? (descByAttId.get(a.id) || null) : null;
        const descPart = desc ? ` — "${desc.replace(/"/g, "'")}"` : '';
        lines.push(`↳ ${kind}: ${a.filename}${sizeKb}${descPart} — ${a.url}`);
        attachmentsManifest.push({ message_id: m.id, kind, filename: a.filename, url: a.url, size: a.size || null, description: desc });
      }

      const tsMs = new Date(m.timestamp).getTime();
      if (!lastTimestamp || tsMs > lastTimestamp) lastTimestamp = tsMs;
    }
    lines.push('');
  }

  const body = lines.join('\n').trimEnd() + '\n';
  const contentHash = createHash('sha256').update(body, 'utf8').digest('hex');

  const fm = renderFrontmatter({
    source: 'discord',
    workspace: ws,
    ingested_at: new Date().toISOString(),
    ingest_version: 1,
    content_hash: `sha256:${contentHash}`,
    provider_modified_at: lastTimestamp ? new Date(lastTimestamp).toISOString() : null,
    contact_slug: friendSlug,
    contact_type: 'individual',
    month: monthKey,
    date_range: [firstDate, lastDate],
    message_count: monthMessages.length,
    my_message_count: myCount,
    their_message_count: theirCount,
    attachments: attachmentsManifest,
    discord_channel_id: channelId,
    discord_channel_kind: 'dm',
    discord_recipient_id: recipient.id,
    discord_recipient_username: recipient.username || null,
    discord_recipient_global_name: recipient.global_name || null,
    deleted_upstream: null,
    superseded_by: null
  });

  return { md: fm + '\n' + body, contentHash, attCount: attachmentsManifest.length };
}

function renderFrontmatter(obj) {
  // Minimal YAML emitter sufficient for our shape (strings, numbers, ISO,
  // null, scalar arrays, array-of-objects with primitive values).
  const yamlValue = (v) => {
    if (v === null || v === undefined) return 'null';
    if (typeof v === 'number') return String(v);
    if (typeof v === 'boolean') return v ? 'true' : 'false';
    if (typeof v === 'string') {
      if (/^[A-Za-z][\w./:-]*$/.test(v) && !['true', 'false', 'null', 'yes', 'no'].includes(v.toLowerCase())) return v;
      return `'${v.replace(/'/g, "''")}'`;
    }
    return JSON.stringify(v);
  };
  const yamlScalarArray = (arr) => '[' + arr.map(v => yamlValue(v)).join(', ') + ']';
  const lines = ['---'];
  for (const [k, v] of Object.entries(obj)) {
    if (Array.isArray(v)) {
      if (v.length === 0) { lines.push(`${k}: []`); continue; }
      if (typeof v[0] === 'object' && v[0] !== null) {
        lines.push(`${k}:`);
        for (const item of v) {
          const entries = Object.entries(item);
          lines.push(`  - ${entries[0][0]}: ${yamlValue(entries[0][1])}`);
          for (let i = 1; i < entries.length; i++) {
            lines.push(`    ${entries[i][0]}: ${yamlValue(entries[i][1])}`);
          }
        }
      } else {
        lines.push(`${k}: ${yamlScalarArray(v)}`);
      }
    } else {
      lines.push(`${k}: ${yamlValue(v)}`);
    }
  }
  lines.push('---');
  return lines.join('\n');
}

export async function runIngest(argv) {
  const target = argv.positional[0];
  const ws = argv.flags.workspace || argv.flags.ws;
  const dryRun = !!argv.flags['dry-run'];
  const noDescribe = !!argv.flags['no-describe'];
  const maxPages = argv.flags['max-pages'] ? Number(argv.flags['max-pages']) : Infinity;

  if (!target) { process.stderr.write('Usage: ingest <name|id> --workspace <ws> [options]\n'); process.exit(2); }
  if (!ws) { process.stderr.write('--workspace is required\n'); process.exit(2); }
  if (!workspaceExists(ws)) { process.stderr.write(`workspace not found: workspaces/${ws}\n`); process.exit(2); }

  const sess = await openSession();
  try {
    log(`resolving "${target}"...`);
    const me = await sess.call('GET', '/api/v9/users/@me');
    const recipient = await resolveUser(sess, target);
    log(`recipient: ${recipient.global_name || recipient.username} (id=${recipient.id})`);

    const channelId = await openDmChannel(sess, recipient.id);
    log(`channel: ${channelId}`);

    log(`pulling all messages (paginated)...`);
    const all = await pullAllMessages(sess, channelId, { maxPages });
    log(`pulled ${all.length} raw messages`);

    const kept = [];
    const dropped = [];
    for (const m of all) {
      const v = shouldKeep(m);
      if (v.keep) kept.push(m); else dropped.push({ id: m.id, reason: v.reason });
    }
    log(`after filter: kept ${kept.length}, dropped ${dropped.length}`);

    const buckets = bucketByMonth(kept);
    log(`months: ${buckets.size}`);

    // Slug = "<global-name-slug>-<username>" when both exist, else username, else id.
    // Discord usernames are globally unique (post-2023 migration); appending the
    // global-name keeps the path human-readable while staying collision-free.
    const friendSlug = (() => {
      const gnSlug = recipient.global_name ? slugify(recipient.global_name) : '';
      const un = recipient.username ? slugify(recipient.username) : '';
      if (gnSlug && un && gnSlug !== un) return `${gnSlug}-${un}`.slice(0, 80);
      return un || gnSlug || slugify(recipient.id);
    })();
    const baseDir = join(ULTRON_ROOT, 'workspaces', ws, 'raw', 'discord', 'individuals', friendSlug);
    const recipientName = recipient.global_name || recipient.username || friendSlug;

    let totalAttachments = 0;
    let writtenCount = 0;
    let unchangedCount = 0;
    const months = [...buckets.keys()].sort();
    for (const monthKey of months) {
      const monthMessages = buckets.get(monthKey);
      const [year] = monthKey.split('-');
      const outDir = join(baseDir, year);
      const outPath = join(outDir, `${monthKey}__${friendSlug}.md`);

      log(`rendering ${monthKey} (${monthMessages.length} msgs) -> ${outPath.replace(ULTRON_ROOT, '.')}`);
      const { md, contentHash, attCount } = await renderMonth({
        ws, friendSlug, recipient, channelId, monthKey, monthMessages,
        mySelfId: me.id, recipientName,
        describe: !noDescribe
      });
      totalAttachments += attCount;

      if (dryRun) {
        const preview = md.split('\n').slice(0, 30).join('\n');
        process.stdout.write(`---DRY-RUN PREVIEW: ${outPath}\n${preview}\n[...${md.length} bytes total]\n\n`);
        continue;
      }

      // Skip-write guard: if the rendered body matches the existing file's content_hash,
      // leave the file untouched so re-runs don't churn ingested_at across 12 months.
      if (existsSync(outPath)) {
        const head = readFileSync(outPath, 'utf8').slice(0, 4096);
        const prev = head.match(/^content_hash:\s*sha256:([0-9a-f]{64})$/m);
        if (prev && prev[1] === contentHash) {
          unchangedCount++;
          continue;
        }
      }

      mkdirSync(outDir, { recursive: true });
      writeFileSync(outPath, md);
      writtenCount++;
    }

    // Watermark / diagnostic file.
    if (!dryRun && all.length > 0) {
      const logDir = join(ULTRON_ROOT, 'workspaces', ws, 'raw', '.ingest-log', 'discord');
      mkdirSync(logDir, { recursive: true });
      const watermark = {
        channel_id: channelId,
        recipient_id: recipient.id,
        recipient_username: recipient.username,
        recipient_global_name: recipient.global_name,
        last_full_pull_at: new Date().toISOString(),
        newest_message_id: all[all.length - 1].id,
        oldest_message_id: all[0].id,
        raw_message_count: all.length,
        kept_message_count: kept.length,
        dropped_message_count: dropped.length,
        months_written: months
      };
      writeFileSync(join(logDir, `${friendSlug}.json`), JSON.stringify(watermark, null, 2));
    }

    log(`done. months=${months.length} written=${writtenCount} unchanged=${unchangedCount} kept=${kept.length} attachments=${totalAttachments} dropped=${dropped.length}`);
  } finally {
    await sess.close();
  }
}
