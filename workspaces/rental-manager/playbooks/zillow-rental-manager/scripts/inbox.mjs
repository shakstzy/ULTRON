// inbox.mjs -- UI-driven Zillow Rental Manager inbox driver.
//
// Strategy: drive the actual UI (navigate to inbox, click conversation, type,
// click Send). Hook page.on('response') to capture the GraphQL responses the
// page's own JS produces. PerimeterX's JS attaches its telemetry headers
// because we're literally inside the page -- requests are indistinguishable
// from a human clicking. Only velocity matters; we govern it with pacing.mjs.
//
// We never construct or replay GraphQL requests ourselves. We observe.

import { enforceMinPacing, humanBeat, recordExternalCall, peekPacing } from './pacing.mjs';
import {
  writeLeadMarkdown,
  writeThreadState,
  readThreadState,
  saveNetworkCapture,
  saveSendBundle,
  appendObservation,
  sha256,
  toE164,
  toLowerEmail
} from './storage.mjs';
import { mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { TMP_SCREENSHOT_DIR } from './paths.mjs';

const INBOX_URL = 'https://www.zillow.com/rental-manager/inbox';

function ensureTmpDir() { if (!existsSync(TMP_SCREENSHOT_DIR)) mkdirSync(TMP_SCREENSHOT_DIR, { recursive: true }); }

// ---------------------------
// response capture helpers
// ---------------------------

/**
 * Install a response listener that captures the body of the next GraphQL
 * response matching `operationName`. Returns a Promise that resolves with
 * the parsed response, or rejects after `timeoutMs`.
 *
 * The listener also calls saveNetworkCapture() for offline forensics.
 */
function awaitGraphqlResponse(page, operationName, { timeoutMs = 25000 } = {}) {
  return new Promise((resolve, reject) => {
    let done = false;
    const timer = setTimeout(() => {
      if (done) return;
      done = true;
      page.off('response', handler);
      reject(new Error(`Timed out waiting for GraphQL operation "${operationName}" after ${timeoutMs}ms`));
    }, timeoutMs);

    const handler = async (resp) => {
      try {
        if (done) return;
        const url = resp.url();
        if (!/inbox\/graphql/.test(url)) return;
        const req = resp.request();
        if (req.method() !== 'POST') return;
        const post = req.postData() || '';
        let parsed = null;
        try { parsed = JSON.parse(post); } catch (_) { return; }
        if (parsed.operationName !== operationName) return;
        const status = resp.status();
        let body = null;
        try { body = await resp.json(); } catch (_) {}
        try {
          saveNetworkCapture({
            operationName,
            requestBody: parsed,
            responseBody: body,
            status
          });
        } catch (_) {}
        if (done) return;
        done = true;
        clearTimeout(timer);
        page.off('response', handler);
        resolve({ status, parsed, body });
      } catch (e) {
        // never let a listener crash the await
      }
    };
    page.on('response', handler);
  });
}

/**
 * Install a passive listener that records EVERY inbox/graphql POST response
 * to disk via saveNetworkCapture. Idempotent (sentinel property on page).
 * Zero behavior change -- just forensic data so we can see which operations
 * Zillow fires that we don't yet normalize. Removed automatically when the
 * page closes.
 */
export function installGlobalGraphqlTap(page) {
  if (page.__zrmGlobalTapInstalled) return;
  page.__zrmGlobalTapInstalled = true;
  page.on('response', async (resp) => {
    try {
      const url = resp.url();
      if (!/inbox\/graphql/.test(url)) return;
      const req = resp.request();
      if (req.method() !== 'POST') return;
      const post = req.postData() || '';
      let parsed = null;
      try { parsed = JSON.parse(post); } catch (_) { return; }
      const opName = parsed.operationName || 'UnknownOp';
      let body = null;
      try { body = await resp.json(); } catch (_) {}
      saveNetworkCapture({
        operationName: opName,
        requestBody: parsed,
        responseBody: body,
        status: resp.status()
      });
    } catch (_) { /* never let a listener crash */ }
  });
}

function detectChallenge(page) {
  return page.evaluate(() => {
    const hits = [];
    if (/captcha|press.?and.?hold|verify you/i.test(document.title || '')) hits.push('title-match');
    const sel = [
      'iframe[src*="captcha"]',
      'iframe[src*="perimeterx"]',
      'iframe[src*="human.com"]',
      'div[class*="px-captcha"]',
      'div[id*="px-captcha"]'
    ];
    for (const s of sel) { try { if (document.querySelector(s)) hits.push(`dom:${s}`); } catch (_) {} }
    if (/Access to this page has been denied/i.test(document.body?.innerText || '')) hits.push('text-deny');
    return hits;
  });
}

// ---------------------------
// list
// ---------------------------

/**
 * Navigate to inbox, wait for ConversationList_GetConversations response,
 * return the parsed conversation array. Optionally paginates by scrolling
 * the inbox list when the response says `pagination.hasNextPage === true`.
 *
 * Each subsequent page costs ONE paced call (enforceMinPacing). Stops when
 * Zillow says no more pages, when no new ids appear (server returned same
 * batch), or when maxPages is hit.
 *
 * NOTE: pacing for page 1 must be applied by the CALLER *before* launching
 * Chrome. Pages 2+ pace themselves inline. Caller pattern:
 *   await enforceMinPacing('pull-inbox-list');
 *   const ctx = await connectOrLaunch(...);
 *   const list = await pullInboxList(ctx.page, { maxPages: 10 });
 */
export async function pullInboxList(page, { maxPages = 12 } = {}) {
  installGlobalGraphqlTap(page);

  // Cumulative listener: collects EVERY ConversationList_GetConversations
  // response that fires during this call. Critical because Zillow's lazy-load
  // can fire 2-3 requests per scroll (prefetch), and the previous one-shot
  // awaitGraphqlResponse only caught the first. Live diagnosis on 2026-05-04:
  // captures showed page 2 (paginationStartIndex=lastIdOfPage1) and page 3
  // (paginationStartIndex=lastIdOfPage2) firing 1 second apart from a single
  // scroll, but my code only captured page 2 then broke on the next iteration.
  const collected = [];
  const collector = async (resp) => {
    try {
      const url = resp.url();
      if (!/inbox\/graphql/.test(url)) return;
      const req = resp.request();
      if (req.method() !== 'POST') return;
      const post = req.postData() || '';
      let parsed = null;
      try { parsed = JSON.parse(post); } catch (_) { return; }
      if (parsed.operationName !== 'ConversationList_GetConversations') return;
      let body = null;
      try { body = await resp.json(); } catch (_) {}
      collected.push({ ts: Date.now(), vars: parsed.variables, body, status: resp.status() });
    } catch (_) { /* never let listener crash */ }
  };
  page.on('response', collector);

  try {
    // Page 1: navigate to inbox.
    if (!page.url().startsWith(INBOX_URL)) {
      await page.goto(INBOX_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
    } else {
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 45000 });
    }
    const challenge = await detectChallenge(page);
    if (challenge.length) {
      throw Object.assign(new Error(`Challenge detected on inbox: ${challenge.join(', ')}`), { code: 'PX_CHALLENGE' });
    }

    // Wait for first response to land (up to 35s).
    {
      const start = Date.now();
      while (collected.length === 0 && Date.now() - start < 35000) {
        await new Promise(r => setTimeout(r, 250));
      }
      if (collected.length === 0) {
        throw new Error('Inbox page 1 timed out: no ConversationList_GetConversations response after 35s');
      }
    }

    let pages = collected.length;
    let lastBody = collected[collected.length - 1].body;
    let hasNext = !!lastBody?.data?.ZRM_getLatestConversationsV2?.pagination?.hasNextPage;
    console.error(`[zrm pagination] page 1: ${(lastBody?.data?.ZRM_getLatestConversationsV2?.conversations || []).length} convos, hasNextPage=${hasNext}`);

    // Account for page 1 in pacing log -- caller already paced ONE call before
    // we ran, but if first nav fired multiple ConversationList ops we record
    // the extras retroactively.
    for (let i = 1; i < collected.length; i++) {
      recordExternalCall(`inbox-page-1-extra-${i}`);
    }

    // Pages 2..maxPages: scroll the list, wait for settling, account for
    // every new response that fires (could be 1, could be 3 in a burst).
    // Pagination is a single human action (scroll wheel) that fires N
    // GraphQL calls naturally. Inserting 50s sleeps between scrolls is
    // pattern-suspicious. We use small jittered 1-3s waits between scrolls
    // (mimics a human pausing to read), and account for every burst response
    // in the pacing log via recordExternalCall so the daily cap stays honest.
    const interScrollWait = () => 1000 + Math.floor(Math.random() * 2000);
    let stalledScrolls = 0;
    while (hasNext && pages < maxPages) {
      // Daily cap respect: still bail if we'd exceed.
      const peek = peekPacing();
      if (peek.callsLastDay + 5 >= peek.dailyCap) {
        console.error(`[zrm pagination] aborting at page ${pages}: daily budget too thin (${peek.callsLastDay}/${peek.dailyCap})`);
        break;
      }

      const beforeCount = collected.length;
      const lastConvId = (lastBody?.data?.ZRM_getLatestConversationsV2?.conversations || []).slice(-1)[0]?.conversationId || null;

      // Diagnostic: identify the largest scrollable element on the page and
      // scroll IT (not the body, not a card). Live diagnosis 2026-05-04:
      // Zillow's inbox is a fixed-height pane with overflow:auto; the body
      // never scrolls, only an inner panel does. Walking up from cards
      // sometimes missed the right element.
      const diag = await page.evaluate((targetConvId) => {
        const out = { targetConvId, cards: 0, scrollables: [] };
        // Find every scrollable element on the page.
        const all = document.querySelectorAll('*');
        for (let i = 0; i < all.length; i++) {
          const el = all[i];
          let cs;
          try { cs = getComputedStyle(el); } catch (_) { continue; }
          if (!['auto', 'scroll', 'overlay'].includes(cs.overflowY)) continue;
          if (el.scrollHeight <= el.clientHeight + 5) continue;
          out.scrollables.push({
            tag: el.tagName,
            id: el.id || null,
            className: (typeof el.className === 'string' ? el.className : '').slice(0, 80),
            scrollHeight: el.scrollHeight,
            clientHeight: el.clientHeight,
            scrollTop: el.scrollTop,
            childCount: el.childElementCount
          });
        }
        // Sort by scroll capacity (scrollHeight - clientHeight) desc.
        out.scrollables.sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
        // Find the conversation card count for sanity.
        const cardSelectors = [
          '[data-testid*="onversation" i]', '[data-test-id*="onversation" i]',
          '[data-zg-conversation-id]', 'li[class*="onversation" i]',
          'div[class*="onversationListItem" i]', 'a[href*="/inbox/"]'
        ];
        for (const s of cardSelectors) {
          try {
            const found = document.querySelectorAll(s);
            if (found.length) { out.cards = found.length; out.matchedSelector = s; break; }
          } catch (_) {}
        }
        return out;
      }, lastConvId);

      const scrollableSummary = (diag.scrollables || []).slice(0, 3).map(s =>
        `${s.tag}${s.id ? '#' + s.id : ''}${s.className ? '.' + s.className.split(' ').slice(0, 2).join('.') : ''}(top=${s.scrollTop}/${s.scrollHeight - s.clientHeight})`
      ).join(' | ');
      console.error(`[zrm pagination] page ${pages + 1}: cards=${diag.cards} sel=${diag.matchedSelector || 'none'} scrollables=[${scrollableSummary || 'NONE'}]`);

      // Scroll: target the largest scrollable element. Slam scrollTop to
      // bottom AND dispatch a synthetic 'scroll' event AND fire a real
      // mouse.wheel event from outside page.evaluate (covers wheel-listener
      // lazy-loads).
      await page.evaluate(() => {
        const all = document.querySelectorAll('*');
        let best = null;
        let bestCap = 0;
        for (let i = 0; i < all.length; i++) {
          const el = all[i];
          let cs;
          try { cs = getComputedStyle(el); } catch (_) { continue; }
          if (!['auto', 'scroll', 'overlay'].includes(cs.overflowY)) continue;
          const cap = el.scrollHeight - el.clientHeight;
          if (cap <= 5) continue;
          if (cap > bestCap) { best = el; bestCap = cap; }
        }
        if (best) {
          best.scrollTop = best.scrollHeight;
          best.dispatchEvent(new Event('scroll', { bubbles: true }));
        }
        try { window.scrollTo(0, document.body.scrollHeight); } catch (_) {}
      });

      // Real wheel event at viewport center -- triggers wheel-event listeners
      // some lazy-loaders attach to (Zillow appears to use both scroll AND
      // wheel listeners in some shells).
      try {
        const vp = await page.viewportSize();
        if (vp) {
          await page.mouse.move(Math.floor(vp.width / 2), Math.floor(vp.height / 2));
          for (let i = 0; i < 8; i++) {
            await page.mouse.wheel(0, 1200);
            await new Promise(r => setTimeout(r, 60 + Math.floor(Math.random() * 80)));
          }
        }
      } catch (_) {}

      // Settling window: wait for responses to arrive. Up to 14s total, with
      // 4s of quiet after first response = burst over.
      const start = Date.now();
      let lastSeen = beforeCount;
      let lastSeenAt = Date.now();
      while (Date.now() - start < 14000) {
        await new Promise(r => setTimeout(r, 400));
        if (collected.length > lastSeen) {
          lastSeen = collected.length;
          lastSeenAt = Date.now();
        }
        if (collected.length > beforeCount && Date.now() - lastSeenAt > 4000) break;
      }

      const burst = collected.length - beforeCount;
      if (burst === 0) {
        stalledScrolls++;
        console.error(`[zrm pagination] page ${pages + 1}: no new requests after scroll (stalled=${stalledScrolls}/2)`);
        // Try again once before giving up; lazy-load may need a 2nd nudge.
        if (stalledScrolls >= 2) {
          console.error(`[zrm pagination] giving up after ${stalledScrolls} consecutive stalled scrolls`);
          break;
        }
        await new Promise(r => setTimeout(r, interScrollWait()));
        continue;
      }
      stalledScrolls = 0;

      // Record every burst response in pacing log (no in-loop enforceMinPacing
      // any more; we record retroactively for the daily cap).
      for (let i = 0; i < burst; i++) {
        recordExternalCall(`inbox-page-${pages + 1 + i}`);
      }

      pages += burst;
      lastBody = collected[collected.length - 1].body;
      hasNext = !!lastBody?.data?.ZRM_getLatestConversationsV2?.pagination?.hasNextPage;
      const lastBatchSize = (lastBody?.data?.ZRM_getLatestConversationsV2?.conversations || []).length;
      console.error(`[zrm pagination] +${burst} response(s), totalPages=${pages}, lastBatch=${lastBatchSize} convos, hasNextPage=${hasNext}`);

      // Small inter-scroll wait (1-3s) between iterations -- mimics a human
      // pausing to read. NOT enforceMinPacing's heavy 10-20s thread-fetch gap.
      await new Promise(r => setTimeout(r, interScrollWait()));
    }

    // Dedupe across all collected responses by conversationId. Use the
    // canonical path AND fall back to extractConversationsFromResponse's
    // deep-walk so a rolled-out shape change degrades to "still works,
    // surfaced fewer fields" rather than "returned 0 leads".
    const seen = new Set();
    const all = [];
    for (const item of collected) {
      let arr = item.body?.data?.ZRM_getLatestConversationsV2?.conversations || null;
      let useDeepWalk = false;
      if (!arr || !Array.isArray(arr) || !arr.length) {
        // Fallback: deep-walk for any array of objects with conversationId.
        const normalized = item.body ? extractConversationsFromResponse(item.body) : [];
        if (normalized.length) {
          for (const c of normalized) {
            if (c.conversation_id && !seen.has(c.conversation_id)) {
              seen.add(c.conversation_id);
              all.push(c);
            }
          }
          useDeepWalk = true;
        }
      }
      if (!useDeepWalk && arr) {
        for (const c of arr) {
          if (c.conversationId && !seen.has(c.conversationId)) {
            seen.add(c.conversationId);
            all.push(normalizeConversationListItem(c));
          }
        }
      }
    }

    appendObservation({
      kind: 'inbox-list',
      count: all.length,
      captures: collected.length,
      pages,
      hasNextPageAtEnd: hasNext
    });
    await humanBeat(page);
    return all;
  } finally {
    page.off('response', collector);
  }
}

