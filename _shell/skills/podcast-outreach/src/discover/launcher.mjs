// Patchright launcher for the podcast-outreach scrape. Anonymous (no
// login), persistent profile reused across runs to keep cookies/cache
// warm. Headful by default per agent-learning ("NOT headless, breaks
// bot detection") with osascript focus-restore so launches don't
// steal focus from whatever Adithya is working on.

import { promises as fs } from "node:fs";
import { spawn } from "node:child_process";
import { chromium } from "patchright";
import { BROWSER_PROFILE } from "../runtime/paths.mjs";
import { dim, warn } from "../runtime/logger.mjs";

const DEFAULT_VIEWPORT = { width: 1280, height: 900 };

async function frontmostApp() {
  return new Promise((resolve) => {
    const child = spawn("osascript", [
      "-e",
      'tell application "System Events" to name of first process whose frontmost is true',
    ]);
    let out = "";
    child.stdout.on("data", (d) => (out += d.toString()));
    child.on("close", () => resolve(out.trim()));
    child.on("error", () => resolve(""));
  });
}

async function activateApp(name) {
  if (!name) return;
  return new Promise((resolve) => {
    const child = spawn("osascript", ["-e", `tell application "${name}" to activate`]);
    child.on("close", () => resolve());
    child.on("error", () => resolve());
  });
}

export async function launchPersistent({
  headless = false,
  viewport = DEFAULT_VIEWPORT,
  restoreFocus = true,
} = {}) {
  await fs.mkdir(BROWSER_PROFILE, { recursive: true });

  const prevFront = restoreFocus ? await frontmostApp() : "";

  const launchOpts = {
    headless,
    viewport,
    args: [
      "--disable-blink-features=AutomationControlled",
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-features=IsolateOrigins,site-per-process",
    ],
  };
  let ctx;
  try {
    ctx = await chromium.launchPersistentContext(BROWSER_PROFILE, launchOpts);
  } catch (e) {
    if (/Executable doesn't exist/i.test(e.message)) {
      warn("patchright chromium not installed. Run: npx patchright install chromium");
    }
    throw e;
  }

  // Tab hygiene
  const pages = ctx.pages();
  for (let i = 1; i < pages.length; i++) {
    try { await pages[i].close({ runBeforeUnload: false }); } catch { /* ignore */ }
  }
  const page = ctx.pages()[0] ?? (await ctx.newPage());
  page.setDefaultTimeout(25_000);
  page.setDefaultNavigationTimeout(35_000);

  if (restoreFocus && prevFront && prevFront !== "Chromium" && prevFront !== "Google Chrome") {
    setTimeout(() => activateApp(prevFront).catch(() => {}), 600);
  } else {
    dim(`[launcher] no focus restore (frontmost was: ${prevFront || "unknown"})`);
  }

  const origClose = ctx.close.bind(ctx);
  ctx.close = async () => {
    for (const p of ctx.pages()) {
      try { await p.close({ runBeforeUnload: false }); } catch { /* ignore */ }
    }
    return origClose();
  };

  return { ctx, page };
}
