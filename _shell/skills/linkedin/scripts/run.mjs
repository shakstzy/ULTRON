#!/usr/bin/env node
// LinkedIn skill dispatcher. Single entrypoint for every verb the QUANTUM tree
// previously exposed as 13 separate scripts. Pattern matches discord/grok-web.
//
//   node scripts/run.mjs <verb> [flags]
//
// Verbs:
//   login, status, diag, pull, get-profile, send-dm, send-connect,
//   list-threads, list-invites, get-conversation, accept-invite,
//   withdraw-invite, search-people
//
// Common flag: --workspace <ws>  (default: personal — controls where raw
// markdown is deposited under workspaces/<ws>/raw/linkedin/)
// Write verbs (send-dm, send-connect, accept-invite, withdraw-invite) default
// to dry-run. Pass --send to execute.

const argv = process.argv.slice(2);
const verb = argv[0];
const rest = argv.slice(1);

if (!verb || verb === "--help" || verb === "-h") {
  printHelp();
  process.exit(verb ? 0 : 1);
}

// --workspace must be parsed BEFORE importing paths.mjs so RAW_DIR resolves
// against the right tree. We reject missing or flag-shaped values to avoid
// silently turning `--workspace --no-write --profile foo` into a workspace
// named "--no-write" that strips the safety flag. Last occurrence wins.
{
  let wsIdx = rest.indexOf("--workspace");
  while (wsIdx >= 0) {
    const wsVal = rest[wsIdx + 1];
    if (wsVal === undefined || wsVal.startsWith("--")) {
      console.error("--workspace requires a non-empty value, e.g. --workspace personal");
      process.exit(1);
    }
    process.env.LINKEDIN_WORKSPACE = wsVal;
    rest.splice(wsIdx, 2);
    wsIdx = rest.indexOf("--workspace");
  }
}

const verbs = {
  login: vLogin,
  status: vStatus,
  diag: vDiag,
  pull: vPull,
  "get-profile": vGetProfile,
  "send-dm": vSendDm,
  "send-connect": vSendConnect,
  "list-threads": vListThreads,
  "list-invites": vListInvites,
  "get-conversation": vGetConversation,
  "accept-invite": vAcceptInvite,
  "withdraw-invite": vWithdrawInvite,
  "search-people": vSearchPeople,
};

const handler = verbs[verb];
if (!handler) {
  console.error(`Unknown verb: ${verb}`);
  printHelp();
  process.exit(1);
}

