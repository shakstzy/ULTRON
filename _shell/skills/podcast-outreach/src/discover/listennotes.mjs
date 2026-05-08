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

// Read podcast metadata directly from Listennotes' "Claim this podcast" widget.
// Every detail page embeds a <div id="claim-podcast-app"> with the full
// channel metadata as data-* attributes, INCLUDING the owner email and the
// RSS URL — the same data that's gated behind a login modal in the visible
// "RSS" button. The widget itself is rendered server-side and visible without
// auth.
//
// Empire example:
//   <div id="claim-podcast-app"
//        data-channel-uuid="..."
//        data-channel-email="podcasts@blockworks.co"
//        data-channel-rss="https://feeds.megaphone.fm/empire"
//        data-channel-title="Empire"
//        data-channel-image="...">
async function extractDetailMeta(page) {
  return page.evaluate(() => {
    const out = {};

    const og = (prop) =>
      document.querySelector(`meta[property="${prop}"]`)?.getAttribute("content") ||
      document.querySelector(`meta[name="${prop}"]`)?.getAttribute("content") ||
      null;
    out.title = og("og:title") || document.title || null;
    out.description = og("og:description") || null;
    out.canonical = document.querySelector('link[rel="canonical"]')?.getAttribute("href") || null;

    // Primary path — claim widget data-channel-* attributes.
    const claim = document.getElementById("claim-podcast-app");
    if (claim) {
      out.channel_email = claim.getAttribute("data-channel-email") || null;
      out.channel_rss = claim.getAttribute("data-channel-rss") || null;
      out.channel_title = claim.getAttribute("data-channel-title") || null;
      out.channel_uuid = claim.getAttribute("data-channel-uuid") || null;
    }

    // Author/host hint — JSON-LD Article schema has an author field.
    let author = null;
    document.querySelectorAll('script[type="application/ld+json"]').forEach((s) => {
      try {
        const j = JSON.parse(s.textContent || "{}");
        if (j.author && typeof j.author === "object") {
          author = author || j.author.name || j.author["@id"] || null;
        }
      } catch { /* skip */ }
    });
    out.author_hint = author
      || document.querySelector('a[href*="/podcaster/"]')?.textContent?.trim()
      || null;

    return out;
  });
}

async function processPodcastDetail(page, url) {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await jitteredSleep(900, 1500);

  const meta = await extractDetailMeta(page);

  // Listennotes' channel email is the gold path. RSS feed is a secondary
  // enrichment pass — gives us host name + latest episode, but isn't required.
  let rssData = {};
  if (meta.channel_rss) {
    rssData = await extractFromRss(meta.channel_rss);
  }

  const email = (meta.channel_email && isValidEmail(meta.channel_email)) ? meta.channel_email
              : (rssData.email && isValidEmail(rssData.email)) ? rssData.email
              : null;

  const podcastName = meta.channel_title
    || rssData.podcast_name
    || meta.title?.replace(/ \| Listen Notes$/, "")
    || null;

  return {
    url,
    email,
    podcast_name: podcastName,
    host_name: rssData.host_name || meta.author_hint || null,
    recent_episode: rssData.latest_episode || null,
    website: rssData.website || meta.canonical || null,
    rss_url: meta.channel_rss || null,
    description: rssData.description || meta.description || null,
    listennotes_uuid: meta.channel_uuid || null,
  };
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
            return await processPodcastDetail(p, link);
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
