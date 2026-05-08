#!/usr/bin/env node
// Dump a Listennotes podcast detail page's HTML + likely-relevant DOM for inspection.

import fs from "node:fs/promises";
import { launchPersistent } from "../src/discover/launcher.mjs";

const url = process.argv[2] || "https://www.listennotes.com/podcasts/empire-blockworks-tBPniFSC1GA/";

const { ctx } = await launchPersistent({ headless: true });
const page = await ctx.newPage();
try {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await new Promise((r) => setTimeout(r, 4000));
  const html = await page.content();
  await fs.writeFile("/tmp/ln-detail.html", html, "utf8");
  console.log(`HTML length: ${html.length}`);

  // Check the email + rss patterns
  const emails = [...html.matchAll(/[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g)].map(m => m[0]);
  console.log(`emails: ${[...new Set(emails)].slice(0, 10).join(", ")}`);

  const rssLikes = [...html.matchAll(/https?:\/\/[^"<>\s]*?(rss|feed|xml)[^"<>\s]*/gi)].map(m => m[0]);
  console.log(`rss candidates: ${[...new Set(rssLikes)].slice(0, 10).join("\n  ")}`);

  // Inspect specific dom landmarks
  const inspect = await page.evaluate(() => {
    const out = {};
    out.title = document.title;
    out.h1 = document.querySelector("h1")?.textContent?.trim()?.slice(0, 100) || null;
    out.rss_button = [...document.querySelectorAll("a, button")].filter(el => /rss/i.test(el.textContent || el.getAttribute("aria-label") || "")).map(el => ({
      tag: el.tagName,
      text: (el.textContent || "").trim().slice(0, 40),
      href: el.getAttribute("href"),
      data: el.outerHTML.slice(0, 200),
    })).slice(0, 5);
    out.copy_button = [...document.querySelectorAll("button, [data-clipboard-text], [data-copy], [data-rss], [data-rss-url]")].slice(0, 5).map(el => ({
      tag: el.tagName,
      data_clipboard: el.getAttribute("data-clipboard-text"),
      data_copy: el.getAttribute("data-copy"),
      data_rss: el.getAttribute("data-rss") || el.getAttribute("data-rss-url"),
      text: (el.textContent || "").trim().slice(0, 40),
    }));
    out.input_with_rss = [...document.querySelectorAll("input")].filter(i => /(rss|feed|xml)/i.test(i.value || "")).map(i => ({ value: i.value, type: i.type, id: i.id }));
    out.json_ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent.slice(0, 500));
    out.meta_og = {};
    document.querySelectorAll("meta[property], meta[name]").forEach(m => {
      const k = m.getAttribute("property") || m.getAttribute("name");
      if (/og:|twitter:|description|email|rss/i.test(k)) out.meta_og[k] = (m.getAttribute("content") || "").slice(0, 120);
    });
    out.next_data = document.getElementById("__NEXT_DATA__")?.textContent?.slice(0, 1500) || null;
    return out;
  });
  console.log("\n=== inspection ===");
  console.log(JSON.stringify(inspect, null, 2));
} finally {
  await ctx.close();
}
