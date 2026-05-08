// Fetch a podcast RSS feed and extract:
//   - <itunes:owner><itunes:email>  ← canonical contact email
//   - <itunes:author> / <managingEditor>  ← host name fallback
//   - latest <item><title>          ← recent_episode hook
//
// We use fast-xml-parser to avoid pulling a full XML lib. Tolerates
// malformed feeds by returning {} rather than throwing.

import { XMLParser } from "fast-xml-parser";

const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  removeNSPrefix: false,
  textNodeName: "#text",
});

const FETCH_TIMEOUT_MS = 12_000;

async function fetchWithTimeout(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "accept": "application/rss+xml, application/xml, text/xml, */*",
      },
      redirect: "follow",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } finally {
    clearTimeout(t);
  }
}

function pluck(obj, keys) {
  for (const k of keys) {
    if (obj && obj[k] != null) {
      const v = obj[k];
      if (typeof v === "string") return v;
      if (typeof v === "object" && v["#text"]) return v["#text"];
    }
  }
  return null;
}

export async function extractFromRss(rssUrl) {
  if (!rssUrl) return {};
  let xml;
  try {
    xml = await fetchWithTimeout(rssUrl);
  } catch (e) {
    return { _error: `fetch: ${e.message}` };
  }

  let doc;
  try {
    doc = parser.parse(xml);
  } catch (e) {
    return { _error: `parse: ${e.message}` };
  }

  const channel = doc?.rss?.channel || doc?.feed || doc?.["rdf:RDF"]?.channel;
  if (!channel) return { _error: "no channel element" };

  const ownerNode = channel["itunes:owner"];
  let ownerEmail = null;
  let ownerName = null;
  if (ownerNode) {
    ownerEmail = pluck(ownerNode, ["itunes:email", "email"]);
    ownerName = pluck(ownerNode, ["itunes:name", "name"]);
  }

  // Fallbacks
  const authorRaw = pluck(channel, ["itunes:author", "author", "dc:creator"]);
  const managingEditor = pluck(channel, ["managingEditor"]);
  // managingEditor format is "email (Name)" — split.
  let editorName = null;
  let editorEmail = null;
  if (managingEditor) {
    const m = managingEditor.match(/^([^\s(]+)\s*\(([^)]+)\)/);
    if (m) {
      editorEmail = m[1];
      editorName = m[2];
    } else if (/@/.test(managingEditor)) {
      editorEmail = managingEditor.trim();
    }
  }

  const items = channel.item ? (Array.isArray(channel.item) ? channel.item : [channel.item]) : [];
  const latestEpisode = items[0]?.title || null;

  return {
    email: (ownerEmail || editorEmail || "").trim() || null,
    host_name: (ownerName || authorRaw || editorName || "").trim() || null,
    podcast_name: pluck(channel, ["title"]),
    description: pluck(channel, ["description", "itunes:summary"]),
    website: pluck(channel, ["link"]),
    latest_episode: typeof latestEpisode === "string" ? latestEpisode : (latestEpisode?.["#text"] || null),
  };
}

export function isLowQualityEmail(email, prefixes) {
  if (!email) return true;
  const local = email.toLowerCase().split("@")[0];
  return prefixes.some((p) => local === p || local.startsWith(p + ".") || local.startsWith(p + "-"));
}

export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((email || "").trim());
}
