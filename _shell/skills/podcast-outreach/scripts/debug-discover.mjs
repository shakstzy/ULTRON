#!/usr/bin/env node
// Diagnostic — runs discover for a small seed batch and dumps RAW candidate
// objects (pre-dedup) so we can see what the scrape actually extracted.
// Not part of the production verbs.

import { launchPersistent } from "../src/discover/launcher.mjs";
import { discoverFromSeeds } from "../src/discover/listennotes.mjs";

const seeds = [
  { kind: "query", q: "crypto founder interview" },
  { kind: "genre", slug: "technology" },
];

const { ctx } = await launchPersistent({ headless: true });
try {
  const candidates = await discoverFromSeeds({
    ctx,
    seeds,
    concurrency: 3,
    perSeedMax: 4,
    capsCfg: { discover_per_seed_max: 4 },
  });
  console.log("\n=== RAW CANDIDATES ===");
  for (const c of candidates) {
    console.log(JSON.stringify({
      podcast_name: c.podcast_name,
      email: c.email,
      host_name: c.host_name,
      website: c.website,
      rss_url: c.rss_url,
      sniff_count: c._sniff_count,
    }));
  }
  console.log(`\nTotal: ${candidates.length} candidates, ${candidates.filter(c => c.email).length} with email`);
} finally {
  await ctx.close();
}
