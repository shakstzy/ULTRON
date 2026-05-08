// recon-deep.mjs -- detailed structural recon to find active-panel signals.
// Switches into a specific cinema mode, then dumps every prompt textbox with
// full ancestor chain + visibility state, so we can identify the correct
// disambiguation signal for selectVisiblePromptAnchor.

import { launchContext } from './browser.mjs';
import { browsePhase } from './behavior.mjs';
import { waitForCapturedJwt } from './jwt.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const OUTPUT_ROOT = '/Users/shakstzy/ULTRON/_shell/skill-output/higgsfield/recon';

async function dumpPromptStructure(page, label) {
  return page.evaluate(lbl => {
    const sel = 'div[role="textbox"][contenteditable="true"], textarea, [contenteditable="true"]';
    const inputs = Array.from(document.querySelectorAll(sel));
    return {
      label: lbl,
      url: location.href,
      input_count: inputs.length,
      inputs: inputs.map((el, i) => {
        const r = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        // Walk ancestors capturing role, aria-selected, data-state, hidden,
        // aria-hidden, data-orientation, data-state, class hints.
        const ancestors = [];
        let p = el.parentElement;
        for (let n = 0; n < 12 && p; n++) {
          ancestors.push({
            depth: n,
            tag: p.tagName,
            role: p.getAttribute('role'),
            ariaSelected: p.getAttribute('aria-selected'),
            ariaHidden: p.getAttribute('aria-hidden'),
            dataState: p.getAttribute('data-state'),
            dataOrientation: p.getAttribute('data-orientation'),
            hidden: p.hasAttribute('hidden'),
            id: p.id,
            classHint: (p.className || '').toString().slice(0, 80)
          });
          p = p.parentElement;
        }
        // Also check siblings — does this prompt sit next to a tab labelled
        // Image / Video?
        const siblingTabs = [];
        if (el.parentElement) {
          for (const s of el.parentElement.children) {
            if (s === el) continue;
            const role = s.getAttribute && s.getAttribute('role');
            if (role === 'tab') {
              siblingTabs.push({
                line1: (s.innerText || '').trim().split('\n')[0].trim(),
                ariaSelected: s.getAttribute('aria-selected')
              });
            }
          }
        }
        return {
          idx: i,
          tag: el.tagName,
          xy: [Math.round(r.x), Math.round(r.y)],
          wh: [Math.round(r.width), Math.round(r.height)],
          visibility: cs.visibility,
          display: cs.display,
          opacity: cs.opacity,
          textContent: (el.innerText || el.value || '').trim().slice(0, 60),
          placeholder: el.getAttribute('placeholder') || el.getAttribute('data-placeholder') || el.getAttribute('aria-placeholder') || '',
          ariaLabel: el.getAttribute('aria-label'),
          tabIndex: el.getAttribute('tabindex'),
          parentRole: el.parentElement?.getAttribute('role'),
          siblingTabs,
          ancestors
        };
      })
    };
  }, label);
}

async function dumpActiveTabs(page, label) {
  return page.evaluate(lbl => {
    const tabs = Array.from(document.querySelectorAll('[role="tab"][aria-selected="true"]'));
    return {
      label: lbl,
      active_tab_count: tabs.length,
      tabs: tabs.map(t => {
        const r = t.getBoundingClientRect();
        const cs = window.getComputedStyle(t);
        return {
          line1: (t.innerText || '').trim().split('\n')[0].trim(),
          xy: [Math.round(r.x), Math.round(r.y)],
          wh: [Math.round(r.width), Math.round(r.height)],
          visibility: cs.visibility,
          ariaControls: t.getAttribute('aria-controls'),
          id: t.id,
          parentRole: t.parentElement?.getAttribute('role')
        };
      })
    };
  }, label);
}

export async function runDeepRecon() {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  mkdirSync(OUTPUT_ROOT, { recursive: true });
  const outPath = join(OUTPUT_ROOT, `deep-${ts}.json`);

  const ctx = await launchContext({ headless: false });
  const page = ctx.page;
  const result = { timestamp: ts, sections: {} };

  try {
    // Cinema in image mode
    await page.goto('https://higgsfield.ai/cinema-studio?autoSelectFolder=true', { waitUntil: 'load', timeout: 45000 });
    await waitForCapturedJwt(ctx.jwtCapture, { timeoutMs: 30000 });
    await browsePhase(page);
    await page.waitForTimeout(3000);

    // Click image tab if not already selected
    await page.evaluate(() => {
      const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
      const img = tabs.find(t => {
        const line1 = (t.innerText || '').trim().split('\n')[0].trim();
        return line1.toLowerCase() === 'image' && t.getAttribute('aria-selected') !== 'true' && t.getBoundingClientRect().y > 50;
      });
      if (img) img.click();
    });
    await page.waitForTimeout(2000);

    result.sections.cinema_image_mode_prompts = await dumpPromptStructure(page, 'cinema_image_mode');
    result.sections.cinema_image_mode_active_tabs = await dumpActiveTabs(page, 'cinema_image_mode');

    // Switch to video
    await page.evaluate(() => {
      const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
      const vid = tabs.find(t => {
        const line1 = (t.innerText || '').trim().split('\n')[0].trim();
        return line1.toLowerCase() === 'video' && t.getAttribute('aria-selected') !== 'true' && t.getBoundingClientRect().y > 50;
      });
      if (vid) vid.click();
    });
    await page.waitForTimeout(2000);

    result.sections.cinema_video_mode_prompts = await dumpPromptStructure(page, 'cinema_video_mode');
    result.sections.cinema_video_mode_active_tabs = await dumpActiveTabs(page, 'cinema_video_mode');

    // Marketing studio
    await page.goto('https://higgsfield.ai/marketing-studio', { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(3000);
    result.sections.marketing_prompts = await dumpPromptStructure(page, 'marketing');
    result.sections.marketing_active_tabs = await dumpActiveTabs(page, 'marketing');

    writeFileSync(outPath, JSON.stringify(result, null, 2));
    console.log(`[deep-recon] wrote ${outPath}`);
    return outPath;
  } finally {
    await ctx.close();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runDeepRecon().catch(err => { console.error(err); process.exit(1); });
}
