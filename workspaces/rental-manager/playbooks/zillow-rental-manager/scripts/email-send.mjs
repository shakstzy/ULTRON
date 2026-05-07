// email-send.mjs — owner-side reply via Gmail to lead's convo.zillow.com relay.
//
// Bypasses the Zillow portal entirely: zero PerimeterX exposure, zero
// rate-limit pressure on the Zillow side, just an SMTP-equivalent send
// over the Gmail API via the local `gog` CLI.
//
// Mechanism: Zillow notifies the listing owner of every inquiry from a
// per-conversation alias `<token>@convo.zillow.com`. Replying to that
// alias forwards to the renter AND mirrors into the portal thread, so
// the renter and the Rental Manager UI both see the message. The owner
// must reply from the email Zillow has on file (Adithya's primary).
//
// Pacing: this path uses the same `enforceMinPacing` budget as portal
// sends so the daemon and the email path can never coordinate-spike.
// A future split-bucket is fine but premature today.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

import {
  readThreadState,
  writeThreadState,
  saveSendBundle,
  appendObservation,
  writeLeadMarkdown,
  toLowerEmail
} from './storage.mjs';
import { enforceMinPacing } from './pacing.mjs';

// Owner email is the From: address Zillow expects on relayed replies.
// Override only for testing against a different listing.
const OWNER_EMAIL = process.env.ZRM_OWNER_EMAIL || 'adithya.shak.kumar@gmail.com';
const OWNER_NAME = process.env.ZRM_OWNER_NAME || 'Adithya Shak Kumar';

// gog wrapper. Always JSON, always on the owner account, always
// results-only so stdout is a clean parseable result.
function gogJson(args, { allowEmpty = false } = {}) {
  const r = spawnSync('gog', ['-a', OWNER_EMAIL, '-j', '--results-only', ...args], {
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024
  });
  if (r.status !== 0) {
    const detail = (r.stderr || r.stdout || '').trim().slice(0, 500);
    throw new Error(`gog ${args.join(' ')} failed (exit=${r.status}): ${detail}`);
  }
  const out = (r.stdout || '').trim();
  if (!out) {
    if (allowEmpty) return null;
    throw new Error(`gog ${args.join(' ')} returned empty stdout`);
  }
  try { return JSON.parse(out); }
  catch (e) { throw new Error(`gog ${args.join(' ')} returned non-JSON: ${out.slice(0, 200)}`); }
}

// Find the most recent Gmail thread from this lead's relay so the reply
// nests under the original inquiry on the renter's side. Best-effort:
// if no thread exists or the search fails we send as a fresh message.
function findGmailThreadForRelay(relayEmail) {
  const out = gogJson(['gmail', 'messages', 'list', `from:${relayEmail}`, '--max', '5'], { allowEmpty: true });
  if (!out || !Array.isArray(out) || !out.length) return null;
  const m = out[0];
  return {
    messageId: m.id || m.messageId || null,
    threadId: m.threadId || m.thread || null,
    subject: m.subject || null
  };
}

function sha256Hex(s) {
  return createHash('sha256').update(s).digest('hex');
}

/**
 * Reply to a lead via the Gmail relay path.
 *
 * @param {string} conversationId        Zillow cid (matches readThreadState).
 * @param {string} body                  Plain-text reply.
 * @param {object} [opts]
 * @param {boolean} [opts.dryRun=true]   Default dry-run; pass false for live.
 * @returns {Promise<{ok, dry_run, audit_dir, to, subject, gmail_message_id}>}
 */
