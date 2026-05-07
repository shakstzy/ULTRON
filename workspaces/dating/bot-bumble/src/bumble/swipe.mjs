// Swipe loop primitives. Skeleton; the loop body mirrors Tinder's swipe.mjs
// but the click selectors / DOM polls come from config/selectors.json which
// is populated by scripts/discover-dom.mjs.

import { readFile } from "node:fs/promises";
import { FILTER_FILE } from "../runtime/paths.mjs";
import { selectors, scanForHalts } from "../runtime/detection.mjs";
import { humanClick, makeCursor, idlePause, microFidget, sleep, jitter } from "../runtime/humanize.mjs";
import { gotoEncounters, readVisibleCard } from "./page.mjs";
import { logSwipe } from "../runtime/logger.mjs";
import { loadCaps, reserveCap, releaseCap } from "../runtime/caps.mjs";
import { assertDateMode } from "../runtime/mode-guard.mjs";
import { setHalt } from "../runtime/halt.mjs";
import { logSession } from "../runtime/logger.mjs";

// Bumble surfaces "You missed!" / "Did you mean to swipe right?" after some
// passes their algo flags. Text-based detection only — modal CSS isn't observed
// live yet. Anti-bot: cap rewinds per session and randomly skip a chunk.
const MISSED_MATCH_RE = /(you missed|did you mean to swipe right|wait,?\s*go back|backtrack)/i;
const SESSION_REWIND_MAX = 3;
const RECOVERY_SKIP_PROBABILITY = 0.30;

let _filter = null;
async function loadFilter() {
  if (_filter) return _filter;
  _filter = JSON.parse(await readFile(FILTER_FILE, "utf8"));
  return _filter;
}

// CODEX-R2-P0-4: fail-closed when gating fields are unknown. Pre-discovery,
// readVisibleCard only returns name; age/distance/bio are null. The previous
// passesFilter treated null as "in-filter," which made every card a like. Now:
//   - if age is unknown AND age_min/max are set, REJECT (cannot prove safety)
//   - if distance is unknown AND max_distance_mi is set, REJECT
//   - if `auto_pass_if_no_bio_and_no_prompts` and we have neither, REJECT
function passesFilter(profile, f) {
  if (f.age_min != null || f.age_max != null) {
    if (profile.age == null) return false;
    if (profile.age < f.age_min || profile.age > f.age_max) return false;
  }
  if (f.max_distance_mi != null) {
    if (profile.distance_mi == null) return false;
    if (profile.distance_mi > f.max_distance_mi) return false;
  }
  if (f.auto_pass_if_no_bio_and_no_prompts) {
    const hasBio = !!(profile.bio && String(profile.bio).trim());
    const hasPrompts = !!(profile.prompts && Object.keys(profile.prompts).length > 0);
    if (!hasBio && !hasPrompts) return false;
  }
  return true;
}

// Try selectors in order; click first match. Returns true on click.
async function tryClickFirst(cursor, page, selList) {
  for (const sel of selList.filter(Boolean)) {
    try {
      const el = await page.$(sel);
      if (el) { await humanClick(cursor, page, sel); return true; }
    } catch { /* skip invalid selector */ }
  }
  return false;
}

// After a pass, check for Bumble's missed-match prompt. If present (and we
// haven't blown our per-session rewind cap or rolled the random skip): click
// rewind, re-read card, re-evaluate filter, re-swipe. Returns rewindsUsed
// (always) and { recovered, finalAction } when a recovery click landed.
async function recoverMissedMatch(page, cursor, profile, filter, ratioCap, liked, swiped, rewindsUsed) {
  await sleep(jitter(450, 850));
  let bodyText = "";
  try { bodyText = await page.evaluate(() => (document.body?.innerText || "").slice(0, 8000)); } catch {}
  if (!MISSED_MATCH_RE.test(bodyText)) return { recovered: false, finalAction: null, rewindsUsed };

  if (rewindsUsed >= SESSION_REWIND_MAX || Math.random() < RECOVERY_SKIP_PROBABILITY) {
    await page.keyboard.press("Escape").catch(() => {});
    const reason = rewindsUsed >= SESSION_REWIND_MAX ? "session_cap" : "random";
    await logSession({ event: "missed_match_skipped", reason, profile: profile.name || null });
    return { recovered: false, finalAction: null, rewindsUsed };
  }

  await sleep(jitter(1400, 3000));
  const sels = await selectors();
  const rewindCandidates = [sels.rewind_button?.selector, ...(sels.rewind_button?.alt || [])];
  if (!await tryClickFirst(cursor, page, rewindCandidates)) {
    await page.keyboard.press("Escape").catch(() => {});
    await logSession({ event: "missed_match_skipped", reason: "rewind_not_found", profile: profile.name || null });
    return { recovered: false, finalAction: null, rewindsUsed };
  }
  rewindsUsed += 1;

  await sleep(jitter(700, 1400));
  const reRead = await readVisibleCard(page);
  const inFilter = passesFilter(reRead, filter);
  const wouldRatio = swiped > 0 ? (liked + (inFilter ? 1 : 0)) / (swiped + 1) : (inFilter ? 1 : 0);
  const wantLike = inFilter && wouldRatio <= ratioCap;
  const btn = wantLike ? sels.like_button : sels.pass_button;
  if (!await tryClickFirst(cursor, page, [btn.selector, ...(btn.alt || [])])) {
    await logSession({ event: "missed_match_recovery_failed", profile: reRead.name || profile.name, intended: wantLike ? "like" : "pass", rewindsUsed });
    return { recovered: false, finalAction: null, rewindsUsed };
  }
  await logSession({ event: "missed_match_recovered", profile: reRead.name || profile.name, final_action: wantLike ? "like" : "pass", in_filter: inFilter, rewindsUsed });
  return { recovered: true, finalAction: wantLike ? "like" : "pass", rewindsUsed };
}

