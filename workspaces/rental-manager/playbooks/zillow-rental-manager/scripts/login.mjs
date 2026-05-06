// login.mjs -- one-time visible-Chrome login into the dedicated Zillow profile.
// Auth detection: navigate to a known owner-only URL and poll until we land there
// without bouncing to identity.zillow.com or hitting captcha. /rental-manager/
// alone is a public marketing page when unauthenticated, so the probe must use
// /rental-manager/properties/ which Zillow gates behind the owner session.
// Respects the circuit breaker (no implicit --force).

import { connectOrLaunch, hasCaptchaInDom, sanitizeUrl, installGracefulShutdown, warmUpZillow } from './browser.mjs';

const OWNER_PROBE_URL = 'https://www.zillow.com/rental-manager/properties/';
const LOGIN_TIMEOUT_MS = 10 * 60 * 1000;
const POLL_INTERVAL_MS = 3000;
const RENAV_INTERVAL_MS = 20 * 1000;

// Hosts where the user might legitimately be mid-signin. Skip renavigation
// while on any of these so we don't yank Chrome away from a password / SSO /
// 2FA challenge. Includes Zillow's own identity host plus the major SSO
// providers Zillow auth0 supports (Google, Apple, Facebook).
const AUTH_HOSTS = [
  'identity.zillow.com',
  'accounts.google.com',
  'appleid.apple.com',
  'idmsa.apple.com',
  'www.facebook.com',
  'm.facebook.com',
  'login.live.com'
];

function isAuthIdentityHost(href) {
  try {
    const h = new URL(href).hostname;
    return AUTH_HOSTS.includes(h) || /\.google\.com$/.test(h) || /\.apple\.com$/.test(h);
  } catch (_) { return false; }
}

function isOwnerProbePath(href) {
  try {
    const u = new URL(href);
    return /\.zillow\.com$/.test(u.hostname) && /^\/rental[-_]?manager\/properties(\/|$)/i.test(u.pathname);
  } catch (_) { return false; }
}

export async function runLogin({ force = false } = {}) {
  console.log('[zrm] Opening visible Chrome. Sign in to Zillow with your owner account.');
  console.log('[zrm] Profile: ~/.shakos/chrome-profiles/zillow-rental-manager/');
  console.log('[zrm] ToS note: automated access to Zillow may violate their ToS. Use at your discretion.');

  const ctx = await connectOrLaunch({ headless: false, force });
  installGracefulShutdown(() => ctx.close());
  console.log(`[zrm] mode=${ctx.mode}${ctx.mode === 'cdp' ? ' (attached to running daemon, no fresh warmup)' : ' (legacy fresh Chrome -- daemon not running)'}`);

  try {
    // PerimeterX warm-up only on legacy launch. CDP-attached sessions inherit
    // the daemon's existing _px3 token, so re-warming would be both redundant
    // and dangerous (back-to-back warmups are exactly what flags the IP).
    if (ctx.mode === 'launch') {
      console.log('[zrm] Warming up PerimeterX session via zillow.com homepage...');
      await warmUpZillow(ctx.page, { homepageWaitMs: 10000 });
    }

    await ctx.page.goto(OWNER_PROBE_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });

    const initialUrl = ctx.page.url();
    if (isAuthIdentityHost(initialUrl)) {
      console.log('[zrm] Not signed in. Sign in via the open Chrome window. Zillow may email a code.');
    } else {
      console.log(`[zrm] Landed on ${sanitizeUrl(initialUrl)}. Verifying server-side auth...`);
    }

    console.log('[zrm] Polling up to 10 minutes. Auth check uses /users/get loggedIn flag (server source of truth).');

    const deadline = Date.now() + LOGIN_TIMEOUT_MS;
    let captchaWarned = false;
    let lastRenavAt = Date.now();
    let loggedHint = 0;
    let success = false;

    while (Date.now() < deadline) {
      if (!captchaWarned && await hasCaptchaInDom(ctx.page)) {
        console.warn('[zrm] Captcha detected. Solve it manually in the open window.');
        captchaWarned = true;
      }

      const href = ctx.page.url();
      const onProbe = isOwnerProbePath(href);
      // Multi-step Zillow signin: step 1 is email-only (no password field).
      // Detect via input[type=email|name=email|autocomplete=email|placeholder=Email],
      // OR password input, OR explicit auth check via /users/get response.
      const probeStatus = await ctx.page.evaluate(async () => {
        const hasEmailField = !!document.querySelector(
          'input[type="email"], input[name="email"], input[autocomplete="email" i], input[placeholder*="Email" i], input[placeholder*="email" i]'
        );
        const hasPasswordField = !!document.querySelector('input[type="password"]');
        const hasLoginForm = !!document.querySelector('form[action*="login"], form[action*="authenticate"]');
        // Server-side auth probe via users/get. This is the source of truth —
        // it returns {response:{loggedIn:true,...}} only when really authed.
        let serverLoggedIn = null;
        try {
          const r = await fetch('/rental-manager-api/api/web/v2/users/get', { credentials: 'include' });
          if (r.ok) {
            const j = await r.json();
            serverLoggedIn = !!(j && j.response && j.response.loggedIn);
          }
        } catch (_) {}
        return { hasEmailField, hasPasswordField, hasLoginForm, serverLoggedIn };
      }).catch(() => ({}));

      if (onProbe && probeStatus.serverLoggedIn === true) { success = true; break; }

      // Periodic progress hint so Adithya knows what state we're in.
      const now = Date.now();
      if (!loggedHint || (now - loggedHint) > 30000) {
        const hint = probeStatus.serverLoggedIn === false
          ? '(server says loggedIn:false — sign in required)'
          : probeStatus.hasEmailField
            ? '(email field present — type your email and continue)'
            : probeStatus.hasPasswordField
              ? '(password field present — finish signing in)'
              : '(no auth state yet — keep waiting)';
        console.log(`[zrm] still polling at ${sanitizeUrl(href)} ${hint}`);
        loggedHint = now;
      }

      // If we've been hanging on a non-probe URL for a while (e.g. user signed in
      // and Zillow dropped them on the dashboard root), nudge by re-navigating to
      // the owner probe. Skip if user is mid-signin on identity.zillow.com.
      if (!isAuthIdentityHost(href) && (Date.now() - lastRenavAt) > RENAV_INTERVAL_MS) {
        try {
          await ctx.page.goto(OWNER_PROBE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
        } catch (_) {}
        lastRenavAt = Date.now();
      }

      await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
    }

    if (!success) {
      console.error(`[zrm] Login timeout. Last URL: ${sanitizeUrl(ctx.page.url())}`);
      console.error('[zrm] Re-run: node scripts/run.mjs login');
      process.exitCode = 2;
      return;
    }

    console.log(`[zrm] Signed in. Owner probe OK at ${sanitizeUrl(ctx.page.url())}`);
    console.log('[zrm] Profile cookies persisted. Future runs reuse this session automatically.');
    console.log('[zrm] Next: node scripts/run.mjs status');
  } finally {
    await ctx.close();
  }
}
