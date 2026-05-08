// recon.mjs -- one-off DOM inventory for new UI surfaces.
// Opens marketing-studio + cinema-studio + ai/video, dumps selector candidates
// for new features (viral hooks, avatar library, 10 content modes, genre tiles,
// audio-sync, AI Director, model picker contents). Output goes to stdout JSON.
//
// Run after a successful smoke test so the JWT/profile is warm:
//   node scripts/run.mjs recon
//
// Output is written to:
//   _shell/skill-output/higgsfield/recon/<timestamp>.json
// Use the JSON to update selectors in marketing.mjs / cinema.mjs / video.mjs.

import { launchContext } from './browser.mjs';
import { browsePhase } from './behavior.mjs';
import { waitForCapturedJwt } from './jwt.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const OUTPUT_ROOT = '/Users/shakstzy/ULTRON/_shell/skill-output/higgsfield/recon';

// Walk the DOM and emit a compact inventory of clickable / textual elements
// that look like preset tiles, model tiles, mode buttons, or feature toggles.
async function dumpClickables(page, label) {
  return page.evaluate(lbl => {
    const out = { url: location.href, label: lbl, items: [] };
    const seen = new Set();
    const candidates = Array.from(document.querySelectorAll(
      'button, [role="button"], [role="tab"], [role="option"], [role="menuitem"], [data-state]'
    ));
    for (const el of candidates) {
      const t = (el.innerText || '').trim();
      if (!t) continue;
      if (t.length > 200) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 30 || r.height < 20) continue;
      if (window.getComputedStyle(el).visibility === 'hidden') continue;
      const line1 = t.split('\n')[0].trim();
      const key = `${el.tagName}|${line1}|${Math.round(r.x)},${Math.round(r.y)}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.items.push({
        tag: el.tagName,
        role: el.getAttribute('role'),
        line1,
        text_short: t.slice(0, 80),
        xy: [Math.round(r.x), Math.round(r.y)],
        wh: [Math.round(r.width), Math.round(r.height)],
        aria_label: el.getAttribute('aria-label'),
        data_state: el.getAttribute('data-state'),
        data_preset: el.getAttribute('data-preset'),
        href: el.getAttribute('href') || null
      });
    }
    return out;
  }, label);
}

// Open the model picker (if present), capture all model tile labels, then close.
async function dumpModelPicker(page, label) {
  const triggerJs = await page.evaluateHandle(() => {
    for (const b of document.querySelectorAll('button, [role="button"]')) {
      const t = (b.innerText || '').trim();
      if (t === 'Select model' || /^Select model(\s|$)/.test(t) || /^Model\n.+/.test(t)) {
        const r = b.getBoundingClientRect();
        if (r.x < 500 && r.width >= 40) return b;
      }
    }
    return null;
  });
  const trig = triggerJs.asElement ? triggerJs.asElement() : null;
  if (!trig) return { url: page.url(), label, models: [] };
  await trig.click({ force: true }).catch(() => {});
  await page.waitForTimeout(1500);
  const models = await page.evaluate(() => {
    const out = [];
    const containers = Array.from(document.querySelectorAll('[role="dialog"], [data-state="open"], [role="menu"], [role="listbox"]'));
    for (const c of containers) {
      for (const b of c.querySelectorAll('button, [role="option"], [role="menuitem"]')) {
        const t = (b.innerText || '').trim();
        if (!t) continue;
        const line1 = t.split('\n')[0].trim();
        const r = b.getBoundingClientRect();
        if (r.width < 30 || r.height < 20) continue;
        out.push({ line1, text_short: t.slice(0, 100), xy: [Math.round(r.x), Math.round(r.y)] });
      }
    }
    return out;
  });
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(300);
  return { url: page.url(), label, models };
}

export async function runRecon() {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  mkdirSync(OUTPUT_ROOT, { recursive: true });
  const outPath = join(OUTPUT_ROOT, `${ts}.json`);

  const ctx = await launchContext({ headless: false });
  const page = ctx.page;
  const result = { timestamp: ts, surfaces: {} };

  try {
    // Marketing Studio V2
    await page.goto('https://higgsfield.ai/marketing-studio', { waitUntil: 'load', timeout: 45000 });
    await waitForCapturedJwt(ctx.jwtCapture, { timeoutMs: 30000 });
    await browsePhase(page);
    await page.waitForTimeout(2000);
    result.surfaces.marketing_studio_v2 = await dumpClickables(page, 'marketing_studio');

    // Cinema Studio 3.5
    await page.goto('https://higgsfield.ai/cinema-studio?autoSelectFolder=true', { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(2000);
    result.surfaces.cinema_studio_3_5 = await dumpClickables(page, 'cinema_studio');

    // /ai/video model picker — grab full list of model tiles
    await page.goto('https://higgsfield.ai/ai/video', { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(2000);
    result.surfaces.video_model_picker = await dumpModelPicker(page, 'video_models');

    // /ai/image model picker — grab full list of model tiles
    await page.goto('https://higgsfield.ai/ai/image', { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(2000);
    result.surfaces.image_model_picker = await dumpModelPicker(page, 'image_models');

    writeFileSync(outPath, JSON.stringify(result, null, 2));
    console.log(`[recon] wrote ${outPath}`);
    console.log(`[recon] surfaces captured: ${Object.keys(result.surfaces).join(', ')}`);
    return outPath;
  } finally {
    await ctx.close();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runRecon().catch(err => { console.error(err); process.exit(1); });
}