export async function sendViaEmail(conversationId, body, opts = {}) {
  const { dryRun = true } = opts;
  if (!body || !body.trim()) throw new Error('sendViaEmail: empty body');

  const threadBefore = readThreadState(conversationId);
  if (!threadBefore) {
    const e = new Error(`sendViaEmail: no thread state for cid=${conversationId}; run pull-thread first`);
    e.code = 'NO_THREAD_STATE';
    throw e;
  }
  const relay = toLowerEmail(threadBefore.lead_reference_email || '');
  if (!relay) {
    const e = new Error(`sendViaEmail: no reference_email captured for cid=${conversationId}`);
    e.code = 'NO_RELAY_ADDRESS';
    throw e;
  }
  if (!/@convo\.zillow\.com$/i.test(relay)) {
    const e = new Error(`sendViaEmail: reference_email "${relay}" is not a convo.zillow.com relay`);
    e.code = 'BAD_RELAY_ADDRESS';
    throw e;
  }

  await enforceMinPacing(`email-send:${conversationId}`);

  // Look up the Gmail thread so we can reply within it (preserves
  // In-Reply-To / References headers). Best-effort.
  let gmailThread = null;
  try { gmailThread = findGmailThreadForRelay(relay); }
  catch (e) {
    appendObservation({ kind: 'email-thread-lookup-failed', conversation_id: conversationId, relay, error: e.message });
  }

  const subject = gmailThread?.subject
    ? `Re: ${gmailThread.subject.replace(/^Re:\s*/i, '')}`
    : `Re: Your inquiry about ${threadBefore.listing_address || 'the listing'}`;

  if (dryRun) {
    const auditDir = saveSendBundle({
      conversationId,
      intent: 'email-dry-run',
      body,
      preScreenshot: null,
      postScreenshot: null,
      threadBefore,
      threadAfter: null,
      mutationResp: { dry_run: true, to: relay, subject, gmail_thread: gmailThread }
    });
    appendObservation({
      kind: 'email-send-dry-run',
      conversation_id: conversationId,
      to: relay,
      audit_dir: auditDir,
      body_len: body.length,
      gmail_thread_id: gmailThread?.threadId || null
    });
    return { ok: true, dry_run: true, audit_dir: auditDir, to: relay, subject };
  }

  // --- LIVE SEND ---
  const sendArgs = [
    'gmail', 'send',
    '--to', relay,
    '--subject', subject,
    '--body', body
  ];
  // Prefer reply-to-message-id (sets full In-Reply-To/References chain);
  // fall back to thread-id; fall back to fresh send.
  if (gmailThread?.messageId) {
    sendArgs.push('--reply-to-message-id', gmailThread.messageId);
  } else if (gmailThread?.threadId) {
    sendArgs.push('--thread-id', gmailThread.threadId);
  }

  const sendResp = gogJson(sendArgs);
  const gmailMsgId = sendResp?.id || sendResp?.messageId || null;

  // Append a synthetic outbound to the persisted thread state so
  // subsequent ingest sweeps don't re-trigger the same response, and
  // regenerate the committed lead markdown.
  const tsMs = Date.now();
  const tsIso = new Date(tsMs).toISOString();
  const synthetic = {
    direction: 'outbound',
    sender_name: OWNER_NAME,
    body,
    ts_ms: tsMs,
    ts_iso: tsIso,
    message_id: gmailMsgId ? `gmail:${gmailMsgId}` : `email-relay:${tsMs}-${conversationId}`,
    message_type: 'emailRelayReply',
    hash: 'sha256:' + sha256Hex(body)
  };

  const messages = Array.isArray(threadBefore.messages) ? threadBefore.messages.slice() : [];
  messages.push(synthetic);

  const threadAfter = {
    ...threadBefore,
    messages,
    last_outbound_at: tsIso,
    last_outbound_hash: synthetic.hash,
    last_replied_via: 'email-relay'
  };
  writeThreadState(conversationId, threadAfter);

  // Regenerate lead markdown so raw/leads/<slug>.md reflects the new
  // outbound. Mirror the lead-shape that persistThread builds.
  try {
    writeLeadMarkdown({
      conversation_id: conversationId,
      listing_alias: threadBefore.listing_alias,
      listing_address: threadBefore.listing_address,
      name: threadBefore.lead_name,
      phone: threadBefore.lead_phone,
      email: null,
      reference_email: threadBefore.lead_reference_email,
      status_label: threadBefore.status_label,
      renter_us_state: threadBefore.renter_us_state,
      pulled_at_iso: threadBefore.last_pulled_at || tsIso,
      messages,
      renter_profile: threadBefore.renter_profile || null
    });
  } catch (e) {
    appendObservation({ kind: 'email-lead-md-failed', conversation_id: conversationId, error: e.message });
  }

  const auditDir = saveSendBundle({
    conversationId,
    intent: 'email-live',
    body,
    preScreenshot: null,
    postScreenshot: null,
    threadBefore,
    threadAfter,
    mutationResp: { gmail_response: sendResp, to: relay, subject }
  });

  appendObservation({
    kind: 'email-send-live',
    conversation_id: conversationId,
    to: relay,
    gmail_message_id: gmailMsgId,
    audit_dir: auditDir,
    body_len: body.length
  });

  return {
    ok: true,
    dry_run: false,
    audit_dir: auditDir,
    to: relay,
    subject,
    gmail_message_id: gmailMsgId
  };
}