function extractConversationsFromResponse(body) {
  // The exact path may vary across Zillow rollouts. Try the common shape first,
  // fall back to a deep-walk that finds any array of objects with conversationId.
  const data = body.data || body;
  const candidates = [];
  function walk(node, path) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      if (node.length && node[0] && typeof node[0] === 'object' && 'conversationId' in node[0]) {
        candidates.push({ path, items: node });
      }
      for (let i = 0; i < node.length; i++) walk(node[i], `${path}[${i}]`);
      return;
    }
    for (const k of Object.keys(node)) walk(node[k], path ? `${path}.${k}` : k);
  }
  walk(data, '');
  if (!candidates.length) return [];
  // Pick the largest array.
  candidates.sort((a, b) => b.items.length - a.items.length);
  return candidates[0].items.map(c => normalizeConversationListItem(c));
}

// Zillow returns statusLabel as {text, linkId, __typename}, not a bare string.
function statusText(s) {
  if (!s) return null;
  if (typeof s === 'string') return s;
  return s.text || s.linkId || null;
}

function normalizeConversationListItem(c) {
  // Inbox-list response embeds the most-recent message in c.conversation[0]
  // (NOT c.lastMessage which is undefined). The first element is the latest.
  const lastMsg = (Array.isArray(c.conversation) && c.conversation.length) ? c.conversation[0] : null;
  return {
    conversation_id: c.conversationId,
    listing_alias: c.listingAlias || null,
    listing_address: c.address || null,
    name: c.inquiry?.name || c.referenceName || null,
    phone: c.inquiry?.phone || null,
    is_phone_lead: !!c.inquiry?.isPhoneLead,
    inquiry_id: c.inquiry?.id || null,
    // c.inquiry.state is the renter's US-state of residence (e.g. "CA"),
    // NOT the lead's progress state.
    renter_us_state: c.inquiry?.state || null,
    reference_email: c.referenceEmail || null,
    status_label: statusText(c.statusLabel) || statusText(c.status?.label) || null,
    has_unread: !!c.hasUnreadMessage,
    is_archived: !!c.status?.isArchived,
    is_spam: !!c.status?.isSpam,
    last_message_preview: lastMsg?.messagePreview || lastMsg?.message || null,
    last_message_at_ms: parseMs(lastMsg?.messageDateMs)
  };
}