export async function swipeSession(page, { sessionMinutesMax = null } = {}) {
  const caps = await loadCaps();
  const filter = await loadFilter();
  const cursor = await makeCursor(page);
  const sels = await selectors();

  if (!sels.like_button?.selector || !sels.pass_button?.selector) {
    throw new Error("pre-discovery: swipeSession needs like_button + pass_button selectors. Run scripts/discover-dom.mjs.");
  }
  // CODEX-R3-P0-4: when swipe-target selectors ARE configured, mode_picker MUST
  // also be configured. Bumble Date/BFF/Bizz makes mode-failure dangerous.
  if (!sels.mode_picker?.selector) {
    throw new Error("missing_selector: mode_picker is null but swipe-target selectors are wired. Refusing to swipe without provable Date mode. Populate config/selectors.json.mode_picker via scripts/discover-dom.mjs.");
  }

  const avgGap = (caps.swipes.between_swipes_ms[0] + caps.swipes.between_swipes_ms[1]) / 2;
  const estMs = caps.swipes.per_session_max * avgGap * 1.5;
  const sessionMs = sessionMinutesMax ? sessionMinutesMax * 60 * 1000 : estMs;
  const sessionEnd = Date.now() + sessionMs;
  const testLimit = parseInt(process.env.BUMBLE_TEST_LIMIT || "0", 10);
  const sessionMaxSwipes = testLimit > 0
    ? testLimit
    : jitter(caps.swipes.per_session_min, caps.swipes.per_session_max + 1);
  if (testLimit > 0) console.log(`TEST MODE: hard-capped at ${testLimit} swipes`);

  const ratioCap = caps.swipes.right_swipe_ratio_max ?? 0.5;

  await gotoEncounters(page);
  await assertDateMode(page);

  let swiped = 0;
  let liked = 0;
  let sessionRewinds = 0;
  let stopReason = "session_end";

  while (swiped < sessionMaxSwipes && Date.now() < sessionEnd) {
    await scanForHalts(page);
    await microFidget(page);

    const profile = await readVisibleCard(page);
    if (!profile.name && !profile.age) {
      await sleep(jitter(800, 1600));
      continue;
    }

    const inFilter = passesFilter(profile, filter);
    // CODEX-R1-P0-2: enforce right_swipe_ratio_max. If liking this profile would
    // push the session ratio above the cap, force pass even if she's in filter.
    // Prevents the "20 in-filter cards in a row -> 20 likes" Bumble-bot signature.
    const wouldBeRatio = swiped > 0 ? (liked + (inFilter ? 1 : 0)) / (swiped + 1) : (inFilter ? 1 : 0);
    const wantLike = inFilter && wouldBeRatio <= ratioCap;

    if (Math.random() < 0.18) await idlePause({ min: 1800, max: 5500 });
    else await idlePause({ min: 1100, max: 3100 });

    // CODEX-R5-P0-2: re-scan halts IMMEDIATELY before the click. Idle pauses
    // open a window where Turnstile / photo-verify / login-wall can appear
    // and we must not click into mitigation surfaces.
    await scanForHalts(page);

    // CODEX-R5-P0-5: reserve cap atomically (under lock). If next steps fail,
    // we release. Replaces the previous peek-then-commit race window.
    let reservation;
    try {
      reservation = await reserveCap("swipe");
    } catch (e) {
      stopReason = e.message;
      break;
    }

    const buttonSel = wantLike ? sels.like_button : sels.pass_button;
    const candidates = [buttonSel.selector, ...(buttonSel.alt || [])].filter(Boolean);
    let clicked = false;
    for (const sel of candidates) {
      try {
        const el = await page.$(sel);
        if (el) { await humanClick(cursor, page, sel); clicked = true; break; }
      } catch { /* continue */ }
    }
    if (!clicked) {
      // Release the reservation - no action happened.
      await releaseCap(reservation);
      stopReason = "button_not_found";
      break;
    }

    // CODEX-R6-P0-2: scan halts FIRST after click, BEFORE the cardChanged
    // check. Otherwise an overlay (Turnstile/verify/restriction) appearing
    // after the click exits via "overlay_after_click" without setting .halt,
    // and the next cron walks straight back into the mitigation surface.
    try { await scanForHalts(page); } catch (e) {
      // Halt fired - reservation is correct (we did click), so don't release.
      stopReason = e.message;
      break;
    }

    // Missed-match recovery. Only runs after a pass — Bumble only surfaces
    // "you missed" when we passed on someone their algo flags. If recovered,
    // the helper has already done a second click; re-scan halts before the
    // card-change probe runs against the post-recovery state.
    let finalDecision = wantLike ? "like" : "pass";
    let recoveredFromMissedMatch = false;
    if (!wantLike) {
      const r = await recoverMissedMatch(page, cursor, profile, filter, ratioCap, liked, swiped, sessionRewinds);
      sessionRewinds = r.rewindsUsed;
      if (r.recovered) {
        recoveredFromMissedMatch = true;
        finalDecision = r.finalAction;
        try { await scanForHalts(page); } catch (e) { stopReason = e.message; break; }
      }
    }

    // CODEX-R3-P0-5 + R4-P0-6 + R6-P0-1: verify the next card. Previous shape
    // released the reservation on stuck_card, but on Bumble a click can succeed
    // AND produce a match modal / upsell / verification interstitial that
    // freezes the visible card. To avoid undercounting actual swipes:
    //   - if a different card appears -> success (keep reservation)
    //   - if the card stays the same with no overlay markers -> stuck (release)
    //   - if no card visible (overlay obscuring) -> KEEP reservation, halt loop
    //     (we did click; we don't know whether it took, so refuse to release
    //      and force the operator to verify).
    // CODEX-R7-P1-7: card-change check used to compare only name. Two consecutive
    // people with the same first name (Sarah, Sarah) registered as "stuck" and
    // released the cap after a real swipe. Compare on the (name, age, distance)
    // identity tuple instead — even same-named profiles will differ on at least one.
    const idOf = (p) => `${p.name || ""}::${p.age ?? ""}::${p.distance_mi ?? ""}`;
    const profileId = idOf(profile);
    let cardChanged = false;
    let lastSeenName = null;
    let lastSeenId = null;
    for (let probe = 0; probe < 6; probe++) {
      await sleep(jitter(250, 500));
      const next = await readVisibleCard(page);
      lastSeenName = next.name;
      lastSeenId = idOf(next);
      if (next.name && lastSeenId !== profileId) { cardChanged = true; break; }
    }
    if (!cardChanged) {
      if (lastSeenId === profileId) {
        // Same card persists, no overlay - the click missed. Safe to release.
        await releaseCap(reservation);
        await logSwipe({ decision: "stuck_card", filter_pass: inFilter, profile, last_seen_name: lastSeenName, day_count: null });
        stopReason = "stuck_card_after_click";
      } else {
        // CODEX-R7-P0-6+7: overlay/modal/interstitial after click. We can't
        // distinguish a benign Bumble match modal from a Cloudflare/photo-verify
        // surface from a same-card stuck retry. Doctrine is fail-closed: KEEP
        // reservation AND set .halt so the next cron does not walk back into
        // the same surface (or open another card on top of an unhandled modal).
        // Operator must dismiss the modal manually and clear the halt.
        const haltReason = `overlay_after_click_kept_reservation:${profile.name || "unknown"}`;
        await setHalt(haltReason);
        await logSwipe({ decision: "overlay_after_click", filter_pass: inFilter, profile, last_seen_name: null, day_count: reservation.dayUsed, halt: haltReason });
        await logSession({ event: "halt", kind: "overlay_after_click", reservation_kept: true });
        stopReason = haltReason;
      }
      break;
    }

    await logSwipe({
      decision: finalDecision,
      filter_pass: inFilter,
      ratio_after: wouldBeRatio,
      profile,
      day_count: reservation.dayUsed,
      ...(recoveredFromMissedMatch ? { recovered_from_missed_match: true } : {}),
    });
    swiped += 1;
    if (finalDecision === "like") liked += 1;

    await sleep(jitter(...caps.swipes.between_swipes_ms));
  }

  return { swiped, liked, stopReason, ratio: swiped > 0 ? liked / swiped : 0 };
}