try {
  const code = await handler(parseArgs(rest));
  process.exit(code ?? 0);
} catch (err) {
  console.error(`[${verb}] ${err.code ?? "ERR"} ${err.message}`);
  // Hard ban / checkpoint signal -> quarantine the profile and trip halt so the
  // next run can't keep poking at a flagged session. Original QUANTUM CLI never
  // wired this up; the SKILL.md claims it, so the dispatcher does it.
  if (err && (err.code === "BAN_SIGNAL" || err.code === "CHECKPOINT")) {
    try {
      const { quarantineOnSignal } = await import("../src/linkedin/ban-signals.mjs");
      await quarantineOnSignal(err);
    } catch (qerr) {
      console.error(`[${verb}] quarantine failed: ${qerr.message}`);
    }
  }
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Verbs
// ---------------------------------------------------------------------------

async function vLogin() {
  const { abortIfHalted, isHalted } = await import("../src/runtime/halt.mjs");
  if (await isHalted()) {
    console.error(`Workspace is halted. Inspect ~/.ultron/linkedin/.halt before re-running login.`);
    return 2;
  }
  await abortIfHalted();
  const { launchPersistent } = await import("../src/runtime/profile.mjs");
  const { ensureLoggedIn } = await import("../src/linkedin/session.mjs");
  const { LinkedInExtractor } = await import("../src/linkedin/extractor.mjs");

  console.log("[login] launching persistent Chrome profile…");
  const { ctx, page } = await launchPersistent({ headless: false });
  try {
    await ensureLoggedIn(page, { allowInteractive: true, interactiveTimeoutMs: 5 * 60_000 });
    console.log("[login] /feed reached. Reading own profile slug from global nav…");
    const navHref = await page.evaluate(() => {
      const cands = [
        'nav a[href*="/in/"]',
        'header a[href*="/in/"]',
        'a[href*="/in/"][data-test-app-aware-link]',
        'a[href*="/in/"]',
      ];
      for (const sel of cands) {
        const a = document.querySelector(sel);
        if (a) {
          const href = a.getAttribute("href") || "";
          const m = href.match(/\/in\/([^/?#]+)/);
          if (m) return { href, publicId: m[1], selector: sel };
        }
      }
      return null;
    }).catch(() => null);

    if (!navHref) {
      console.log("[login] OK — session is good (could not parse self /in/ link from nav).");
      return 0;
    }
    console.log(`[login] self public_id from nav: ${navHref.publicId} (selector=${navHref.selector})`);
    try {
      const ext = new LinkedInExtractor(page);
      const me = await ext.getPersonProfile(navHref.publicId);
      console.log("[login] OK. Self profile:");
      console.log(JSON.stringify({
        url: me.url,
        displayName: me.displayName,
        profileUrn: me.profileUrn,
        publicId: navHref.publicId,
        mainTextLen: (me.sections.main_profile || "").length,
      }, null, 2));
    } catch (err) {
      console.error(`[login] self-profile fetch failed: ${err.code ?? "ERR"} ${err.message}`);
    }
    return 0;
  } finally {
    await ctx.close();
  }
}

async function vStatus(args) {
  const { readCounters } = await import("../src/runtime/caps.mjs");
  const { isHalted, readHaltReason } = await import("../src/runtime/halt.mjs");
  const { tailLog } = await import("../src/runtime/logger.mjs");

  const halted = await isHalted();
  const reason = halted ? await readHaltReason() : "";
  const counters = await readCounters();
  const tail = await tailLog(10);

  const out = {
    halted,
    halt_reason: halted ? reason : null,
    active_hours_now: counters._active_hours_now,
    daily: Object.fromEntries(
      Object.entries(counters)
        .filter(([k]) => !k.startsWith("_"))
        .map(([k, v]) => [k, `${v.used}/${v.cap}${v.week_cap ? ` (week ${v.week_used}/${v.week_cap})` : ""}`])
    ),
    recent_actions: tail.map((r) => ({ ts: r.ts, action: r.action, target: r.target, ok: r.success !== false })),
  };

  if (args.json) {
    console.log(JSON.stringify(out, null, 2));
    return 0;
  }
  if (out.halted) console.log(`HALTED: ${out.halt_reason}`);
  console.log(`Active hours now: ${out.active_hours_now ? "yes" : "no"}`);
  console.log("Daily budgets:");
  for (const [k, v] of Object.entries(out.daily)) console.log(`  ${k.padEnd(28)} ${v}`);
  console.log("\nRecent actions:");
  for (const r of out.recent_actions) {
    console.log(`  ${r.ts}  ${(r.action ?? "").padEnd(20)} ${r.ok ? "OK " : "ERR"}  ${r.target ?? ""}`);
  }
  return 0;
}

async function vDiag(args) {
  const { promises: fs } = await import("node:fs");
  const { join } = await import("node:path");
  const { abortIfHalted } = await import("../src/runtime/halt.mjs");
  const { launchPersistent } = await import("../src/runtime/profile.mjs");
  const { ensureLoggedIn } = await import("../src/linkedin/session.mjs");
  const { DIAG_DIR } = await import("../src/runtime/paths.mjs");

  await abortIfHalted();
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const outDir = join(DIAG_DIR, ts);
  await fs.mkdir(outDir, { recursive: true });

  const url = args.url ?? "https://www.linkedin.com/feed/";
  const { ctx, page } = await launchPersistent({ headless: false });
  try {
    await ensureLoggedIn(page);
    console.log(`[diag] -> ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: join(outDir, "screenshot.png"), fullPage: true });
    const innerText = await page.evaluate(() => (document.body?.innerText || "").slice(0, 8000));
    await fs.writeFile(join(outDir, "page-text.txt"), innerText, "utf8");

    const survey = await page.evaluate(() => {
      function describe(sel) {
        const els = Array.from(document.querySelectorAll(sel));
        return { count: els.length, sample: els[0]?.outerHTML?.slice(0, 240) ?? null };
      }
      return {
        "main": describe("main"),
        "main h1": describe("main h1"),
        "main a[href*='/preload/custom-invite/']": describe("main a[href*='/preload/custom-invite/']"),
        "main a[href*='/messaging/compose/']": describe("main a[href*='/messaging/compose/']"),
        "main a[href*='/edit/intro/']": describe("main a[href*='/edit/intro/']"),
        "dialog[open], [role='dialog']": describe("dialog[open], [role='dialog']"),
        "[role='dialog'] textarea, dialog textarea": describe("[role='dialog'] textarea, dialog textarea"),
        "main label[aria-label^='Select conversation']": describe("main label[aria-label^='Select conversation']"),
        "div[role='textbox'][contenteditable='true']": describe("div[role='textbox'][contenteditable='true']"),
        "button[aria-label*='Send']": describe("button[aria-label*='Send']"),
        "button[aria-label*='Withdraw']": describe("button[aria-label*='Withdraw']"),
        "main a[href*='/in/']": describe("main a[href*='/in/']"),
      };
    }).catch((e) => ({ _error: String(e) }));
    await fs.writeFile(join(outDir, "selector-survey.json"), JSON.stringify(survey, null, 2), "utf8");
    console.log(`[diag] artifacts: ${outDir}`);
    return 0;
  } finally {
    await ctx.close();
  }
}

async function vPull(args) {
  const threadLimit = Number(args["thread-limit"] ?? 10);
  const { launchPersistent } = await import("../src/runtime/profile.mjs");
  const { ensureLoggedIn } = await import("../src/linkedin/session.mjs");
  const { LinkedInExtractor } = await import("../src/linkedin/extractor.mjs");
  const { upsertPerson } = await import("../src/runtime/entity-store.mjs");
  const { toSlug } = await import("../src/runtime/slug.mjs");
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { sleep, jitter } = await import("../src/runtime/humanize.mjs");
  const { loadCaps } = await import("../src/runtime/caps.mjs");
  const { sprinkleBetween, tickBurst, maybeGetDistracted } = await import("../src/runtime/messy-human.mjs");

  const { ctx, page } = await launchPersistent({ headless: false });
  try {
    await ensureLoggedIn(page);
    const ext = new LinkedInExtractor(page);

    const inbox = await ext.getInbox({ limit: threadLimit });
    console.log(`[pull] inbox refs: ${inbox.threads.length}`);

    for (const t of inbox.threads.slice(0, threadLimit)) {
      await maybeGetDistracted();
      await sprinkleBetween(page);
      try { await gate("get_profile"); } catch { console.log("[pull] budget exhausted, stopping thread enrichment"); break; }
      try {
        const conv = await ext.getConversation({ threadId: t.threadId });
        const slug = toSlug(t.name || t.threadId);
        await upsertPerson({
          slug,
          frontmatter: { slug, linkedin_thread_id: t.threadId, name: t.name || null, source: "thread_sync", last_pulled_at: new Date().toISOString() },
          profileSnapshot: null,
          threadEvent: { direction: "system", text: `Pulled thread snapshot (${(conv.sections.conversation || "").length} chars)`, ts: new Date().toISOString() },
        });
        await record("get_profile", { target: t.threadId });
      } catch (err) {
        console.error(`[pull] thread ${t.threadId} skipped: ${err.code ?? "ERR"} ${err.message}`);
      }
      const [lo, hi] = (await loadCaps()).pacing.inter_action_seconds;
      await sleep(jitter(lo * 1000, hi * 1000));
      await tickBurst(page);
    }

    for (const direction of ["received", "sent"]) {
      await sprinkleBetween(page);
      try {
        const inv = await ext.listInvites({ direction });
        console.log(`[pull] invites (${direction}): ${(inv.sections.invites || "").length} chars`);
      } catch (err) {
        console.error(`[pull] invites ${direction} skipped: ${err.code ?? "ERR"} ${err.message}`);
      }
    }

    console.log("[pull] done");
    return 0;
  } finally {
    await ctx.close();
  }
}

async function vGetProfile(args) {
  if (!args.profile) {
    console.error('Usage: run.mjs get-profile --profile <id_or_url> [--no-write] [--no-promote] [--json]');
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { upsertPerson, upsertGlobalPersonStub } = await import("../src/runtime/entity-store.mjs");
  const { toSlug } = await import("../src/runtime/slug.mjs");
  const { urlOrIdToPublicId } = await import("../src/runtime/identity.mjs");

  await gate("get_profile");
  const publicId = urlOrIdToPublicId(args.profile);
  if (!publicId) { console.error("Cannot derive public_id from input."); return 1; }

  return withSession(async (ext) => {
    const result = await ext.getPersonProfile(publicId);
    const slug = result.displayName ? toSlug(result.displayName) : toSlug(publicId);

    if (args["no-write"]) {
      if (args.json) console.log(JSON.stringify(result, null, 2));
      else console.log(result.sections.main_profile.slice(0, 600));
      return 0;
    }
    const fm = {
      slug,
      linkedin_public_id: publicId,
      linkedin_url: result.url,
      linkedin_urn: result.profileUrn,
      name: result.displayName,
      last_pulled_at: new Date().toISOString(),
    };
    const file = await upsertPerson({ slug, frontmatter: fm, profileSnapshot: result.sections.main_profile });

    // Auto-create thin provisional global stub unless opted out. Idempotent —
    // if contacts-sync already wrote a stub at this slug we leave it alone.
    let globalStub = null;
    if (!args["no-promote"]) {
      globalStub = await upsertGlobalPersonStub({
        slug,
        name: result.displayName,
        linkedinPublicId: publicId,
        linkedinUrl: result.url,
      });
    }

    await record("get_profile", { target: publicId, extra: { slug, file, globalStub: globalStub?.file ?? null } });
    if (args.json) {
      console.log(JSON.stringify({
        slug, file, displayName: result.displayName, profileUrn: result.profileUrn, url: result.url,
        globalStub: globalStub?.file ?? null, globalStubCreated: globalStub?.created ?? false,
      }, null, 2));
    } else {
      const stubLabel = globalStub
        ? (globalStub.created ? `; created ${globalStub.file}` : `; existing ${globalStub.file}`)
        : "";
      console.log(`OK  ${result.displayName ?? publicId}  ->  ${file}${stubLabel}`);
    }
    return 0;
  });
}

async function vSendDm(args) {
  if (!args.profile || !args.text) {
    console.error('Usage: run.mjs send-dm --profile <id> --text "..." [--send] [--to-connection] [--profile-urn <urn>]');
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { urlOrIdToPublicId } = await import("../src/runtime/identity.mjs");
  const { upsertPerson } = await import("../src/runtime/entity-store.mjs");
  const { toSlug } = await import("../src/runtime/slug.mjs");

  const publicId = urlOrIdToPublicId(args.profile);
  if (!publicId) { console.error("Cannot derive public_id from input."); return 1; }
  const dryRun = !args.send;
  const action = args["to-connection"] ? "send_dm_to_connection" : "send_dm_to_non_connection";
  await gate(action);

  return withSession(async (ext) => {
    const result = await ext.sendMessage(publicId, args.text, { confirmSend: !dryRun, profileUrn: args["profile-urn"] ?? null });
    console.log(`[send-dm] ${JSON.stringify(result)}`);
    if (result.ok && !dryRun) {
      await record(action, { target: publicId });
      const slug = toSlug(publicId);
      await upsertPerson({
        slug,
        frontmatter: { linkedin_public_id: publicId, linkedin_url: result.url, source: "manual_url" },
        threadEvent: { direction: "outbound", text: args.text, ts: new Date().toISOString() },
      });
    }
    return 0;
  });
}

async function vSendConnect(args) {
  if (!args.profile) {
    console.error('Usage: run.mjs send-connect --profile <id> [--note "..."] [--send] [--skip-ceiling]');
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { enforcePendingCeiling } = await import("../src/policy/pending-budget.mjs");
  const { urlOrIdToPublicId } = await import("../src/runtime/identity.mjs");
  const { upsertPerson } = await import("../src/runtime/entity-store.mjs");
  const { toSlug } = await import("../src/runtime/slug.mjs");

  const publicId = urlOrIdToPublicId(args.profile);
  if (!publicId) { console.error("Cannot derive public_id from input."); return 1; }
  const dryRun = !args.send;
  await gate("send_connect");

  return withSession(async (ext, page) => {
    if (!args["skip-ceiling"]) {
      const ceiling = await enforcePendingCeiling(page, ext, { dryRun, gate, record });
      console.log(`[pending-ceiling] ${JSON.stringify(ceiling)}`);
      if (!ceiling.ok) {
        const reason = ceiling.reason ?? ceiling.action;
        console.error(`[send-connect] BLOCKED by pending-ceiling: ${reason}`);
        return dryRun ? 0 : 2;
      }
    }
    const result = await ext.connectWithPerson(publicId, { note: args.note ?? null, dryRun });
    console.log(`[send-connect] ${JSON.stringify(result)}`);
    if (result.ok && !dryRun) {
      await record("send_connect", { target: publicId });
      const slug = toSlug(publicId);
      await upsertPerson({
        slug,
        frontmatter: { linkedin_public_id: publicId, linkedin_url: result.url, connection_status: result.status === "accepted" ? "connected" : "pending", source: "manual_url" },
        threadEvent: { direction: "system", text: `Connection ${result.status}${args.note ? " (with note)" : " (no note)"}`, ts: new Date().toISOString() },
      });
    }
    return 0;
  });
}

async function vListThreads(args) {
  const limit = Number(args.limit ?? 20);
  const { withSession } = await openSessionFactory();
  return withSession(async (ext) => {
    const result = await ext.getInbox({ limit });
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`Inbox (${result.threads.length} thread refs):`);
      for (const t of result.threads) console.log(`  ${t.threadId}  ${t.name}`);
      console.log("\n--- raw inbox text (truncated) ---");
      console.log((result.sections.inbox || "").slice(0, 1500));
    }
    return 0;
  });
}

async function vListInvites(args) {
  const direction = args.direction ?? "received";
  const { withSession } = await openSessionFactory();
  return withSession(async (ext) => {
    const result = await ext.listInvites({ direction });
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`Invitations (${direction}) at ${result.url}:`);
      console.log(`Entries (${result.entries.length}):`);
      for (const e of result.entries) console.log(`  ${e.slug}\t${e.displayName ?? ""}`);
      console.log("\n--- raw page text (truncated) ---");
      console.log((result.sections.invites || "").slice(0, 2000));
    }
    return 0;
  });
}

async function vGetConversation(args) {
  if (!args.thread && !args.profile) {
    console.error("Usage: run.mjs get-conversation (--thread <id> | --profile <username>) [--json]");
    return 1;
  }
  const { withSession } = await openSessionFactory();
  return withSession(async (ext) => {
    const result = await ext.getConversation({ threadId: args.thread, username: args.profile });
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`Conversation @ ${result.url}\n`);
      console.log(result.sections.conversation || "(empty)");
    }
    return 0;
  });
}

async function vAcceptInvite(args) {
  if (!args.profile) {
    console.error("Usage: run.mjs accept-invite --profile <id> [--send]");
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { urlOrIdToPublicId } = await import("../src/runtime/identity.mjs");
  const publicId = urlOrIdToPublicId(args.profile);
  if (!publicId) { console.error("Cannot derive public_id."); return 1; }
  const dryRun = !args.send;
  await gate("accept_invite");
  return withSession(async (ext) => {
    const result = await ext.connectWithPerson(publicId, { dryRun });
    console.log(`[accept-invite] ${JSON.stringify(result)}`);
    if (result.ok && !dryRun) await record("accept_invite", { target: publicId });
    return 0;
  });
}

async function vWithdrawInvite(args) {
  if (!args.profile) {
    console.error("Usage: run.mjs withdraw-invite --profile <id> [--send]");
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  const { urlOrIdToPublicId } = await import("../src/runtime/identity.mjs");
  const publicId = urlOrIdToPublicId(args.profile);
  if (!publicId) { console.error("Cannot derive public_id."); return 1; }
  const dryRun = !args.send;
  await gate("withdraw_invite");
  return withSession(async (ext) => {
    const result = await ext.withdrawInvite(publicId, { dryRun });
    console.log(`[withdraw-invite] ${JSON.stringify(result)}`);
    if (result.ok && !dryRun) await record("withdraw_invite", { target: publicId });
    return 0;
  });
}

async function vSearchPeople(args) {
  if (!args.query) {
    console.error('Usage: run.mjs search-people --query "..." [--location "..."] [--json]');
    return 1;
  }
  const { withSession } = await openSessionFactory();
  const { gate, record } = await import("../src/policy/rate-limits.mjs");
  await gate("search_people");
  return withSession(async (ext) => {
    const result = await ext.searchPeople({ query: args.query, location: args.location ?? null });
    await record("search_people", { target: args.query, extra: { hits: result.profiles?.length ?? 0 } });
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`Found ${result.profiles.length} profile links:`);
      for (const p of result.profiles.slice(0, 25)) console.log(`  ${p.username}`);
      console.log("\n--- raw search text (truncated) ---");
      console.log((result.sections.search_results || "").slice(0, 2000));
    }
    return 0;
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Lazy session opener — keeps top-of-file imports cheap so `--help` and
// argument-validation errors don't spin up patchright.
async function openSessionFactory() {
  const { launchPersistent } = await import("../src/runtime/profile.mjs");
  const { ensureLoggedIn } = await import("../src/linkedin/session.mjs");
  const { LinkedInExtractor } = await import("../src/linkedin/extractor.mjs");
  return {
    async withSession(fn) {
      const { ctx, page } = await launchPersistent({ headless: false });
      try {
        await ensureLoggedIn(page);
        const ext = new LinkedInExtractor(page);
        return await fn(ext, page);
      } finally {
        await ctx.close();
      }
    },
  };
}

// Permissive flag parser. Accepts `--key value` and bare `--flag` booleans.
// Unknown flags are kept under their literal name so verbs can read whatever
// they need (e.g. --to-connection, --no-write, --skip-ceiling, --send).
function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) {
      out[key] = true;
    } else {
      out[key] = next;
      i++;
    }
  }
  return out;
}

function printHelp() {
  console.error(`Usage: node scripts/run.mjs <verb> [flags]

Verbs:
  login                                              one-time interactive Chrome login
  status [--json]                                    halt + budgets + recent actions
  diag [--url <u>]                                   screenshot + page-text + selector survey
  pull [--thread-limit N]                            inbox + each thread + invites (read-only)
  get-profile --profile <id> [--no-write]            fetch a profile, optionally upsert markdown
          [--no-promote] [--json]                    --no-promote skips auto-creating the global stub
  send-dm --profile <id> --text "..." [--send]       compose and send a DM
          [--to-connection] [--profile-urn <urn>]
  send-connect --profile <id> [--note "..."]         send a connection request
          [--send] [--skip-ceiling]
  list-threads [--limit N] [--json]                  inbox listing
  list-invites [--direction sent|received] [--json]  invitation manager
  get-conversation (--thread <id> | --profile <u>)   read one thread
          [--json]
  accept-invite --profile <id> [--send]              accept an incoming request
  withdraw-invite --profile <id> [--send]            withdraw an outstanding sent invite
  search-people --query "..." [--location "..."]     people search
          [--json]

Common:
  --workspace <ws>    raw markdown writes under workspaces/<ws>/raw/linkedin/ (default: network)
  --send              required to actually execute write verbs (default is dry-run)
`);
}
