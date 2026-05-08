// Render initial-outreach.md with placeholders. Frontmatter declares
// subject + from. Body has three substitutions:
//   {podcast_name}    — required
//   {host_first}      — defaults to "there"
//   {recent_episode}  — optional (the line "I've been listening to ..." is
//                       only emitted if a recent episode title is provided)
//
// Returns { subject, fromName, fromEmail, body }.

import fs from "node:fs/promises";
import { TEMPLATE_FILE } from "../runtime/paths.mjs";

let cached = null;

async function loadTemplate() {
  if (cached) return cached;
  const raw = await fs.readFile(TEMPLATE_FILE, "utf8");
  // Minimal frontmatter parser — no need for gray-matter for 3 fields.
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) throw new Error(`template missing frontmatter: ${TEMPLATE_FILE}`);
  const fm = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^(\w+):\s*"?([^"]*)"?$/);
    if (kv) fm[kv[1]] = kv[2];
  }
  cached = { fm, body: m[2] };
  return cached;
}

function firstNameOf(host) {
  if (!host) return "";
  const trimmed = String(host).trim();
  if (!trimmed) return "";
  // Crude — first whitespace-separated token, drop honorifics.
  const tokens = trimmed.split(/\s+/);
  let first = tokens[0];
  if (/^(dr|mr|mrs|ms|mx|prof|professor)\.?$/i.test(first) && tokens[1]) {
    first = tokens[1];
  }
  return first.replace(/[^A-Za-z'\-]/g, "");
}

export async function renderEmail(vars) {
  const { fm, body } = await loadTemplate();
  if (!vars.podcast_name) {
    throw new Error("renderEmail: podcast_name is required");
  }
  const hostFirst = firstNameOf(vars.host_name) || "there";
  const recentLine = vars.recent_episode
    ? `\nI caught your recent episode "${vars.recent_episode}" — really enjoyed it.\n`
    : "";

  let rendered = body
    .replaceAll("{podcast_name}", vars.podcast_name)
    .replaceAll("{host_first}", hostFirst);

  // Insert recent-episode line after the first paragraph if present.
  if (recentLine) {
    rendered = rendered.replace(
      /(simple, low-effort revenue opportunity for [^.]+\.\n)/,
      `$1${recentLine}`,
    );
  }

  return {
    subject: fm.subject || "Interested in Licensing Your Podcast Library?",
    fromName: fm.from_name || "Adithya",
    fromEmail: fm.from || "adithya@eclipse.builders",
    body: rendered.trim() + "\n",
    vars: { ...vars, host_first: hostFirst },
  };
}
