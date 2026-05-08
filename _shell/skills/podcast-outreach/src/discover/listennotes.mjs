// Listennotes scraper. For each seed (genre board or keyword search):
//   1. Visit the seed URL.
//   2. Collect podcast detail links (anchor[href*="/podcasts/"]).
//   3. For each podcast, in parallel batches:
//      a. Open detail page.
//      b. Attach a CDP session and listen for JSON network responses;
//         capture any email-shaped strings that pass through.
//      c. Read the RSS feed URL from page metadata (Listennotes exposes
//         it in plain text on the detail page — usually a "RSS feed"
//         button + a copyable RSS URL in the right rail).
//      d. Fetch the RSS feed; extract owner email + host + latest ep.
//   4. Emit normalized candidate rows.
//
// We don't depend on Listennotes' paid API. Discovery is purely page-driven.

import { extractFromRss, isValidEmail } from "./rss-extractor.mjs";
import { dim, info, warn } from "../runtime/logger.mjs";
import { jitteredSleep } from "../runtime/humanize.mjs";

const LN_BASE = "https://www.listennotes.com";

function seedUrl(seed) {
  if (seed.kind === "genre") return `${LN_BASE}/best-podcasts/${seed.slug}/`;
  if (seed.kind === "query") return `${LN_BASE}/search/?q=${encodeURIComponent(seed.q)}&sort_by_date=0&scope=podcast`;
  throw new Error(`unknown seed kind: ${seed.kind}`);
}

function seedLabel(seed) {
  return seed.kind === "genre" ? `genre:${seed.slug}` : `q:${seed.q}`;
}

async function collectPodcastLinks(page, { perSeedMax }) {
  // Listennotes detail pages live at /podcasts/<slug>-<id>/.
  const links = await page.evaluate(() => {
    const set = new Set();
    document.querySelectorAll('a[href*="/podcasts/"]').forEach((a) => {
      const h = a.getAttribute("href") || "";
      if (h.match(/\/podcasts\/[^/]+-[A-Za-z0-9]{6,}\/?$/)) {
        const url = h.startsWith("http") ? h : new URL(h, location.origin).toString();
        set.add(url);
      }
    });
    return [...set];
  });
  return links.slice(0, perSeedMax);
}

// Read RSS URL + title + description + host from the podcast detail page.
async function extractDetailMeta(page) {
  return page.evaluate(() => {
    const out = {};

    // 1. og: / twitter: tags often have title + description
    const og = (prop) =>
      document.querySelector(`meta[property="${prop}"]`)?.getAttribute("content") ||
      document.querySelector(`meta[name="${prop}"]`)?.getAttribute("content") ||
      null;
    out.title = og("og:title") || document.title || null;
    out.description = og("og:description") || null;
    out.canonical = document.querySelector('link[rel="canonical"]')?.getAttribute("href") || null;

    // 2. RSS URL — Listennotes exposes it in a few places. Most reliable:
    //    - Anchor with href ending in feed, /rss, /podcast.xml etc., often within an "RSS feed" button.
    //    - Sometimes: <input value="https://...feed..."> for copy-to-clipboard.
    //    - Fallback: scan all anchors for likely RSS hrefs.
    const looksLikeRss = (u) => {
      if (!u) return false;
      const lower = u.toLowerCase();
      if (lower.endsWith(".xml")) return true;
      if (lower.includes("/rss")) return true;
      if (lower.includes("/feed")) return true;
      if (lower.includes("feed.xml")) return true;
      if (lower.includes("podcast.xml")) return true;
      return false;
    };

    const rssCandidates = new Set();
    document.querySelectorAll('a[href]').forEach((a) => {
      const h = a.getAttribute("href") || "";
      if (looksLikeRss(h) && !h.includes("listennotes.com")) rssCandidates.add(h);
    });
    document.querySelectorAll('input[type="text"], input[type="url"], input:not([type])').forEach((i) => {
      const v = i.value || i.getAttribute("value") || "";
      if (looksLikeRss(v) && !v.includes("listennotes.com")) rssCandidates.add(v);
    });
    // JSON-LD
    document.querySelectorAll('script[type="application/ld+json"]').forEach((s) => {
      try {
        const j = JSON.parse(s.textContent || "{}");
        const stack = [j];
        while (stack.length) {
          const obj = stack.pop();
          if (!obj || typeof obj !== "object") continue;
          for (const [k, v] of Object.entries(obj)) {
            if (typeof v === "string" && looksLikeRss(v) && !v.includes("listennotes.com")) {
              rssCandidates.add(v);
            } else if (typeof v === "object") {
              stack.push(v);
            }
          }
        }
      } catch { /* skip */ }
    });

    // Also look for the dedicated "RSS feed" button — Listennotes wraps the URL
    // either in a link or a button-with-data attribute.
    document.querySelectorAll('[data-rss], [data-rss-url]').forEach((el) => {
      const v = el.getAttribute("data-rss") || el.getAttribute("data-rss-url");
      if (v) rssCandidates.add(v);
    });

    out.rss_candidates = [...rssCandidates];

    // 3. Author/host hint — Listennotes often shows "by <name>" in a span.
    out.author_hint = document.querySelector('a[href*="/podcaster/"]')?.textContent?.trim()
      || document.querySelector('[itemprop="author"]')?.textContent?.trim()
      || null;

    return out;
  });
}