// ---------------------------
// thread
// ---------------------------

/**
 * Navigate directly to the thread URL and capture MessageList_GetConversation.
 *
 * URL pattern: /rental-manager/inbox/<listingAlias>/<conversationId>
 *
 * NOTE: pacing must be applied by the CALLER *before* this function runs.
 * Same reason as pullInboxList: Chrome may auto-quit during a long sleep
 * with only an inactive tab.
 *
 * We previously tried clicking the conversation-item element, but Zillow's
 * SPA detects "click on already-selected thread" and skips the GraphQL refire.
 * Direct page.goto always triggers a fresh fetch. (2026-04-30 fix.)
 */
export async function pullThread(page, conversationId, listingAlias) {
  if (!listingAlias) throw new Error('pullThread: listingAlias required (URL pattern is /inbox/<alias>/<cid>)');
  installGlobalGraphqlTap(page);
  const targetUrl = `https://www.zillow.com/rental-manager/inbox/${listingAlias}/${conversationId}`;

  // If we're already on this exact thread URL, force a re-render by going to
  // the inbox root first. Otherwise the SPA sees no URL change and skips the
  // re-fetch.
  // FIX (2026-04-30): install the response listener AFTER the inbox-root goto
  // so we don't capture a stale MessageList_GetConversation fired for the
  // previously-selected thread on the inbox root render.
  if (page.url() === targetUrl || page.url().startsWith(targetUrl)) {
    await page.goto('https://www.zillow.com/rental-manager/inbox', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(800);
  }

  const waitResp = awaitGraphqlResponse(page, 'MessageList_GetConversation', { timeoutMs: 35000 });
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

  const challenge = await detectChallenge(page);
  if (challenge.length) {
    throw Object.assign(new Error(`Challenge detected on thread nav: ${challenge.join(', ')}`), { code: 'PX_CHALLENGE' });
  }

  const { body } = await waitResp;
  const thread = extractThreadFromResponse(body);
  if (!thread) {
    throw new Error('MessageList_GetConversation had no recognizable thread shape: ' + JSON.stringify(body).slice(0, 300));
  }
  appendObservation({ kind: 'thread-pull', conversation_id: conversationId, listing_alias: listingAlias, message_count: thread.messages?.length });
  await humanBeat(page);
  return thread;
}

// Zillow returns messageDateMs as a STRING ("1777581290891"), not a number.
// new Date("string") parses as a date string, not millis -> Invalid Date.
// Coerce numerically before constructing the Date.
function parseMs(raw) {
  if (raw === null || raw === undefined || raw === '') return null;
  const n = typeof raw === 'number' ? raw : parseInt(String(raw), 10);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function safeIso(ms) {
  if (!ms) return null;
  try { return new Date(ms).toISOString(); }
  catch (_) { return null; }
}

function extractThreadFromResponse(body) {
  const data = body?.data;
  if (!data) return null;
  // Common path: data.ZRM_getConversationById
  const root = data.ZRM_getConversationById || data;
  if (!root || typeof root !== 'object') return null;
  const conv = Array.isArray(root.conversation) ? root.conversation : [];
  const messages = conv.map(m => {
    const ms = parseMs(m.messageDateMs);
    return {
      direction: m.isMessageOwner ? 'outbound' : 'inbound',
      sender_name: m.senderName || null,
      body: m.message || '',
      ts_ms: ms,
      ts_iso: safeIso(ms),
      message_id: m.messageId || null,
      message_type: m.messageType || null,
      hash: sha256(m.message || '')
    };
  });
  const renterAttrs = root.renterProfile?.attributes || null;
  const inquiry = root.inquiry || null;
  return {
    conversation_id: root.conversationId,
    listing_alias: root.listingAlias || null,
    listing_address: root.address || null,
    name: inquiry?.name || root.referenceName || null,
    phone: inquiry?.phone || null,
    is_phone_lead: !!inquiry?.isPhoneLead,
    inquiry_id: inquiry?.id || null,
    renter_us_state: inquiry?.state || null,
    reference_email: root.referenceEmail || null,
    status_label: statusText(root.statusLabel) || null,
    has_unread: !!root.hasUnreadMessage,
    is_archived: !!root.status?.isArchived,
    is_spam: !!root.status?.isSpam,
    application_completed: !!root.applicationCompleted,
    application_already_sent: !!root.applicationAlreadySent,
    is_active: root.isActive !== false,
    not_replied_to: !!root.notRepliedTo,
    renter_profile: renterAttrs,
    messages
  };
}

// ---------------------------
// persist (combine list + thread into raw markdown + thread state)
// ---------------------------

export function persistThread(thread, { listItem } = {}) {
  // Merge list-item data (for fields the thread response doesn't carry).
  const merged = {
    ...listItem,
    ...thread,
    pulled_at_iso: new Date().toISOString(),
    renter_us_state: thread.renter_us_state || listItem?.renter_us_state || null,
    status_label: thread.status_label || listItem?.status_label || null
  };

  // Tier 1: per-lead markdown.
  const { path: mdPath, slug } = writeLeadMarkdown({
    conversation_id: merged.conversation_id,
    listing_alias: merged.listing_alias,
    listing_address: merged.listing_address,
    name: merged.name,
    phone: merged.phone,
    email: null, // Zillow doesn't expose lead's real email; reference_email forwards.
    reference_email: merged.reference_email,
    status_label: merged.status_label,
    renter_us_state: merged.renter_us_state,
    pulled_at_iso: merged.pulled_at_iso,
    messages: merged.messages,
    renter_profile: merged.renter_profile
  });

  // Tier 2: per-thread JSON state.
  const prior = readThreadState(merged.conversation_id);
  writeThreadState(merged.conversation_id, {
    ...(prior || {}),
    listing_alias: merged.listing_alias,
    listing_address: merged.listing_address,
    lead_name: merged.name,
    lead_phone: toE164(merged.phone),
    lead_reference_email: toLowerEmail(merged.reference_email),
    inquiry_id: merged.inquiry_id,
    status_label: merged.status_label,
    renter_us_state: merged.renter_us_state,
    // Lead-checkpoint signal (per Gemini bypass strategy 2026-05-02): the
    // inbox-list response includes lastMessage.messageDateMs. Storing it
    // here lets pull-inbox skip thread fetches when the list timestamp
    // hasn't advanced since our last successful pull. Cuts call volume
    // ~80% on a steady-state inbox.
    last_observed_list_message_at_ms: listItem?.last_message_at_ms || null,
    application_completed: merged.application_completed,
    application_already_sent: merged.application_already_sent,
    has_unread: merged.has_unread,
    is_archived: merged.is_archived,
    is_spam: merged.is_spam,
    is_active: merged.is_active,
    last_pulled_at: merged.pulled_at_iso,
    last_inbound_at: lastByDirection(merged.messages, 'inbound')?.ts_iso || null,
    last_inbound_hash: lastByDirection(merged.messages, 'inbound')?.hash || null,
    last_outbound_at: lastByDirection(merged.messages, 'outbound')?.ts_iso || null,
    last_outbound_hash: lastByDirection(merged.messages, 'outbound')?.hash || null,
    messages: merged.messages,
    renter_profile: merged.renter_profile,
    quantum_lead_path: mdPath,
    quantum_lead_slug: slug
  });

  return { md_path: mdPath, slug, conversation_id: merged.conversation_id };
}

function lastByDirection(messages, dir) {
  if (!messages) return null;
  const arr = messages.filter(m => m.direction === dir).sort((a, b) => (a.ts_ms || 0) - (b.ts_ms || 0));
  return arr[arr.length - 1] || null;
}

// ---------------------------
// send
// ---------------------------

/**
 * Send a reply on the currently open conversation. Caller is responsible for
 * having driven to the right thread first (via pullThread or pullThreadByIndex).
 *
 * Captures pre/post screenshots and the mutation response into an audit bundle.
 *
 * Returns { ok, audit_dir, mutation_response }.
 */
export async function sendReply(page, conversationId, body, { dryRun = true } = {}) {
  if (!body || !body.trim()) throw new Error('sendReply: empty body');
  ensureTmpDir();
  await enforceMinPacing(`send:${conversationId}`);

  // Pre-state.
  const preShot = join(TMP_SCREENSHOT_DIR, `pre-${Date.now()}-${conversationId}.png`);
  await page.screenshot({ path: preShot, fullPage: false }).catch(() => {});
  const threadBefore = readThreadState(conversationId);

  // Find the compose textarea. Zillow's Constellation design system renders
  // the underlying <textarea data-testid=textarea-autosize> as visually-hidden
  // (clipped/positioned offscreen) while the UI shows a styled div that
  // forwards keystrokes. Playwright's visibility check rejects the textarea,
  // but it IS the keyboard-focus target for both the user and us.
  //
  // Pattern: wait for the testid'd textarea to be present (attached) but not
  // visible-checked. Use force:true to focus it, then type via page.keyboard
  // which bypasses element-visibility checks. React picks up the input events.
  const textarea = page.locator('[data-testid="textarea-autosize"]').first();
  await textarea.waitFor({ state: 'attached', timeout: 8000 });
  await textarea.focus({ timeout: 4000 });
  // Clear any prior draft (server-side autosave may have repopulated).
  await page.evaluate(() => {
    const el = document.querySelector('[data-testid="textarea-autosize"]');
    if (el) {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(el, '');
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await humanBeat(page);
  // Speed change 2026-05-05: paste-style fill via the native value setter +
  // input event, instead of 35-105ms/char keyboard.type(). Per-char typing
  // burned 25-75s on a 700-char body for zero server-observable benefit
  // (the only signal exposed across the wire is "time between focus and
  // submit"; per-keystroke events are local). A real user copy/pasting a
  // templated reply leaves the same DOM trace this code does. Codex
  // adversarial review (2026-05-05) confirmed this is fine if React's input
  // handlers still fire, which they do here because we dispatch the same
  // 'input' event the existing clear-textarea path uses on lines above.
  // Fallback: set ZRM_HUMAN_TYPING=1 to revert to per-char if a future PX
  // model rolls out that scores no-keystroke submits as suspicious.
  if (process.env.ZRM_HUMAN_TYPING === '1') {
    for (const ch of body) {
      await page.keyboard.type(ch, { delay: 35 + Math.floor(Math.random() * 70) });
    }
  } else {
    // Adversarial review (Codex/Gemini 2026-05-05): native value-setter bypasses
    // HTML maxLength, so we must respect it ourselves; throw if textarea
    // disappeared between focus and set; verify the value actually round-tripped
    // before trusting that Send will submit the right body. Also dispatch
    // 'change' alongside 'input' for component libraries that flush on change.
    const fillResult = await page.evaluate((text) => {
      const el = document.querySelector('[data-testid="textarea-autosize"]');
      if (!el) return { ok: false, reason: 'textarea-disappeared' };
      const max = el.maxLength;
      if (max && max > 0 && text.length > max) {
        return { ok: false, reason: `body-exceeds-maxlength: ${text.length}/${max}` };
      }
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      return { ok: el.value === text, observedLen: el.value.length, expectedLen: text.length, maxLength: max || null };
    }, body);
    if (!fillResult.ok) {
      throw new Error(`paste-fill failed: ${fillResult.reason || `value mismatch ${fillResult.observedLen}/${fillResult.expectedLen}`}`);
    }
  }
  await humanBeat(page);

  if (dryRun) {
    // Don't click Send. Capture state, clear textarea, abort.
    const postShot = join(TMP_SCREENSHOT_DIR, `dryrun-${Date.now()}-${conversationId}.png`);
    await page.screenshot({ path: postShot, fullPage: false }).catch(() => {});
    try {
      await page.evaluate(() => {
        const el = document.querySelector('[data-testid="textarea-autosize"]');
        if (el) {
          const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
          setter.call(el, '');
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
    } catch (_) {}
    const auditDir = saveSendBundle({
      conversationId,
      intent: 'dry-run',
      body,
      preScreenshot: preShot,
      postScreenshot: postShot,
      threadBefore,
      threadAfter: null,
      mutationResp: null
    });
    appendObservation({ kind: 'send-dry-run', conversation_id: conversationId, audit_dir: auditDir, body_len: body.length });
    return { ok: true, dry_run: true, audit_dir: auditDir };
  }

  // Live send: install response listener for any mutation hitting inbox/graphql,
  // then click Send. Capture FIRST mutation we see (best-effort discovery).
  const mutationP = new Promise((resolve) => {
    let done = false;
    const handler = async (resp) => {
      try {
        if (done) return;
        if (!/inbox\/graphql/.test(resp.url())) return;
        const req = resp.request();
        if (req.method() !== 'POST') return;
        const post = req.postData() || '';
        let parsed = null;
        try { parsed = JSON.parse(post); } catch (_) { return; }
        const q = parsed.query || '';
        if (!/^mutation\b/.test(q.trim()) && !/Send|Reply|Create|Mutation/i.test(parsed.operationName || '')) return;
        let respBody = null;
        try { respBody = await resp.json(); } catch (_) {}
        try {
          saveNetworkCapture({
            operationName: parsed.operationName,
            requestBody: parsed,
            responseBody: respBody,
            status: resp.status()
          });
        } catch (_) {}
        if (done) return;
        done = true;
        page.off('response', handler);
        resolve({ status: resp.status(), parsed, body: respBody });
      } catch (_) {}
    };
    page.on('response', handler);
    setTimeout(() => {
      if (done) return;
      done = true;
      page.off('response', handler);
      resolve(null);
    }, 25000);
  });

  // Click Send.
  let sendClicked = false;
  for (const sel of ['button[type=submit]:not([disabled])', '[data-testid*=send]:not([disabled])', '[aria-label*="Send" i]:not([disabled])', 'button:has-text("Send")']) {
    try {
      const loc = page.locator(sel).first();
      if (await loc.count() === 0) continue;
      if (!(await loc.isVisible())) continue;
      await loc.click({ timeout: 4000 });
      sendClicked = true;
      break;
    } catch (_) { /* try next */ }
  }
  if (!sendClicked) {
    try {
      await page.evaluate(() => {
        const el = document.querySelector('[data-testid="textarea-autosize"]');
        if (el) {
          const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
          setter.call(el, '');
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
    } catch (_) {}
    throw new Error('Could not find a clickable Send button');
  }

  const mutation = await mutationP;
  await page.waitForTimeout(2500);

  const postShot = join(TMP_SCREENSHOT_DIR, `post-${Date.now()}-${conversationId}.png`);
  await page.screenshot({ path: postShot, fullPage: false }).catch(() => {});

  // Pull the thread again to capture canonical post-send state.
  // FIX (2026-04-30): pullThread now requires listingAlias as third arg.
  // Extract from threadBefore if available, else fall back to current URL.
  let threadAfter = null;
  try {
    const aliasForRefresh = threadBefore?.listing_alias
      || (page.url().match(/\/inbox\/([^/]+)\//) || [])[1]
      || null;
    if (!aliasForRefresh) throw new Error('cannot determine listingAlias for post-send refresh');
    threadAfter = await pullThread(page, conversationId, aliasForRefresh);
    persistThread(threadAfter);
  } catch (e) {
    appendObservation({ kind: 'send-post-pull-failed', conversation_id: conversationId, error: e.message });
  }

  const auditDir = saveSendBundle({
    conversationId,
    intent: 'live',
    body,
    preScreenshot: preShot,
    postScreenshot: postShot,
    threadBefore,
    threadAfter,
    mutationResp: mutation
  });

  appendObservation({ kind: 'send-live', conversation_id: conversationId, audit_dir: auditDir, ok: !!mutation });
  return { ok: !!mutation, dry_run: false, audit_dir: auditDir, mutation_response: mutation };
}