// Run a CDP listener that scans every JSON response for email-shaped strings.
// Pure defense-in-depth — if Listennotes ever ships an email field directly,
// we'll catch it without changes. Returns a deactivator function.
async function attachEmailSniffer(page, sink) {
  let cdp;
  try {
    cdp = await page.context().newCDPSession(page);
  } catch (e) {
    // CDP attach failure is non-fatal — RSS extraction still runs.
    return () => {};
  }
  await cdp.send("Network.enable");

  const seenRequests = new Map(); // requestId -> mimeType
  cdp.on("Network.responseReceived", (evt) => {
    const mime = evt.response?.mimeType || "";
    if (mime.includes("json") || mime.includes("javascript")) {
      seenRequests.set(evt.requestId, mime);
    }
  });
  cdp.on("Loading.finished", async (evt) => {
    if (!seenRequests.has(evt.requestId)) return;
    try {
      const body = await cdp.send("Network.getResponseBody", { requestId: evt.requestId });
      const txt = body.base64Encoded ? Buffer.from(body.body, "base64").toString("utf8") : (body.body || "");
      const matches = txt.match(/[\w.+-]+@[\w-]+\.[\w.-]+/g);
      if (matches) {
        for (const m of matches) sink.add(m.toLowerCase());
      }
    } catch { /* swallow */ }
  });

  return async () => {
    try { await cdp.detach(); } catch { /* ignore */ }
  };
}

async function processPodcastDetail(page, url, { capsCfg }) {
  const sniffSink = new Set();
  const detach = await attachEmailSniffer(page, sniffSink);
  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    // Let lazy hydration / async fetches settle briefly.
    await jitteredSleep(900, 1500);

    const meta = await extractDetailMeta(page);
    let rssData = {};
    if (meta.rss_candidates && meta.rss_candidates.length) {
      // Try each candidate until one yields a parseable feed.
      for (const candidate of meta.rss_candidates) {
        rssData = await extractFromRss(candidate);
        if (rssData && rssData.email && isValidEmail(rssData.email)) {
          rssData._source = candidate;
          break;
        }
      }
    }

    // Pick best email: RSS owner email > sniffed (if a single, podcast-domain match)
    const sniffEmails = [...sniffSink].filter(isValidEmail);
    const podcastDomainHints = [meta.canonical, rssData?.website].filter(Boolean).map((u) => {
      try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return null; }
    }).filter(Boolean);
    const sniffOnDomain = sniffEmails.find((e) => {
      const d = e.split("@")[1];
      return podcastDomainHints.some((h) => d === h || d.endsWith("." + h));
    });

    const email = (rssData.email && isValidEmail(rssData.email)) ? rssData.email
                : sniffOnDomain || null;

    return {
      url,
      email,
      podcast_name: rssData.podcast_name || meta.title?.replace(/ \| Listen Notes$/, "") || null,
      host_name: rssData.host_name || meta.author_hint || null,
      recent_episode: rssData.latest_episode || null,
      website: rssData.website || meta.canonical || null,
      rss_url: rssData._source || (meta.rss_candidates?.[0] ?? null),
      description: rssData.description || meta.description || null,
      _sniff_count: sniffEmails.length,
    };
  } finally {
    await detach();
  }
}

// Public entry. Given an array of seeds, returns a flat array of candidates.
// Concurrency is implemented as N pages within the same persistent context.
export async function discoverFromSeeds({ ctx, seeds, concurrency = 4, perSeedMax = 50, capsCfg }) {
  const allCandidates = [];
  for (const seed of seeds) {
    const url = seedUrl(seed);
    info(`[discover] seed ${seedLabel(seed)} → ${url}`);

    let seedPage;
    try {
      seedPage = await ctx.newPage();
      seedPage.setDefaultTimeout(25_000);
      await seedPage.goto(url, { waitUntil: "domcontentloaded" });
      await jitteredSleep(800, 1400);
      // Trigger lazy-load by scrolling the page once.
      await seedPage.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "auto" }));
      await jitteredSleep(800, 1400);
      const links = await collectPodcastLinks(seedPage, { perSeedMax });
      dim(`[discover] ${seedLabel(seed)} → ${links.length} podcast links`);
      await seedPage.close();
      seedPage = null;

      // Process detail pages in concurrent batches.
      for (let i = 0; i < links.length; i += concurrency) {
        const batch = links.slice(i, i + concurrency);
        const settled = await Promise.allSettled(batch.map(async (link) => {
          const p = await ctx.newPage();
          p.setDefaultTimeout(25_000);
          try {
            return await processPodcastDetail(p, link, { capsCfg });
          } finally {
            try { await p.close(); } catch { /* ignore */ }
          }
        }));
        for (const r of settled) {
          if (r.status === "fulfilled" && r.value) {
            r.value._source_seed = seedLabel(seed);
            allCandidates.push(r.value);
          } else if (r.status === "rejected") {
            dim(`[discover] detail-page error: ${r.reason?.message || r.reason}`);
          }
        }
      }
    } catch (e) {
      warn(`[discover] seed failed (${seedLabel(seed)}): ${e.message}`);
    } finally {
      if (seedPage) try { await seedPage.close(); } catch { /* ignore */ }
    }
  }
  return allCandidates;
}
